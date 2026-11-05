from ai.sql_validator import validate_sql
from ai.sql_correction import correct_and_revalidate
from ai.correction_memory import get_corrections

schema = {
    "table_name": "zomato",
    "columns": {"city": "VARCHAR", "ratings": "FLOAT", "time_taken": "INTEGER"},
}


test_queries = [
    # Syntax error
    "SELEC city FROM zomato;",
    # Syntax error
    "SELECT city AVG(time_taken) FROM zomato;",
    # Invalid column
    "SELECT location FROM zomato;",
]


for query in test_queries:

    print("\n" + "=" * 70)

    # -----------------------------
    # 1. Original SQL
    # -----------------------------
    print("ORIGINAL SQL:")
    print(query)

    # -----------------------------
    # 2. Initial Validation
    # -----------------------------
    initial_validation = validate_sql(query, schema)

    print("\nINITIAL VALIDATION:")
    print(f"Status       : {'VALID' if initial_validation['valid'] else 'INVALID'}")
    print(f"Query Type   : {initial_validation['query_type']}")
    print(f"Syntax Valid : {initial_validation['syntax_valid']}")
    print(f"Schema Valid : {initial_validation['schema_valid']}")
    print(f"Message      : {initial_validation['message']}")

    # -----------------------------
    # 3. Automatic Correction
    # -----------------------------
    correction_result = correct_and_revalidate(
        schema=schema, sql_query=query, validation_result=initial_validation
    )

    # -----------------------------
    # 4. Corrected SQL
    # -----------------------------
    print("\nCORRECTED SQL:")

    if correction_result["sql"]:
        print(correction_result["sql"])
    else:
        print("No corrected SQL generated.")

    # -----------------------------
    # 5. Final Validation
    # -----------------------------
    final_validation = correction_result["validation"]

    print("\nFINAL VALIDATION:")
    print(f"Status       : {'VALID' if final_validation['valid'] else 'INVALID'}")
    print(f"Query Type   : {final_validation['query_type']}")
    print(f"Syntax Valid : {final_validation['syntax_valid']}")
    print(f"Schema Valid : {final_validation['schema_valid']}")
    print(f"Message      : {final_validation['message']}")

    print(f"\nCorrection Attempts: {correction_result['attempts']}")

    print("=" * 70)

    print("\n" + "=" * 70)
print("CORRECTION MEMORY AFTER TESTING:")

corrections = get_corrections()

print("Total saved corrections:", len(corrections))

for item in corrections[-3:]:
    print("\nOriginal:", item["original_sql"])
    print("Corrected:", item["corrected_sql"])
    print("Error:", item["error_message"])
