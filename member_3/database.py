
import os
import re
import pandas as pd

from dotenv import load_dotenv
from sqlalchemy import create_engine, URL, text


# Load database credentials from .env
load_dotenv()


def get_engine():
    """Create and return a PostgreSQL database connection."""

    required_vars = [
        "DB_HOST",
        "DB_PORT",
        "DB_NAME",
        "DB_USER",
        "DB_PASSWORD"
    ]

    missing = [var for var in required_vars if not os.getenv(var)]

    if missing:
        raise ValueError(
            f"Missing database settings in .env: {', '.join(missing)}"
        )

    database_url = URL.create(
        drivername="postgresql+psycopg2",
        username=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        database=os.getenv("DB_NAME")
    )

    return create_engine(database_url, pool_pre_ping=True)


def validate_table_name(table_name):
    """Allow only simple, valid table names."""

    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", table_name):
        raise ValueError("Invalid table name.")

    return table_name


def load_dataframe_into_database(df, table_name="data"):
    """Upload a Pandas DataFrame into PostgreSQL."""

    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a Pandas DataFrame.")

    if df.empty:
        raise ValueError("The uploaded dataset is empty.")

    table_name = validate_table_name(table_name)
    engine = get_engine()

    try:
        df.to_sql(
            name=table_name,
            con=engine,
            schema="public",
            if_exists="replace",
            index=False
        )

        return True

    finally:
        engine.dispose()


def load_csv_into_database(csv_path, table_name="data"):
    """Read a CSV file and upload it into PostgreSQL."""

    df = pd.read_csv(csv_path)

    load_dataframe_into_database(df, table_name)

    return True


def execute_sql(sql_query):
    """Execute a read-only SQL query and return a DataFrame."""

    if not isinstance(sql_query, str) or not sql_query.strip():
        raise ValueError("SQL query cannot be empty.")

    query = sql_query.strip()

    if not re.match(r"^(SELECT|WITH)\b", query, re.IGNORECASE):
        raise ValueError("Only SELECT and WITH queries are allowed.")

    # Reject multiple SQL statements.
    if ";" in query.rstrip(";"):
        raise ValueError("Only one SQL statement is allowed.")

    engine = get_engine()

    try:
        with engine.connect() as connection:
            with connection.begin():
                connection.exec_driver_sql(
                    "SET TRANSACTION READ ONLY"
                )

                result_df = pd.read_sql_query(
                    text(query),
                    connection
                )

                return result_df

    finally:
        engine.dispose()
