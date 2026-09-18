from datetime import datetime

import pandas as pd
import streamlit as st

from lib.data import (
    format_currency,
    get_snowpark_session,
    load_drift_summary,
    render_timeframe_selector,
)
from lib.theme import inject_css, metric_card


st.set_page_config(page_title="What If We Act | SnowTrace", page_icon=":bar_chart:", layout="wide")
inject_css()

st.markdown('<div class="story-kicker">What Happens If We Act</div>', unsafe_allow_html=True)
st.title("Test a pricing move before it reaches the customer")

session = get_snowpark_session()
baseline_start, baseline_end, comparison_start, comparison_end = render_timeframe_selector()
df = load_drift_summary(session, baseline_start, baseline_end, comparison_start, comparison_end)

if df.empty:
    st.info("No categories are available for the selected periods. Adjust the timeframe to continue scenario planning.")
    st.stop()

if "saved_scenarios" not in st.session_state:
    st.session_state["saved_scenarios"] = []

departments = sorted(df["DEPARTMENT"].dropna().unique().tolist())
selected_department = st.selectbox("Department", departments)
row = df[df["DEPARTMENT"] == selected_department].iloc[0]

slider_key = f"proposed_price_delta_{selected_department}"
if slider_key not in st.session_state:
    st.session_state[slider_key] = 0.0

price_delta = st.slider(
    "Proposed additional price change",
    min_value=-25.0,
    max_value=25.0,
    step=0.5,
    format="%.1f%%",
    key=slider_key,
)

current_price_change = float(row.PRICE_CHANGE_PCT)
simulated_price_change = current_price_change + float(price_delta)
volume_change = float(row.VOLUME_CHANGE_PCT)
current_volume = float(row.CURRENT_VOLUME) if pd.notna(row.CURRENT_VOLUME) else 0.0
current_price = float(row.CURRENT_AVG_PRICE) if pd.notna(row.CURRENT_AVG_PRICE) else 0.0
revenue_impact = current_volume * current_price * (float(price_delta) / 100)
current_revenue = float(row.CURRENT_REVENUE) if pd.notna(row.CURRENT_REVENUE) else 0.0
baseline_revenue = float(row.BASELINE_REVENUE) if pd.notna(row.BASELINE_REVENUE) else 0.0
simulated_revenue_change = (
    ((current_revenue + revenue_impact - baseline_revenue) / baseline_revenue) * 100
    if baseline_revenue
    else float("nan")
)

if pd.isna(row.BASELINE_VOLUME) or pd.isna(row.CURRENT_VOLUME):
    simulated_status = "INSUFFICIENT_DATA"
elif (
    abs(simulated_price_change) >= 8
    or abs(volume_change) >= 18
    or (pd.notna(simulated_revenue_change) and abs(simulated_revenue_change) >= 20)
    or (pd.notna(row.REVIEW_SCORE_CHANGE) and abs(float(row.REVIEW_SCORE_CHANGE)) >= 0.4)
):
    simulated_status = "DRIFT"
else:
    simulated_status = "STABLE"

kpi_top = st.columns(2)
with kpi_top[0]:
    metric_card("Current Status", row.DRIFT_STATUS, "Before the proposed action.")
with kpi_top[1]:
    metric_card("Simulated Status", simulated_status, "After applying the slider value.")
kpi_bottom = st.columns(2)
with kpi_bottom[0]:
    metric_card("New Price Change", f"{simulated_price_change:.1f}%", "Current drift plus proposed action.")
with kpi_bottom[1]:
    metric_card("Monthly Revenue Impact", format_currency(revenue_impact), "Current volume x current price x proposed change.")

st.markdown(
    """
    Adjust the proposed price move to see how the category status and monthly revenue impact change.
    Save several scenarios to compare options side by side during planning.
    """
)

if st.button("Save This Scenario"):
    st.session_state["saved_scenarios"].append(
        {
            "Saved At": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "Department": selected_department,
            "Division": row.DIVISION,
            "Additional Price Delta %": round(float(price_delta), 1),
            "Simulated Price Change %": round(simulated_price_change, 1),
            "Simulated Status": simulated_status,
            "Revenue Impact": revenue_impact,
            "Revenue Impact Label": format_currency(revenue_impact),
        }
    )
    st.success("Scenario saved for comparison.")

if st.session_state["saved_scenarios"] and st.button("Clear saved scenarios", type="tertiary"):
    st.session_state["saved_scenarios"] = []
    st.rerun()

st.subheader("Saved action scenarios")
if st.session_state["saved_scenarios"]:
    scenarios = pd.DataFrame(st.session_state["saved_scenarios"])
    st.dataframe(
        scenarios[
            [
                "Saved At",
                "Division",
                "Department",
                "Additional Price Delta %",
                "Simulated Price Change %",
                "Simulated Status",
                "Revenue Impact Label",
            ]
        ],
        width="stretch",
        hide_index=True,
    )
else:
    st.info("Save a scenario to begin comparing possible actions.")
