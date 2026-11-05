from ai.query_understanding import understand_query


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
        "festival": "VARCHAR"
    }
}


# test_questions = [

#     # Clearly understandable
#     "Find the average delivery time.",
#     "Find the average rating.",
#     "Show distinct cities.",

#     # Ambiguous
#     "Find the average.",
#     "Show the top 5.",
#     "Compare the performance.",

#     # Partially specified
#     "Show the top 5 cities.",
#     "Show the top 5 by delivery time.",
#     "Show the average by city.",

#     # Clear complex questions
#     "Show the top 5 cities by average delivery time.",
#     "Find the average delivery time for each vehicle type.",
#     "Compare average ratings across different weather conditions."
# ]


test_questions = [
    "Show the top 5 by delivery time.",
    "Show the top 5 cities by delivery time.",
    "Show the top 5 cities.",
    "Show the top 5 vehicle types by average rating."
]


for question in test_questions:

    print("\n" + "=" * 70)

    print("USER QUESTION:")
    print(question)

    result = understand_query(
        schema,
        question
    )

    print("\nUNDERSTANDING RESULT:")

    print(f"Status: {result.get('status')}")
    print(f"Clarification: {result.get('clarification_question')}")
    print(f"Reason: {result.get('reason')}")