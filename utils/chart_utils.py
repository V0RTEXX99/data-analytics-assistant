"""
chart_utils.py
--------------
Helper functions for building Plotly Express charts from a DataFrame,
based on a user-selected chart type and X/Y columns.
"""

import plotly.express as px
import pandas as pd


CHART_TYPES = ["Bar Chart", "Line Chart", "Scatter Plot", "Pie Chart", "Histogram"]


def build_chart(df: pd.DataFrame, chart_type: str, x_col: str, y_col: str = None):
    """
    Build a Plotly Express figure based on the selected chart type.

    Parameters
    ----------
    df : pd.DataFrame
        The data to visualize.
    chart_type : str
        One of CHART_TYPES.
    x_col : str
        Column name to use for the X-axis (or the "names"/"values"
        column for pie charts / the single column for histograms).
    y_col : str, optional
        Column name to use for the Y-axis. Not required for
        Pie Chart or Histogram.

    Returns
    -------
    plotly.graph_objects.Figure
    """
    if chart_type == "Bar Chart":
        fig = px.bar(df, x=x_col, y=y_col, title=f"Bar Chart: {y_col} by {x_col}")

    elif chart_type == "Line Chart":
        fig = px.line(df, x=x_col, y=y_col, title=f"Line Chart: {y_col} over {x_col}")

    elif chart_type == "Scatter Plot":
        fig = px.scatter(df, x=x_col, y=y_col, title=f"Scatter Plot: {y_col} vs {x_col}")

    elif chart_type == "Pie Chart":
        # For pie charts, x_col is treated as the category ("names")
        # and y_col (if given) as the values; otherwise Plotly counts rows.
        if y_col:
            fig = px.pie(df, names=x_col, values=y_col, title=f"Pie Chart: {y_col} by {x_col}")
        else:
            fig = px.pie(df, names=x_col, title=f"Pie Chart: distribution of {x_col}")

    elif chart_type == "Histogram":
        fig = px.histogram(df, x=x_col, title=f"Histogram of {x_col}")

    else:
        raise ValueError(f"Unsupported chart type: {chart_type}")

    fig.update_layout(margin=dict(l=20, r=20, t=50, b=20))
    return fig
