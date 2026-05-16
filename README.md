# SnowTrace

SnowTrace is a Snowflake-native luxury retail decision intelligence project that detects post-holiday customer behaviour drift across fashion, beauty, fragrance, and premium lifestyle categories.

## One-Line Pitch

SnowTrace detects whether customers changed what they are willing to pay after the holiday season, helping luxury merchandising teams act before revenue impact becomes obvious.

## Business Problem

During December, luxury customers often buy premium gifts such as fragrances, designer wear, and handbags. In January, purchasing intent may change. A standard dashboard may show revenue decline, but SnowTrace asks a sharper question:

> Did the average unit price customers are willing to pay shift significantly?

That makes the dashboard useful for merchandising, pricing, promotion, and inventory decisions.

## Technical Architecture

```text
SnowTrace/
├── app/
│   └── app.py
├── data/
│   └── drift_summary_sample.csv
├── sql/
│   └── 01_setup_snowtrace.sql
├── assets/
├── requirements.txt
├── README.md
└── .gitignore
```

## Layers

- `RAW.RETAIL_TRANSACTIONS`: raw transaction source of truth.
- `ANALYTICS.HOLIDAY_BASELINE`: December benchmark by division and department.
- `ANALYTICS.POST_HOLIDAY_CURRENT`: January comparison layer.
- `ANALYTICS.DRIFT_DETECTION`: physical table with drift classification.
- `ANALYTICS.DRIFT_SUMMARY`: business-facing view with explanations and recommended actions.
- Streamlit dashboard: executive scorecards, drift chart, summary table, and insight cards.

## Drift Formula

```text
Average Unit Price = SUM(REVENUE) / SUM(QUANTITY)
Price Change % = ((January Avg Price - December Avg Price) / December Avg Price) * 100
```

A category is classified as `DRIFT` when absolute average price movement exceeds 15 percent and enough data exists.

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app/app.py
```

When running locally, the app uses `data/drift_summary_sample.csv`.

## Run in Snowflake

1. Run `sql/01_setup_snowtrace.sql` in a Snowflake worksheet.
2. Create a Streamlit app in Snowflake.
3. Upload or paste `app/app.py`.
4. Make sure the app has access to:

```sql
SNOWTRACE_DB.ANALYTICS.DRIFT_SUMMARY
```

Inside Snowflake, the app automatically uses `get_active_session()`.

## GitHub

```bash
git init
git add .
git commit -m "Initial SnowTrace implementation"
git branch -M main
git remote add origin https://github.com/25nehasinhaa/SnowTrace.git
git push -u origin main
```
