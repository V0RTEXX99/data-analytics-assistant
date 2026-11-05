from ai.sql_validator import validate_sql
from ai.sql_correction import correct_and_revalidate

schema = {
    "table_name": "zomato",
    "columns": {"city": "VARCHAR", "ratings": "FLOAT", "time_taken": "INTEGER"},
}

question = "Find the average delivery time."

wrong_sql = "SELECT MAX(time_taken) FROM zomato;"

# Step 1: Initial SQL validation
initial_validation = validate_sql(wrong_sql, schema)

print("\nORIGINAL SQL:")
print(wrong_sql)

print("\nINITIAL VALIDATION:")
print(initial_validation)

# Step 2: Semantic correction pipeline
result = correct_and_revalidate(
    schema=schema,
    sql_query=wrong_sql,
    validation_result=initial_validation,
    user_question=question,
)

print("\nCORRECTION RESULT:")
print("Success:", result["success"])
print("Corrected SQL:", result["sql"])
print("Attempts:", result["attempts"])

print("\nFINAL VALIDATION:")
print(result["validation"])

print("\nFINAL SEMANTIC VALIDATION:")
print(result["semantic_validation"])
