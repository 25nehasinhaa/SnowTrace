from html import escape

import streamlit as st

from lib.data import (
    format_currency,
    get_data_source_label,
    get_snowpark_session,
    load_drift_summary,
    render_timeframe_selector,
)
from lib.theme import action_card, inject_css, metric_card


st.set_page_config(page_title="Executive Brief | SnowTrace", page_icon=":material/description:", layout="wide")
inject_css()

session = get_snowpark_session()
baseline_start, baseline_end, comparison_start, comparison_end = render_timeframe_selector()
df = load_drift_summary(session, baseline_start, baseline_end, comparison_start, comparison_end)

if df.empty:
    st.info("No categories are available for the selected periods. Adjust the timeframe to generate an executive brief.")
    st.stop()

drifting = df[df["DRIFT_STATUS"] == "DRIFT"].copy()
drifting["PRIORITY_SCORE"] = drifting[["REVENUE_CHANGE_PCT", "VOLUME_CHANGE_PCT", "PRICE_CHANGE_PCT"]].abs().fillna(0).sum(axis=1)
drifting["REVENUE_EXPOSURE"] = (drifting["BASELINE_REVENUE"] - drifting["CURRENT_REVENUE"]).clip(lower=0).fillna(0)
drifting = drifting.sort_values(["PRIORITY_SCORE", "DEPARTMENT"], ascending=[False, True])

st.markdown(
    f"""
    <section class="brief-hero">
        <div class="brief-hero-inner">
            <div class="brief-kicker">Executive decision brief</div>
            <div class="brief-title">Where commercial attention is needed now</div>
            <div class="brief-lede">A focused view of the categories moving furthest from plan, the revenue currently exposed, and the next decisions for merchandising leaders.</div>
            <div class="brief-period">{baseline_start:%d %b %Y} - {baseline_end:%d %b %Y} baseline &nbsp; / &nbsp; {comparison_start:%d %b %Y} - {comparison_end:%d %b %Y} current</div>
        </div>
    </section>
    """,
    unsafe_allow_html=True,
)

drift_count = len(drifting)
revenue_exposure = drifting["REVENUE_EXPOSURE"].sum()
high_confidence_count = int((drifting["CONFIDENCE_LEVEL"] == "High").sum())
top_division = drifting["DIVISION"].value_counts().index[0] if not drifting.empty else "No concentration"
top_department = drifting.iloc[0]["DEPARTMENT"] if not drifting.empty else "No active alert"

kpi_top = st.columns(2)
with kpi_top[0]:
    metric_card("Categories flagged", str(drift_count), "Departments outside the active movement thresholds.")
with kpi_top[1]:
    metric_card("Revenue exposure", format_currency(revenue_exposure), "Baseline revenue not retained in flagged categories.")

kpi_bottom = st.columns(2)
with kpi_bottom[0]:
    metric_card("High-confidence signals", str(high_confidence_count), "Alerts supported by the strongest transaction volume.")
with kpi_bottom[1]:
    metric_card("Largest concentration", top_division, f"Most flagged categories; first review: {top_department}.")

if drifting.empty:
    st.success("No categories are outside the active thresholds for this comparison window.")
else:
    st.markdown(
        f"""
        <section class="executive-pulse">
            <div class="pulse-label">Executive pulse</div>
            <div class="pulse-title">{escape(str(top_division))} carries the largest concentration of flagged categories.</div>
            <div class="pulse-copy">Across {drift_count} alerts, estimated downside exposure is {escape(format_currency(revenue_exposure))}. Start with {escape(str(top_department))}, then validate availability, promotion mix, and customer experience before changing the commercial plan.</div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("Priority decisions")
    st.caption("The six strongest shifts, ranked by combined revenue, unit, and price movement.")
    priority_rows = list(drifting.head(6).itertuples(index=False))
    for row_start in range(0, len(priority_rows), 2):
        columns = st.columns(2)
        for offset, row in enumerate(priority_rows[row_start : row_start + 2]):
            with columns[offset]:
                action_card(
                    row_start + offset + 1,
                    row.DIVISION,
                    row.DEPARTMENT,
                    float(row.REVENUE_CHANGE_PCT),
                    float(row.VOLUME_CHANGE_PCT),
                    float(row.PRICE_CHANGE_PCT),
                    row.BUSINESS_EXPLANATION,
                    row.RECOMMENDED_ACTION,
                )

    st.subheader("Division exposure")
    st.markdown('<div class="brief-table-note">A compact roll-up for allocating analyst and category-lead attention.</div>', unsafe_allow_html=True)
    division_summary = (
        drifting.groupby("DIVISION", as_index=False)
        .agg(
            FLAGGED_CATEGORIES=("DEPARTMENT", "count"),
            CURRENT_REVENUE=("CURRENT_REVENUE", "sum"),
            REVENUE_EXPOSURE=("REVENUE_EXPOSURE", "sum"),
            AVG_REVENUE_CHANGE=("REVENUE_CHANGE_PCT", "mean"),
        )
        .sort_values(["REVENUE_EXPOSURE", "FLAGGED_CATEGORIES"], ascending=[False, False])
        .rename(
            columns={
                "DIVISION": "Division",
                "FLAGGED_CATEGORIES": "Flagged categories",
                "CURRENT_REVENUE": "Current revenue (BRL)",
                "REVENUE_EXPOSURE": "Revenue exposure (BRL)",
                "AVG_REVENUE_CHANGE": "Avg revenue change",
            }
        )
    )
    st.dataframe(
        division_summary,
        width="stretch",
        hide_index=True,
        column_config={
            "Division": st.column_config.TextColumn(width="large", pinned=True),
            "Flagged categories": st.column_config.NumberColumn(format="%d"),
            "Current revenue (BRL)": st.column_config.NumberColumn(format="%.2f"),
            "Revenue exposure (BRL)": st.column_config.NumberColumn(format="%.2f"),
            "Avg revenue change": st.column_config.NumberColumn(format="%.1f%%"),
        },
    )

lines = [
    "# SnowTrace Executive Brief",
    "",
    f"Source: {get_data_source_label(session, df)}",
    f"Baseline period: {baseline_start} to {baseline_end}",
    f"Comparison period: {comparison_start} to {comparison_end}",
    "",
    f"Categories flagged: {drift_count}",
    f"Revenue exposure: {format_currency(revenue_exposure)}",
    f"Highest priority: {top_department}",
    "",
    "## Recommended actions",
    "",
]
if drifting.empty:
    lines.append("No categories were outside the active movement thresholds.")
else:
    for row in drifting.itertuples(index=False):
        lines.extend(
            [
                f"### {row.DIVISION} / {row.DEPARTMENT}",
                str(row.BUSINESS_EXPLANATION),
                f"Recommended action: {row.RECOMMENDED_ACTION}",
                "",
            ]
        )

st.divider()
footer_left, footer_right = st.columns([2, 1], vertical_alignment="center")
with footer_left:
    with st.container(horizontal=True, wrap=True, gap="small"):
        st.page_link("pages/1_Where_Behavior_Shifts.py", label="Return to drift map", icon=":material/arrow_back:")
        st.page_link("pages/2_What_If_We_Act.py", label="Open scenario lab", icon=":material/tune:")
with footer_right:
    st.download_button(
        "Download full brief",
        data="\n".join(lines),
        file_name="snowtrace_executive_brief.md",
        mime="text/markdown",
        icon=":material/download:",
        width="stretch",
    )
