from __future__ import annotations

from html import escape

import streamlit as st


def inject_css() -> None:
    """Apply SnowTrace's shared monochrome editorial theme."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600&family=Inter:wght@400;500;600;700;800&family=Manrope:wght@500;600;700;800&display=swap');

        :root {
            --firefly: #111111;
            --navy: #111111;
            --blue: #3a3a3a;
            --east-bay: #4d4d4d;
            --sky: #b4c7cc;
            --polo: #b7babb;
            --cornflower: #b4c7cc;
            --frost: #e8edef;
            --ice: #f5f5f2;
            --white: #ffffff;
            --ink: #111111;
            --muted: #4d4d4d;
            --line: #b7babb;
        }

        .stApp { background: var(--ice); color: var(--ink); font-family: "Inter", sans-serif; }
        h1, h2, h3 { color: var(--navy); font-family: "Manrope", sans-serif; letter-spacing: 0; }
        h1 { font-size: 3rem; line-height: 1.06; margin-bottom: 0.5rem; }
        h2 { font-size: 2rem; }
        h3 { font-size: 1.3rem; }
        .block-container { max-width: 1180px; padding-top: 4rem; padding-bottom: 4rem; }
        header[data-testid="stHeader"] { background: rgba(245, 245, 242, 0.96); border-bottom: 1px solid var(--line); }
        [data-testid="stSidebar"] { background: var(--navy); border-right: 0; }
        [data-testid="stSidebar"] * { color: var(--white); }
        [data-testid="stSidebarNav"] a[aria-current="page"] { background: rgba(130, 175, 229, 0.25); }

        .story-kicker { color: var(--blue); font-size: 0.78rem; font-weight: 800; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 0.5rem; }
        .snowtrace-wordmark { color: var(--navy); font-family: "Manrope", sans-serif; font-size: 1.28rem; font-weight: 700; line-height: 2.25rem; white-space: nowrap; }
        .snowtrace-wordmark span { color: var(--sky); margin-right: 0.42rem; }
        .st-key-brand_header { margin-top: 1rem; }

        .hero-panel { position: relative; overflow: hidden; box-sizing: border-box; min-height: 470px; padding: 3.8rem 3.8rem 3rem; border: 1px solid var(--navy); border-radius: 0; background: var(--navy); animation: hero-arrive 600ms ease-out both; }
        .hero-panel::after { content: ""; position: absolute; inset: 0; background: linear-gradient(90deg, rgba(17,17,17,0.98) 0%, rgba(17,17,17,0.92) 48%, rgba(17,17,17,0.08) 72%); pointer-events: none; z-index: 1; }
        .hero-copy { position: relative; z-index: 3; max-width: 620px; }
        .hero-kicker { color: var(--sky); font-size: 0.76rem; font-weight: 800; letter-spacing: 0.12em; text-transform: uppercase; animation: snowtrace-reveal 500ms 80ms ease-out both; }
        .hero-title { color: var(--ice); font-family: "Cormorant Garamond", serif; font-size: 6.4rem; font-weight: 500; line-height: 0.88; margin-top: 1.7rem; animation: snowtrace-reveal 620ms 150ms ease-out both; }
        .hero-subtitle { color: var(--white); font: 600 1.25rem "Manrope", sans-serif; margin-top: 1.2rem; animation: snowtrace-reveal 560ms 230ms ease-out both; }
        .hero-support { color: #d9ddde; font-size: 1.02rem; line-height: 1.7; margin-top: 1rem; max-width: 520px; animation: snowtrace-reveal 560ms 300ms ease-out both; }
        .hero-scroll { color: var(--sky); font-size: 0.74rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; margin-top: 2.2rem; animation: snowtrace-reveal 560ms 380ms ease-out both; }
        .hero-scroll span { display: inline-block; color: var(--ice); font-size: 1rem; margin-right: 0.55rem; animation: scroll-cue 1.9s ease-in-out infinite; }
        .hero-visual-stage { position: absolute; z-index: 0; right: 0; top: 0; width: 53%; height: 100%; background: var(--ink); overflow: hidden; }
        .hero-visual-stage img { width: 100%; height: 100%; object-fit: cover; object-position: center 57%; filter: grayscale(1) contrast(1.04); }
        .hero-visual-stage > span { position: absolute; z-index: 2; right: 1.2rem; bottom: 1rem; padding: 0.35rem 0.5rem; color: rgba(255,255,255,0.78); background: rgba(17,17,17,0.68); font-size: 0.62rem; letter-spacing: 0.1em; text-transform: uppercase; }

        .editorial-intro { margin: 6rem 0 3rem; max-width: 790px; }
        .editorial-intro > span { color: var(--sky); font-size: 0.74rem; font-weight: 800; letter-spacing: 0.11em; text-transform: uppercase; }
        .editorial-intro h2 { font: 500 4.2rem/0.98 "Cormorant Garamond", serif; margin: 0.8rem 0 1rem; }
        .editorial-intro p { color: var(--muted); font-size: 1rem; line-height: 1.65; max-width: 590px; }
        .editorial-story { display: grid; grid-template-columns: 1.15fr 0.85fr; min-height: 500px; margin: 0 0 6rem; border-top: 1px solid var(--line); border-bottom: 1px solid var(--line); overflow: hidden; }
        .editorial-story.reverse .editorial-media { order: 2; }
        .editorial-story.reverse .editorial-copy { order: 1; }
        .editorial-media { position: relative; min-height: 500px; overflow: hidden; background: var(--navy); isolation: isolate; }
        .editorial-story.beauty .editorial-media { background: var(--sky); }
        .editorial-story.fragrance .editorial-media { background: var(--ink); }
        .editorial-media::after { content: ""; position: absolute; z-index: 1; inset: 0; background: linear-gradient(180deg, rgba(17,17,17,0.04) 44%, rgba(17,17,17,0.76) 100%); pointer-events: none; }
        .editorial-image { width: 100%; height: 100%; position: absolute; inset: 0; object-fit: cover; object-position: center; filter: grayscale(1) contrast(1.03); transition: transform 700ms ease, filter 700ms ease; }
        .editorial-story:hover .editorial-image-primary { transform: scale(1.018); filter: grayscale(1) contrast(1.08); }
        .fashion .editorial-image-primary { object-position: center 42%; }
        .fragrance .editorial-image-primary { object-position: center 54%; }
        .editorial-image-secondary { z-index: 2; inset: auto 1.5rem 1.5rem auto; width: 38%; height: 46%; border: 7px solid var(--white); object-position: center; box-shadow: 0 16px 34px rgba(17,17,17,0.22); }
        .fragrance .editorial-image-secondary { display: none; }
        .editorial-media-label { position: absolute; z-index: 3; left: 2rem; bottom: 1.7rem; color: rgba(255,255,255,0.94); font: 500 4.7rem/0.9 "Cormorant Garamond", serif; text-shadow: 0 2px 20px rgba(17,17,17,0.48); text-transform: uppercase; }
        .beauty .editorial-media-label { max-width: 55%; }
        .editorial-media-index { position: absolute; z-index: 3; top: 1.5rem; left: 1.6rem; padding: 0.35rem 0.48rem; color: rgba(255,255,255,0.88); background: rgba(17,17,17,0.62); font-size: 0.66rem; letter-spacing: 0.1em; text-transform: uppercase; }
        .editorial-copy { display: flex; flex-direction: column; justify-content: center; padding: 3.2rem; background: var(--white); }
        .editorial-eyebrow { color: var(--sky); font-size: 0.72rem; font-weight: 800; letter-spacing: 0.1em; text-transform: uppercase; }
        .editorial-title { color: var(--navy); font: 500 2.65rem/1.04 "Cormorant Garamond", serif; margin-top: 1rem; }
        .editorial-description { color: var(--muted); line-height: 1.65; margin-top: 1rem; }
        .editorial-signal { display: grid; grid-template-columns: 1fr 1fr; gap: 0; margin-top: 2rem; border-top: 1px solid var(--line); border-bottom: 1px solid var(--line); }
        .editorial-stat { padding: 1rem 0.75rem 1rem 0; }
        .editorial-stat + .editorial-stat { border-left: 1px solid var(--line); padding-left: 1rem; }
        .editorial-stat strong { display: block; color: var(--navy); font: 700 1rem "Manrope", sans-serif; }
        .editorial-stat span { display: block; color: var(--muted); font-size: 0.75rem; line-height: 1.35; margin-top: 0.25rem; }
        .editorial-focus { color: var(--navy); font-size: 0.78rem; font-weight: 700; margin-top: 1.2rem; }

        .st-key-top_nav [data-testid="stPageLink"] a { color: var(--navy); font-size: 0.86rem; font-weight: 600; padding: 0.45rem 0.58rem; text-decoration: none; }
        .st-key-top_nav [data-testid="stPageLink"] a * { color: var(--navy) !important; }
        .st-key-top_nav [data-testid="stPageLink"] a:hover { color: var(--blue); background: var(--frost); }
        .st-key-hero_actions [data-testid="stPageLink"] a { min-height: 2.75rem; padding: 0.68rem 1rem; border: 1px solid var(--blue) !important; border-radius: 6px; background: var(--blue) !important; color: var(--white) !important; font-weight: 700; text-decoration: none; }
        .st-key-hero_actions [data-testid="stPageLink"] a * { color: var(--white) !important; }

        .section-heading { margin: 2.6rem 0 1rem; }
        .section-heading h2 { margin: 0; }
        .section-heading p { color: var(--muted); margin: 0.35rem 0 0; }
        .category-card { overflow: hidden; min-height: 264px; border: 1px solid var(--line); border-radius: 8px; background: var(--white); box-shadow: 0 14px 35px rgba(18, 44, 79, 0.07); transition: transform 160ms ease, box-shadow 160ms ease, border-color 160ms ease; }
        .category-card:hover { transform: translateY(-2px); border-color: var(--sky); box-shadow: 0 18px 40px rgba(18, 44, 79, 0.12); }
        .category-visual { position: relative; height: 138px; overflow: hidden; background: var(--category-color); }
        .category-visual::before, .category-visual::after { content: ""; position: absolute; border: 1px solid rgba(255,255,255,0.72); transform: rotate(35deg); }
        .category-visual::before { width: 115px; height: 115px; right: 22px; top: -30px; }
        .category-visual::after { width: 72px; height: 72px; right: 90px; top: 58px; }
        .category-body { padding: 1rem 1.1rem 1.15rem; }
        .category-name { color: var(--navy); font: 700 1.28rem "Manrope", sans-serif; }
        .category-meta { color: var(--muted); font-size: 0.88rem; margin-top: 0.35rem; }
        .status-chip { display: inline-block; margin-top: 0.72rem; padding: 0.26rem 0.56rem; border-radius: 999px; color: var(--navy); background: var(--frost); font-size: 0.74rem; font-weight: 700; }
        .status-chip.alert { color: var(--white); background: var(--ink); }

        .metric-card { min-height: 142px; padding: 1.15rem; border: 1px solid var(--line); border-top: 3px solid var(--sky); border-radius: 8px; background: var(--white); box-shadow: 0 14px 35px rgba(18, 44, 79, 0.06); transition: transform 160ms ease, box-shadow 160ms ease; animation: snowtrace-reveal 260ms ease-out both; }
        .metric-card:hover { transform: translateY(-2px); box-shadow: 0 18px 38px rgba(18, 44, 79, 0.11); }
        .metric-label { color: var(--muted); font-size: 0.74rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.08em; }
        .metric-value { color: var(--navy); font: 700 1.72rem "Manrope", sans-serif; margin-top: 0.45rem; overflow-wrap: anywhere; }
        .metric-help { color: var(--muted); font-size: 0.84rem; margin-top: 0.4rem; line-height: 1.45; }

        .process-card { min-height: 168px; padding: 1.25rem; border-left: 2px solid var(--sky); background: var(--white); }
        .process-step { color: var(--sky); font: 700 0.8rem "Manrope", sans-serif; }
        .process-title { color: var(--navy); font: 700 1.4rem "Manrope", sans-serif; margin-top: 0.65rem; }
        .process-copy { color: var(--muted); line-height: 1.55; margin-top: 0.45rem; }

        .recommendation { border: 1px solid var(--line); border-left: 3px solid var(--navy); border-radius: 7px; padding: 1rem 1.1rem; background: var(--white); margin-bottom: 0.85rem; }
        .recommendation strong { color: var(--navy); }
        .action-card { height: 410px; box-sizing: border-box; border: 1px solid var(--line); border-radius: 8px; background: var(--white); overflow: hidden; margin-bottom: 1rem; transition: transform 160ms ease, box-shadow 160ms ease; animation: snowtrace-reveal 280ms ease-out both; }
        .action-card:hover { transform: translateY(-2px); box-shadow: 0 16px 34px rgba(18, 44, 79, 0.12); }
        .action-card-head { display: flex; align-items: center; justify-content: space-between; gap: 0.75rem; padding: 0.85rem 1rem; background: var(--blue); color: var(--white); }
        .action-rank { font-size: 0.72rem; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; }
        .action-division { font-size: 0.75rem; opacity: 0.82; }
        .action-card-body { padding: 1rem; }
        .action-title { color: var(--navy); font: 700 1.15rem "Manrope", sans-serif; }
        .action-signals { display: flex; flex-wrap: wrap; gap: 0.4rem; margin: 0.8rem 0; }
        .action-signal { padding: 0.25rem 0.48rem; border: 1px solid var(--line); border-radius: 999px; color: var(--navy); background: var(--frost); font-size: 0.72rem; font-weight: 600; }
        .action-copy { color: var(--muted); font-size: 0.88rem; line-height: 1.5; }
        .action-next { color: var(--navy); font-size: 0.88rem; font-weight: 700; line-height: 1.45; margin-top: 0.7rem; }
        .st-key-analysis_next [data-testid="stPageLink"] a { min-height: 2.65rem; padding: 0.62rem 0.9rem; border: 1px solid var(--navy) !important; border-radius: 6px; color: var(--navy) !important; background: var(--ice) !important; font-weight: 700; text-decoration: none; }
        .st-key-analysis_next [data-testid="stPageLink"] a * { color: var(--navy) !important; }
        div[data-testid="stDataFrame"] { border: 1px solid var(--line); border-radius: 7px; }
        .stButton > button, .stDownloadButton > button { border-radius: 6px; border: 1px solid var(--blue); background: var(--blue); color: var(--white); font-weight: 700; }
        .stButton > button, .stDownloadButton > button, [data-testid="stPageLink"] a { transition: transform 140ms ease, box-shadow 140ms ease, background-color 140ms ease, border-color 140ms ease; }
        .stButton > button:hover, .stDownloadButton > button:hover { border-color: var(--sky); background: var(--blue); color: var(--white); transform: translateY(-1px); box-shadow: 0 7px 18px rgba(17, 17, 17, 0.18); }
        .stButton > button:active, .stDownloadButton > button:active, [data-testid="stPageLink"] a:active { transform: scale(0.98); }
        [data-testid="stSelectbox"] div[data-baseweb="select"] > div, [data-testid="stDateInput"] input { background: var(--white); border-color: var(--sky); color: var(--ink); border-radius: 7px; }
        .stSlider [data-baseweb="slider"] div { color: var(--blue); }

        .brief-hero { margin: 0 0 2rem; padding: 3rem; background: var(--navy); color: var(--white); animation: snowtrace-reveal 260ms ease-out both; }
        .brief-hero-inner { max-width: 900px; }
        .brief-kicker { color: var(--sky); font-size: 0.76rem; font-weight: 800; letter-spacing: 0.1em; text-transform: uppercase; }
        .brief-title { color: var(--white); font: 700 3rem/1.08 "Manrope", sans-serif; margin-top: 0.65rem; max-width: 780px; }
        .brief-lede { color: #d9ddde; font-size: 1.04rem; line-height: 1.65; margin-top: 1rem; max-width: 750px; }
        .brief-period { display: inline-block; color: var(--sky); border-top: 1px solid var(--sky); margin-top: 1.3rem; padding-top: 0.8rem; font-size: 0.82rem; font-weight: 600; }
        .executive-pulse { margin: 1.3rem 0 2.2rem; padding: 1.5rem 1.65rem; border-left: 4px solid var(--cornflower); background: var(--blue); color: var(--white); }
        .pulse-label { color: var(--sky); font-size: 0.72rem; font-weight: 800; letter-spacing: 0.09em; text-transform: uppercase; }
        .pulse-title { font: 700 1.35rem/1.35 "Manrope", sans-serif; margin-top: 0.45rem; }
        .pulse-copy { color: #d9ddde; line-height: 1.6; margin-top: 0.45rem; }
        .brief-table-note { color: var(--muted); font-size: 0.88rem; margin: -0.35rem 0 0.85rem; }

        @keyframes hero-arrive { from { opacity: 0; transform: scale(0.992); } to { opacity: 1; transform: scale(1); } }
        @keyframes snowtrace-reveal { from { opacity: 0; transform: translateY(14px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes scroll-cue { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(4px); } }
        @supports (animation-timeline: view()) {
            .editorial-intro, .editorial-story, .section-heading, .process-card { animation: snowtrace-reveal linear both; animation-timeline: view(); animation-range: entry 8% cover 28%; }
        }
        @media (hover: hover) and (pointer: fine) {
            .stApp { cursor: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24'%3E%3Cpath d='M12 2v20M3.34 7l17.32 10M3.34 17L20.66 7M9 4l3 3 3-3M9 20l3-3 3 3M4.2 10.5l4.1 1.1-1.1 4.1M19.8 13.5l-4.1-1.1 1.1-4.1M7.2 8.3l1.1 4.1-4.1 1.1M16.8 15.7l-1.1-4.1 4.1-1.1' fill='none' stroke='%23111111' stroke-width='1.4' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E") 12 12, default; }
            button, a, input, select, textarea, [role="button"], [role="slider"], [data-baseweb="select"] { cursor: pointer; }
        }

        @media (prefers-reduced-motion: reduce) {
            *, *::before, *::after { animation-duration: 0.01ms !important; animation-iteration-count: 1 !important; transition-duration: 0.01ms !important; scroll-behavior: auto !important; }
        }

        @media (max-width: 760px) {
            .block-container { padding-top: 4.5rem; }
            .st-key-brand_header { margin-top: 0.75rem; }
            .hero-panel { min-height: 520px; padding: 3rem 1.4rem 2rem; }
            .hero-title { font-size: 4.3rem; }
            .hero-panel::after { background: linear-gradient(180deg, rgba(17,17,17,0.98) 0%, rgba(17,17,17,0.88) 58%, rgba(17,17,17,0.24) 100%); }
            .hero-visual-stage { width: 100%; height: 46%; right: 0; top: auto; bottom: 0; opacity: 0.66; }
            .hero-scroll { margin-top: 1.5rem; }
            .editorial-intro { margin-top: 4.5rem; }
            .editorial-intro h2 { font-size: 3.1rem; }
            .editorial-story { grid-template-columns: 1fr; min-height: 0; margin-bottom: 4rem; }
            .editorial-story.reverse .editorial-media, .editorial-story.reverse .editorial-copy { order: initial; }
            .editorial-media { min-height: 390px; }
            .editorial-media-label { font-size: 3.7rem; }
            .editorial-image-secondary { width: 34%; height: 42%; right: 1rem; bottom: 1rem; border-width: 5px; }
            .editorial-copy { padding: 2.2rem 1.5rem; }
            .snowtrace-wordmark { font-size: 1.1rem; }
            .brief-hero { padding: 2.2rem 1.25rem; }
            .brief-title { font-size: 2.25rem; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def metric_card(label: str, value: str, help_text: str = "") -> None:
    st.markdown(
        f'<div class="metric-card"><div class="metric-label">{escape(str(label))}</div><div class="metric-value">{escape(str(value))}</div><div class="metric-help">{escape(str(help_text))}</div></div>',
        unsafe_allow_html=True,
    )


def category_card(name: str, status: str, detail: str, color: str) -> None:
    status_class = "alert" if status == "Drift detected" else ""
    st.markdown(
        f'<div class="category-card" style="--category-color:{escape(color)}"><div class="category-visual"></div><div class="category-body"><div class="category-name">{escape(name)}</div><div class="category-meta">{escape(detail)}</div><span class="status-chip {status_class}">{escape(status)}</span></div></div>',
        unsafe_allow_html=True,
    )


def editorial_story(
    section_id: str,
    eyebrow: str,
    name: str,
    title: str,
    description: str,
    status: str,
    primary_metric: str,
    secondary_metric: str,
    focus: str,
    class_name: str,
    image_src: str,
    image_alt: str,
    secondary_src: str | None = None,
    secondary_alt: str = "",
) -> None:
    secondary_image = ""
    if secondary_src:
        secondary_image = (
            f'<img class="editorial-image editorial-image-secondary" '
            f'src="{escape(secondary_src)}" alt="{escape(secondary_alt)}">'
        )
    st.html(
        f"""
        <section id="{escape(section_id)}" class="editorial-story {escape(class_name)}">
            <div class="editorial-media">
                <img class="editorial-image editorial-image-primary" src="{escape(image_src)}" alt="{escape(image_alt)}">
                {secondary_image}
                <div class="editorial-media-index">Category signal / {escape(eyebrow)}</div>
                <div class="editorial-media-label">{escape(name)}</div>
            </div>
            <div class="editorial-copy">
                <div class="editorial-eyebrow">{escape(eyebrow)} · {escape(status)}</div>
                <div class="editorial-title">{escape(title)}</div>
                <div class="editorial-description">{escape(description)}</div>
                <div class="editorial-signal">
                    <div class="editorial-stat"><strong>{escape(primary_metric)}</strong><span>Current drift read</span></div>
                    <div class="editorial-stat"><strong>{escape(secondary_metric)}</strong><span>Selected comparison window</span></div>
                </div>
                <div class="editorial-focus">Primary focus: {escape(focus)}</div>
            </div>
        </section>
        """
    )


def process_card(step: str, title: str, copy: str) -> None:
    st.markdown(
        f'<div class="process-card"><div class="process-step">{escape(step)}</div><div class="process-title">{escape(title)}</div><div class="process-copy">{escape(copy)}</div></div>',
        unsafe_allow_html=True,
    )


def action_card(
    rank: int,
    division: str,
    department: str,
    revenue_change: float,
    volume_change: float,
    price_change: float,
    explanation: str,
    action: str,
) -> None:
    st.markdown(
        f"""
        <div class="action-card">
            <div class="action-card-head">
                <span class="action-rank">Priority {rank:02d}</span>
                <span class="action-division">{escape(str(division))}</span>
            </div>
            <div class="action-card-body">
                <div class="action-title">{escape(str(department))}</div>
                <div class="action-signals">
                    <span class="action-signal">Revenue {revenue_change:+.1f}%</span>
                    <span class="action-signal">Units {volume_change:+.1f}%</span>
                    <span class="action-signal">Price {price_change:+.1f}%</span>
                </div>
                <div class="action-copy">{escape(str(explanation))}</div>
                <div class="action-next">{escape(str(action))}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
