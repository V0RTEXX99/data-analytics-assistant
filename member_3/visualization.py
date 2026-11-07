
import pandas as pd
import plotly.express as px


def analyze_result(result_df):
    """
    Analyze a DataFrame dynamically without assuming fixed column names.
    """

    if not isinstance(result_df, pd.DataFrame):
        raise TypeError("Input must be a Pandas DataFrame.")

    analysis = {
        "rows": len(result_df),
        "columns": list(result_df.columns),
        "numeric_columns": [],
        "categorical_columns": [],
        "datetime_columns": []
    }

    for column in result_df.columns:

        if pd.api.types.is_numeric_dtype(result_df[column]):
            analysis["numeric_columns"].append(column)

        elif pd.api.types.is_datetime64_any_dtype(result_df[column]):
            analysis["datetime_columns"].append(column)

        else:
            # Try recognizing dates stored as text
            if (
                pd.api.types.is_object_dtype(result_df[column])
                or pd.api.types.is_string_dtype(result_df[column])
            ):
                converted_dates = pd.to_datetime(
                    result_df[column],
                    errors="coerce"
                )

                if (
                    converted_dates.notna().mean() >= 0.8
                    and converted_dates.notna().any()
                ):
                    analysis["datetime_columns"].append(column)
                else:
                    analysis["categorical_columns"].append(column)
            else:
                analysis["categorical_columns"].append(column)

    return analysis


def get_chart_recommendations(analysis):
    """
    Recommend charts according to the available column types.
    """

    recommendations = []

    numeric_columns = analysis["numeric_columns"]
    categorical_columns = analysis["categorical_columns"]
    datetime_columns = analysis["datetime_columns"]

    if categorical_columns and numeric_columns:
        recommendations.append("Bar Chart")
        recommendations.append("Pie Chart")

    if (datetime_columns or categorical_columns) and numeric_columns:
        recommendations.append("Line Chart")

    if len(numeric_columns) >= 2:
        recommendations.append("Scatter Plot")

    if numeric_columns:
        recommendations.append("Histogram")

    return recommendations


def create_chart(result_df, chart_type, x_column, y_column=None):
    """
    Create charts dynamically with input validation.
    """

    if not isinstance(result_df, pd.DataFrame):
        raise TypeError("Input must be a Pandas DataFrame.")

    if result_df.empty:
        raise ValueError("Cannot create a chart from an empty dataset.")

    if not x_column or x_column not in result_df.columns:
        raise ValueError("Please select a valid X-axis column.")

    if chart_type in [
        "Bar Chart",
        "Line Chart",
        "Scatter Plot",
        "Pie Chart"
    ]:

        if not y_column or y_column not in result_df.columns:
            raise ValueError("Please select a valid Y-axis column.")

        if not pd.api.types.is_numeric_dtype(result_df[y_column]):
            raise ValueError("The Y-axis column must contain numeric data.")

    if chart_type == "Bar Chart":

        chart_df = (
            result_df
            .groupby(x_column, dropna=False, observed=True)[y_column]
            .sum()
            .reset_index()
        )

        return px.bar(
            chart_df,
            x=x_column,
            y=y_column,
            title=f"Total {y_column} by {x_column}",
            text_auto=True
        )

    elif chart_type == "Line Chart":

        chart_df = result_df.copy()

        if x_column in chart_df.columns:
            # Convert to dates when possible; keep the original values
            # otherwise. (errors="ignore" was removed in pandas 3.)
            try:
                chart_df[x_column] = pd.to_datetime(chart_df[x_column])
            except (ValueError, TypeError):
                pass

        return px.line(
            chart_df,
            x=x_column,
            y=y_column,
            markers=True,
            title=f"{y_column} over {x_column}"
        )

    elif chart_type == "Scatter Plot":

        if not pd.api.types.is_numeric_dtype(result_df[x_column]):
            raise ValueError("The scatter plot X-axis must be numeric.")

        return px.scatter(
            result_df,
            x=x_column,
            y=y_column,
            title=f"{y_column} vs {x_column}"
        )

    elif chart_type == "Histogram":

        if not pd.api.types.is_numeric_dtype(result_df[x_column]):
            raise ValueError("Histogram requires a numeric column.")

        return px.histogram(
            result_df,
            x=x_column,
            title=f"Distribution of {x_column}"
        )

    elif chart_type == "Pie Chart":

        chart_df = (
            result_df
            .groupby(x_column, dropna=False, observed=True)[y_column]
            .sum()
            .reset_index()
        )

        return px.pie(
            chart_df,
            names=x_column,
            values=y_column,
            title=f"Total {y_column} by {x_column}"
        )

    else:
        raise ValueError(f"Unsupported chart type: {chart_type}")
