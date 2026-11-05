from ai.sql_generator import generate_sql
from ai.correction_memory import get_corrections

schema = {
    "table_name": "zomato",
    "columns": {"city": "VARCHAR", "ratings": "FLOAT", "time_taken": "INTEGER"},
}


# Check saved correction memory
corrections = get_corrections()

print("\n" + "=" * 60)
print("CORRECTION MEMORY CHECK")
print(f"Total saved corrections: {len(corrections)}")

for item in corrections[-5:]:
    print("\nOriginal SQL:", item["original_sql"])
    print("Corrected SQL:", item["corrected_sql"])


questions = [
    "Give me all distinct cities.",
    "Find the average delivery time.",
    "Find the average delivery time for each city.",
    "Show the top 5 cities with the highest average delivery time.",
]


for question in questions:

    print("\n" + "=" * 60)
    print("QUESTION:")
    print(question)

    result = generate_sql(schema, question)

    print("\nSTATUS:")
    print(result["status"])

    print("\nPRIMARY SQL:")
    print(result["primary_sql"])

    print("\nALTERNATIVE SQL:")
    print(result["alternative_sql"])

    print("\nERROR:")
    print(result["error"])
