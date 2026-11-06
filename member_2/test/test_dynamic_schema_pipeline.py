import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
member_2_path = os.path.dirname(current_dir)
sys.path.insert(0, member_2_path)

from main.pipeline import process_user_question

# A completely different dataset schema
schema = {
    "table_name": "retail_sales",
    "columns": {
        "product_name": "VARCHAR",
        "category": "VARCHAR",
        "sales": "INTEGER",
        "profit": "NUMERIC"
    }
}

# User's natural-language question
question = "Show total sales by category, sorted from highest to lowest."

print("\n" + "=" * 60)
print("DYNAMIC SCHEMA TEST")
print("=" * 60)

print("\nUSER QUESTION:")
print(question)

result = process_user_question(schema, question)

print("\nSTATUS:")
print(result["status"])

if result["status"] == "success":

    print("\nINTERPRETED QUESTION:")
    print(result["interpreted_question"])

    print("\nPRIMARY SQL:")
    print(result["primary_sql"])

    print("\nALTERNATIVE SQL:")
    print(result["alternative_sql"])

    print("\nVALIDATION:")
    print(result["validation"])

    print("\nSEMANTIC VALIDATION:")
    print(result["semantic_validation"])

    print("\nALTERNATIVE ERROR:")
    print(result.get("alternative_error"))

else:
    print("\nERROR:")
    print(result.get("error"))

    print("\nCLARIFICATION:")
    print(result.get("clarification_question"))
