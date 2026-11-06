import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
member_2_path = os.path.dirname(current_dir)
sys.path.insert(0, member_2_path)

from main.prompt_builder import build_sql_prompt

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