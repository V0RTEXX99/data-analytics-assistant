import json

from .llm_client import get_client, get_model_name


def format_schema_for_understanding(schema):
    """Convert schema dictionary into readable text."""

    table_name = schema["table_name"]
    columns = schema["columns"]

    schema_text = f"Table: {table_name}\n\nColumns:\n"

    for column_name, data_type in columns.items():
        schema_text += f"- {column_name}: {data_type}\n"

    return schema_text


def understand_query(schema, user_question):
    """
    Determines whether the user's request is clear enough
    for SQL generation.
    """

    schema_text = format_schema_for_understanding(schema)

    prompt = f"""
You are a query-understanding assistant for a data analytics system.

DATABASE SCHEMA:
{schema_text}

USER REQUEST AND CLARIFICATION CONTEXT:
{user_question}

Your task is to determine whether the request is complete enough
to generate SQL.

A request is CLEAR when the user's intent is understandable.

IMPORTANT RULES:

1. Do not guess missing information.
2. Do not assume an entity from an earlier example.
3. For "Show the top 5", identify both the entity and metric.
4. If either is missing, ask for clarification.
5. Check previous clarification answers before asking again.
5A. When clarification history is provided:
    - Treat the original request and all clarification answers
      as one combined request.
    - Never ask again for information already provided.
    - Use previous answers to fill the missing details.
    - Ask only for information that is still missing.
    - Once all required details are available, return CLEAR.
6. Ask all currently missing details in one concise question.
7. Natural-language synonyms are allowed when they reasonably
   map to the schema.

8. Before asking clarification, check whether the requested
   metric or column exists in the schema.

9. If the requested metric or column does NOT exist:
   - Return status CLEAR.
   - Preserve the original user intent.
   - Do not ask which column represents the missing metric.
   - Do not substitute another column.
   The SQL generation module must return an unavailable
   information error.

10. Missing schema columns are not clarification requests.

11. If the user asks to rank a category by a specified metric,
    rank ALL categories by default.

12. Do not ask how many categories to rank unless the user
    explicitly specifies a number or top N.

13. Example:
    User: "Rank cities by average delivery time."
    This is CLEAR.
    Interpreted question:
    "Rank all cities by average delivery time in descending order."

14. "Show the top 5" without an entity or metric requires
    clarification.

15. "Show the top 5 cities by average delivery time" is CLEAR.

16. Interpret "top" as highest metric value (descending)
    and "bottom" as lowest metric value (ascending),
    unless specified otherwise.

17. Do not generate SQL.

18. When CLEAR, create a complete, self-contained interpreted
    question preserving the user's intent.

Return ONLY valid JSON with these four keys:

{{
    "status": "CLEAR" or "CLARIFICATION_NEEDED",
    "clarification_question": "question for user or null",
    "interpreted_question": "complete question or null",
    "reason": "short reason"
}}

For CLEAR:
- clarification_question must be null.
- interpreted_question must contain the complete question.

For CLARIFICATION_NEEDED:
- clarification_question must contain the question to ask.
- interpreted_question must be null.
"""

    response = get_client().chat.completions.create(
        model=get_model_name(),
        messages=[
            {
                "role": "system",
                "content": (
                    "You determine whether a data analytics request "
                    "is complete enough for SQL generation. "
                    "Always return a valid JSON object matching "
                    "the requested structure."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0,
        reasoning_effort="low",
        max_completion_tokens=1500,
        response_format={"type": "json_object"},
    )

    response_text = response.choices[0].message.content

    result = json.loads(response_text)

    # Validate response structure
    required_keys = {
        "status",
        "clarification_question",
        "interpreted_question",
        "reason",
    }

    if not isinstance(result, dict) or not required_keys.issubset(result):
        raise ValueError("Invalid query understanding response.")

    if result["status"] not in {"CLEAR", "CLARIFICATION_NEEDED"}:
        raise ValueError("Unexpected query understanding status.")

    return result
