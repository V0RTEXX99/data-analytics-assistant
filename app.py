"""
app.py
------
AI-Powered Data Analytics Assistant - Streamlit Frontend.

A fully self-contained (mock backend) Streamlit app that walks a user
through: upload CSV -> view schema -> ask a natural language question ->
(mock) generate SQL -> (mock) run SQL -> approve results -> visualize ->
view simple insights.

Run with:
    streamlit run app.py
"""

import streamlit as st
import pandas as pd

from utils.sql_utils import generate_sql, execute_query
from utils.chart_utils import build_chart, CHART_TYPES
from utils.insights_utils import generate_insights


# --------------------------------------------------------------------------
# Page configuration
# --------------------------------------------------------------------------
st.set_page_config(
    page_title="AI-Powered Data Analytics Assistant",
    page_icon="📊",
    layout="wide",
)


# --------------------------------------------------------------------------
# Session state initialization
# --------------------------------------------------------------------------
def init_session_state():
    """Initialize all session state keys used across the app, once."""
    defaults = {
        "df": None,                 # Uploaded raw DataFrame
        "schema_info": None,        # Schema DataFrame (Column Name / Data Type)
        "generated_sql": None,      # SQL text generated from user query
        "query_result": None,       # DataFrame returned by execute_query
        "results_approved": False,  # Whether user approved the results
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_session_state()


# --------------------------------------------------------------------------
# Helper functions
# --------------------------------------------------------------------------
def build_schema_info(df: pd.DataFrame) -> pd.DataFrame:
    """Build a schema table (Column Name / Data Type) from a DataFrame."""
    return pd.DataFrame(
        {
            "Column Name": df.columns,
            "Data Type": [str(dtype) for dtype in df.dtypes],
        }
    )


def reset_downstream_state():
    """
    Reset everything that depends on a fresh SQL query so stale results
    don't linger when the user submits a new natural language query.
    """
    st.session_state.query_result = None
    st.session_state.results_approved = False


# --------------------------------------------------------------------------
# Page title
# --------------------------------------------------------------------------
st.title("📊 AI-Powered Data Analytics Assistant")
st.caption(
    "Upload a CSV, ask questions in plain English, review the generated SQL, "
    "and explore your data with interactive charts and insights."
)
st.divider()


# ==========================================================================
# 1. CSV Upload Section
# ==========================================================================
st.header("1️⃣ Upload Your Data")

uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file is not None:
    # Display the uploaded file name
    st.success(f"Uploaded file: **{uploaded_file.name}**")

    try:
        df = pd.read_csv(uploaded_file)
        st.session_state.df = df
        st.session_state.schema_info = build_schema_info(df)
    except Exception as e:
        st.error(f"Could not read this CSV file: {e}")
        st.session_state.df = None

if st.session_state.df is not None:
    df = st.session_state.df

    st.subheader("Preview (first 10 rows)")
    st.dataframe(df.head(10), use_container_width=True)

    st.subheader("Dataset Overview")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Number of Rows", df.shape[0])
    with col2:
        st.metric("Number of Columns", df.shape[1])

    col3, col4 = st.columns(2)
    with col3:
        st.write("**Column Names:**")
        st.write(list(df.columns))
    with col4:
        st.write("**Data Types:**")
        st.write(df.dtypes.astype(str))

else:
    st.info("Upload a CSV file to get started.")

st.divider()


# ==========================================================================
# 2. Schema Display Section
# ==========================================================================
st.header("2️⃣ Detected Schema")

if st.session_state.schema_info is not None:
    schema_info = st.session_state.schema_info  # noqa: F841  (kept as required variable name)
    st.table(schema_info)
else:
    st.info("Schema will appear here once a CSV file is uploaded.")

st.divider()


# ==========================================================================
# 3. Natural Language Query Section
# ==========================================================================
st.header("3️⃣ Ask a Question About Your Data")

user_query = st.text_area(
    "Enter your natural language query",
    placeholder="e.g. Show me the top 10 records sorted by value",
    height=100,
)

generate_sql_clicked = st.button("Generate SQL", type="primary")

if generate_sql_clicked:
    if st.session_state.schema_info is None:
        st.warning("Please upload a CSV file first so a schema is available.")
    elif not user_query.strip():
        st.warning("Please enter a natural language query first.")
    else:
        # Call the (mock) SQL generation function
        sql_query = generate_sql(user_query, st.session_state.schema_info)
        st.session_state.generated_sql = sql_query
        reset_downstream_state()  # a new SQL query invalidates old results

if st.session_state.generated_sql:
    st.write("**Generated SQL:**")
    st.code(st.session_state.generated_sql, language="sql")

st.divider()


# ==========================================================================
# 4. Query Result Section
# ==========================================================================
st.header("4️⃣ Query Results")

run_query_clicked = st.button("Run Query", disabled=(st.session_state.generated_sql is None))

if run_query_clicked:
    # Call the (mock) SQL execution function
    result_df = execute_query(st.session_state.generated_sql, st.session_state.df)
    st.session_state.query_result = result_df
    st.session_state.results_approved = False  # require re-approval on new results

if st.session_state.query_result is not None:
    st.dataframe(st.session_state.query_result, use_container_width=True)
else:
    st.info("Click **Run Query** after generating SQL to see results here.")

st.divider()


# ==========================================================================
# 5. Approval Section
# ==========================================================================
st.header("5️⃣ Approve Results")

approve_disabled = st.session_state.query_result is None
if st.button("✅ Approve Results", disabled=approve_disabled):
    st.session_state.results_approved = True

if st.session_state.results_approved:
    st.success("Results approved! Scroll down to visualize your data.")
elif st.session_state.query_result is not None:
    st.info("Review the results above, then click **Approve Results** to continue.")
else:
    st.info("Run a query first to enable approval.")

st.divider()


# ==========================================================================
# 6. Visualization Section (only visible after approval)
# ==========================================================================
if st.session_state.results_approved and st.session_state.query_result is not None:
    st.header("6️⃣ Visualize Your Data")

    result_df = st.session_state.query_result
    all_columns = list(result_df.columns)
    numeric_columns = list(result_df.select_dtypes(include="number").columns)

    viz_col1, viz_col2, viz_col3 = st.columns(3)

    with viz_col1:
        chart_type = st.selectbox("Chart Type", CHART_TYPES)

    with viz_col2:
        x_col = st.selectbox("X-axis Column", all_columns, key="x_axis_select")

    with viz_col3:
        # Y-axis is not required for Histogram
        y_options = ["(none)"] + all_columns if chart_type == "Histogram" else all_columns
        y_col_raw = st.selectbox("Y-axis Column", y_options, key="y_axis_select")
        y_col = None if y_col_raw == "(none)" else y_col_raw

    try:
        fig = build_chart(result_df, chart_type, x_col, y_col)
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Could not build chart: {e}")

    st.divider()

    # ======================================================================
    # 7. Insights Section
    # ======================================================================
    st.header("7️⃣ Insights")

    if numeric_columns:
        insight_col = st.selectbox(
            "Choose a numeric column for insights", numeric_columns, key="insight_col_select"
        )
        insights = generate_insights(result_df, insight_col)

        if insights:
            m1, m2, m3, m4, m5 = st.columns(5)
            m1.metric("Records", insights["Number of Records"])
            m2.metric("Highest", insights["Highest Value"])
            m3.metric("Lowest", insights["Lowest Value"])
            m4.metric("Mean", insights["Mean"])
            m5.metric("Median", insights["Median"])
        else:
            st.info("No insights available for the selected column.")
    else:
        st.info("No numeric columns available in the result set for insights.")

else:
    st.header("6️⃣ Visualize Your Data")
    st.info("Approve the query results above to unlock chart visualization and insights.")
