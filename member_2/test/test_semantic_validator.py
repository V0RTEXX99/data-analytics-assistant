from ai.semantic_validator import validate_sql_semantics

schema = {
    "table_name": "zomato",
    "columns": {"city": "VARCHAR", "ratings": "FLOAT", "time_taken": "INTEGER"},
}

test_cases = [
    {
        "question": "Find the average delivery time.",
        "sql": "SELECT AVG(time_taken) FROM zomato;",
    },
    {
        "question": "Find the average delivery time.",
        "sql": "SELECT MAX(time_taken) FROM zomato;",
    },
    {
        "question": "Find the average delivery time for each city.",
        "sql": """
            SELECT city, AVG(time_taken)
            FROM zomato
            GROUP BY city;
        """,
    },
    {
        "question": "Show the top 5 cities with the highest average delivery time.",
        "sql": """
            SELECT city, AVG(time_taken) AS avg_time
            FROM zomato
            GROUP BY city
            ORDER BY avg_time DESC
            LIMIT 5;
        """,
    },
]

for index, test in enumerate(test_cases, start=1):

    print("\n" + "=" * 60)
    print(f"TEST CASE {index}")

    print("\nQUESTION:")
    print(test["question"])

    print("\nSQL:")
    print(test["sql"])

    result = validate_sql_semantics(
        schema=schema, user_question=test["question"], sql_query=test["sql"]
    )

    print("\nSEMANTIC VALIDATION:")
    print("Status:", "VALID" if result["valid"] else "INVALID")
    print("Reason:", result["reason"])
    print("Suggestion:", result["suggestion"])

    print("=" * 60)
