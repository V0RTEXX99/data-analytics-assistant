import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

schema = """
Table: zomato

Columns:
city VARCHAR
ratings FLOAT
time_taken INTEGER
weather VARCHAR
traffic VARCHAR
"""

tests = [
    "Show the city and average delivery time. Use only the columns available in the provided schema.",

"Find the average salary for each city.",

"Show the average delivery time for cities with ratings above 4.5, sorted from highest to lowest.",
]

for question in tests:

    prompt = f"""
You are a PostgreSQL SQL generation assistant.

DATABASE SCHEMA:
{schema}

USER QUESTION:
{question}

RULES:
1. Generate PostgreSQL-compatible SQL.
2. Use only the table and columns provided in the schema.
3. Only read-only SQL queries are allowed.
4. Never generate INSERT, UPDATE, DELETE, DROP, ALTER, or TRUNCATE.
5. Never invent tables or columns.
6. Return only the SQL query.
7. Do not provide explanations or markdown.

SQL:
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": "You generate safe PostgreSQL read-only SQL queries."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0,
        max_completion_tokens=300
    )

    result = response.choices[0].message.content

    print("\n" + "=" * 70)
    print("USER QUESTION:")
    print(question)

    print("\nMODEL RESPONSE:")
    print(result)