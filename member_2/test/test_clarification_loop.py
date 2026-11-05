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

original_question = "Show the top 5."
clarification_history = []

print("\nUSER QUESTION:", original_question)

# First pipeline call
result = process_user_question(schema, original_question)

# Handle multiple clarification rounds
max_clarifications = 5
count = 0

while result["status"] == "clarification_needed" and count < max_clarifications:

    print("\nSYSTEM:", result["clarification_question"])

    answer = input("\nYOUR ANSWER: ").strip()

    if not answer:
        print("Please provide a clarification answer.")
        continue

    clarification_history.append(answer)
    count += 1

    result = process_user_question(
        schema, original_question, clarification_history=clarification_history
    )

# Display final result
print("\n" + "=" * 50)
print("FINAL RESULT")
print("=" * 50)

print("STATUS:", result["status"])

if result["status"] == "success":

    print("\nINTERPRETED QUESTION:")
    print(result["interpreted_question"])

    print("\nPRIMARY SQL:")
    print(result["primary_sql"])

    print("\nALTERNATIVE SQL:")
    print(result["alternative_sql"])

elif result["status"] == "clarification_needed":
    print("\nMaximum clarification attempts reached.")
    print(result["clarification_question"])

else:
    print("\nERROR / MESSAGE:")
    print(result.get("error"))

    print("\nVALIDATION DETAILS:")
    print(result.get("validation"))

    print("\nSEMANTIC VALIDATION:")
    print(result.get("semantic_validation"))

    print("\nGENERATED SQL:")
    print(result.get("generated_sql"))

    print("\nCORRECTION ATTEMPTS:")
    print(result.get("attempts"))
