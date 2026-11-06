import os
import pandas as pd
import psycopg2


def execute_approved_sql(sql_query):
    """
    Execute approved SQL on PostgreSQL
    and return the result as a Pandas DataFrame.
    """

    connection = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

    try:
        result_df = pd.read_sql_query(sql_query, connection)
        return result_df

    finally:
        connection.close()
 #we r build a function that member 2 ka puri dictionary we can recive       
def execute_member2_output(member2_output):
    """
    Receive Member 2's validated SQL output,
    execute the SQL, and return a DataFrame.
    """

    if member2_output["status"] != "success":
        raise ValueError("SQL generation was not successful.")

    if member2_output["query_type"] != "READ":
        raise ValueError("Only READ queries are allowed for visualization.")

    validation = member2_output["validation"]

    if not validation["syntax_valid"]:
        raise ValueError("SQL syntax validation failed.")

    if not validation["schema_valid"]:
        raise ValueError("SQL schema validation failed.")

    sql_query = member2_output["sql"]

    return execute_approved_sql(sql_query)