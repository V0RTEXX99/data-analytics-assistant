import os

from dotenv import load_dotenv
from groq import Groq

from sql_validator import validate_sql, clean_sql_response
from semantic_validator import validate_sql_semantics
from correction_memory import save_correction

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def correct_sql(schema, sql_query, validation_message, user_question=None):
    """
    Corrects SQL using the schema, original question,
    and validation feedback.
    """

    table_name = schema["table_name"]
    columns = schema["columns"]

    schema_text = f"Table: {table_name}\n\nColumns:\n"

    for column_name, data_type in columns.items():
        schema_text += f"- {column_name}: {data_type}\n"

    prompt = f"""
You are an expert PostgreSQL SQL correction assistant.

DATABASE SCHEMA:
{schema_text}

USER QUESTION:
{user_question or "Not provided"}

ORIGINAL SQL:
{sql_query}

VALIDATION ERROR:
{validation_message}

TASK:
Correct the SQL query so that it:
1. Uses valid PostgreSQL syntax.
2. Uses only available tables and columns.
3. Correctly answers the original user question.
4. Preserves the user's intended meaning.

RULES:
- Fix syntax errors.
- Fix invalid table or column references.
- Fix incorrect aggregations and calculations.
- Fix incorrect grouping, filtering, sorting and ranking.
- Do not invent tables or columns.
- Generate only read-only SELECT SQL.
- Do not change the user's original intent.
- Return only the corrected SQL query.
- Do not provide explanations or markdown.

CORRECTED SQL:
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": "You correct PostgreSQL SQL queries accurately.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0,
        max_completion_tokens=500,
    )

    corrected_sql = response.choices[0].message.content.strip()

    return clean_sql_response(corrected_sql)


def correct_and_revalidate(
    schema, sql_query, validation_result, user_question=None, max_retries=2
):
    """
    Corrects SQL syntax, schema and semantic errors.
    Revalidates the corrected SQL after every attempt.
    """

    original_sql = sql_query
    current_sql = sql_query
    current_validation = validation_result

    original_error = validation_result.get("message", "Validation failed.")

    for attempt in range(max_retries):

        # Step 1: Syntax and schema validation
        if current_validation["valid"]:

            # Step 2: Semantic validation
            if user_question:
                semantic_result = validate_sql_semantics(
                    schema=schema, user_question=user_question, sql_query=current_sql
                )

                if semantic_result["valid"]:
                    return {
                        "success": True,
                        "sql": current_sql,
                        "validation": current_validation,
                        "semantic_validation": semantic_result,
                        "attempts": attempt,
                    }

                current_error = (
                    "Semantic error: "
                    + semantic_result["reason"]
                    + "\nSuggestion: "
                    + str(semantic_result["suggestion"])
                )

                original_error = current_error

            else:
                return {
                    "success": True,
                    "sql": current_sql,
                    "validation": current_validation,
                    "semantic_validation": None,
                    "attempts": attempt,
                }

        else:
            current_error = current_validation["message"]
            semantic_result = None

        # Step 3: Generate corrected SQL
        corrected_sql = correct_sql(
            schema=schema,
            sql_query=current_sql,
            validation_message=current_error,
            user_question=user_question,
        )

        if not corrected_sql:
            return {
                "success": False,
                "sql": None,
                "validation": current_validation,
                "semantic_validation": semantic_result,
                "attempts": attempt + 1,
            }

        current_sql = corrected_sql

        # Step 4: Revalidate syntax and schema
        current_validation = validate_sql(current_sql, schema)

        # Save only after all validations pass
        if current_validation["valid"] and user_question:

            semantic_result = validate_sql_semantics(
                schema=schema, user_question=user_question, sql_query=current_sql
            )

            if semantic_result["valid"]:
                save_correction(
                    original_sql=original_sql,
                    corrected_sql=current_sql,
                    error_message=original_error,
                )

                return {
                    "success": True,
                    "sql": current_sql,
                    "validation": current_validation,
                    "semantic_validation": semantic_result,
                    "attempts": attempt + 1,
                }

    return {
        "success": False,
        "sql": None,
        "validation": current_validation,
        "semantic_validation": semantic_result,
        "attempts": max_retries,
    }
