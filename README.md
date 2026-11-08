# AI-Powered Data Analytics Assistant

A Streamlit application that lets you analyse a CSV file by asking questions in plain English. The app loads your CSV into an in-memory SQL database, uses an LLM (through the Groq API) to turn your question into SQL, runs the SQL only after you approve it, and then shows the result as interactive charts together with AI-generated insights.

## Features

- Upload any CSV file. It is loaded into a table in an in-memory SQLite database.
- View the generated SQL schema, column details (types, missing values, unique counts) and a random sample of records.
- Ask questions in natural language. If the question is ambiguous, the assistant asks a follow-up question before generating SQL.
- Every generated query is checked for valid syntax, correct tables and columns, and semantic correctness. Queries that fail are corrected automatically where possible.
- A primary SQL query and, when a genuinely different approach exists, an alternative SQL query are shown. Only the primary query runs, and only after you approve it.
- Smart chart options (Bar, Line, Scatter, Pie, Histogram) chosen from the column types in the query result.
- AI-written business insights about the query result.
- Ask as many questions as you like, or upload a different file at any time. The previous table is removed when a new file is uploaded.

## Control Flow

### Overview

```
                          streamlit run app.py
                                   |
                                   v
     +---------------------------------------------------------------+
     | 1. Upload CSV                                                 |
     |    pd.read_csv -> clean_column_names -> make_table_name       |
     |    InMemorySQL.load_dataframe  (creates the SQLite table)     |
     |    InMemorySQL.describe_table  (returns the schema dict)      |
     +---------------------------------------------------------------+
                                   |
                                   v
     +---------------------------------------------------------------+
     | 2. Detected Schema (display only)                             |
     |    CREATE TABLE statement, record count, column details,      |
     |    10 random records                                          |
     +---------------------------------------------------------------+
                                   |
                                   v
     +---------------------------------------------------------------+
     | 3. Ask a Question                                             |
     |    process_user_question(schema, question, clarifications)    |
     |       |                                                       |
     |       +-- clarification_needed -> user answers -> call again  |
     |       +-- error                -> message shown, stop         |
     |       +-- success              -> primary_sql, alternative_sql|
     +---------------------------------------------------------------+
                                   |
                                   v
     +---------------------------------------------------------------+
     | 4. Approve and Run (primary_sql only)                         |
     |    run_read_query -> classify_sql must be READ                |
     |                   -> to_sqlite (PostgreSQL -> SQLite)         |
     |                   -> InMemorySQL.run_query                    |
     |    Result: a pandas DataFrame                                 |
     +---------------------------------------------------------------+
                                   |
                  +----------------+----------------+
                  v                                 v
     +---------------------------+     +---------------------------+
     | 5. Visualize              |     | 6. AI Insights            |
     |    analyze_result         |     |    generate_ai_insights   |
     |    get_chart_recommend... |     |    (runs on button click) |
     |    create_chart           |     |                           |
     +---------------------------+     +---------------------------+
                  |                                 |
                  +----------------+----------------+
                                   |
              Ask another question  -> back to step 3
              Upload a different CSV -> back to step 1
```

### Step by step

1. **Upload CSV.** When a file is uploaded, `app.py` reads it with pandas, makes the column names SQL-safe (for example `Order Date` becomes `order_date`) and derives a table name from the file name (`Sales Data.csv` becomes `sales_data`). `InMemorySQL.load_dataframe` creates the table in an in-memory SQLite database, and `InMemorySQL.describe_table` returns the schema in the format the SQL pipeline expects.
2. **Detected Schema.** The app shows the CREATE TABLE statement that SQLite generated, the number of records read back from the table, the number of columns, missing values and duplicate rows, a per-column table (SQL type, pandas dtype, non-null, missing and unique counts) and 10 random records. The random records are picked once per upload so they do not change on every interaction.
3. **Ask a question.** The question and the schema are passed to `process_user_question` in `member_2/main/pipeline.py`. The result is handled by its `status` field:
   - `clarification_needed`: the question is shown to you. Your answer is added to the clarification history and the pipeline is called again with the original question plus all answers.
   - `error`: the reason is shown (for example, the requested column does not exist, or SQL validation failed even after correction attempts).
   - `success`: the interpreted question, `primary_sql` and, if present, `alternative_sql` are displayed together with the validation details.
4. **Approve and run.** Clicking **Approve & Run Primary SQL** runs only `primary_sql`. The alternative query is shown for reference and is never executed. Before running, the query is checked again to confirm it is a single read-only SELECT statement, and it is converted from PostgreSQL to SQLite syntax.
5. **Visualize.** The query result DataFrame is analysed to find numeric, categorical and date columns. Only chart types that fit those columns are offered, and the X-axis and Y-axis selectors are filled with the matching columns.
6. **AI insights.** Clicking **Generate AI Insights** sends summary statistics and a sample of the result to the LLM, together with the interpreted question, and displays the returned analysis. Insights are generated on a button click so that the LLM is not called on every Streamlit re-run.

### SQL generation pipeline (member_2)

`process_user_question(schema, user_question, clarification_history)` runs these stages:

```
1. Build context          original question + previous clarification answers
2. understand_query       LLM decides: CLEAR or CLARIFICATION_NEEDED
3. generate_sql           LLM returns primary_sql and optional alternative_sql
                          (recent entries from correction_memory.json are
                           included in the prompt as lessons)
4. validate_sql           single SELECT only, parses as PostgreSQL,
                          tables and columns exist in the schema
5. correct_and_revalidate semantic check by the LLM; if the SQL is invalid or
                          answers the wrong question, the LLM corrects it
                          (up to 2 attempts). Successful corrections are saved
                          to correction_memory.json
6. alternative_sql        validated and corrected independently; dropped if
                          it cannot be validated
7. Return                 structured dictionary (see below)
```

### Data formats between components

| Step | Function | Input | Output |
|---|---|---|---|
| Schema | `InMemorySQL.describe_table(table_name)` | table name (string) | `{"table_name": "...", "columns": {"column": "SQL_TYPE", ...}}` |
| SQL generation | `process_user_question(schema, question, clarification_history)` | schema dict, question string, list of answer strings | dict with `status` (`success`, `clarification_needed` or `error`), `primary_sql`, `alternative_sql`, `interpreted_question`, `validation`, `semantic_validation`, `correction_attempts`, `error` |
| Execution | `run_read_query(db, primary_sql)` | `InMemorySQL` object, SQL string | `(DataFrame, SQL text that was executed)` |
| Charts | `analyze_result(df)`, `get_chart_recommendations(analysis)`, `create_chart(df, chart_type, x, y)` | result DataFrame | analysis dict, list of chart names, Plotly figure |
| Insights | `generate_ai_insights(df, question)` | result DataFrame, question string | markdown text |

### State handling

- Generating SQL for a new question clears the previous SQL, query result, charts and insights.
- Uploading a different file drops the previous table from the database, clears all derived state and builds a new table from the new file.
- Removing the uploaded file drops its table and clears everything.
- Chart widgets and insights are tied to each query run, so they never carry over from an earlier query.

## Project Structure

```
.
|-- app.py                         Main Streamlit program (run this)
|-- requirements.txt               Python dependencies
|-- .env.example                   Template for the .env file
|-- correction_memory.json         Saved SQL corrections (created and updated by the app)
|
|-- database_utils/
|   `-- in_memory_sql_db.py        InMemorySQL: SQLite in-memory database wrapper
|
|-- utils/
|   `-- db_helpers.py              Table/column name cleaning, column profile,
|                                  PostgreSQL-to-SQLite conversion, read-only query runner
|
|-- member_2/                      Natural language to SQL
|   |-- main/
|   |   |-- pipeline.py            process_user_question: the full pipeline
|   |   |-- query_understanding.py Decides whether a question is clear enough
|   |   |-- sql_generator.py       Generates primary and alternative SQL
|   |   |-- prompt_builder.py      Builds the SQL generation prompt
|   |   |-- sql_validator.py       Syntax, schema and read-only validation
|   |   |-- semantic_validator.py  Checks that the SQL answers the question
|   |   |-- sql_correction.py      Corrects invalid SQL and revalidates it
|   |   |-- correction_memory.py   Stores and loads past corrections
|   |   `-- llm_client.py          Reads GROQ_API_KEY and GROQ_MODEL from .env
|   `-- test/                      Test scripts for the pipeline
|
|-- member_3/                      Visualization and insights
|   |-- visualization.py           Used by app.py: chart analysis and creation
|   |-- ai_insights.py             Used by app.py: AI-generated insights
|   `-- (other files)              Separate standalone PostgreSQL version; not used by app.py
|
`-- testing/                       Placeholder for additional tests
```

The files in `member_3` other than `visualization.py` and `ai_insights.py` (its own `app.py`, `dashboard.py`, `database.py`, `postgres_executor.py` and `sql_generator.py`) belong to a separate standalone version and are not used by the main app. They need `sqlalchemy` and `psycopg2`, which are not listed in `requirements.txt`.

## Requirements

- Python 3.10 or newer (developed and tested on Python 3.12)
- A Groq API key
- The Python packages in `requirements.txt`: streamlit, pandas, plotly, numpy, groq, python-dotenv, sqlglot, sqlparse

## Setup and Running

1. Clone the repository and move into it:

   ```bash
   git clone https://github.com/V0RTEXX99/data-analytics-assistant.git
   cd data-analytics-assistant
   ```

2. Create and activate a virtual environment (recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate        # Windows: venv\Scripts\activate
   ```

3. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the repository root. You can copy the template:

   ```bash
   cp .env.example .env            # Windows: copy .env.example .env
   ```

   Then edit `.env` and fill in both values:

   ```
   GROQ_API_KEY=your_api_key
   GROQ_MODEL=openai/gpt-oss-20b
   ```

   - `GROQ_API_KEY` is your key from the Groq console.
   - `GROQ_MODEL` is the model used for every AI step: query understanding, SQL generation, validation, correction and insights.

5. Start the app from the repository root:

   ```bash
   streamlit run app.py
   ```

6. Open the address Streamlit prints in the terminal, usually `http://localhost:8501`.

Run the command from the repository root. The `member_2`, `member_3` and `utils` imports resolve relative to it, and `correction_memory.json` is read and written in the directory you start the app from.

## Using the App

1. Upload a CSV file in section 1.
2. Review the generated schema, column details and random records in section 2.
3. Type a question in section 3, for example `Show the top 5 cities by average rating`, and click **Generate SQL**. Answer the follow-up question if one appears.
4. Check the primary SQL (and the alternative, if shown), then click **Approve & Run Primary SQL** in section 4.
5. Choose a chart type and axes in section 5.
6. Click **Generate AI Insights** in section 6.
7. To continue, edit the question and click **Generate SQL** again, or upload a different CSV.

## Design Notes

- **Read-only execution.** The pipeline only accepts a single SELECT statement. The app checks this again immediately before running the query, so INSERT, UPDATE, DELETE, DDL and multiple statements are rejected.
- **SQL dialect.** The SQL pipeline generates and validates PostgreSQL syntax, while the in-memory database is SQLite. The query is converted with sqlglot just before it runs. If the executed text differs from the generated text, both are shown.
- **Column and table names.** Names are converted to lowercase snake_case, and SQL reserved words get a suffix. This keeps the generated SQL consistent with the schema the validator checks against.
- **One model for all AI steps.** The model name is read from `.env` and is not hard-coded anywhere. The SQL generation stage sends `reasoning_effort` and a strict JSON schema, which are written for the gpt-oss models. If you choose a different model and Groq rejects those parameters, switch back to a gpt-oss model.
- **Correction memory.** When an invalid query is corrected successfully, the original query, the error and the fix are stored in `correction_memory.json` and included as lessons in later prompts.

## Running the Tests

The scripts in `member_2/test` are standalone and can be run from the repository root:

```bash
python member_2/test/test_sql_validator.py
python member_2/test/test_security.py
```

These two use only the SQL validator and need no API key. Most of the other scripts in `member_2/test` call the Groq API and require the `.env` values described above.

## Troubleshooting

| Problem | Cause and fix |
|---|---|
| The page shows that `GROQ_API_KEY` and/or `GROQ_MODEL` is missing | Add both to the `.env` file in the repository root and restart Streamlit. |
| `ModuleNotFoundError: No module named 'member_2'` (or `utils`) | Start the app from the repository root with `streamlit run app.py`. |
| A 400 error from Groq that mentions `reasoning_effort` or `json_schema` | The selected `GROQ_MODEL` does not support these parameters. Use a gpt-oss model such as `openai/gpt-oss-20b`. |
| The query could not be run | The generated SQL used a function SQLite does not support. Rephrase the question, or check the executed SQL shown in section 4. |
| "Could not load this CSV file" | The file could not be parsed as a CSV, or it contains no data rows. |