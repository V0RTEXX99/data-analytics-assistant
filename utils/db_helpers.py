"""
db_helpers.py
-------------
Small helpers that sit between app.py, the in-memory SQLite database
(database_utils.in_memory_sql_db.InMemorySQL) and the member_2 pipeline.
"""

import re
from pathlib import Path

import pandas as pd
import sqlglot

from member_2.main.sql_validator import classify_sql

# Words that would break an unquoted table/column name in SQL.
RESERVED_WORDS = {
    "all", "and", "any", "as", "asc", "between", "by", "case", "check",
    "create", "default", "delete", "desc", "distinct", "drop", "else",
    "end", "exists", "false", "from", "group", "having", "in", "index",
    "insert", "into", "is", "join", "key", "like", "limit", "not", "null",
    "offset", "on", "or", "order", "primary", "select", "set", "table",
    "then", "to", "true", "union", "unique", "update", "user", "using",
    "values", "when", "where", "with",
}


def _safe_identifier(raw, fallback, reserved_suffix):
    """Turn any text into a lowercase snake_case SQL identifier."""

    name = re.sub(r"[^0-9a-zA-Z]+", "_", str(raw)).strip("_").lower()

    if not name:
        name = fallback

    if name[0].isdigit():
        name = f"{reserved_suffix}_{name}"

    if name in RESERVED_WORDS:
        name = f"{name}_{reserved_suffix}"

    return name


def make_table_name(filename):
    """'Sales Data 2024.csv' -> 'sales_data_2024'."""

    return _safe_identifier(Path(filename).stem, "uploaded_data", "t")


def clean_column_names(columns):
    """
    Make CSV headers safe for SQL: 'Order Date' -> 'order_date'.
    Duplicate names get a numeric suffix.
    """

    cleaned = []
    used = set()

    for position, column in enumerate(columns, start=1):
        name = _safe_identifier(column, f"column_{position}", "col")

        candidate = name
        counter = 1

        while candidate in used:
            candidate = f"{name}_{counter}"
            counter += 1

        used.add(candidate)
        cleaned.append(candidate)

    return cleaned


def build_column_profile(df, schema):
    """
    Per-column summary table for the 'Detected Schema' section.

    schema is the dict returned by InMemorySQL.describe_table():
        {"table_name": "...", "columns": {"col": "SQL_TYPE", ...}}
    """

    return pd.DataFrame(
        {
            "Column": list(df.columns),
            "SQL Type": [schema["columns"].get(col, "") for col in df.columns],
            "Pandas Dtype": [str(dtype) for dtype in df.dtypes],
            "Non-Null": df.notna().sum().to_list(),
            "Missing": df.isna().sum().to_list(),
            "Unique": df.nunique().to_list(),
        }
    )


def to_sqlite(sql_query):
    """
    member_2 generates and validates PostgreSQL SQL, but the in-memory
    database is SQLite. Convert the dialect before running; if the
    conversion fails, fall back to the original text.
    """

    try:
        return sqlglot.transpile(sql_query, read="postgres", write="sqlite")[0]
    except Exception:
        return sql_query


def run_read_query(db, sql_query):
    """
    Run ONE read-only query on the InMemorySQL database.

    Returns (result_dataframe, sql_that_was_executed).
    Raises ValueError / RuntimeError with a readable message on failure.
    """

    if classify_sql(sql_query) != "READ":
        raise ValueError("Only a single read-only SELECT query can be run.")

    sqlite_sql = to_sqlite(sql_query)

    result = db.run_query(sqlite_sql)

    if result is None:
        raise RuntimeError(db.last_error or "The query could not be executed.")

    return result, sqlite_sql
