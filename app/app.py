from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

try:
    from snowflake.snowpark.context import get_active_session
except ImportError:
    get_active_session = None


ROOT = Path(__file__).resolve().parents[1]
SAMPLE_PATH = ROOT / "data" / "drift_summary_sample.csv"


st.set_page_config(page_title="SnowTrace", page_icon="ST", layout="wide")


def inject_css() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Playfair+Display:wght@700;800&display=swap');

        :root {
            --midnight: #122C4F;
            --pearl: #FBF9E4;
            --noir: #000000;
            --ocean: #5B88B2;
            --ice: #DDECF7;
            --frost: #F7FBFF;
            --line: rgba(18, 44, 79, .16);
            --muted: rgba(18, 44, 79, .68);
            --drift: #C95D72;
            --stable: #3D9B83;
            --data: #5B88B2;
        }

        .stApp {
            background:
                radial-gradient(circle at 12% 14%, rgba(91, 136, 178, .18), transparent 22rem),
                radial-gradient(circle at 88% 8%, rgba(221, 236, 247, .9), transparent 20rem),
                linear-gradient(180deg, var(--pearl) 0%, #f7fbff 48%, #edf5fb 100%);
            color: var(--midnight);
            font-family: Inter, sans-serif;
        }

        [data-testid="stHeader"], #MainMenu, footer { visibility: hidden; }
        .block-container { padding-top: 1.2rem; padding-bottom: 3rem; max-width: 1360px; }
        h1, h2, h3 { color: var(--midnight); letter-spacing: -0.03em; }
        h1 {
            font-family: "Playfair Display", serif;
            font-size: clamp(4rem, 8vw, 8.7rem) !important;
            line-height: .82 !important;
            margin: .2rem 0 1rem !important;
        }
        .snow-stage h1 { color: var(--pearl) !important; }
        h2, h3 { font-family: "Playfair Display", serif; }

        .lux-nav {
            position: sticky;
            top: 0;
            z-index: 10;
            display: grid;
            grid-template-columns: 1fr auto 1fr;
            align-items: center;
            gap: 24px;
            padding: 15px 0 18px;
            margin-bottom: 14px;
            background: linear-gradient(180deg, rgba(251,249,228,.96), rgba(251,249,228,.82));
            backdrop-filter: blur(16px);
            border-bottom: 1px solid var(--line);
        }
        .nav-left, .nav-right {
            display: flex;
            gap: 22px;
            align-items: center;
            color: var(--midnight);
            font-size: .76rem;
            font-weight: 800;
            letter-spacing: .15em;
            text-transform: uppercase;
        }
        .nav-right { justify-content: flex-end; }
        .brand {
            font-family: "Playfair Display", serif;
            color: var(--midnight);
            font-size: 1.75rem;
            font-weight: 800;
            letter-spacing: .02em;
            text-align: center;
        }

        .snow-stage {
            position: relative;
            overflow: hidden;
            border-radius: 0 0 34px 34px;
            min-height: 430px;
            background:
                linear-gradient(100deg, rgba(18,44,79,.94) 0%, rgba(18,44,79,.90) 44%, rgba(91,136,178,.78) 100%),
                repeating-linear-gradient(90deg, transparent 0 70px, rgba(255,255,255,.035) 70px 71px);
            color: var(--pearl);
            padding: 54px 58px 42px;
            box-shadow: 0 28px 70px rgba(18, 44, 79, .22);
            margin-bottom: 26px;
        }
        .snow-stage:before, .snow-stage:after {
            content: "";
            position: absolute;
            inset: 18px;
            border: 1px solid rgba(251,249,228,.24);
            border-radius: 0 0 28px 28px;
            pointer-events: none;
        }
        .snow-stage:after {
            inset: auto 52px 36px auto;
            width: 168px;
            height: 168px;
            border-radius: 50%;
            border: 1px solid rgba(251,249,228,.30);
        }
        .snow-doodle {
            position: absolute;
            color: rgba(251,249,228,.28);
            font-size: 1.2rem;
            user-select: none;
        }
        .flake-1 { left: 7%; top: 18%; animation-delay: .2s; }
        .flake-2 { left: 72%; top: 18%; font-size: 2.5rem; animation-delay: 1s; }
        .flake-3 { left: 88%; top: 55%; animation-delay: .5s; }
        .flake-4 { left: 48%; top: 76%; font-size: 1.2rem; animation-delay: 1.8s; }
        .hero-kicker {
            color: var(--ice);
            text-transform: uppercase;
            letter-spacing: .24em;
            font-size: .77rem;
            font-weight: 800;
        }
        .hero-copy {
            color: rgba(251,249,228,.86);
            max-width: 790px;
            font-size: 1.08rem;
            line-height: 1.85;
        }
        .hero-actions {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
            margin-top: 26px;
        }
        .pill {
            border: 1px solid rgba(251,249,228,.42);
            border-radius: 999px;
            padding: 11px 16px;
            color: var(--pearl);
            font-size: .78rem;
            font-weight: 800;
            letter-spacing: .1em;
            text-transform: uppercase;
            transition: transform .2s ease, background .2s ease;
        }
        .pill:hover {
            transform: translateY(-2px);
            background: rgba(251,249,228,.12);
        }

        .section-label {
            color: var(--ocean);
            text-transform: uppercase;
            letter-spacing: .2em;
            font-size: .75rem;
            font-weight: 900;
            margin: 12px 0 10px;
        }
        .filter-card, .chart-card {
            border: 1px solid var(--line);
            border-radius: 22px;
            background: rgba(255,255,255,.58);
            box-shadow: 0 18px 48px rgba(18,44,79,.08);
            padding: 18px;
        }
        .filter-card {
            background: linear-gradient(180deg, rgba(255,255,255,.82), rgba(221,236,247,.62));
        }

        .metric-card {
            position: relative;
            overflow: hidden;
            border: 1px solid var(--line);
            border-radius: 22px;
            padding: 22px 22px 20px;
            background:
                linear-gradient(180deg, rgba(255,255,255,.78), rgba(251,249,228,.7)),
                var(--frost);
            min-height: 150px;
            box-shadow: 0 18px 46px rgba(18,44,79,.08);
            transition: transform .22s ease, box-shadow .22s ease, border-color .22s ease;
        }
        .metric-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 24px 58px rgba(18,44,79,.15);
            border-color: rgba(91,136,178,.44);
        }
        .metric-card:after {
            content: "\\2744";
            position: absolute;
            right: 16px;
            top: 12px;
            color: rgba(91,136,178,.22);
            font-size: 2rem;
        }
        .metric-label {
            color: var(--muted);
            font-size: .72rem;
            text-transform: uppercase;
            letter-spacing: .14em;
            font-weight: 900;
        }
        .metric-value {
            color: var(--midnight);
            font-family: "Playfair Display", serif;
            font-size: 3rem;
            line-height: 1;
            margin-top: 16px;
        }
        .metric-note {
            color: var(--ocean);
            font-size: .84rem;
            margin-top: 10px;
            font-weight: 700;
        }

        [data-testid="stDataFrame"] {
            border: 1px solid var(--line);
            border-radius: 18px;
            overflow: hidden;
            box-shadow: 0 18px 44px rgba(18,44,79,.08);
        }
        div[data-testid="stSelectbox"] label {
            color: var(--midnight);
            font-weight: 900;
            letter-spacing: .08em;
            text-transform: uppercase;
            font-size: .76rem;
        }
        div[data-baseweb="select"] > div {
            background: rgba(255,255,255,.86);
            border-color: var(--line);
            border-radius: 14px;
            color: var(--midnight);
        }

        .insight-grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 16px;
        }
        .insight-card {
            position: relative;
            border: 1px solid var(--line);
            border-radius: 22px;
            padding: 22px 24px;
            background:
                linear-gradient(135deg, rgba(255,255,255,.88), rgba(221,236,247,.55)),
                var(--frost);
            box-shadow: 0 18px 46px rgba(18,44,79,.08);
            transition: transform .22s ease, border-color .22s ease;
            min-height: 214px;
        }
        .insight-card:hover {
            transform: translateY(-4px) rotate(-.25deg);
            border-color: rgba(91,136,178,.48);
        }
        .insight-card:before {
            content: "";
            position: absolute;
            top: 0;
            left: 24px;
            right: 24px;
            height: 4px;
            background: linear-gradient(90deg, var(--midnight), var(--ocean), transparent);
            border-radius: 0 0 999px 999px;
        }
        .insight-title {
            color: var(--midnight);
            font-family: "Playfair Display", serif;
            font-weight: 800;
            font-size: 1.35rem;
            margin-bottom: 10px;
        }
        .insight-body {
            color: var(--muted);
            line-height: 1.72;
            font-size: .95rem;
        }
        .status {
            display: inline-block;
            border-radius: 999px;
            padding: 5px 9px;
            font-family: Inter, sans-serif;
            font-size: .65rem;
            font-weight: 900;
            letter-spacing: .12em;
            vertical-align: middle;
        }
        .status-drift { color: #fff; background: var(--drift); }
        .status-stable { color: #fff; background: var(--stable); }
        .status-data { color: #fff; background: var(--data); }

        .objective {
            border: 1px solid rgba(18,44,79,.14);
            border-radius: 28px;
            background: var(--midnight);
            color: var(--pearl);
            padding: 28px 30px;
            margin-top: 18px;
            position: relative;
            overflow: hidden;
        }
        .objective:after {
            content: "\\2744  \\2744  \\2744";
            position: absolute;
            right: 28px;
            bottom: 22px;
            color: rgba(251,249,228,.22);
            letter-spacing: .8em;
            font-size: 1.8rem;
        }
        .objective h3 { color: var(--pearl); margin-top: 0; }
        .objective p { color: rgba(251,249,228,.82); line-height: 1.8; max-width: 860px; }

        @keyframes floatSnow {
            0%, 100% { transform: translateY(0) rotate(0deg); }
            50% { transform: translateY(-14px) rotate(12deg); }
        }
        @keyframes spinSlow {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
        @media (max-width: 900px) {
            .lux-nav { grid-template-columns: 1fr; text-align: center; }
            .nav-left, .nav-right { justify-content: center; flex-wrap: wrap; }
            .snow-stage { padding: 42px 28px; min-height: 390px; }
            .insight-grid { grid-template-columns: 1fr; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data(ttl=300)
def load_data() -> tuple[pd.DataFrame, str]:
    if get_active_session is not None:
        try:
            session = get_active_session()
            df = session.sql("SELECT * FROM SNOWTRACE_DB.ANALYTICS.DRIFT_SUMMARY").to_pandas()
            return df, "Snowflake"
        except Exception:
            pass
    return pd.read_csv(SAMPLE_PATH), "Local sample"


def format_currency(value: float) -> str:
    return f"INR {value:,.0f}"


def status_badge(status: str) -> str:
    if status == "DRIFT":
        return '<span class="status status-drift">DRIFT</span>'
    if status == "STABLE":
        return '<span class="status status-stable">STABLE</span>'
    return '<span class="status status-data">INSUFFICIENT DATA</span>'


inject_css()

df, data_source = load_data()

st.markdown(
    """
    <nav class="lux-nav">
        <div class="nav-left">
            <span>Beauty</span>
            <span>Fashion</span>
            <span>Fragrance</span>
        </div>
        <div class="brand">SnowTrace</div>
        <div class="nav-right">
            <span>Insights</span>
            <span>Drift Edit</span>
            <span>Snowflake</span>
        </div>
    </nav>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <section class="snow-stage">
        <div class="snow-doodle flake-1">&#10052;</div>
        <div class="snow-doodle flake-2">&#10052;</div>
        <div class="snow-doodle flake-3">&#10053;</div>
        <div class="snow-doodle flake-4">&#10052;</div>
        <div class="hero-kicker">Luxury retail decision intelligence</div>
        <h1>SnowTrace</h1>
        <p class="hero-copy">
            A boutique analytics experience for understanding how customers move from holiday gifting
            to post-season purchasing. SnowTrace compares December luxury behaviour with January intent,
            then turns category drift into clear merchandising actions.
        </p>
        <div class="hero-actions">
            <div class="pill">Post-Holiday Drift</div>
            <div class="pill">Premium Category Signals</div>
            <div class="pill">Snowflake Native</div>
            <div class="pill">Source: {data_source}</div>
        </div>
    </section>
    """,
    unsafe_allow_html=True,
)

filter_col, copy_col = st.columns([1, 2.2])
with filter_col:
    st.markdown('<div class="section-label">Boutique Filter</div>', unsafe_allow_html=True)
    with st.container():
        division_filter = st.selectbox("Luxury Division", ["All"] + sorted(df["DIVISION"].unique().tolist()))
with copy_col:
    st.markdown(
        """
        <div class="filter-card">
            <div class="section-label" style="margin-top:0;">How to read this</div>
            <p style="color:rgba(18,44,79,.72);line-height:1.75;margin:0;">
                A large negative price shift means customers are still buying, but at a more accessible tier.
                That is a different business signal from a simple sales decline, and it calls for category-specific
                merchandising rather than a blanket January discount.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

filtered = df.copy()
if division_filter != "All":
    filtered = filtered[filtered["DIVISION"] == division_filter]

total_categories = len(filtered)
drift_count = int((filtered["DRIFT_STATUS"] == "DRIFT").sum())
stable_count = int((filtered["DRIFT_STATUS"] == "STABLE").sum())
avg_price_shift = float(filtered["PRICE_CHANGE_PCT"].mean()) if total_categories else 0.0

cols = st.columns(4)
metric_payload = [
    ("Departments Analysed", total_categories, "Luxury categories in scope"),
    ("Behaviour Drift", drift_count, "Needs merchandising action"),
    ("Stable Segments", stable_count, "Premium intent retained"),
    ("Avg Price Shift", f"{avg_price_shift:.1f}%", "Holiday to current"),
]

for col, (label, value, note) in zip(cols, metric_payload):
    with col:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{value}</div>
                <div class="metric-note">{note}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown('<div class="section-label">Editorial Drift Overview</div>', unsafe_allow_html=True)

chart_df = filtered.assign(
    PRICE_DIRECTION=filtered["PRICE_CHANGE_PCT"].apply(lambda x: "Increase" if x >= 0 else "Decrease")
)
fig = px.bar(
    chart_df,
    x="DEPARTMENT",
    y="PRICE_CHANGE_PCT",
    color="DRIFT_STATUS",
    text="PRICE_CHANGE_PCT",
    color_discrete_map={
        "DRIFT": "#C95D72",
        "STABLE": "#3D9B83",
        "INSUFFICIENT_DATA": "#5B88B2",
    },
    labels={"PRICE_CHANGE_PCT": "Price Change %", "DEPARTMENT": "Department"},
)
fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside", marker_line_width=0)
fig.update_layout(
    height=410,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(255,255,255,.46)",
    font_color="#122C4F",
    margin=dict(l=10, r=10, t=24, b=10),
    legend_title_text="Behaviour Status",
    yaxis_gridcolor="rgba(18,44,79,.12)",
    xaxis_gridcolor="rgba(18,44,79,0)",
    bargap=.38,
)
st.plotly_chart(fig, use_container_width=True)

st.markdown('<div class="section-label">Luxury Drift Detection Summary</div>', unsafe_allow_html=True)

display_df = filtered.rename(
    columns={
        "DIVISION": "Division",
        "DEPARTMENT": "Department",
        "HOLIDAY_PRICE": "Holiday Avg Price",
        "CURRENT_PRICE": "Current Avg Price",
        "PRICE_CHANGE_PCT": "Price Change %",
        "HOLIDAY_VOLUME": "Holiday Volume",
        "CURRENT_VOLUME": "Current Volume",
        "VOLUME_CHANGE_PCT": "Volume Change %",
        "DRIFT_STATUS": "Behaviour Status",
        "CONFIDENCE_LEVEL": "Confidence",
    }
)

display_df["Holiday Avg Price"] = display_df["Holiday Avg Price"].map(format_currency)
display_df["Current Avg Price"] = display_df["Current Avg Price"].map(format_currency)
display_df["Price Change %"] = display_df["Price Change %"].map(lambda x: f"{x:.1f}%")

st.dataframe(
    display_df[
        [
            "Division",
            "Department",
            "Holiday Avg Price",
            "Current Avg Price",
            "Price Change %",
            "Behaviour Status",
            "Confidence",
        ]
    ],
    use_container_width=True,
    hide_index=True,
)

st.caption("Confidence levels are derived from transaction count, volume coverage, and behavioural consistency.")

st.markdown('<div class="section-label">SnowTrace Boutique Recommendations</div>', unsafe_allow_html=True)

cards = ['<div class="insight-grid">']
for _, row in filtered.iterrows():
    cards.append(
        '<div class="insight-card">'
        '<div class="insight-title">'
        f'{row["DIVISION"]} / {row["DEPARTMENT"]}<br>{status_badge(row["DRIFT_STATUS"])}'
        '</div>'
        '<div class="insight-body">'
        f'{row["BUSINESS_EXPLANATION"]}<br><br>'
        f'<strong>Recommended Action:</strong> {row["RECOMMENDED_ACTION"]}'
        '</div>'
        '</div>'
    )
cards.append("</div>")
st.markdown("".join(cards), unsafe_allow_html=True)

st.markdown(
    """
    <section class="objective">
        <h3>Project Objective</h3>
        <p>
            SnowTrace helps luxury retailers proactively identify behavioural purchasing drift across fashion,
            beauty, fragrance, and premium lifestyle categories using Snowflake-based analytical intelligence
            workflows. The experience is designed like a premium retail editorial surface, while the logic
            remains grounded in Snowflake SQL and Snowpark-ready querying.
        </p>
    </section>
    """,
    unsafe_allow_html=True,
)
