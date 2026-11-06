

import streamlit as st

from visualization import (
    analyze_result,
    get_chart_recommendations,
    create_chart
)

from ai_insights import generate_ai_insights


def show_dashboard(result_df, key_prefix="dashboard"):
    """
    Display an interactive dashboard with visualizations
    and AI-powered business insights.
    """

    if result_df.empty:
        st.warning("No data available for analysis.")
        return

    # Display query results
    st.subheader("Query Result")
    st.dataframe(result_df, use_container_width=True)

    # Analyze dataset
    analysis = analyze_result(result_df)

    st.subheader("Data Summary")

    col1, col2, col3 = st.columns(3)

    col1.metric("Rows", analysis["rows"])
    col2.metric("Columns", len(analysis["columns"]))
    col3.metric("Numeric Columns", len(analysis["numeric_columns"]))

    # AI INSIGHTS
    st.subheader("AI-Powered Business Insights")

    question = st.text_input(
        "Ask a question about your data (optional)",
        placeholder="Example: Which city generated the highest revenue?",
        key=f"{key_prefix}_ai_question"
    )

    if st.button(
        "Generate AI Insights",
        key=f"{key_prefix}_generate_insights"
    ):

        try:
            with st.spinner("AI is analyzing your dataset..."):

                insights = generate_ai_insights(
                    result_df,
                    question if question.strip() else None
                )

                st.session_state[
                    f"{key_prefix}_ai_result"
                ] = insights

        except Exception as e:
            st.error(f"Unable to generate AI insights: {e}")

    # Display generated insights
    saved_insights = st.session_state.get(
        f"{key_prefix}_ai_result"
    )

    if saved_insights:
        st.markdown("---")
        st.markdown(saved_insights)

    # DATA VISUALIZATION
    st.subheader("Visualization")

    recommendations = get_chart_recommendations(analysis)

    if not recommendations:
        st.warning("No suitable visualization found for this dataset.")
        return

    chart_type = st.selectbox(
        "Choose a chart",
        recommendations,
        key=f"{key_prefix}_chart_type"
    )

    numeric_columns = analysis["numeric_columns"]
    categorical_columns = analysis["categorical_columns"]
    datetime_columns = analysis["datetime_columns"]

    x_column = None
    y_column = None

    if chart_type in ["Bar Chart", "Pie Chart"]:

        if not categorical_columns or not numeric_columns:
            st.warning("This chart requires a category and numeric column.")
            return

        x_column = st.selectbox(
            "Select category column",
            categorical_columns,
            key=f"{key_prefix}_category"
        )

        y_column = st.selectbox(
            "Select numeric column",
            numeric_columns,
            key=f"{key_prefix}_numeric"
        )

    elif chart_type == "Line Chart":

        x_options = datetime_columns + categorical_columns

        if not x_options or not numeric_columns:
            st.warning("This chart requires an X-axis and numeric column.")
            return

        x_column = st.selectbox(
            "Select X-axis column",
            x_options,
            key=f"{key_prefix}_line_x"
        )

        y_column = st.selectbox(
            "Select numeric column",
            numeric_columns,
            key=f"{key_prefix}_line_y"
        )

    elif chart_type == "Scatter Plot":

        if len(numeric_columns) < 2:
            st.warning("Scatter plot requires two numeric columns.")
            return

        x_column = st.selectbox(
            "Select X-axis numeric column",
            numeric_columns,
            key=f"{key_prefix}_scatter_x"
        )

        y_options = [
            column for column in numeric_columns
            if column != x_column
        ]

        y_column = st.selectbox(
            "Select Y-axis numeric column",
            y_options,
            key=f"{key_prefix}_scatter_y"
        )

    elif chart_type == "Histogram":

        if not numeric_columns:
            st.warning("Histogram requires a numeric column.")
            return

        x_column = st.selectbox(
            "Select numeric column",
            numeric_columns,
            key=f"{key_prefix}_histogram"
        )

    # Generate chart safely
    try:
        figure = create_chart(
            result_df,
            chart_type,
            x_column,
            y_column
        )

        st.plotly_chart(
            figure,
            use_container_width=True
        )

    except Exception as e:
        st.error(f"Unable to create visualization: {e}")
