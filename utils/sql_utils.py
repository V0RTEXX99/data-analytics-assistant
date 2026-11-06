"""
sql_utils.py
------------
Mock/placeholder functions that simulate an AI-powered SQL generation
and execution backend. In a real system, `generate_sql` would call an
LLM (e.g. via the Anthropic API) with the user's natural language query
and the table schema, and `execute_query` would run the SQL against a
real database or DataFrame engine (e.g. DuckDB / SQLite).

Both functions are kept intentionally simple so the Streamlit UI can be
demoed end-to-end without any backend or API keys.
"""

import pandas as pd
import numpy as np


def generate_sql(user_query: str, schema_info: pd.DataFrame) -> str:
    """
    Placeholder for an LLM-based natural-language-to-SQL generator.

    Parameters
    ----------
    user_query : str
        The natural language question typed by the user.
    schema_info : pd.DataFrame
        DataFrame with columns ["Column Name", "Data Type"] describing
        the uploaded dataset's schema.

    Returns
    -------
    str
        A SQL query string. Currently returns a dummy query regardless
        of input, but the function signature is what a real
        implementation (e.g. calling an LLM) would use.
    """
    # In a real implementation you would build a prompt using
    # `user_query` and `schema_info`, send it to an LLM, and parse the
    # SQL out of the response. For now we just return a fixed dummy query.
    dummy_sql = "SELECT * FROM data LIMIT 10;"
    return dummy_sql


def execute_query(sql_query: str, source_df: pd.DataFrame = None) -> pd.DataFrame:
    """
    Placeholder for a SQL execution engine.

    Parameters
    ----------
    sql_query : str
        The SQL query to "execute".
    source_df : pd.DataFrame, optional
        The original uploaded DataFrame. If provided, a small sample of
        it is returned so results feel connected to the real data.
        Otherwise a synthetic sample DataFrame is generated.

    Returns
    -------
    pd.DataFrame
        A sample result set.
    """
    # If we have real uploaded data, just return the first few rows of it
    # to simulate "running" the SQL query.
    if source_df is not None and not source_df.empty:
        n = min(10, len(source_df))
        return source_df.head(n).reset_index(drop=True)

    # Fallback: synthetic sample data, used only if no file was uploaded.
    rng = np.random.default_rng(seed=42)
    sample_df = pd.DataFrame(
        {
            "id": range(1, 11),
            "category": rng.choice(["A", "B", "C", "D"], size=10),
            "value": rng.integers(10, 500, size=10),
            "score": np.round(rng.uniform(0, 100, size=10), 2),
        }
    )
    return sample_df
