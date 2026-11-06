import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
member_2_path = os.path.dirname(current_dir)
sys.path.insert(0, member_2_path)

from main.sql_generator import generate_sql


schema = {
    "table_name": "zomato",
    "columns": {
        "city": "VARCHAR",
        "ratings": "FLOAT",
        "time_taken": "INTEGER"
    }
}


# questions = [

#     # =========================
#     # LEVEL 1 — EASY
#     # =========================

#     "Show all cities.",

#     "Show all records where the rating is greater than 4.5.",

#     "Find the highest rating.",

#     "Find the lowest delivery time.",


#     # =========================
#     # LEVEL 2 — MEDIUM
#     # =========================

#     "Count the number of records in each city.",

#     "Find the average rating for each city.",

#     "Show cities where the average delivery time is greater than 30.",

#     "Find the top 3 cities with the highest average rating.",

#     "Show the average delivery time and average rating for each city.",


#     # =========================
#     # LEVEL 3 — HARD
#     # =========================

#     "Find cities where the average rating is above 4.5 and the average delivery time is below 30.",

#     "Show the city with the fastest average delivery time.",

#     "Find the difference between the maximum and minimum delivery time.",

#     "For each city, show the total number of records and average delivery time, sorted by the highest average delivery time.",

#     "Find the top 3 cities with the highest average rating, but only include cities where the average delivery time is less than 30.",


#     # =========================
#     # LEVEL 4 — EDGE CASES
#     # =========================

#     "Find the average salary for each city.",

#     "Delete all records where rating is below 3.",

#     "Show the average delivery time for each city and explain which city performs best."
# ]

# questions = [
#     "Give me distinct cities.",
#     "Find the average delivery time.",
#     "Show the top 5 cities by delivery time.",
#     "Show all locations.",
#     "Find the average salary for each city.",
#     "Show the average delivery time by city and weather."
# ]

questions = [

    # Basic
    "Show all cities.",

    "Find the highest rating.",

    "Find the lowest delivery time.",

    # Aggregation
    "Find the average delivery time for each city.",

    "Count the number of records in each city.",

    # Ranking
    "Show the top 5 cities by delivery time.",

    "Show the top 3 cities by average rating.",

    # Ambiguous semantic test
    "Show the 5 deliveries with the highest delivery time.",

    # Complex
    "Find the top 3 cities with the highest average rating, but only include cities where the average delivery time is less than 30.",

    # Missing schema attributes
    "Show all weather conditions.",

    "Find the average salary for each city.",

    # Write query test
    "Delete all records where ratings are below 3."
]

for question in questions:

    print("\n" + "=" * 60)

    print("USER QUESTION:")
    print(question)

    sql = generate_sql(
        schema,
        question
    )

    print("\nGENERATED SQL:")
    print(sql)