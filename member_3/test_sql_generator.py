
from database import execute_sql
from sql_generator import generate_sql

# Load our existing sample data
df = execute_sql("SELECT * FROM test_data")

questions = [
    "Which city has the highest total revenue?",
    "Which city has the lowest total revenue?",
    "Which city has the highest average revenue?",
    "Show the number of transactions for each city."
]

for question in questions:
    print("\n" + "=" * 60)
    print("QUESTION:", question)

    try:
        sql = generate_sql(question, df, table_name="test_data")
        print("\nVALIDATED SQL:")
        print(sql)

    except Exception as error:
        print("\nVALIDATION FAILED:")
        print(error)
