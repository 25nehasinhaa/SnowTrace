import pandas as pd
import streamlit as st

from lib.data import get_snowpark_session, load_drift_summary, render_timeframe_selector
from lib.theme import inject_css


st.set_page_config(page_title="Pivot Builder | SnowTrace", page_icon=":bar_chart:", layout="wide")
inject_css()

st.markdown('<div class="story-kicker">Pivot Builder</div>', unsafe_allow_html=True)
st.title("Reshape the signal for category planning")

session = get_snowpark_session()
baseline_start, baseline_end, comparison_start, comparison_end = render_timeframe_selector()
df = load_drift_summary(session, baseline_start, baseline_end, comparison_start, comparison_end)

if df.empty:
    st.info("No categories are available for the selected periods. Adjust the timeframe to build a comparison.")
    st.stop()

row_options = {
    "Division": "DIVISION",
    "Department": "DEPARTMENT",
    "Confidence Level": "CONFIDENCE_LEVEL",
}
value_options = {
    "Price Change Percent": "PRICE_CHANGE_PCT",
    "Volume Change Percent": "VOLUME_CHANGE_PCT",
    "Revenue Change Percent": "REVENUE_CHANGE_PCT",
    "Review Score Change": "REVIEW_SCORE_CHANGE",
    "Delivery Days Change": "DELIVERY_DAYS_CHANGE",
}

col1, col2 = st.columns(2)
with col1:
    row_label = st.selectbox("Row grouping", list(row_options.keys()))
with col2:
    value_label = st.selectbox("Value column", list(value_options.keys()))

pivot = pd.pivot_table(
    df,
    index=row_options[row_label],
    columns="DRIFT_STATUS",
    values=value_options[value_label],
    aggfunc="mean",
).round(2)

st.dataframe(pivot, width="stretch")

st.caption(
    "Use this view to compare average movement across planning cuts without changing the underlying dataset."
)
