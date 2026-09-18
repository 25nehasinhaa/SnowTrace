from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd
import streamlit as st


APP_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = APP_ROOT.parent
SAMPLE_PATH = PROJECT_ROOT / "data" / "drift_summary_sample.csv"

DEFAULT_BASELINE = (date(2025, 12, 1), date(2025, 12, 31))
DEFAULT_COMPARISON = (date(2026, 1, 1), date(2026, 1, 31))


def init_timeframe_state() -> None:
    defaults = {
        "baseline_range": DEFAULT_BASELINE,
        "comparison_range": DEFAULT_COMPARISON,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_timeframe_selector() -> tuple[date, date, date, date]:
    init_timeframe_state()
    st.sidebar.markdown("### Timeframe")
    baseline = st.sidebar.date_input(
        "Baseline period",
        value=st.session_state["baseline_range"],
        key="baseline_range",
    )
    comparison = st.sidebar.date_input(
        "Comparison period",
        value=st.session_state["comparison_range"],
        key="comparison_range",
    )
    baseline_start, baseline_end = _coerce_range(baseline, DEFAULT_BASELINE)
    comparison_start, comparison_end = _coerce_range(comparison, DEFAULT_COMPARISON)
    return baseline_start, baseline_end, comparison_start, comparison_end


def _coerce_range(value, fallback: tuple[date, date]) -> tuple[date, date]:
    if isinstance(value, tuple) and len(value) == 2:
        return min(value), max(value)
    if isinstance(value, list) and len(value) == 2:
        return min(value), max(value)
    return fallback


@st.cache_resource(show_spinner=False)
def get_snowpark_session():
    try:
        from snowflake.snowpark.context import get_active_session

        return get_active_session()
    except Exception:
        return None


@st.cache_data(ttl=300, show_spinner="Loading drift signals...")
def load_drift_summary(
    _session,
    baseline_start: date,
    baseline_end: date,
    comparison_start: date,
    comparison_end: date,
) -> pd.DataFrame:
    # `_session` is intentionally prefixed with an underscore because Snowpark
    # session objects are not hashable/serializable. Streamlit excludes underscored
    # args from the cache key, while the date inputs still invalidate cached results.
    if _session is not None:
        return _query_snowflake(
            _session,
            baseline_start,
            baseline_end,
            comparison_start,
            comparison_end,
        )

    df = pd.read_csv(SAMPLE_PATH, parse_dates=["BASELINE_START", "BASELINE_END", "COMPARISON_START", "COMPARISON_END"])
    df["BASELINE_START"] = pd.to_datetime(baseline_start)
    df["BASELINE_END"] = pd.to_datetime(baseline_end)
    df["COMPARISON_START"] = pd.to_datetime(comparison_start)
    df["COMPARISON_END"] = pd.to_datetime(comparison_end)
    return df


def get_data_source_label(session) -> str:
    return "Snowflake warehouse" if session is not None else "Local sample dataset"


def _query_snowflake(
    session,
    baseline_start: date,
    baseline_end: date,
    comparison_start: date,
    comparison_end: date,
) -> pd.DataFrame:
    query = """
        WITH baseline AS (
            SELECT
                division,
                department,
                SUM(units_sold) AS baseline_volume,
                AVG(unit_price) AS baseline_avg_price
            FROM raw.retail_transactions
            WHERE transaction_date BETWEEN ? AND ?
            GROUP BY division, department
        ),
        comparison AS (
            SELECT
                division,
                department,
                SUM(units_sold) AS current_volume,
                AVG(unit_price) AS current_avg_price
            FROM raw.retail_transactions
            WHERE transaction_date BETWEEN ? AND ?
            GROUP BY division, department
        ),
        drift AS (
            SELECT
                COALESCE(b.division, c.division) AS division,
                COALESCE(b.department, c.department) AS department,
                ?::DATE AS baseline_start,
                ?::DATE AS baseline_end,
                ?::DATE AS comparison_start,
                ?::DATE AS comparison_end,
                b.baseline_volume,
                c.current_volume,
                ROUND(b.baseline_avg_price, 2) AS baseline_avg_price,
                ROUND(c.current_avg_price, 2) AS current_avg_price,
                ROUND(((c.current_volume - b.baseline_volume) / NULLIF(b.baseline_volume, 0)) * 100, 2) AS volume_change_pct,
                ROUND(((c.current_avg_price - b.baseline_avg_price) / NULLIF(b.baseline_avg_price, 0)) * 100, 2) AS price_change_pct
            FROM baseline b
            FULL OUTER JOIN comparison c
                ON b.division = c.division
               AND b.department = c.department
        ),
        scored AS (
            SELECT
                *,
                CASE
                    WHEN baseline_volume IS NULL OR current_volume IS NULL THEN 'INSUFFICIENT_DATA'
                    WHEN ABS(price_change_pct) >= 8 OR ABS(volume_change_pct) >= 18 THEN 'DRIFT'
                    ELSE 'STABLE'
                END AS drift_status,
                CASE
                    WHEN baseline_volume IS NULL OR current_volume IS NULL THEN 'Low'
                    WHEN baseline_volume + current_volume >= 250 THEN 'High'
                    ELSE 'Medium'
                END AS confidence_level
            FROM drift
        )
        SELECT
            division,
            department,
            baseline_start,
            baseline_end,
            comparison_start,
            comparison_end,
            baseline_volume,
            current_volume,
            baseline_avg_price,
            current_avg_price,
            volume_change_pct,
            price_change_pct,
            drift_status,
            confidence_level,
            RANK() OVER (PARTITION BY division ORDER BY ABS(price_change_pct) DESC NULLS LAST) AS drift_severity_rank,
            ROUND(AVG(price_change_pct) OVER (PARTITION BY division), 2) AS division_avg_price_change,
            CASE
                WHEN baseline_volume IS NULL OR current_volume IS NULL THEN 'This department needs more complete history before a reliable read is possible.'
                WHEN drift_status = 'DRIFT' THEN department || ' is moving differently from its holiday baseline, with a ' || price_change_pct || '% price change and ' || volume_change_pct || '% volume change.'
                ELSE department || ' is broadly stable versus the selected baseline period.'
            END AS business_explanation,
            CASE
                WHEN baseline_volume IS NULL OR current_volume IS NULL THEN 'Collect another cycle of transactions before taking action.'
                WHEN price_change_pct > 8 AND volume_change_pct < 0 THEN 'Test targeted offers or bundle mechanics before discounting the whole category.'
                WHEN price_change_pct < -8 AND volume_change_pct > 0 THEN 'Protect margin by narrowing promotions to high-intent customer segments.'
                WHEN ABS(volume_change_pct) >= 18 THEN 'Review inventory, campaign timing, and merchandising placement for this department.'
                ELSE 'Monitor the department and keep the current commercial plan.'
            END AS recommended_action
        FROM scored
        ORDER BY division, drift_severity_rank, department
    """

    # Bind parameters keep dynamic date filters out of the SQL string itself,
    # which avoids SQL injection risk and lets Snowflake reuse the query plan.
    params = [
        baseline_start,
        baseline_end,
        comparison_start,
        comparison_end,
        baseline_start,
        baseline_end,
        comparison_start,
        comparison_end,
    ]
    return session.sql(query, params=params).to_pandas()


def format_currency_rupees(value: float) -> str:
    sign = "-" if value < 0 else ""
    return f"{sign}Rs. {abs(value):,.0f}"
