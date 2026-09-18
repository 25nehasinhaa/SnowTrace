from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd
import streamlit as st


APP_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = APP_ROOT.parent
SAMPLE_PATH = PROJECT_ROOT / "data" / "drift_summary_sample.csv"
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

DEFAULT_BASELINE = (date(2018, 7, 1), date(2018, 7, 31))
DEFAULT_COMPARISON = (date(2018, 8, 1), date(2018, 8, 31))

DIVISION_MAP = {
    "health_beauty": "Beauty & Wellness",
    "perfumery": "Beauty & Wellness",
    "fashion_bags_accessories": "Fashion",
    "fashion_shoes": "Fashion",
    "fashion_male_clothing": "Fashion",
    "fashion_female_clothing": "Fashion",
    "fashion_underwear_beach": "Fashion",
    "watches_gifts": "Fashion",
    "bed_bath_table": "Home & Living",
    "furniture_decor": "Home & Living",
    "housewares": "Home & Living",
    "home_confort": "Home & Living",
    "home_comfort_2": "Home & Living",
    "garden_tools": "Home & Living",
    "computers_accessories": "Electronics",
    "telephony": "Electronics",
    "electronics": "Electronics",
    "audio": "Electronics",
    "small_appliances": "Electronics",
    "sports_leisure": "Lifestyle",
    "toys": "Lifestyle",
    "books_general_interest": "Lifestyle",
    "books_technical": "Lifestyle",
    "stationery": "Lifestyle",
    "pet_shop": "Lifestyle",
}


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
        key="baseline_range",
    )
    comparison = st.sidebar.date_input(
        "Comparison period",
        key="comparison_range",
    )
    baseline_start, baseline_end = _coerce_range(baseline, DEFAULT_BASELINE)
    comparison_start, comparison_end = _coerce_range(comparison, DEFAULT_COMPARISON)
    if baseline_start <= comparison_end and comparison_start <= baseline_end:
        st.sidebar.warning("The baseline and comparison periods overlap, so some orders contribute to both windows.")
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


@st.cache_data(ttl=300, show_spinner="Loading retail signals...")
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
        try:
            result = _query_snowflake(
                _session,
                baseline_start,
                baseline_end,
                comparison_start,
                comparison_end,
            )
            result.attrs["snowtrace_data_source"] = "Snowflake warehouse"
            return result
        except Exception:
            fallback_source = "Local fallback (Snowflake unavailable)"
    else:
        fallback_source = None

    if _raw_olist_available():
        result = _build_local_olist_summary(
            baseline_start,
            baseline_end,
            comparison_start,
            comparison_end,
        )
        result.attrs["snowtrace_data_source"] = fallback_source or "Olist commerce"
        return result

    df = pd.read_csv(SAMPLE_PATH, parse_dates=["BASELINE_START", "BASELINE_END", "COMPARISON_START", "COMPARISON_END"])
    df["BASELINE_START"] = pd.to_datetime(baseline_start)
    df["BASELINE_END"] = pd.to_datetime(baseline_end)
    df["COMPARISON_START"] = pd.to_datetime(comparison_start)
    df["COMPARISON_END"] = pd.to_datetime(comparison_end)
    df.attrs["snowtrace_data_source"] = fallback_source or "Local sample dataset"
    return df


def get_data_source_label(session, summary: pd.DataFrame | None = None) -> str:
    if summary is not None and summary.attrs.get("snowtrace_data_source"):
        return str(summary.attrs["snowtrace_data_source"])
    if session is not None:
        return "Snowflake warehouse"
    if _raw_olist_available():
        return "Olist commerce"
    return "Local sample dataset"


def _raw_olist_available() -> bool:
    required = [
        "olist_orders_dataset.csv",
        "olist_order_items_dataset.csv",
        "olist_products_dataset.csv",
        "olist_order_reviews_dataset.csv",
        "product_category_name_translation.csv",
    ]
    return all((RAW_DATA_DIR / filename).exists() for filename in required)


def _build_local_olist_summary(
    baseline_start: date,
    baseline_end: date,
    comparison_start: date,
    comparison_end: date,
) -> pd.DataFrame:
    fact = _load_local_order_fact()
    baseline = _aggregate_period(fact, baseline_start, baseline_end, "baseline")
    comparison = _aggregate_period(fact, comparison_start, comparison_end, "current")

    df = baseline.merge(comparison, on=["DIVISION", "DEPARTMENT"], how="outer")
    df["BASELINE_START"] = pd.to_datetime(baseline_start)
    df["BASELINE_END"] = pd.to_datetime(baseline_end)
    df["COMPARISON_START"] = pd.to_datetime(comparison_start)
    df["COMPARISON_END"] = pd.to_datetime(comparison_end)

    df["VOLUME_CHANGE_PCT"] = _pct_change(df["CURRENT_VOLUME"], df["BASELINE_VOLUME"])
    df["PRICE_CHANGE_PCT"] = _pct_change(df["CURRENT_AVG_PRICE"], df["BASELINE_AVG_PRICE"])
    df["REVENUE_CHANGE_PCT"] = _pct_change(df["CURRENT_REVENUE"], df["BASELINE_REVENUE"])
    df["REVIEW_SCORE_CHANGE"] = (df["CURRENT_REVIEW_SCORE"] - df["BASELINE_REVIEW_SCORE"]).round(2)
    df["DELIVERY_DAYS_CHANGE"] = (df["CURRENT_DELIVERY_DAYS"] - df["BASELINE_DELIVERY_DAYS"]).round(2)

    df["DRIFT_STATUS"] = df.apply(_classify_drift, axis=1)
    df["CONFIDENCE_LEVEL"] = df.apply(_confidence_level, axis=1)
    df["DRIFT_SEVERITY_SCORE"] = (
        df[["PRICE_CHANGE_PCT", "VOLUME_CHANGE_PCT", "REVENUE_CHANGE_PCT"]].abs().fillna(0).sum(axis=1)
    )
    df["DRIFT_SEVERITY_RANK"] = (
        df.groupby("DIVISION")["DRIFT_SEVERITY_SCORE"].rank(method="dense", ascending=False).astype(int)
    )
    df["DIVISION_AVG_PRICE_CHANGE"] = df.groupby("DIVISION")["PRICE_CHANGE_PCT"].transform("mean").round(2)
    df["BUSINESS_EXPLANATION"] = df.apply(_business_explanation, axis=1)
    df["RECOMMENDED_ACTION"] = df.apply(_recommended_action, axis=1)

    ordered = [
        "DIVISION",
        "DEPARTMENT",
        "BASELINE_START",
        "BASELINE_END",
        "COMPARISON_START",
        "COMPARISON_END",
        "BASELINE_VOLUME",
        "CURRENT_VOLUME",
        "BASELINE_AVG_PRICE",
        "CURRENT_AVG_PRICE",
        "BASELINE_REVENUE",
        "CURRENT_REVENUE",
        "VOLUME_CHANGE_PCT",
        "PRICE_CHANGE_PCT",
        "REVENUE_CHANGE_PCT",
        "REVIEW_SCORE_CHANGE",
        "DELIVERY_DAYS_CHANGE",
        "DRIFT_STATUS",
        "CONFIDENCE_LEVEL",
        "DRIFT_SEVERITY_RANK",
        "DIVISION_AVG_PRICE_CHANGE",
        "BUSINESS_EXPLANATION",
        "RECOMMENDED_ACTION",
    ]
    return df[ordered].sort_values(["DIVISION", "DRIFT_SEVERITY_RANK", "DEPARTMENT"]).reset_index(drop=True)


@st.cache_data(show_spinner=False)
def _load_local_order_fact() -> pd.DataFrame:
    orders = pd.read_csv(
        RAW_DATA_DIR / "olist_orders_dataset.csv",
        usecols=[
            "order_id",
            "order_status",
            "order_purchase_timestamp",
            "order_delivered_customer_date",
            "order_estimated_delivery_date",
        ],
        parse_dates=[
            "order_purchase_timestamp",
            "order_delivered_customer_date",
            "order_estimated_delivery_date",
        ],
    )
    items = pd.read_csv(
        RAW_DATA_DIR / "olist_order_items_dataset.csv",
        usecols=["order_id", "order_item_id", "product_id", "price", "freight_value"],
    )
    items = items.drop_duplicates(["order_id", "order_item_id"])
    products = pd.read_csv(
        RAW_DATA_DIR / "olist_products_dataset.csv",
        usecols=["product_id", "product_category_name"],
    )
    products = products.drop_duplicates("product_id")
    translations = pd.read_csv(RAW_DATA_DIR / "product_category_name_translation.csv")
    translations = translations.drop_duplicates("product_category_name")
    reviews = pd.read_csv(
        RAW_DATA_DIR / "olist_order_reviews_dataset.csv",
        usecols=["order_id", "review_score"],
    ).groupby("order_id", as_index=False)["review_score"].mean()

    fact = (
        items.merge(orders, on="order_id", how="inner")
        .merge(products, on="product_id", how="left")
        .merge(translations, on="product_category_name", how="left")
        .merge(reviews, on="order_id", how="left")
    )
    fact = fact[fact["order_status"].isin(["delivered", "shipped", "invoiced"])].copy()
    fact["ORDER_DATE"] = fact["order_purchase_timestamp"].dt.date
    fact["DEPARTMENT"] = (
        fact["product_category_name_english"]
        .fillna(fact["product_category_name"])
        .fillna("uncategorized")
        .str.replace("_", " ")
        .str.title()
    )
    fact["DIVISION"] = fact["product_category_name_english"].map(DIVISION_MAP).fillna("Marketplace")
    fact["DELIVERY_DAYS"] = (
        fact["order_delivered_customer_date"] - fact["order_purchase_timestamp"]
    ).dt.total_seconds() / 86400
    fact["REVENUE"] = fact["price"].fillna(0) + fact["freight_value"].fillna(0)
    return fact


def _aggregate_period(fact: pd.DataFrame, start: date, end: date, prefix: str) -> pd.DataFrame:
    period = fact[(fact["ORDER_DATE"] >= start) & (fact["ORDER_DATE"] <= end)]
    grouped = period.groupby(["DIVISION", "DEPARTMENT"], as_index=False).agg(
        VOLUME=("order_item_id", "count"),
        REVENUE=("REVENUE", "sum"),
        AVG_PRICE=("price", "mean"),
        REVIEW_SCORE=("review_score", "mean"),
        DELIVERY_DAYS=("DELIVERY_DAYS", "mean"),
    )
    rename = {
        "VOLUME": f"{prefix.upper()}_VOLUME",
        "REVENUE": f"{prefix.upper()}_REVENUE",
        "AVG_PRICE": f"{prefix.upper()}_AVG_PRICE",
        "REVIEW_SCORE": f"{prefix.upper()}_REVIEW_SCORE",
        "DELIVERY_DAYS": f"{prefix.upper()}_DELIVERY_DAYS",
    }
    return grouped.rename(columns=rename)


def _pct_change(current: pd.Series, baseline: pd.Series) -> pd.Series:
    numeric_current = pd.to_numeric(current, errors="coerce")
    numeric_baseline = pd.to_numeric(baseline, errors="coerce")
    return (((numeric_current - numeric_baseline) / numeric_baseline.mask(numeric_baseline == 0)) * 100).round(2)


def _classify_drift(row: pd.Series) -> str:
    if pd.isna(row.get("BASELINE_VOLUME")) or pd.isna(row.get("CURRENT_VOLUME")):
        return "INSUFFICIENT_DATA"
    if (
        abs(row.get("PRICE_CHANGE_PCT", 0)) >= 8
        or abs(row.get("VOLUME_CHANGE_PCT", 0)) >= 18
        or abs(row.get("REVENUE_CHANGE_PCT", 0)) >= 20
        or abs(row.get("REVIEW_SCORE_CHANGE", 0)) >= 0.4
    ):
        return "DRIFT"
    return "STABLE"


def _confidence_level(row: pd.Series) -> str:
    if pd.isna(row.get("BASELINE_VOLUME")) or pd.isna(row.get("CURRENT_VOLUME")):
        return "Low"
    volume = float(row.get("BASELINE_VOLUME", 0)) + float(row.get("CURRENT_VOLUME", 0))
    if volume >= 400:
        return "High"
    if volume >= 120:
        return "Medium"
    return "Directional"


def _business_explanation(row: pd.Series) -> str:
    if row["DRIFT_STATUS"] == "INSUFFICIENT_DATA":
        return f"{row['DEPARTMENT']} needs more complete order history before a reliable read is possible."
    if row["DRIFT_STATUS"] == "DRIFT":
        return (
            f"{row['DEPARTMENT']} moved materially versus the baseline, with "
            f"{row['REVENUE_CHANGE_PCT']:.1f}% revenue change, {row['VOLUME_CHANGE_PCT']:.1f}% unit change, "
            f"and {row['PRICE_CHANGE_PCT']:.1f}% average price movement."
        )
    return f"{row['DEPARTMENT']} is broadly stable versus the selected baseline period."


def _recommended_action(row: pd.Series) -> str:
    if row["DRIFT_STATUS"] == "INSUFFICIENT_DATA":
        return "Collect another cycle of orders before changing the commercial plan."
    if row["REVENUE_CHANGE_PCT"] < -20 and row["VOLUME_CHANGE_PCT"] < -18:
        return "Review demand generation, availability, and merchandising placement before discounting."
    if row["PRICE_CHANGE_PCT"] > 8 and row["VOLUME_CHANGE_PCT"] < 0:
        return "Test targeted offers or bundles for high-intent customers instead of broad markdowns."
    if row["REVIEW_SCORE_CHANGE"] < -0.4:
        return "Check product quality signals and delivery experience before scaling promotions."
    if row["DELIVERY_DAYS_CHANGE"] > 2:
        return "Investigate fulfillment delays that may be suppressing repeat demand."
    return "Monitor the department and keep the current commercial plan."


def _query_snowflake(
    session,
    baseline_start: date,
    baseline_end: date,
    comparison_start: date,
    comparison_end: date,
) -> pd.DataFrame:
    query = """
        WITH order_fact AS (
            SELECT
                COALESCE(cm.division, 'Marketplace') AS division,
                INITCAP(REPLACE(COALESCE(t.product_category_name_english, p.product_category_name, 'uncategorized'), '_', ' ')) AS department,
                CAST(o.order_purchase_timestamp AS DATE) AS order_date,
                oi.order_item_id,
                oi.price,
                oi.freight_value,
                oi.price + oi.freight_value AS revenue,
                r.review_score,
                DATEDIFF('day', o.order_purchase_timestamp, o.order_delivered_customer_date) AS delivery_days
            FROM raw.order_items oi
            INNER JOIN raw.orders o ON oi.order_id = o.order_id
            LEFT JOIN raw.products p ON oi.product_id = p.product_id
            LEFT JOIN raw.product_category_name_translation t ON p.product_category_name = t.product_category_name
            LEFT JOIN raw.category_map cm ON t.product_category_name_english = cm.product_category_name_english
            LEFT JOIN (
                SELECT order_id, AVG(review_score) AS review_score
                FROM raw.order_reviews
                GROUP BY order_id
            ) r ON oi.order_id = r.order_id
            WHERE o.order_status IN ('delivered', 'shipped', 'invoiced')
        ),
        baseline AS (
            SELECT
                division,
                department,
                COUNT(*) AS baseline_volume,
                SUM(revenue) AS baseline_revenue,
                AVG(price) AS baseline_avg_price,
                AVG(review_score) AS baseline_review_score,
                AVG(delivery_days) AS baseline_delivery_days
            FROM order_fact
            WHERE order_date BETWEEN ? AND ?
            GROUP BY division, department
        ),
        comparison AS (
            SELECT
                division,
                department,
                COUNT(*) AS current_volume,
                SUM(revenue) AS current_revenue,
                AVG(price) AS current_avg_price,
                AVG(review_score) AS current_review_score,
                AVG(delivery_days) AS current_delivery_days
            FROM order_fact
            WHERE order_date BETWEEN ? AND ?
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
                ROUND(b.baseline_revenue, 2) AS baseline_revenue,
                ROUND(c.current_revenue, 2) AS current_revenue,
                ROUND(((c.current_volume - b.baseline_volume) / NULLIF(b.baseline_volume, 0)) * 100, 2) AS volume_change_pct,
                ROUND(((c.current_avg_price - b.baseline_avg_price) / NULLIF(b.baseline_avg_price, 0)) * 100, 2) AS price_change_pct,
                ROUND(((c.current_revenue - b.baseline_revenue) / NULLIF(b.baseline_revenue, 0)) * 100, 2) AS revenue_change_pct,
                ROUND(c.current_review_score - b.baseline_review_score, 2) AS review_score_change,
                ROUND(c.current_delivery_days - b.baseline_delivery_days, 2) AS delivery_days_change
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
                    WHEN ABS(price_change_pct) >= 8 OR ABS(volume_change_pct) >= 18 OR ABS(revenue_change_pct) >= 20 OR ABS(review_score_change) >= 0.4 THEN 'DRIFT'
                    ELSE 'STABLE'
                END AS drift_status,
                CASE
                    WHEN baseline_volume IS NULL OR current_volume IS NULL THEN 'Low'
                    WHEN baseline_volume + current_volume >= 400 THEN 'High'
                    WHEN baseline_volume + current_volume >= 120 THEN 'Medium'
                    ELSE 'Directional'
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
            baseline_revenue,
            current_revenue,
            volume_change_pct,
            price_change_pct,
            revenue_change_pct,
            review_score_change,
            delivery_days_change,
            drift_status,
            confidence_level,
            RANK() OVER (
                PARTITION BY division
                ORDER BY
                    COALESCE(ABS(price_change_pct), 0)
                    + COALESCE(ABS(volume_change_pct), 0)
                    + COALESCE(ABS(revenue_change_pct), 0) DESC
            ) AS drift_severity_rank,
            ROUND(AVG(price_change_pct) OVER (PARTITION BY division), 2) AS division_avg_price_change,
            CASE
                WHEN baseline_volume IS NULL OR current_volume IS NULL THEN department || ' needs more complete order history before a reliable read is possible.'
                WHEN drift_status = 'DRIFT' THEN department || ' moved materially versus the baseline, with ' || revenue_change_pct || '% revenue change, ' || volume_change_pct || '% unit change, and ' || price_change_pct || '% average price movement.'
                ELSE department || ' is broadly stable versus the selected baseline period.'
            END AS business_explanation,
            CASE
                WHEN baseline_volume IS NULL OR current_volume IS NULL THEN 'Collect another cycle of orders before changing the commercial plan.'
                WHEN revenue_change_pct < -20 AND volume_change_pct < -18 THEN 'Review demand generation, availability, and merchandising placement before discounting.'
                WHEN price_change_pct > 8 AND volume_change_pct < 0 THEN 'Test targeted offers or bundles for high-intent customers instead of broad markdowns.'
                WHEN review_score_change < -0.4 THEN 'Check product quality signals and delivery experience before scaling promotions.'
                WHEN delivery_days_change > 2 THEN 'Investigate fulfillment delays that may be suppressing repeat demand.'
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


def format_currency(value: float) -> str:
    sign = "-" if value < 0 else ""
    return f"{sign}R$ {abs(value):,.0f}"
