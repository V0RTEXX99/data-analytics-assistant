from ai.sql_generator import generate_sql
from ai.sql_validator import validate_sql
from ai.sql_correction import correct_and_revalidate
from ai.query_understanding import understand_query


def process_user_question(schema, user_question, clarification_history=None):
    """
    Complete Member 2 pipeline.

    Handles:
    1. Query understanding
    2. Clarification context
    3. SQL generation
    4. Syntax and schema validation
    5. Semantic validation and correction
    6. Structured output
    """

    if clarification_history is None:
        clarification_history = []

    # STEP 1: Build question context
    context = f"Original user request:\n{user_question}\n"

    if clarification_history:
        context += "\nPrevious clarification answers:\n"

        for answer in clarification_history:
            context += f"- {answer}\n"

    # STEP 2: Understand the question
    understanding = understand_query(schema, context)

    if understanding["status"] == "CLARIFICATION_NEEDED":
        return {
            "status": "clarification_needed",
            "original_question": user_question,
            "clarifications": clarification_history,
            "clarification_question": understanding["clarification_question"],
            "primary_sql": None,
            "alternative_sql": None,
            "error": None,
        }

    if understanding["status"] != "CLEAR":
        return {
            "status": "error",
            "original_question": user_question,
            "clarifications": clarification_history,
            "primary_sql": None,
            "alternative_sql": None,
            "error": "Unable to understand the user request.",
        }

    interpreted_question = understanding["interpreted_question"]

    if not interpreted_question:
        return {
            "status": "error",
            "original_question": user_question,
            "clarifications": clarification_history,
            "primary_sql": None,
            "alternative_sql": None,
            "error": "No interpreted question was returned.",
        }

    # STEP 3: Generate SQL
    generation = generate_sql(schema, interpreted_question)

    if generation["status"] != "success":
        return {
            "status": "error",
            "original_question": user_question,
            "clarifications": clarification_history,
            "primary_sql": None,
            "alternative_sql": None,
            "error": generation.get("error"),
        }

    primary_sql = generation["primary_sql"]

    # STEP 4: Validate primary SQL
    initial_validation = validate_sql(primary_sql, schema)

    # STEP 5: Correct and semantically validate primary SQL
    correction_result = correct_and_revalidate(
        schema=schema,
        sql_query=primary_sql,
        validation_result=initial_validation,
        user_question=interpreted_question,
    )

    if not correction_result["success"]:
        return {
            "status": "error",
            "original_question": user_question,
            "clarifications": clarification_history,
            "primary_sql": None,
            "alternative_sql": None,
            "error": "SQL validation or semantic correction failed.",
            "validation": correction_result.get("validation"),
            "semantic_validation": correction_result.get("semantic_validation"),
            "attempts": correction_result.get("attempts"),
            "generated_sql": primary_sql,
        }

    # STEP 6: Validate alternative SQL independently

    alternative_sql = generation.get("alternative_sql")
    alternative_result = None
    alternative_error = None

    if alternative_sql:

        alternative_validation = validate_sql(alternative_sql, schema)

        alternative_result = correct_and_revalidate(
            schema=schema,
            sql_query=alternative_sql,
            validation_result=alternative_validation,
            user_question=interpreted_question,
        )

        if alternative_result["success"]:
            alternative_sql = alternative_result["sql"]

        else:
            # Do not hand off an unvalidated alternative
            alternative_sql = None

            alternative_error = (
                alternative_result.get("validation", {}).get("message")
                or "Alternative SQL failed validation."
            )

    # STEP 7: Return structured output
    return {
        "status": "success",
        "original_question": user_question,
        "clarifications": clarification_history,
        "interpreted_question": interpreted_question,
        "primary_sql": correction_result["sql"],
        "alternative_sql": alternative_sql,
        "validation": correction_result["validation"],
        "semantic_validation": correction_result["semantic_validation"],
        "correction_attempts": correction_result["attempts"],
        "alternative_validation": (
            alternative_result["validation"]
            if alternative_result and alternative_result["success"]
            else None
        ),
        "alternative_error": alternative_error,
        "error": None,
    }
