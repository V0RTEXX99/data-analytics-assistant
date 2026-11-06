import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
member_2_path = os.path.dirname(current_dir)
sys.path.insert(0, member_2_path)

from main.sql_validator import validate_sql


schema = {
    "table_name": "zomato",
    "columns": {
        "city": "VARCHAR",
        "ratings": "FLOAT",
        "time_taken": "INTEGER"
    }
}


# test_queries = [

#     # Valid SQL
#     "SELECT city FROM zomato;",

#     "SELECT city, AVG(time_taken) AS avg_time "
#     "FROM zomato GROUP BY city;",

#     # Invalid column
#     "SELECT location FROM zomato;",

#     # Invalid syntax
#     "SELEC city FROM zomato;",

#     # Valid DELETE
#     "DELETE FROM zomato WHERE ratings < 3;",

#     # Unknown table
#     "SELECT city FROM employees;"
# ]


test_queries = [

    # Existing tests
    "SELECT city FROM zomato;",
    "SELECT city, AVG(time_taken) AS avg_time FROM zomato GROUP BY city;",
    "SELECT location FROM zomato;",
    "SELEC city FROM zomato;",
    "DELETE FROM zomato WHERE ratings < 3;",
    "SELECT city FROM employees;",

    # New lowercase tests
    "select city from zomato;",
    "select city, avg(time_taken) as avg_time "
    "from zomato group by city;",
    "select city from zomato where ratings > 4.5;",

    # New mixed-case tests
    "SeLeCt city FrOm zomato;",
    "SeLeCt city, AvG(time_taken) "
    "FrOm zomato GrOuP By city;",

    # Lowercase errors
    "selec city from zomato;",
    "select location from zomato;"
]



for query in test_queries:

    result = validate_sql(
        query,
        schema
    )

    print("\n" + "=" * 70)
    print("QUERY:")
    print(query)

    print("\nVALIDATION RESULT:")
    print(result)