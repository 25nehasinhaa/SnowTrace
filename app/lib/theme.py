import streamlit as st


def inject_css() -> None:
    """Apply the shared editorial theme across every Streamlit page."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');

        :root {
            --black: #08090d;
            --ink: #111827;
            --charcoal: #202026;
            --cream: #f6f1e8;
            --pearl: #fbf8f1;
            --mist: #e9ece8;
            --line: rgba(17, 24, 39, 0.13);
            --muted: #747474;
            --blue: #9ecce0;
            --clay: #b96863;
            --olive: #657761;
        }

        .stApp {
            background: linear-gradient(180deg, var(--cream) 0%, #edf1ee 100%);
            color: var(--ink);
            font-family: "Inter", sans-serif;
        }

        h1, h2, h3 {
            font-family: "Playfair Display", serif;
            color: var(--ink);
            letter-spacing: 0;
        }

        h1 {
            font-size: 3.2rem;
            line-height: 1;
            margin-bottom: 0.4rem;
        }

        .block-container {
            max-width: 1120px;
            padding-top: 3.25rem;
            padding-bottom: 3rem;
        }

        header[data-testid="stHeader"] {
            background: var(--black);
            height: 46px;
        }

        [data-testid="stSidebar"] {
            background: var(--black);
            border-right: 1px solid rgba(255,255,255,0.08);
        }

        [data-testid="stSidebar"] * {
            color: var(--pearl);
        }

        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] span {
            color: var(--pearl);
        }

        .story-kicker {
            color: var(--muted);
            font-size: 0.9rem;
            font-weight: 700;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            margin-bottom: 0.35rem;
        }

        .lede {
            color: #343434;
            font-size: 1.08rem;
            line-height: 1.7;
            max-width: 820px;
        }

        .brand-hero {
            background: var(--black);
            color: var(--cream);
            min-height: 330px;
            margin: -3.25rem calc(50% - 50vw) 2rem;
            padding: 3rem max(3rem, calc((100vw - 1120px) / 2)) 2rem;
            overflow: hidden;
            position: relative;
        }

        .brand-hero:after {
            content: "";
            position: absolute;
            inset: 0;
            background:
                radial-gradient(circle at 70% 20%, rgba(158, 204, 224, 0.35), transparent 24%),
                linear-gradient(110deg, transparent 0 45%, rgba(255,255,255,0.06) 45% 47%, transparent 47%);
            pointer-events: none;
        }

        .brand-mark {
            position: relative;
            z-index: 1;
            font-family: "Playfair Display", serif;
            font-size: clamp(4.8rem, 15vw, 13rem);
            font-weight: 700;
            letter-spacing: -0.04em;
            line-height: 0.82;
            color: var(--cream);
            margin-top: 1.2rem;
        }

        .brand-line {
            position: relative;
            z-index: 1;
            max-width: 720px;
            color: rgba(246, 241, 232, 0.82);
            font-size: 1.08rem;
            line-height: 1.65;
            margin-top: 1.4rem;
        }

        .hero-nav {
            position: relative;
            z-index: 1;
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-top: 1.8rem;
        }

        .hero-pill {
            border: 1px solid rgba(246,241,232,0.62);
            border-radius: 999px;
            color: var(--cream);
            padding: 0.42rem 0.78rem;
            font-size: 0.86rem;
            background: rgba(246,241,232,0.06);
        }

        .section-band {
            margin: 1.5rem calc(50% - 50vw);
            padding: 1.8rem max(3rem, calc((100vw - 1120px) / 2));
            background: rgba(251,248,241,0.5);
            border-top: 1px solid var(--line);
            border-bottom: 1px solid var(--line);
        }

        .metric-card {
            border: 1px solid var(--line);
            border-left: 3px solid var(--black);
            border-radius: 7px;
            padding: 1rem;
            background: rgba(251,248,241,0.78);
            min-height: 118px;
            box-shadow: 0 18px 45px rgba(17,24,39,0.05);
        }

        .metric-label {
            color: var(--muted);
            font-size: 0.78rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }

        .metric-value {
            color: var(--ink);
            font-size: 1.8rem;
            font-weight: 700;
            margin-top: 0.25rem;
        }

        .metric-help {
            color: var(--muted);
            font-size: 0.88rem;
            margin-top: 0.35rem;
        }

        .recommendation {
            border: 1px solid var(--line);
            border-radius: 7px;
            padding: 1rem 1.1rem;
            background: rgba(251,248,241,0.86);
            margin-bottom: 0.85rem;
            box-shadow: 0 16px 35px rgba(17,24,39,0.04);
        }

        .recommendation strong {
            color: var(--ink);
        }

        div[data-testid="stDataFrame"] {
            border: 1px solid var(--line);
            border-radius: 7px;
        }

        .stButton > button, .stDownloadButton > button {
            border-radius: 6px;
            border: 1px solid var(--black);
            background: var(--black);
            color: var(--cream);
            font-weight: 700;
        }

        .stButton > button:hover, .stDownloadButton > button:hover {
            border-color: var(--charcoal);
            background: var(--charcoal);
            color: var(--cream);
        }

        [data-testid="stSelectbox"] div[data-baseweb="select"] > div,
        [data-testid="stDateInput"] input {
            background: #171820;
            border-color: #171820;
            color: var(--cream);
            border-radius: 7px;
        }

        .stSlider [data-baseweb="slider"] div {
            color: var(--black);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def metric_card(label: str, value: str, help_text: str = "") -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-help">{help_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
