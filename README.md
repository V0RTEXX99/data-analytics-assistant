# AI-Powered Data Analytics Assistant

A Streamlit frontend for an AI-powered data analytics workflow:
upload a CSV → view its schema → ask a question in plain English →
review the generated SQL → run it → approve the results → visualize →
see quick insights.

This version uses **mock functions** for SQL generation and execution,
so it runs completely standalone with no backend or API keys required.
Swap `generate_sql` and `execute_query` in `utils/sql_utils.py` for real
implementations (e.g. an LLM call and a database/DuckDB query) to make
it fully functional.

## Project Structure

```
ai_data_analytics_assistant/
├── app.py                    # Main Streamlit app (page layout & workflow)
├── requirements.txt          # Python dependencies
├── README.md                 # This file
└── utils/
    ├── __init__.py
    ├── sql_utils.py           # generate_sql() and execute_query() mocks
    ├── chart_utils.py         # build_chart() using Plotly Express
    └── insights_utils.py      # generate_insights() summary stats
```

## Setup

1. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the app:
   ```bash
   streamlit run app.py
   ```

4. Open the URL Streamlit prints (usually `http://localhost:8501`).

## Workflow

1. **Upload CSV** — upload any `.csv` file; see a preview, row/column
   counts, column names, and data types.
2. **Schema** — the detected schema is shown in a table and stored in
   the `schema_info` DataFrame.
3. **Natural Language Query** — type a question and click
   **Generate SQL** to get a (mock) SQL query.
4. **Run Query** — click **Run Query** to get a (mock) result set.
5. **Approve Results** — click **Approve Results** to unlock the
   visualization section.
6. **Visualize** — pick a chart type (Bar, Line, Scatter, Pie,
   Histogram) plus X/Y columns to render an interactive Plotly chart.
7. **Insights** — pick a numeric column to see record count, max, min,
   mean, and median.

## Making It "Real"

To connect a real backend, edit `utils/sql_utils.py`:
- `generate_sql(user_query, schema_info)` — call an LLM (e.g. the
  Anthropic API) with a prompt built from the user's question and the
  schema, and parse out the SQL.
- `execute_query(sql_query, source_df)` — run the SQL against a real
  engine, such as [DuckDB](https://duckdb.org/) directly on the
  uploaded DataFrame, or a proper SQL database.

No other files need to change — `app.py` only calls these two
functions and doesn't care how they're implemented internally.
