
from ai.sql_validator import validate_sql

# Test database schema
schema = {
    "table_name": "zomato",
    "columns": {
        "city": "VARCHAR",
        "ratings": "FLOAT",
        "time_taken": "INTEGER"
    }
}

# Five security test cases
test_cases = [
    {
        "name": "Normal SELECT",
        "sql": "SELECT city FROM zomato;",
        "expected": True
    },
    {
        "name": "WITH + SELECT",
        "sql": """
            WITH city_data AS (
                SELECT city FROM zomato
            )
            SELECT city FROM city_data;
        """,
        "expected": True
    },
    {
        "name": "INSERT",
        "sql": "INSERT INTO zomato (city) VALUES ('Mumbai');",
        "expected": False
    },
    {
        "name": "WITH + DELETE",
        "sql": """
            WITH deleted_rows AS (
                DELETE FROM zomato
                WHERE city = 'Mumbai'
                RETURNING city
            )
            SELECT city FROM deleted_rows;
        """,
        "expected": False
    },
    {
        "name": "Multiple SQL statements",
        "sql": """
            SELECT city FROM zomato;
            DELETE FROM zomato;
        """,
        "expected": False
    }
]

passed = 0

for test in test_cases:
    print("\n" + "=" * 65)
    print("TEST:", test["name"])

    result = validate_sql(test["sql"], schema)

    actual = result["valid"]
    expected = test["expected"]

    print("Expected:", "ALLOWED" if expected else "BLOCKED")
    print("Actual:", "ALLOWED" if actual else "BLOCKED")
    print("Message:", result["message"])

    if actual == expected:
        print("RESULT: PASS")
        passed += 1
    else:
        print("RESULT: FAIL")

print("\n" + "=" * 65)
print(f"SECURITY TEST SUMMARY: {passed}/{len(test_cases)} PASSED")
print("=" * 65)
