import streamlit as st

from database import execute_sql
from dashboard import show_dashboard
from sql_generator import generate_sql
from ai_insights import generate_ai_insights


# ---------------- PAGE CONFIGURATION ----------------

st.set_page_config(
    page_title="AI-Powered Data Analytics Assistant",
    page_icon="📊",
    layout="wide"
)

st.title("📊 AI-Powered Data Analytics Assistant")
st.write("Ask questions about your data and get instant analytics using AI.")


# ---------------- SESSION STATE ----------------

if "pending_sql" not in st.session_state:
    st.session_state.pending_sql = None

if "query_result" not in st.session_state:
    st.session_state.query_result = None

if "question" not in st.session_state:
    st.session_state.question = ""


# ---------------- LOAD DATABASE DATA ----------------

try:
    df = execute_sql("SELECT * FROM test_data")

    if df.empty:
        st.warning("No data found in PostgreSQL.")
        st.stop()

    st.success("Connected to PostgreSQL successfully!")

except Exception as e:
    st.error(f"Database error: {e}")
    st.stop()


# ---------------- ORIGINAL DATA ----------------

st.header("📁 Your Dataset")

st.dataframe(df, use_container_width=True)

st.subheader("📊 Dataset Visualizations")

show_dashboard(df, key_prefix="original")

# ---------------- NATURAL LANGUAGE TO SQL ----------------

st.divider()

st.header("🤖 Ask Questions About Your Data")

st.write(
    "Type a question in normal English. "
    "AI will convert it into an SQL query."
)

question = st.text_input(
    "Enter your question:",
    placeholder="Which city has the highest total revenue?",
    key="question"
)

if st.button("Generate SQL", type="primary"):

    if not question.strip():
        st.warning("Please enter a question.")

    else:
        try:
            with st.spinner("AI is generating your SQL query..."):

                sql = generate_sql(
                    question,
                    df,
                    table_name="test_data"
                )

                st.session_state.pending_sql = sql
                st.session_state.query_result = None

        except Exception as e:
            st.error(f"SQL generation failed: {e}")


# ---------------- SQL APPROVAL ----------------

if st.session_state.pending_sql:

    st.subheader("Generated SQL Query")

    st.code(
        st.session_state.pending_sql,
        language="sql"
    )

    st.info("Review the SQL query before approving execution.")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("✅ Approve and Execute", type="primary"):

            try:
                with st.spinner("Executing SQL query..."):

                    result = execute_sql(
                        st.session_state.pending_sql
                    )

                    st.session_state.query_result = result
                    st.session_state.pending_sql = None

            except Exception as e:
                st.error(f"Query execution failed: {e}")

    with col2:
        if st.button("❌ Reject Query"):

            st.session_state.pending_sql = None
            st.session_state.query_result = None

            st.warning("SQL query rejected.")


# ---------------- QUERY RESULTS ----------------

if st.session_state.query_result is not None:

    result_df = st.session_state.query_result

    st.divider()
    st.header("📈 Query Results")

    if result_df.empty:
        st.warning("The query returned no results.")

    else:
        st.success("SQL query executed successfully!")

        st.dataframe(
            result_df,
            use_container_width=True
        )

        st.subheader("Result Visualizations")

        show_dashboard(result_df, key_prefix="query")
        
        # ---------------- AI INSIGHTS ----------------

        st.divider()
        st.header("✨ AI Insights on Query Results")

        if st.button("Generate Insights"):

            try:
                with st.spinner("AI is analyzing the results..."):

                    insights = generate_ai_insights(
                        result_df,
                        question=st.session_state.question
                    )

                    st.markdown(insights)

            except Exception as e:
                st.error(f"AI insights failed: {e}")
