"""
app.py
------
AI-Powered Data Analytics Assistant - main Streamlit program.

Flow:
    1. Upload a CSV  -> loaded into a table in an in-memory SQLite database
    2. Detected Schema -> generated SQL schema, column info, random records
    3. Ask a question -> member_2 pipeline -> primary_sql (+ alternative_sql)
    4. Approve & Run -> ONLY primary_sql is executed on the in-memory table
    5. Visualize     -> member_3 chart options and charts
    6. AI Insights   -> member_3 AI insights

Run with:
    streamlit run app.py
"""

import os

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from database_utils.in_memory_sql_db import InMemorySQL
from member_2.main.pipeline import process_user_question
from member_3.ai_insights import generate_ai_insights
from member_3.visualization import (
    analyze_result,
    create_chart,
    get_chart_recommendations,
)
from utils.db_helpers import (
    build_column_profile,
    clean_column_names,
    make_table_name,
    run_read_query,
)

load_dotenv()

SAMPLE_SIZE = 10


# --------------------------------------------------------------------------
# Page configuration
# --------------------------------------------------------------------------
st.set_page_config(
    page_title="AI-Powered Data Analytics Assistant",
    page_icon="📊",
    layout="wide",
)


# --------------------------------------------------------------------------
# Session state
# --------------------------------------------------------------------------
def init_session_state():
    """Create every session-state key used by the app, once."""
    defaults = {
        # --- loaded CSV / database ---
        "db": None,                   # InMemorySQL instance
        "file_id": None,              # identifies the uploaded file
        "table_name": None,           # table created for the CSV
        "df": None,                   # cleaned DataFrame that was loaded
        "schema": None,               # member_2 schema dict (from describe_table)
        "create_sql": None,           # CREATE TABLE statement SQLite generated
        "profile_df": None,           # per-column info table
        "sample_df": None,            # random records (picked once per upload)
        "record_count": None,         # COUNT(*) read back from the table
        # --- question / SQL generation ---
        "pending_question": None,     # the question sent to member_2
        "clarification_history": [],  # answers given to clarification questions
        "pipeline_result": None,      # dict returned by process_user_question
        # --- query execution ---
        "query_result": None,         # DataFrame returned by the primary SQL
        "executed_sql": None,         # SQL text that actually ran on SQLite
        "run_id": 0,                  # changes on every run -> fresh chart widgets
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_session_state()


def get_db():
    """Return this session's in-memory database, creating it if needed."""
    if st.session_state.db is None:
        st.session_state.db = InMemorySQL()
    return st.session_state.db


def reset_query_state():
    """Forget the current question, generated SQL and query results."""
    st.session_state.pending_question = None
    st.session_state.clarification_history = []
    st.session_state.pipeline_result = None
    st.session_state.query_result = None
    st.session_state.executed_sql = None


def clear_loaded_data():
    """Drop the current table from the database and forget everything about it."""
    if st.session_state.table_name is not None:
        get_db().delete_table(st.session_state.table_name)

    for key in (
        "file_id", "table_name", "df", "schema", "create_sql",
        "profile_df", "sample_df", "record_count",
    ):
        st.session_state[key] = None

    reset_query_state()


def load_csv_into_database(uploaded_file):
    """CSV -> DataFrame -> SQLite table -> schema, ready for member_2."""
    df = pd.read_csv(uploaded_file)

    if df.empty:
        raise ValueError("The CSV file has no data rows.")

    df.columns = clean_column_names(df.columns)
    table_name = make_table_name(uploaded_file.name)

    db = get_db()
    db.load_dataframe(df, table_name)
    st.session_state.table_name = table_name  # remembered so it can be dropped later

    schema = db.describe_table(table_name)  # {"table_name": ..., "columns": {...}}
    if schema is None:
        raise RuntimeError("Could not read the schema of the generated table.")

    count_df = db.run_query(f'SELECT COUNT(*) AS n FROM "{table_name}"')

    st.session_state.df = df
    st.session_state.schema = schema
    st.session_state.create_sql = db.get_create_statement(table_name)
    st.session_state.profile_df = build_column_profile(df, schema)
    st.session_state.sample_df = df.sample(n=min(SAMPLE_SIZE, len(df))).reset_index(drop=True)
    st.session_state.record_count = int(count_df.iloc[0, 0])


def run_pipeline():
    """Send the pending question (+ clarification answers) to member_2."""
    try:
        with st.spinner("Understanding your question and generating SQL..."):
            st.session_state.pipeline_result = process_user_question(
                st.session_state.schema,
                st.session_state.pending_question,
                st.session_state.clarification_history,
            )
    except Exception as e:
        st.session_state.pipeline_result = {
            "status": "error",
            "error": f"{type(e).__name__}: {e}",
        }


def normalize_sql(sql):
    """Whitespace/semicolon/case-insensitive form, used only to compare SQL text."""
    return " ".join(sql.split()).rstrip(";").strip().upper()


# --------------------------------------------------------------------------
# Chart section (member_3 smart chart options)
# --------------------------------------------------------------------------
def render_chart_section(result_df, key_prefix):
    """Chart-type / X / Y options are chosen from the result's column types."""
    analysis = analyze_result(result_df)
    recommendations = get_chart_recommendations(analysis)

    if not recommendations:
        st.warning("No suitable visualization found for this result.")
        return

    chart_type = st.selectbox("Choose a chart", recommendations, key=f"{key_prefix}_chart_type")

    numeric_columns = analysis["numeric_columns"]
    categorical_columns = analysis["categorical_columns"]
    datetime_columns = analysis["datetime_columns"]

    x_column = None
    y_column = None

    if chart_type in ["Bar Chart", "Pie Chart"]:
        x_column = st.selectbox("Select category column", categorical_columns, key=f"{key_prefix}_category")
        y_column = st.selectbox("Select numeric column", numeric_columns, key=f"{key_prefix}_numeric")

    elif chart_type == "Line Chart":
        x_column = st.selectbox(
            "Select X-axis column", datetime_columns + categorical_columns, key=f"{key_prefix}_line_x"
        )
        y_column = st.selectbox("Select numeric column", numeric_columns, key=f"{key_prefix}_line_y")

    elif chart_type == "Scatter Plot":
        x_column = st.selectbox("Select X-axis numeric column", numeric_columns, key=f"{key_prefix}_scatter_x")
        y_options = [column for column in numeric_columns if column != x_column]
        y_column = st.selectbox("Select Y-axis numeric column", y_options, key=f"{key_prefix}_scatter_y")

    elif chart_type == "Histogram":
        x_column = st.selectbox("Select numeric column", numeric_columns, key=f"{key_prefix}_histogram")

    try:
        figure = create_chart(result_df, chart_type, x_column, y_column)
        st.plotly_chart(figure)
    except Exception as e:
        st.error(f"Unable to create visualization: {e}")


# --------------------------------------------------------------------------
# Page title
# --------------------------------------------------------------------------
st.title("📊 AI-Powered Data Analytics Assistant")
st.caption(
    "Upload a CSV, ask questions in plain English, approve the generated SQL, "
    "and explore the result with charts and AI insights."
)
st.divider()


# ==========================================================================
# 1. CSV Upload
# ==========================================================================
st.header("1️⃣ Upload Your Data")

uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file is None:
    # File removed: drop its table and everything derived from it.
    if st.session_state.table_name is not None:
        clear_loaded_data()
else:
    file_id = getattr(uploaded_file, "file_id", None) or (uploaded_file.name, uploaded_file.size)

    if file_id != st.session_state.file_id:
        # New / different file: remove the previous table, then build a new one.
        clear_loaded_data()
        try:
            load_csv_into_database(uploaded_file)
            st.session_state.file_id = file_id
        except Exception as e:
            st.error(f"Could not load this CSV file: {e}")

if st.session_state.schema is not None:
    st.success(
        f"Loaded **{uploaded_file.name}** into the in-memory database "
        f"as table **`{st.session_state.table_name}`**."
    )
else:
    st.info("Upload a CSV file to get started.")

st.divider()


# ==========================================================================
# 2. Detected Schema
# ==========================================================================
st.header("2️⃣ Detected Schema")

if st.session_state.schema is not None:
    df = st.session_state.df

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Records", st.session_state.record_count)
    m2.metric("Columns", len(st.session_state.schema["columns"]))
    m3.metric("Missing Values", int(df.isna().sum().sum()))
    m4.metric("Duplicate Rows", int(df.duplicated().sum()))

    st.subheader("Generated SQL Schema")
    st.code(st.session_state.create_sql, language="sql")

    st.subheader("Column Details")
    st.dataframe(st.session_state.profile_df, hide_index=True)

    st.subheader(f"Random Records ({len(st.session_state.sample_df)} of {st.session_state.record_count})")
    st.dataframe(st.session_state.sample_df)
else:
    st.info("The schema will appear here once a CSV file is uploaded.")

st.divider()


# ==========================================================================
# 3. Ask a Question  (member_2 pipeline)
# ==========================================================================
st.header("3️⃣ Ask a Question About Your Data")

llm_ready = bool(os.getenv("GROQ_API_KEY")) and bool(os.getenv("GROQ_MODEL"))
if not llm_ready:
    st.error("GROQ_API_KEY and/or GROQ_MODEL is missing. Add them to your .env file and restart the app.")

user_query = st.text_area(
    "Enter your natural language query",
    placeholder="e.g. Show the top 5 cities by average rating",
    height=100,
)

if st.button("Generate SQL", type="primary", disabled=not llm_ready):
    if st.session_state.schema is None:
        st.warning("Please upload a CSV file first so a table is available.")
    elif not user_query.strip():
        st.warning("Please enter a question first.")
    else:
        reset_query_state()  # a new question invalidates the old SQL and results
        st.session_state.pending_question = user_query.strip()
        run_pipeline()

pipeline_result = st.session_state.pipeline_result

if pipeline_result is not None:
    status = pipeline_result["status"]

    if status == "clarification_needed":
        st.info(f"🤔 I need a little more detail: {pipeline_result['clarification_question']}")

        with st.form("clarification_form", clear_on_submit=True):
            answer = st.text_input("Your answer")
            submitted = st.form_submit_button("Submit answer")

        if submitted:
            if answer.strip():
                st.session_state.clarification_history.append(answer.strip())
                run_pipeline()
                st.rerun()
            else:
                st.warning("Please type an answer.")

    elif status == "error":
        st.error(pipeline_result.get("error") or "Something went wrong while generating SQL.")

        if pipeline_result.get("generated_sql"):
            st.write("**SQL that failed validation:**")
            st.code(pipeline_result["generated_sql"], language="sql")

        details = (pipeline_result.get("validation") or {}).get("message")
        semantic = (pipeline_result.get("semantic_validation") or {}).get("reason")
        if details or semantic:
            with st.expander("Validation details"):
                if details:
                    st.write(f"**Syntax/schema check:** {details}")
                if semantic:
                    st.write(f"**Semantic check:** {semantic}")

    else:  # success
        st.caption(f"Interpreted question: {pipeline_result['interpreted_question']}")

        st.write("**Primary SQL** — this is the query that runs after you approve it:")
        st.code(pipeline_result["primary_sql"], language="sql")

        if pipeline_result.get("alternative_sql"):
            st.write("**Alternative SQL** — for reference only, it is not executed:")
            st.code(pipeline_result["alternative_sql"], language="sql")
        elif pipeline_result.get("alternative_error"):
            st.caption(f"An alternative query was generated but failed validation: {pipeline_result['alternative_error']}")
        else:
            st.caption("No alternative query was suggested for this question.")

        with st.expander("Validation details"):
            st.write(f"**Syntax/schema check:** {pipeline_result['validation']['message']}")
            semantic = pipeline_result.get("semantic_validation")
            if semantic:
                st.write(f"**Semantic check:** {semantic['reason']}")
            st.write(f"**Correction attempts:** {pipeline_result.get('correction_attempts', 0)}")

st.divider()


# ==========================================================================
# 4. Approve & Run  (only the primary SQL is executed)
# ==========================================================================
st.header("4️⃣ Approve & Run Query")

sql_ready = pipeline_result is not None and pipeline_result["status"] == "success"

if st.button("✅ Approve & Run Primary SQL", disabled=not sql_ready):
    try:
        with st.spinner("Running the query..."):
            result_df, executed_sql = run_read_query(get_db(), pipeline_result["primary_sql"])

        st.session_state.query_result = result_df
        st.session_state.executed_sql = executed_sql
        st.session_state.run_id += 1  # new run -> fresh chart widgets and insights
    except Exception as e:
        st.session_state.query_result = None
        st.error(f"The query could not be run: {e}")

if st.session_state.query_result is not None:
    st.success(f"Query returned {len(st.session_state.query_result)} row(s).")

    if normalize_sql(st.session_state.executed_sql) != normalize_sql(pipeline_result["primary_sql"]):
        st.caption("Executed on the in-memory SQLite database as:")
        st.code(st.session_state.executed_sql, language="sql")

    st.dataframe(st.session_state.query_result)
elif sql_ready:
    st.info("Review the primary SQL above, then click **Approve & Run Primary SQL**.")
else:
    st.info("Generate a SQL query first.")

st.divider()


# ==========================================================================
# 5. Visualize  (member_3)
# ==========================================================================
st.header("5️⃣ Visualize Your Data")

query_result = st.session_state.query_result
key_prefix = f"run{st.session_state.run_id}"

if query_result is None:
    st.info("Run a query to unlock chart visualization and AI insights.")
elif query_result.empty:
    st.warning("The query returned no rows, so there is nothing to visualize.")
else:
    render_chart_section(query_result, key_prefix)

st.divider()


# ==========================================================================
# 6. AI Insights  (member_3)
# ==========================================================================
st.header("6️⃣ AI Insights")

if query_result is None or query_result.empty:
    st.info("Insights appear here after a query returns data.")
else:
    insights_key = f"{key_prefix}_ai_insights"

    if st.button("✨ Generate AI Insights", key=f"{key_prefix}_insights_button"):
        try:
            with st.spinner("AI is analyzing the query result..."):
                st.session_state[insights_key] = generate_ai_insights(
                    query_result,
                    pipeline_result.get("interpreted_question") or st.session_state.pending_question,
                )
        except Exception as e:
            st.error(f"Unable to generate AI insights: {e}")

    if st.session_state.get(insights_key):
        st.markdown(st.session_state[insights_key])
