import json

from .llm_client import get_client, get_model_name


def validate_sql_semantics(schema, user_question, sql_query):
    """
    Checks whether generated SQL correctly answers
    the user's original question.
    """

    schema_text = f"Table: {schema['table_name']}\nColumns:\n"

    for column, data_type in schema["columns"].items():
        schema_text += f"- {column}: {data_type}\n"

    prompt = f"""
You are an expert PostgreSQL SQL semantic validator.

DATABASE SCHEMA:
{schema_text}

USER QUESTION:
{user_question}

GENERATED SQL:
{sql_query}

TASK:
Determine whether the SQL correctly answers the user's question.

CHECK:
1. Correct aggregation and calculations.
2. Correct columns and grouping.
3. Correct filters and conditions.
4. Correct sorting and ranking.
5. Correct LIMIT or requested number of results.
6. Whether the SQL changes the intended meaning.

IMPORTANT:
- Valid SQL syntax does not automatically mean semantic correctness.
- Do not approve SQL that answers a different question.
- Judge only using the supplied schema and question.
- Do not invent requirements that the user did not specify.

Return ONLY a valid JSON object:

{{
    "valid": true,
    "reason": "Short explanation",
    "suggestion": null
}}

RULES:
- valid must be true or false (boolean).
- reason must be a string.
- suggestion must be a string or null.
- If SQL is correct, use valid=true and suggestion=null.
- If SQL is incorrect, use valid=false and explain the correction.
- Do not include Markdown or text outside the JSON object.
"""

    response = get_client().chat.completions.create(
        model=get_model_name(),
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a strict SQL semantic validator. "
                    "Evaluate SQL against the user's exact intent. "
                    "Return only a valid JSON object."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0,
        reasoning_effort="low",
        max_completion_tokens=1500,
        response_format={
            "type": "json_object"
        }
    )

    response_text = response.choices[0].message.content

    if not response_text:
        raise ValueError("The semantic validator returned an empty response.")

    result = json.loads(response_text)

    required_keys = {
        "valid",
        "reason",
        "suggestion"
    }

    if not isinstance(result, dict):
        raise ValueError("Invalid semantic validation response.")

    if not required_keys.issubset(result):
        raise ValueError("Missing fields in semantic validation response.")

    if not isinstance(result["valid"], bool):
        raise ValueError("'valid' must be a boolean.")

    if not isinstance(result["reason"], str):
        raise ValueError("'reason' must be a string.")

    if result["suggestion"] is not None and not isinstance(
        result["suggestion"], str
    ):
        raise ValueError("'suggestion' must be a string or null.")

    return result
