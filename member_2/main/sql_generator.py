import json

from .llm_client import get_client, get_model_name
from .prompt_builder import build_sql_prompt
from .sql_validator import clean_sql_response
from .correction_memory import get_corrections


    # Format for schema:
    
    # schema = {
    #     "table_name": "retail_sales",
    #     "columns": {
    #         "category": "VARCHAR",
    #         "sales": "FLOAT",
    #         "quantity": "INTEGER",
    #         "order_date": "DATE"
    #     }
    # }
    
    # Format for result:
    
    # result = {
    #     "status": "success",
    #     "primary_sql": primary_sql,
    #     "alternative_sql": alternative_sql,
    #     "error": None,
    # }
    

def generate_sql(schema, user_question):
    """
    Generate PostgreSQL SQL using the supplied dynamic schema.
    Returns primary SQL and an optional alternative SQL.
    """

    # Load correction memory
    corrections = get_corrections()

    # Build schema-based prompt
    prompt = build_sql_prompt(schema, user_question, corrections)

    system_prompt = """
You are an expert PostgreSQL SQL generator.

STRICT REQUIREMENTS:

1. Always use the exact table name and available columns
   from the current database schema.

2. Never invent tables or columns.

3. Generate only read-only SELECT queries.

4. If requested information is unavailable in the schema,
   return status="error" and explain why.

5. PRIMARY SQL must be the simplest correct solution.

6. ALTERNATIVE SQL must be genuinely useful and semantically
   equivalent. Return null if no meaningful alternative exists.

RANKING REQUIREMENTS:

7. Carefully distinguish between sorting and ranking.

8. If the user explicitly asks to "rank", "give rank",
   "show ranking", or requests rank numbers, the primary SQL
   MUST include a ranking function such as:
   RANK(), DENSE_RANK(), or ROW_NUMBER().

9. For category-based ranking using an aggregate metric,
   first calculate the aggregate for each category and then
   apply the ranking function to that aggregate.

10. Example:
    User: Rank cities by average delivery ratings.

    Correct approach:

    SELECT
        city,
        AVG(delivery_person_ratings) AS avg_rating,
        RANK() OVER (
            ORDER BY AVG(delivery_person_ratings) DESC
        ) AS city_rank
    FROM zomato_delivery
    GROUP BY city;

    IMPORTANT: This is an illustrative example only.
    Always use the actual table and columns supplied
    in the current schema.

11. If the user only asks to sort or order results,
    ORDER BY is sufficient. Do not add an unnecessary
    ranking column.

12. Both primary and alternative SQL must follow
    the user's explicit ranking requirements.

13. Return complete executable PostgreSQL SQL.

Return only the required structured JSON response.
"""

    response = get_client().chat.completions.create(
        model=get_model_name(),
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        temperature=0,
        reasoning_effort="low",
        max_completion_tokens=1500,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "sql_generation",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "enum": ["success", "error"]},
                        "primary_sql": {"type": ["string", "null"]},
                        "alternative_sql": {"type": ["string", "null"]},
                        "error": {"type": ["string", "null"]},
                    },
                    "required": ["status", "primary_sql", "alternative_sql", "error"],
                    "additionalProperties": False,
                },
            },
        },
    )

    response_text = response.choices[0].message.content

    if not response_text:
        raise ValueError("SQL generator returned an empty response.")

    result = json.loads(response_text)

    if result["status"] == "error":
        return result

    primary_sql = result["primary_sql"]

    if not primary_sql:
        return {
            "status": "error",
            "primary_sql": None,
            "alternative_sql": None,
            "error": "The model returned an empty primary SQL query.",
        }

    primary_sql = clean_sql_response(primary_sql)

    alternative_sql = result["alternative_sql"]

    if alternative_sql:
        alternative_sql = clean_sql_response(alternative_sql)

    return {
        "status": "success",
        "primary_sql": primary_sql,
        "alternative_sql": alternative_sql,
        "error": None,
    }
