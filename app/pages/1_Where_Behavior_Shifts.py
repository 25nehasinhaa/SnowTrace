import plotly.express as px
import streamlit as st

from lib.data import get_data_source_label, get_snowpark_session, load_drift_summary, render_timeframe_selector
from lib.theme import action_card, inject_css, metric_card


st.set_page_config(page_title="Where Behavior Shifts | SnowTrace", page_icon=":bar_chart:", layout="wide")
inject_css()

st.markdown('<div class="story-kicker">Where Behavior Is Shifting</div>', unsafe_allow_html=True)
st.title("Find the departments moving away from plan")

session = get_snowpark_session()
baseline_start, baseline_end, comparison_start, comparison_end = render_timeframe_selector()
df = load_drift_summary(session, baseline_start, baseline_end, comparison_start, comparison_end)

st.caption(f"Source: {get_data_source_label(session, df)}")

if df.empty:
    st.info("No completed-order activity was found for the selected periods. Choose dates that overlap the available order history.")
    st.stop()

division_options = ["All"] + sorted(df["DIVISION"].dropna().unique().tolist())
selected_division = st.selectbox("Division", division_options)
filtered = df if selected_division == "All" else df[df["DIVISION"] == selected_division]

drift_count = int((filtered["DRIFT_STATUS"] == "DRIFT").sum())
avg_price_change = filtered["PRICE_CHANGE_PCT"].mean()
avg_revenue_change = filtered["REVENUE_CHANGE_PCT"].mean() if "REVENUE_CHANGE_PCT" in filtered else filtered["VOLUME_CHANGE_PCT"].mean()
top_ranked = filtered.sort_values(["DRIFT_SEVERITY_RANK", "DEPARTMENT"]).head(1)
top_department = top_ranked["DEPARTMENT"].iloc[0] if not top_ranked.empty else "None"

kpi_top = st.columns(2)
with kpi_top[0]:
    metric_card("Departments in Drift", str(drift_count), "Flagged by price or volume movement.")
with kpi_top[1]:
    metric_card("Avg Price Change", f"{avg_price_change:.1f}%", "Across the selected departments.")
kpi_bottom = st.columns(2)
with kpi_bottom[0]:
    metric_card("Avg Revenue Change", f"{avg_revenue_change:.1f}%", "Versus the selected baseline.")
with kpi_bottom[1]:
    metric_card("Highest Priority", top_department, "The department with the strongest movement.")

st.subheader("Department movement")
chart_data = filtered.assign(ABS_PRICE_CHANGE=filtered["PRICE_CHANGE_PCT"].abs()).nlargest(20, "ABS_PRICE_CHANGE")
chart_data = chart_data.sort_values("PRICE_CHANGE_PCT")
fig = px.bar(
    chart_data,
    x="PRICE_CHANGE_PCT",
    y="DEPARTMENT",
    orientation="h",
    color="DRIFT_STATUS",
    hover_data=["DIVISION", "VOLUME_CHANGE_PCT", "DRIFT_SEVERITY_RANK", "DIVISION_AVG_PRICE_CHANGE"],
    color_discrete_map={"DRIFT": "#111111", "STABLE": "#B4C7CC", "INSUFFICIENT_DATA": "#4D4D4D"},
)
fig.update_layout(
    xaxis_title="Price change (%)",
    yaxis_title=None,
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font_family="Inter",
    height=max(460, min(820, 34 * len(chart_data) + 150)),
    margin=dict(l=220, r=24, t=24, b=48),
    legend_title_text="Status",
)
fig.update_xaxes(ticksuffix="%", zeroline=True, zerolinecolor="#A8BFD3", gridcolor="rgba(91,136,178,0.18)")
fig.update_yaxes(automargin=True, tickfont=dict(size=11))
st.plotly_chart(fig, width="stretch")
st.caption(f"Showing the {len(chart_data)} categories with the largest absolute price movement for the selected division.")

st.subheader("Category readout")
view_mode = st.segmented_control(
    "Category view",
    ["Priority only", "All categories"],
    default="Priority only",
    key="category_view",
    label_visibility="collapsed",
)

readout = filtered.copy()
readout["PRIORITY_SCORE"] = readout[["REVENUE_CHANGE_PCT", "VOLUME_CHANGE_PCT", "PRICE_CHANGE_PCT"]].abs().fillna(0).sum(axis=1)
readout = readout.sort_values(["PRIORITY_SCORE", "DEPARTMENT"], ascending=[False, True])
if view_mode == "Priority only":
    readout = readout[readout["DRIFT_STATUS"] == "DRIFT"].head(12)

display = readout[
    [
        "DIVISION",
        "DEPARTMENT",
        "DRIFT_STATUS",
        "CONFIDENCE_LEVEL",
        "CURRENT_REVENUE",
        "REVENUE_CHANGE_PCT",
        "VOLUME_CHANGE_PCT",
        "PRICE_CHANGE_PCT",
    ]
].rename(
    columns={
        "DIVISION": "Division",
        "DEPARTMENT": "Department",
        "DRIFT_STATUS": "Status",
        "CONFIDENCE_LEVEL": "Confidence",
        "CURRENT_REVENUE": "Current revenue (BRL)",
        "REVENUE_CHANGE_PCT": "Revenue change",
        "VOLUME_CHANGE_PCT": "Unit change",
        "PRICE_CHANGE_PCT": "Price change",
    }
)

st.dataframe(
    display,
    width="stretch",
    height=438,
    hide_index=True,
    column_config={
        "Division": st.column_config.TextColumn(width="medium", pinned=True),
        "Department": st.column_config.TextColumn(width="medium", pinned=True),
        "Status": st.column_config.TextColumn(width="small"),
        "Confidence": st.column_config.TextColumn(width="small"),
        "Current revenue (BRL)": st.column_config.NumberColumn(format="%.2f", width="small"),
        "Revenue change": st.column_config.NumberColumn(format="%.1f%%", width="small"),
        "Unit change": st.column_config.NumberColumn(format="%.1f%%", width="small"),
        "Price change": st.column_config.NumberColumn(format="%.1f%%", width="small"),
    },
)
st.caption(f"Showing {len(display)} of {len(filtered)} categories for the selected division.")

st.subheader("Recommended actions")
st.caption("The six strongest shifts, ranked by combined revenue, unit, and price movement.")
priorities = filtered[filtered["DRIFT_STATUS"] == "DRIFT"].copy()
priorities["PRIORITY_SCORE"] = priorities[["REVENUE_CHANGE_PCT", "VOLUME_CHANGE_PCT", "PRICE_CHANGE_PCT"]].abs().fillna(0).sum(axis=1)
priorities = priorities.sort_values(["PRIORITY_SCORE", "DEPARTMENT"], ascending=[False, True]).head(6)

priority_rows = list(priorities.itertuples(index=False))
for row_start in range(0, len(priority_rows), 2):
    action_columns = st.columns(2)
    for offset, row in enumerate(priority_rows[row_start : row_start + 2]):
        rank = row_start + offset + 1
        with action_columns[offset]:
            action_card(
                rank,
                row.DIVISION,
                row.DEPARTMENT,
                float(row.REVENUE_CHANGE_PCT),
                float(row.VOLUME_CHANGE_PCT),
                float(row.PRICE_CHANGE_PCT),
                row.BUSINESS_EXPLANATION,
                row.RECOMMENDED_ACTION,
            )

with st.container(horizontal=True, wrap=True, gap="small"):
    st.page_link("pages/2_What_If_We_Act.py", label="Model a pricing action", icon=":material/tune:")
    st.page_link("pages/4_Executive_Brief.py", label="Open executive brief", icon=":material/description:")
