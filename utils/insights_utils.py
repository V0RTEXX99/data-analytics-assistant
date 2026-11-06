"""
insights_utils.py
------------------
Simple statistical insight generation for a chosen numeric column.
"""

import pandas as pd


def generate_insights(df: pd.DataFrame, numeric_col: str) -> dict:
    """
    Compute simple summary statistics for a numeric column.

    Parameters
    ----------
    df : pd.DataFrame
        The dataset (typically the query result).
    numeric_col : str
        The numeric column to summarize.

    Returns
    -------
    dict
        Dictionary of insight name -> value. Returns an empty dict if
        the column is missing or not numeric.
    """
    if numeric_col not in df.columns:
        return {}

    series = pd.to_numeric(df[numeric_col], errors="coerce").dropna()

    if series.empty:
        return {}

    insights = {
        "Number of Records": len(df),
        "Highest Value": series.max(),
        "Lowest Value": series.min(),
        "Mean": round(series.mean(), 2),
        "Median": series.median(),
    }
    return insights
