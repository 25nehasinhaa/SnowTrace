import plotly.express as px
import streamlit as st

from lib.data import get_data_source_label, get_snowpark_session, load_drift_summary, render_timeframe_selector
from lib.theme import inject_css, metric_card


st.set_page_config(page_title="Where Behavior Shifts | SnowTrace", page_icon=":bar_chart:", layout="wide")
inject_css()

st.markdown('<div class="story-kicker">Where Behavior Is Shifting</div>', unsafe_allow_html=True)
st.title("Find the departments moving away from plan")

session = get_snowpark_session()
baseline_start, baseline_end, comparison_start, comparison_end = render_timeframe_selector()
df = load_drift_summary(session, baseline_start, baseline_end, comparison_start, comparison_end)

st.caption(f"Source: {get_data_source_label(session)}")

division_options = ["All"] + sorted(df["DIVISION"].dropna().unique().tolist())
selected_division = st.selectbox("Division", division_options)
filtered = df if selected_division == "All" else df[df["DIVISION"] == selected_division]

drift_count = int((filtered["DRIFT_STATUS"] == "DRIFT").sum())
avg_price_change = filtered["PRICE_CHANGE_PCT"].mean()
avg_volume_change = filtered["VOLUME_CHANGE_PCT"].mean()
top_ranked = filtered.sort_values(["DRIFT_SEVERITY_RANK", "DEPARTMENT"]).head(1)
top_department = top_ranked["DEPARTMENT"].iloc[0] if not top_ranked.empty else "None"

col1, col2, col3, col4 = st.columns(4)
with col1:
    metric_card("Departments in Drift", str(drift_count), "Flagged by price or volume movement.")
with col2:
    metric_card("Avg Price Change", f"{avg_price_change:.1f}%", "Across the selected departments.")
with col3:
    metric_card("Avg Volume Change", f"{avg_volume_change:.1f}%", "Versus the selected baseline.")
with col4:
    metric_card("Highest Priority", top_department, "The department with the strongest movement.")

st.subheader("Department movement")
fig = px.bar(
    filtered.sort_values("PRICE_CHANGE_PCT"),
    x="DEPARTMENT",
    y="PRICE_CHANGE_PCT",
    color="DRIFT_STATUS",
    hover_data=["DIVISION", "VOLUME_CHANGE_PCT", "DRIFT_SEVERITY_RANK", "DIVISION_AVG_PRICE_CHANGE"],
    color_discrete_map={"DRIFT": "#b96863", "STABLE": "#657761", "INSUFFICIENT_DATA": "#747474"},
)
fig.update_layout(
    xaxis_title="Department",
    yaxis_title="Price change %",
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font_family="Inter",
    height=430,
)
st.plotly_chart(fig, use_container_width=True)

st.subheader("Category readout")
display_columns = [
    "DIVISION",
    "DEPARTMENT",
    "DRIFT_STATUS",
    "CONFIDENCE_LEVEL",
    "PRICE_CHANGE_PCT",
    "VOLUME_CHANGE_PCT",
    "DRIFT_SEVERITY_RANK",
    "DIVISION_AVG_PRICE_CHANGE",
    "BUSINESS_EXPLANATION",
    "RECOMMENDED_ACTION",
]
st.dataframe(filtered[display_columns], use_container_width=True, hide_index=True)

st.subheader("Recommended actions")
for row in filtered.sort_values(["DRIFT_STATUS", "DRIFT_SEVERITY_RANK"]).itertuples(index=False):
    if row.DRIFT_STATUS == "DRIFT":
        st.markdown(
            f"""
            <div class="recommendation">
                <strong>{row.DEPARTMENT}</strong><br>
                {row.BUSINESS_EXPLANATION}<br>
                <em>{row.RECOMMENDED_ACTION}</em>
            </div>
            """,
            unsafe_allow_html=True,
        )
