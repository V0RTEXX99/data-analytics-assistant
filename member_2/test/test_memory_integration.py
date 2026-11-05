from ai.correction_memory import get_corrections
from ai.prompt_builder import build_sql_prompt

schema = {
    "table_name": "zomato_delivery",
    "columns": {
        "city": "VARCHAR",
        "time_taken_min": "INTEGER",
        "delivery_person_ratings": "NUMERIC",
    },
}

corrections = get_corrections()

prompt = build_sql_prompt(
    schema=schema,
    user_question="Find the average delivery time.",
    corrections=corrections,
)

print("TOTAL SAVED CORRECTIONS:", len(corrections))

print("\nPROMPT LENGTH:")
print(len(prompt))

print("\nPROMPT CONTENT:")
print(prompt)

print("\nCORRECTION RECORDS:")
print(corrections)
