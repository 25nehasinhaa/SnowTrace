# SnowTrace Interview Guide

This guide explains SnowTrace from the business problem down to the implementation details. Use it to understand the project, not as a script to memorize. In an interview, describe what the repository actually does, acknowledge its boundaries, and explain how you would extend it in production.

## 1. Thirty-Second Explanation

SnowTrace is a multi-page retail decision intelligence application built with Python, Streamlit, Pandas, Plotly, SQL, Snowflake, and Snowpark. It compares a baseline period with a current period, detects material category movement across price, units, revenue, reviews, and delivery performance, ranks the strongest signals, and turns them into business-facing analysis, directional pricing scenarios, pivots, and an executive brief.

It uses the Brazilian E-Commerce Public Dataset by Olist. The application can use an active Snowflake session, process raw Olist files locally with Pandas, or fall back to a committed processed sample.

## 2. Business Problem

Commercial teams often receive many metrics but still need to answer three practical questions:

1. Which categories moved materially from the previous period?
2. Is the movement large and reliable enough to investigate?
3. What decision should the team consider next?

Looking at revenue alone is not sufficient. Revenue may rise because price increased while units fell. Stable sales may hide weaker reviews or slower delivery. SnowTrace combines these signals into a category-level read that a merchandising or brand team can use during a weekly performance review.

The application does not claim to prove causality. It identifies unusual movement and supplies an explainable starting point for investigation.

## 3. What Decision Drift Means

Decision Drift is the project's name for a category moving materially away from a selected baseline across one or more business signals.

A category is classified as `DRIFT` when both periods have volume and at least one condition is true:

- absolute price change is at least 8%;
- absolute volume change is at least 18%;
- absolute revenue change is at least 20%; or
- absolute review-score change is at least 0.4 points.

If either period is missing, the result is `INSUFFICIENT_DATA`. If no threshold is crossed, it is `STABLE`.

The thresholds are fixed in Python and SQL. They are business rules for this implementation, not statistically learned anomaly thresholds and not currently configurable by users.

## 4. End-to-End Data Flow

```text
Olist source data
    |
    +-- Snowflake RAW tables -> SQL/Snowpark query --+
    |                                                |
    +-- local CSV files -> Pandas joins/aggregation -+-> shared drift summary
    |                                                |
    +-- committed processed sample ------------------+
                                                     |
                                                     v
                         Streamlit filters, KPIs, Plotly chart,
                         scenario calculator, pivot, executive brief
```

The important design choice is a shared output schema. Every data source produces the same columns, so the Streamlit pages do not need separate UI logic for Snowflake and local execution.

Source priority in `load_drift_summary()`:

1. Query through an active Snowpark session.
2. Build the summary from the required files in `data/raw/`.
3. Read `data/drift_summary_sample.csv`.

If the Snowflake query fails, the application falls back to local processing instead of failing the entire interface.

## 5. Repository Walkthrough

```text
SnowTrace/
  .streamlit/
    config.toml
  app/
    Home.py
    lib/
      data.py
      theme.py
    pages/
      1_Where_Behavior_Shifts.py
      2_What_If_We_Act.py
      3_Pivot_Builder.py
      4_Executive_Brief.py
    static/images/
  data/
    drift_summary_sample.csv
  docs/
    images/
    SNOWTRACE_INTERVIEW_GUIDE.md
  sql/
    01_setup.sql
  tests/
    test_data_logic.py
  .gitignore
  README.md
  requirements.txt
```

### `.streamlit/config.toml`

Defines the approved application theme and enables static asset serving. The main palette uses black, neutral gray, and pastel blue. Credentials are not stored here.

### `app/Home.py`

The business introduction and visual entry point. It:

- creates the top navigation;
- explains the product's purpose;
- loads the same drift summary used by the analytical pages;
- presents Fashion, Beauty, and Fragrance category stories;
- shows operating-picture KPIs;
- explains the detect, simulate, and act workflow.

The category sections are not independent datasets. They are editorial views over filtered rows from the shared summary.

### `app/lib/data.py`

The application's data and business-logic layer. It owns:

- timeframe defaults and shared session state;
- Snowpark active-session detection;
- cached data loading;
- source fallback behavior;
- local CSV ingestion and natural-key deduplication;
- joins and order-fact construction;
- period aggregation;
- percentage-change calculations;
- drift and confidence classification;
- severity ranking;
- business explanations and recommended actions;
- parameterized Snowflake SQL execution;
- currency and source labels.

This separation keeps data rules out of page scripts and gives every page consistent metrics.

### `app/lib/theme.py`

Contains shared presentation helpers and CSS. It supplies metric cards, action cards, editorial category layouts, typography, responsive behavior, hover states, scroll effects, and the custom snowflake cursor.

The cursor is purely presentational. Interactive elements retain pointer behavior, and the cursor does not intercept events.

### `app/pages/1_Where_Behavior_Shifts.py`

The main diagnostic page. A business user can:

- choose a division;
- review drift count, average price change, average revenue change, and highest-priority department;
- inspect a horizontal Plotly chart of the 20 largest absolute price movements;
- switch between priority-only and all-category readouts;
- inspect confidence and multiple percentage changes;
- review ranked recommended actions;
- continue to scenario planning or the executive brief.

The horizontal chart is intentional because long category names are easier to read on the y-axis than as rotated x-axis labels.

### `app/pages/2_What_If_We_Act.py`

A directional pricing calculator. The user selects a department and adjusts an additional price-change slider. The page recalculates:

- the resulting price-change percentage;
- an estimated revenue impact using current volume, current average price, and the proposed percentage;
- the drift classification after the proposed change.

Saved scenarios live in `st.session_state`, so they survive Streamlit reruns and page navigation during the browser session. They are not persisted to a database.

This is not a forecasting or elasticity model. It assumes current volume remains constant and is best described as a directional planning tool.

### `app/pages/3_Pivot_Builder.py`

Uses `pandas.pivot_table()` to regroup the shared summary. Users can choose a row grouping such as division, department, or confidence level and a measure such as price, volume, revenue, review, or delivery change.

This demonstrates lightweight business exploration without issuing a separate query for every view when the summary is already in memory.

### `app/pages/4_Executive_Brief.py`

Turns the analytical output into a concise stakeholder artifact. It calculates:

- flagged category count;
- downside revenue exposure;
- high-confidence signal count;
- division with the highest concentration of alerts;
- six highest-priority decisions;
- division-level exposure roll-up.

The page builds a Markdown brief in memory and exposes it through `st.download_button`.

### `sql/01_setup.sql`

Creates the Snowflake project objects:

- `SNOWTRACE_WH` warehouse;
- `SNOWTRACE` database;
- `RAW` and `ANALYTICS` schemas;
- raw Olist tables;
- category mapping;
- `ANALYTICS.ORDER_FACT`;
- `ANALYTICS.CATEGORY_MONTHLY_METRICS`;
- `ANALYTICS.DRIFT_SUMMARY`.

The SQL demonstrates joins, aggregations, null-safe percentage calculations, full outer joins between periods, `CASE` business rules, and window functions for rank and division averages.

The setup script uses `CREATE OR REPLACE` and `ACCOUNTADMIN` for a controlled project setup. A production implementation should use migrations and a dedicated least-privilege role.

### `tests/test_data_logic.py`

Uses Python's standard `unittest` framework. The five tests cover:

- a valid percentage change and a zero baseline;
- missing-period classification;
- revenue-driven drift classification;
- recommendation selection for simultaneous revenue and volume decline;
- preservation of expected columns for an empty aggregation.

These are focused unit tests. The repository does not contain live Snowflake integration tests or browser end-to-end tests.

## 6. Core Metrics

### Volume

Count of order items in the selected period, grouped by division and department.

### Revenue

For this implementation, item revenue is `price + freight_value`.

### Average price

Mean item price for the category and period.

### Review score

Reviews are first averaged by order to avoid multiplying review rows during the order-item join. The category metric is then averaged over the analytical fact.

### Delivery days

Elapsed days from purchase timestamp to delivered-customer timestamp.

### Percentage change

```text
((current - baseline) / baseline) * 100
```

A zero baseline becomes null instead of causing division by zero.

### Severity score and rank

```text
abs(price change) + abs(volume change) + abs(revenue change)
```

Categories are ranked within their division. This score is explainable but is not weighted by revenue scale, statistical significance, or strategic importance.

### Confidence

Based on combined item volume across the two periods:

- `High`: at least 400;
- `Medium`: at least 120;
- `Directional`: below 120;
- `Low`: one period is missing.

### Revenue exposure

For drifting categories:

```text
max(baseline revenue - current revenue, 0)
```

It represents downside relative to the baseline and does not count revenue growth as negative exposure.

## 7. Pandas Processing Details

The local path loads only required columns where practical. Before joining:

- order items are deduplicated by `(order_id, order_item_id)`;
- products are deduplicated by `product_id`;
- category translations are deduplicated by the source category key;
- reviews are averaged by `order_id`.

The join order is items to orders, then products, translations, and reviews. Missing translated categories fall back to the original category and then to `uncategorized`. Categories not present in the curated division map fall back to `Marketplace`.

Only delivered, shipped, and invoiced orders are retained. The local and Snowflake paths apply equivalent transformation logic, although they are alternative paths rather than concurrent processing.

## 8. Snowflake and Snowpark Details

### Why Snowflake

Snowflake is appropriate for the warehouse layer because the project uses relational commerce data, repeated aggregations, governed analytical views, and SQL transformations that can execute close to the data. It separates storage and compute and provides a clear path from raw tables to analytical objects.

### Where Snowpark is used

`get_snowpark_session()` calls `snowflake.snowpark.context.get_active_session()`. When available, `_query_snowflake()` passes SQL and bound date parameters to `session.sql()` and converts the result with `to_pandas()` for Streamlit.

The project does not use the Snowpark DataFrame transformation API extensively. Be precise: Snowpark supplies the active session and executes parameterized SQL; the UI consumes the returned Pandas DataFrame.

### Query safety

Date values are passed through `params`, not inserted into SQL strings. This avoids SQL injection through the date controls and improves clarity around parameter handling.

### Caching

- `@st.cache_resource` stores the Snowpark session because it is a connection-like resource.
- `@st.cache_data(ttl=300)` stores the serializable drift-summary DataFrame for five minutes.
- The session parameter is named `_session`, so Streamlit does not attempt to hash a non-serializable Snowpark session object.

The date inputs remain normal cache-key arguments, so changing a timeframe produces a distinct cached result.

### Failure behavior

Session acquisition is wrapped safely. If there is no active session, or if the Snowflake query raises an exception, the application falls back to local Olist processing or the sample summary.

For production, the broad exception handling should log a sanitized operational error and distinguish authentication, authorization, object-not-found, timeout, and query failures.

## 9. Streamlit Design Decisions

### Multi-page layout

Each page maps to one business task instead of placing every control on one dashboard. This reduces cognitive load and creates a clear diagnostic-to-action workflow.

### Session state

Shared timeframe values and saved scenarios use `st.session_state`. Streamlit reruns the page script after widget interactions; session state prevents user selections from disappearing on each rerun.

### Cached data versus session state

Caching avoids repeated expensive loading or querying. Session state preserves user-specific interaction state. They solve different problems and should not be described interchangeably.

### Empty states

Pages stop with a business-readable message when no rows are available. Categories missing one comparison period are classified separately instead of being treated as stable.

### Tables and exports

`st.dataframe` provides sorting, searching, column visibility, fullscreen mode, and CSV download. The executive brief adds a purpose-built Markdown download.

### Responsive behavior

The theme adapts editorial sections and typography for narrower viewports. Category stories stack vertically on small screens, and fixed-format elements have stable dimensions to avoid layout shifts.

## 10. Business Reason for Each Section

### Home

Answers “What is this product and where should I begin?” The category stories provide context before the user enters detailed tables.

### Where Behavior Shifts

Answers “Where should I investigate?” It prioritizes diagnosis, comparison, and category ranking.

### What If We Act

Answers “What does a proposed price move imply under a simple constant-volume assumption?” It supports discussion, not automated pricing decisions.

### Pivot Builder

Answers “Can I regroup the same analytical result for a different planning question?” It gives analysts flexibility without changing the underlying data.

### Executive Brief

Answers “What should a business owner know and do next?” It compresses the analysis into exposure, priorities, actions, and a downloadable artifact.

## 11. Recommended Interview Demonstration

1. Start on the home page and explain Decision Drift in business language.
2. Open **Where Behavior Shifts** and change the division filter.
3. Point out the KPI definitions and the horizontal chart choice.
4. Switch between **Priority only** and **All categories**.
5. Open a recommended action and explain that rules are transparent and deterministic.
6. Move to **What If We Act**, adjust the slider, and save two scenarios.
7. Explain `st.session_state` and the constant-volume limitation.
8. Open **Pivot Builder** and change both selectors.
9. Open **Executive Brief** and download the Markdown summary.
10. Finish with the Snowflake/local fallback architecture and production improvements.

## 12. Questions You Should Be Ready to Answer

### “Why did you build this?”

Retail teams need to distinguish meaningful category movement from routine variation. I built one workflow that connects detection, investigation, a simple action scenario, exploratory reshaping, and stakeholder communication.

### “Why not just show a dashboard?”

The work is sequential. A user first identifies movement, then investigates a category, tests a possible action, and communicates a decision. Separate pages reduce control density and make the workflow easier for non-technical users.

### “How do filters affect the data?”

The date ranges are inputs to the cached data loader and Snowflake query. Division filtering is applied to the returned summary on the diagnostic page. Scenario and pivot selectors operate over the shared summary DataFrame.

### “How do you handle Streamlit reruns?”

Widget interactions rerun the page. Shared timeframes and saved scenarios are kept in session state, expensive resource acquisition uses `cache_resource`, and serializable result data uses `cache_data` with a five-minute TTL.

### “What caused serialization concerns?”

A Snowpark session is a connection-like object and should not be serialized as cached data. It is cached as a resource. The `_session` argument is excluded from Streamlit's data-cache hashing, while dates still determine result-cache entries.

### “How would you improve performance on a large warehouse?”

Push filtering and aggregation into Snowflake, select only needed columns, inspect the query profile, reduce repeated joins through governed analytical tables or dynamic tables, use clustering only when access patterns justify it, limit returned rows, paginate large tables, and measure cache hit behavior. I would validate performance with real warehouse volumes before tuning.

### “How would you productionize it?”

Use a least-privilege role, managed secrets or workload identity, controlled migrations, automated unit and integration tests, environment-specific configuration, structured logging, warehouse resource monitors, data-quality checks, CI/CD, and observability. I would also replace silent broad fallback with monitored and user-visible source status.

### “How would you make thresholds configurable?”

Move them into a governed configuration table with effective dates, validation, ownership, and an audit trail. Load the active policy once, pass it to both SQL and Python logic, and test parity between execution paths.

### “How do you know the local and Snowflake results agree?”

They implement equivalent formulas and schema, but the repository does not yet contain an automated parity test against a Snowflake test schema. That is a clear next integration test.

### “What is the biggest analytical limitation?”

Thresholds are heuristic, severity is unweighted, and the scenario calculator assumes constant volume. The tool supports prioritization and discussion; it is not a causal model or production pricing optimizer.

## 13. Mapping to the Streamlit / Junior Data Scientist Role

### Strong direct matches

- Multi-page Streamlit application structure.
- Business-facing filters, metric cards, charts, tables, pivots, date controls, calculators, and exports.
- Snowflake SQL with joins, aggregation, full outer joins, and window functions.
- Pandas transformations and source fallback.
- Session-state scenario comparison.
- `cache_resource` versus `cache_data` decisions.
- Handling an unhashable Snowpark resource by excluding `_session` from the data-cache key.
- E-commerce domain and non-technical stakeholder workflow.
- Git history and recruiter-facing documentation.

### Honest boundaries

- SnowTrace has been tested primarily with the local Olist path; live Snowflake integration requires an active session.
- The repository does not demonstrate migration between deployment environments.
- It does not benchmark very large warehouse result sets.
- Scenario calculations are deterministic, not model output from a data-science pipeline.

### Best positioning

Lead with this project for that role. Demonstrate the application and spend time explaining page ownership, stakeholder workflow, SQL design, caching, session state, failure fallback, and how you would collaborate with model owners.

## 14. Mapping to the Snowflake Developer Role

### What SnowTrace supports

- Snowflake database, schema, warehouse, table, and view creation.
- Layered raw and analytical schemas.
- SQL joins, aggregation, window functions, business rules, and parameterized retrieval.
- Snowpark session use.
- Local and warehouse transformation parity.
- Basic security awareness: ignored secrets, parameter binding, and least-privilege recommendation.

### What it does not prove

- Stored procedures.
- Snowflake tasks or streams.
- Snowpipe, Kafka, or real-time ingestion.
- AWS or GCP integration.
- Production orchestration and monitoring.
- Query-profile tuning at scale.
- Formal governance controls, masking policies, row-access policies, or lineage tooling.

### Best positioning

Use SnowTrace to discuss SQL, warehouse-layer modeling, parameterized access, and application integration. Do not claim production ELT orchestration or cloud integration from this project. Prepare a separate conceptual answer for tasks, streams, Snowpipe, dynamic tables, warehouse sizing, query profile analysis, and role-based access control.

## 15. Mapping to the Senior Software Engineer Role

### Transferable evidence

- Python module organization.
- Separation between data/business logic and UI.
- Unit tests around important edge cases.
- Git-based delivery.
- Defensive fallback and empty-state behavior.
- Clear documentation and security-conscious configuration.

### Major gaps relative to that role

- No backend API or microservice framework.
- No AWS services.
- No MongoDB or NoSQL modeling.
- No Docker or Kubernetes manifests.
- No CI/CD workflow in this repository.
- No PL/SQL stored procedures.
- No production incident history, RCA artifact, or observability stack.
- No LLM pipeline.

### Best positioning

SnowTrace is supporting evidence for Python and product thinking, not proof of senior cloud-native backend experience. For that interview, pair it with genuine examples from your professional experience involving APIs, AWS, databases, deployment, testing, and incidents. Do not stretch SnowTrace to cover technologies it does not use.

## 16. Production Improvements by Priority

1. Add a dedicated application role and replace account-level setup privileges.
2. Add Snowflake integration and Python/SQL parity tests.
3. Add structured error logging and explicit source-health indicators.
4. Move thresholds to governed configuration.
5. Add data-quality checks for uniqueness, nulls, accepted values, and period completeness.
6. Add CI checks for tests, formatting, dependency review, and secret scanning.
7. Add environment-specific deployment configuration.
8. Add query profiling and performance tests with production-scale volumes.
9. Persist approved scenarios and audit decisions if the workflow requires collaboration.
10. Replace the simple scenario arithmetic with a validated elasticity or forecasting model when sufficient data exists.

## 17. Claims to Avoid

Do not say that SnowTrace currently includes:

- concurrent local and cloud processing;
- user-configurable drift thresholds;
- machine-learning anomaly detection;
- demand forecasting or price elasticity;
- production-grade real-time ingestion;
- Snowflake tasks, streams, or stored procedures;
- AWS or GCP deployment;
- MongoDB;
- Docker, Kubernetes, or CI/CD;
- persistent multi-user scenario storage;
- proven large-scale query optimization.

Accurate phrasing is more defensible than a longer technology list.

## 18. Final Interview Checklist

Before an interview, make sure you can explain without looking at the code:

- the business problem and intended user;
- the source selection and fallback order;
- every drift threshold;
- the percentage-change and exposure formulas;
- confidence and severity logic;
- why the chart is horizontal;
- the difference between session state and caching;
- why the Snowpark session uses `cache_resource`;
- why `_session` is excluded from cache hashing;
- what the scenario calculator assumes;
- what the SQL views contain;
- how date parameters reach Snowflake;
- how nulls, missing periods, duplicates, and zero baselines are handled;
- what the tests cover and do not cover;
- how you would secure, test, monitor, and scale a production version;
- which requirements from each target role are demonstrated and which require other evidence.
