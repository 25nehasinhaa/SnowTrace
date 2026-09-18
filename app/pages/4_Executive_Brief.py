import streamlit as st

from lib.data import get_snowpark_session, load_drift_summary, render_timeframe_selector
from lib.theme import inject_css


st.set_page_config(page_title="Executive Brief | SnowTrace", page_icon=":bar_chart:", layout="wide")
inject_css()

st.markdown('<div class="story-kicker">Executive Takeaway</div>', unsafe_allow_html=True)
st.title("A concise readout for the business owner")

session = get_snowpark_session()
baseline_start, baseline_end, comparison_start, comparison_end = render_timeframe_selector()
df = load_drift_summary(session, baseline_start, baseline_end, comparison_start, comparison_end)

drifting = df[df["DRIFT_STATUS"] == "DRIFT"].sort_values(["DIVISION", "DRIFT_SEVERITY_RANK"])

lines = [
    "# SnowTrace Executive Brief",
    "",
    f"Baseline period: {baseline_start} to {baseline_end}",
    f"Comparison period: {comparison_start} to {comparison_end}",
    "",
]

if drifting.empty:
    st.success("No drifting departments were detected for the selected timeframe.")
    lines.append("No drifting departments were detected for the selected timeframe.")
else:
    for row in drifting.itertuples(index=False):
        paragraph = (
            f"{row.DIVISION} / {row.DEPARTMENT}: {row.BUSINESS_EXPLANATION} "
            f"Recommended action: {row.RECOMMENDED_ACTION}"
        )
        st.markdown(f'<div class="recommendation">{paragraph}</div>', unsafe_allow_html=True)
        lines.append(paragraph)
        lines.append("")

brief_markdown = "\n".join(lines)

st.download_button(
    "Download Markdown Brief",
    data=brief_markdown,
    file_name="snowtrace_executive_brief.md",
    mime="text/markdown",
)
