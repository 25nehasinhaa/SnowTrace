import streamlit as st

from lib.data import (
    DEFAULT_BASELINE,
    DEFAULT_COMPARISON,
    format_currency,
    get_data_source_label,
    get_snowpark_session,
    init_timeframe_state,
    load_drift_summary,
)
from lib.theme import editorial_story, inject_css, metric_card, process_card


st.set_page_config(
    page_title="SnowTrace | Retail drift intelligence",
    page_icon=":material/ac_unit:",
    layout="wide",
)
inject_css()
init_timeframe_state()

session = get_snowpark_session()

with st.container(key="brand_header"):
    header_left, header_right = st.columns([1.1, 3], vertical_alignment="center")
    with header_left:
        st.markdown('<div class="snowtrace-wordmark"><span>❄</span>SnowTrace</div>', unsafe_allow_html=True)
    with header_right:
        with st.container(key="top_nav", horizontal=True, horizontal_alignment="right", vertical_alignment="center", gap="xsmall"):
            st.page_link("pages/1_Where_Behavior_Shifts.py", label="Drift map")
            st.page_link("pages/2_What_If_We_Act.py", label="Scenario lab")
            st.page_link("pages/3_Pivot_Builder.py", label="Pivot")
            st.page_link("pages/4_Executive_Brief.py", label="Executive brief")

st.markdown(
    """
    <section class="hero-panel">
        <div class="hero-visual-stage">
            <img src="app/static/images/hero-fashion-reflection.jpg" alt="Fashion collection viewed through reflective glass">
            <span>Retail signals / category movement</span>
        </div>
        <div class="hero-copy">
            <div class="hero-kicker">Retail decision intelligence</div>
            <div class="hero-title">SnowTrace</div>
            <div class="hero-subtitle">Decision Drift Intelligence</div>
            <div class="hero-support">Trace the moment customer behavior moves away from plan, understand the commercial consequence, and decide where to act.</div>
            <div class="hero-scroll"><span>↓</span> Explore intelligence</div>
        </div>
    </section>
    """,
    unsafe_allow_html=True,
)

hero_action_columns = st.columns([1, 1, 3])
with hero_action_columns[0]:
    if st.button("Explore drift", type="primary", icon=":material/arrow_forward:", width="stretch"):
        st.switch_page("pages/1_Where_Behavior_Shifts.py")
with hero_action_columns[1]:
    if st.button("View brief", type="primary", icon=":material/description:", width="stretch"):
        st.switch_page("pages/4_Executive_Brief.py")

baseline = st.session_state.get("baseline_range", DEFAULT_BASELINE)
comparison = st.session_state.get("comparison_range", DEFAULT_COMPARISON)
df = load_drift_summary(session, baseline[0], baseline[1], comparison[0], comparison[1])
if df.empty:
    st.info("No completed-order activity was found for the active periods. Open a workspace page and adjust the timeframe.")
    st.stop()
drifting = df[df["DRIFT_STATUS"] == "DRIFT"]

def category_story_values(subset):
    drift_count = int((subset["DRIFT_STATUS"] == "DRIFT").sum())
    status = "Drift detected" if drift_count else "Stable"
    revenue_change = subset["REVENUE_CHANGE_PCT"].mean() if len(subset) else 0
    top_row = subset.assign(IMPACT=subset["REVENUE_CHANGE_PCT"].abs()).sort_values("IMPACT", ascending=False).head(1)
    focus = top_row["DEPARTMENT"].iloc[0] if not top_row.empty else "No active category"
    return status, drift_count, float(revenue_change), focus


beauty = df[df["DIVISION"] == "Beauty & Wellness"]
fashion = df[df["DIVISION"] == "Fashion"]
fragrance = df[df["DEPARTMENT"].str.contains("Perfumery", case=False, na=False)]

st.markdown(
    '<div class="editorial-intro"><span>Category intelligence</span><h2>Three commercial stories.<br>One connected signal.</h2><p>Move from editorial context to measurable behavior without leaving the decision flow.</p></div>',
    unsafe_allow_html=True,
)

fashion_status, fashion_drift, fashion_revenue, fashion_focus = category_story_values(fashion)
editorial_story(
    "fashion-intelligence",
    "01 / Fashion",
    "Fashion",
    "Demand is expressive. The signal is measurable.",
    "Track price sensitivity and unit movement across apparel and accessories before broad commercial action.",
    fashion_status,
    f"{fashion_drift} departments flagged",
    f"{fashion_revenue:+.1f}% average revenue movement",
    fashion_focus,
    "fashion",
    "app/static/images/fashion-rack.jpg",
    "Fashion garments arranged on a retail rail",
    "app/static/images/hero-fashion-reflection.jpg",
    "Fashion assortment seen through a shop window",
)

beauty_status, beauty_drift, beauty_revenue, beauty_focus = category_story_values(beauty)
editorial_story(
    "beauty-intelligence",
    "02 / Beauty",
    "Beauty",
    "Routine categories reveal changes early.",
    "Separate genuine demand shifts from pricing noise across beauty and wellness departments.",
    beauty_status,
    f"{beauty_drift} departments flagged",
    f"{beauty_revenue:+.1f}% average revenue movement",
    beauty_focus,
    "beauty reverse",
    "app/static/images/beauty-application.jpg",
    "Makeup artist applying product with a brush",
    "app/static/images/beauty-brushes.jpg",
    "Editorial arrangement of makeup brushes",
)

fragrance_status, fragrance_drift, fragrance_revenue, fragrance_focus = category_story_values(fragrance)
editorial_story(
    "fragrance-intelligence",
    "03 / Fragrance",
    "Fragrance",
    "A narrow category can carry a clear commercial signal.",
    "Read price, revenue, and customer response together before adjusting a premium assortment.",
    fragrance_status,
    f"{fragrance_drift} departments flagged",
    f"{fragrance_revenue:+.1f}% average revenue movement",
    fragrance_focus,
    "fragrance",
    "app/static/images/fragrance-spray.jpg",
    "Perfume atomizer creating a fine fragrance mist",
    "app/static/images/fragrance-spray.jpg",
    "",
)

revenue_exposure = (
    drifting.assign(EXPOSURE=(drifting["BASELINE_REVENUE"] - drifting["CURRENT_REVENUE"]).clip(lower=0))["EXPOSURE"]
    .fillna(0)
    .sum()
)
comparison_end = df["COMPARISON_END"].max()
data_through = comparison_end.strftime("%d %b %Y") if hasattr(comparison_end, "strftime") else str(comparison_end)

st.markdown('<div class="section-heading"><h2>Current operating picture</h2><p>The metrics a category lead needs before deciding where to investigate.</p></div>', unsafe_allow_html=True)
kpi_columns = st.columns(4)
with kpi_columns[0]:
    metric_card("Departments flagged", f"{len(drifting)}", "Categories outside the current drift thresholds.")
with kpi_columns[1]:
    metric_card("Revenue exposure", format_currency(revenue_exposure), "Decline versus baseline across flagged categories.")
with kpi_columns[2]:
    metric_card("Categories monitored", f"{len(df)}", "Distinct ecommerce departments in the active window.")
with kpi_columns[3]:
    metric_card("Data through", data_through, get_data_source_label(session, df))

st.markdown('<div class="section-heading"><h2>From signal to decision</h2><p>A focused workflow for weekly merchandising and performance reviews.</p></div>', unsafe_allow_html=True)
process_columns = st.columns(3)
with process_columns[0]:
    process_card("01 / DETECT", "Find the shift", "Locate categories where price, volume, revenue, ratings, or delivery performance moved materially.")
with process_columns[1]:
    process_card("02 / SIMULATE", "Test the response", "Model a pricing action before committing and save scenarios for side-by-side discussion.")
with process_columns[2]:
    process_card("03 / ACT", "Align the business", "Turn the strongest signals into a concise brief with a recommended next action.")
