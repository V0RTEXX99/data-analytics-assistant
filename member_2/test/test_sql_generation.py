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
"""

questions = [
    "Give me all distinct cities.",
    "Find the average delivery time.",
    "Find the average delivery time for each city.",
    "Show the top 5 cities with the highest average delivery time.",
    "Find the number of records in each city."
]

for question in questions:

    prompt = f"""
You are a PostgreSQL SQL query generator.

Database schema:
{schema}

User question:
{question}

Rules:
1. Generate a valid PostgreSQL query.
2. Use only the table and columns provided in the schema.
3. Generate only a SELECT query.
4. Do not invent any table or column.
5. Return only the SQL query.
6. Do not provide explanations or markdown.

SQL:
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    sql = response.choices[0].message.content

    print("\n" + "=" * 60)
    print("QUESTION:")
    print(question)
    print("\nGENERATED SQL:")
    print(sql)