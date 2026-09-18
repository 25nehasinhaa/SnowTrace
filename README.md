# SnowTrace

SnowTrace is a Streamlit retail intelligence workspace for explaining post-holiday customer behavior drift through a BI frontend backed by Snowflake-style data. It uses a luxury retail dataset as a stand-in for ecommerce, CPG, and marketplace analytics: multi-page navigation, cached Snowflake reads, custom timeframe filters, scenario planning, pivot views, and stakeholder exports.

## Structure

```text
app/
  Home.py
  pages/
    1_Where_Behavior_Shifts.py
    2_What_If_We_Act.py
    3_Pivot_Builder.py
    4_Executive_Brief.py
  lib/
    data.py
    theme.py
sql/
  01_setup.sql
data/
  drift_summary_sample.csv
requirements.txt
README.md
```

## Run Locally

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app/Home.py
```

When the app is not running inside Snowflake, it falls back to `data/drift_summary_sample.csv` so the pages remain demoable without credentials.

## Snowflake Setup

Human action needed before I can help you push or deploy:

1. Create a new Snowflake trial account and sign in.
2. Open a Snowflake SQL worksheet.
3. Paste and run `sql/01_setup.sql`.
4. Confirm the final `SELECT * FROM ANALYTICS.DRIFT_SUMMARY` returns rows.
5. Create a Streamlit app in Snowflake or connect this repository through your preferred deployment flow.

The setup script creates:

- `SNOWTRACE_WH`
- `SNOWTRACE` database
- `RAW.RETAIL_TRANSACTIONS`
- `ANALYTICS.HOLIDAY_BASELINE`
- `ANALYTICS.POST_HOLIDAY_CURRENT`
- `ANALYTICS.DRIFT_DETECTION`
- `ANALYTICS.DRIFT_SUMMARY`

## Implementation Notes

- `st.cache_resource` caches the Snowpark session separately from query results because the session is a connection-like resource.
- `st.cache_data(ttl=300)` caches result DataFrames for five minutes so user navigation and repeated filters stay responsive.
- The Snowpark session argument is named `_session` in the cached loader. Streamlit does not hash underscored arguments, which avoids serialization errors for unhashable Snowpark session objects.
- Timeframe filters are passed to Snowflake with bind parameters instead of string-formatted SQL.
- The what-if calculator uses `st.session_state` for both the slider and saved scenario list, so choices persist across reruns and page switches.
- The SQL includes `RANK() OVER (PARTITION BY DIVISION ORDER BY ABS(PRICE_CHANGE_PCT) DESC)` and `AVG() OVER (PARTITION BY DIVISION)`, both surfaced in the app table and chart hover.

## GitHub Setup

Human action needed when you are ready to publish:

1. Create a new empty GitHub repository named `SnowTrace`.
2. Authenticate Git locally if needed.
3. Add the remote:

```bash
git remote add origin https://github.com/<your-username>/SnowTrace.git
git branch -M main
git push -u origin main
```
