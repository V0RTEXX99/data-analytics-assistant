import sqlite3
import pandas as pd


class InMemorySQL:
    def __init__(self):
        """Initialize an in-memory SQLite database."""
        # check_same_thread=False: Streamlit re-runs the script in a new
        # thread on every interaction, and SQLite otherwise refuses to be
        # used from a thread other than the one that created it.
        self.conn = sqlite3.connect(":memory:", check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.last_error = None

    def load_dataframe(self, df: pd.DataFrame, table_name: str):
        """
        Load a Pandas DataFrame into an in-memory SQL table.
        """
        if not isinstance(df, pd.DataFrame):
            raise TypeError("Input must be a pandas DataFrame.")

        df.to_sql(
            name=table_name,
            con=self.conn,
            if_exists="replace",
            index=False
        )

        print(f"Table '{table_name}' created successfully.")

    def run_query(self, query: str):
        """Execute an SQL query and return a DataFrame."""
        self.last_error = None

        try:
            return pd.read_sql_query(query, self.conn)

        except Exception as e:
            self.last_error = str(e)
            print(f"SQL Error: {e}")
            return None

    def execute(self, query: str):
        """Execute INSERT, UPDATE, DELETE, etc."""
        try:
            self.cursor.execute(query)
            self.conn.commit()
            return self.cursor.rowcount

        except Exception as e:
            print(f"SQL Error: {e}")
            return None

    def describe_table(self, table_name: str):
        """
        Return table name, column names and datatypes
        as a Python dictionary.
        """
        try:
            self.cursor.execute(
                "SELECT name FROM sqlite_master "
                "WHERE type='table' AND name=?",
                (table_name,)
            )

            if self.cursor.fetchone() is None:
                raise ValueError(f"Table '{table_name}' does not exist.")

            self.cursor.execute(
                f'PRAGMA table_info("{table_name}")'
            )

            columns = self.cursor.fetchall()

            return {
                "table_name": table_name,
                "columns": {
                    column[1]: column[2]
                    for column in columns
                }
            }

        except Exception as e:
            print(f"Error describing table: {e}")
            return None

    def get_create_statement(self, table_name: str):
        """Return the CREATE TABLE statement SQLite generated for a table."""
        self.cursor.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,)
        )

        row = self.cursor.fetchone()
        return row[0] if row else None

    def delete_table(self, table_name: str):
        """Delete a specific table."""
        safe_name = table_name.replace('"', '""')

        self.cursor.execute(
            f'DROP TABLE IF EXISTS "{safe_name}"'
        )

        self.conn.commit()
        print(f"Table '{table_name}' deleted.")

    def close(self):
        """Close connection and destroy the in-memory database."""
        self.conn.close()
        print("In-memory database destroyed.")
