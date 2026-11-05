from ai.pipeline import process_user_question

schema = {
    "table_name": "zomato",
    "columns": {
        "city": "VARCHAR",
        "ratings": "FLOAT",
        "time_taken": "INTEGER",
        "weather": "VARCHAR",
        "traffic": "VARCHAR",
        "vehicle_type": "VARCHAR",
        "order_type": "VARCHAR",
        "festival": "VARCHAR",
    },
}

questions = [
    "Show the top 5.",
    "Calculate average delivery time by city.",
    "Show the average ratings for each city.",
    "Find the average salary of delivery persons in each city.",
    "Rank cities by average delivery time.",
]

for question in questions:
    print("\n" + "=" * 60)
    print("QUESTION:", question)

    result = process_user_question(schema, question)

    print("\nSTATUS:", result["status"])

    if result["status"] == "clarification_needed":
        print("CLARIFICATION:", result["clarification_question"])

    elif result["status"] == "success":
        print("INTERPRETED:", result["interpreted_question"])
        print("PRIMARY SQL:", result["primary_sql"])
        print("ALTERNATIVE SQL:", result["alternative_sql"])
        print("VALIDATION:", result.get("validation"))
        print("SEMANTIC VALIDATION:", result.get("semantic_validation"))
        print("ALTERNATIVE ERROR:", result.get("alternative_error"))

    else:
        print("ERROR:", result["error"])
