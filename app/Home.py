import streamlit as st

from lib.data import get_data_source_label, get_snowpark_session, init_timeframe_state
from lib.theme import inject_css, metric_card


st.set_page_config(
    page_title="SnowTrace | Retail Drift Intelligence",
    page_icon=":bar_chart:",
    layout="wide",
)
inject_css()
init_timeframe_state()

session = get_snowpark_session()

st.markdown(
    """
    <section class="brand-hero">
        <div class="story-kicker" style="color:rgba(246,241,232,0.72)">Retail Intelligence Suite</div>
        <div class="brand-mark">SnowTrace</div>
        <div class="brand-line">
        A decision workspace for spotting post-holiday demand shifts, testing commercial actions,
        and turning retail signals into a clear operating brief.
        </div>
        <div class="hero-nav">
            <span class="hero-pill">Demand drift</span>
            <span class="hero-pill">Pricing actions</span>
            <span class="hero-pill">Executive brief</span>
            <span class="hero-pill">Snowflake-ready</span>
        </div>
    </section>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="lede">
    Built for business teams that need to understand where customer behavior is changing, what action
    is worth testing, and which categories need attention before the next planning cycle.
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")

col1, col2, col3, col4 = st.columns(4)
with col1:
    metric_card("Signal View", "Drift Map", "Spot category movement by price and volume.")
with col2:
    metric_card("Decision Layer", "What-if", "Model a commercial action before committing.")
with col3:
    metric_card("Planning Layer", "Pivot", "Reshape the signal for category reviews.")
with col4:
    metric_card("Data Source", get_data_source_label(session), "Connected source used for this session.")

st.subheader("Operating Flow")
st.markdown(
    """
    Start with **Where Behavior Shifts** to identify departments with meaningful movement. Move into
    **What If We Act** to test a pricing response and compare saved scenarios. Use **Pivot Builder**
    to reshape the readout for category planning, then finish with **Executive Brief** for a manager-ready
    summary.
    """
)
