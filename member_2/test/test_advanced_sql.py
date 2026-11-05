from ai.sql_generator import generate_sql


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
        "order_date": "DATE"
    }
}


# questions = [

#     # COALESCE
#     "Find the average rating for each city, treating missing ratings as 0.",
#     "Find the average rating for each city, treating missing ratings as 0.",

#     # CASE WHEN
#     "Classify each delivery as Fast if delivery time is below 25, "
#     "Moderate if it is between 25 and 35, and Slow if it is above 35.",

#     # Subquery
#     "Show the cities whose average delivery time is greater than "
#     "the overall average delivery time.",

#     # Complex subquery
#     "Find the top 3 cities with the highest average rating among "
#     "cities whose average delivery time is below 30 minutes.",

#     # Window functions
#     "Rank all cities by their average delivery time from highest to lowest.",

#     "Give each city a dense rank based on average delivery time, "
#     "from fastest to slowest.",

#     "Rank cities by average delivery time separately for each weather condition.",

#     # Edge case
#     "Find the average salary for each city.",

#     "Show the 5 deliveries with the highest delivery time.",

#     "Show the top 5 cities by delivery time."
# ]


questions = [

    "Rank all cities by their average delivery time from highest to lowest.",

    "Sort all cities by their average delivery time from highest to lowest."
]


for question in questions:

    print("\n" + "=" * 80)

    print("USER QUESTION:")
    print(question)

    sql = generate_sql(
        schema,
        question
    )

    print("\nGENERATED SQL:")
    print(sql)