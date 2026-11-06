import sqlite3
import pandas as pd

class InMemorySQL:
    def __init__(self):
        """Initialize an in-memory SQLite database."""
        self.conn = sqlite3.connect(":memory:")
        self.cursor = self.conn.cursor()

    def load_csv(self, csv_path, table_name):
        """
        Load a CSV file into an in-memory SQL table.
        """
        df = pd.read_csv(csv_path)

        df.to_sql(
            name=table_name,
            con=self.conn,
            if_exists="replace",
            index=False
        )

        print(f"Table '{table_name}' created successfully.")

    def run_query(self, query):
        """
        Execute an SQL query and return results.
        """
        try:
            result = pd.read_sql_query(query, self.conn)
            return result

        except Exception as e:
            print(f"SQL Error: {e}")
            return None

    def execute(self, query):
        """
        Execute SQL statements that don't return tabular results.
        Example: UPDATE, INSERT, DELETE.
        """
        try:
            self.cursor.execute(query)
            self.conn.commit()
            return self.cursor.rowcount

        except Exception as e:
            print(f"SQL Error: {e}")
            return None

    def delete_table(self, table_name):
        """
        Delete a specific table.
        """
        self.cursor.execute(
            f'DROP TABLE IF EXISTS "{table_name}"'
        )
        self.conn.commit()

        print(f"Table '{table_name}' deleted.")

    def close(self):
        """
        Close the connection and destroy the in-memory database.
        """
        self.conn.close()
        print("In-memory database destroyed.")
