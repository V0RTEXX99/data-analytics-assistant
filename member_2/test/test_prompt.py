from ai.prompt_builder import build_sql_prompt

schema = {
    "table_name": "zomato",
    "columns": {
        "city": "VARCHAR",
        "ratings": "FLOAT",
        "time_taken": "INTEGER"
    }
}

user_question = "Find the average delivery time for each city."

prompt = build_sql_prompt(
    schema,
    user_question
)

print(prompt)