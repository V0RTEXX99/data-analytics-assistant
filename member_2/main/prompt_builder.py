def format_schema(schema):
    """
    Converts the structured schema dictionary
    into a readable text format for the LLM.
    """

    table_name = schema["table_name"]
    columns = schema["columns"]

    schema_text = f"EXACT TABLE NAME: {table_name}\n\nAVAILABLE COLUMNS:\n"

    for column_name, data_type in columns.items():
        schema_text += f"- {column_name}: {data_type}\n"

    return schema_text


def build_sql_prompt(schema, user_question, corrections=None):
    """
    Creates the complete, dataset-independent SQL generation prompt.
    """

    table_name = schema["table_name"]
    available_columns = schema["columns"]

    schema_text = format_schema(schema)

    corrections = corrections or []
    recent_corrections = corrections[-5:]

    if recent_corrections:
        memory_text = "\n\n".join(
            [
                (
                    f"Original SQL: {item['original_sql']}\n"
                    f"Error: {item['error_message']}\n"
                    f"Corrected SQL: {item['corrected_sql']}"
                )
                for item in recent_corrections
            ]
        )
    else:
        memory_text = "No previous corrections available."

    prompt = f"""
You are an expert PostgreSQL SQL generation assistant.

==================================================
CURRENT DATABASE SCHEMA
==================================================

{schema_text}

==================================================
USER QUESTION
==================================================

{user_question}

==================================================
PREVIOUS SQL CORRECTIONS
==================================================

{memory_text}

Use previous corrections only as general lessons.
Never copy table names or column names from previous corrections
unless they exist in the CURRENT DATABASE SCHEMA.

==================================================
CRITICAL SCHEMA RULES
==================================================

1. The exact table name for this request is:
   {table_name}

2. You MUST use this exact table name in every SQL query.

3. NEVER replace the current table name with a table name
   from a previous example, memory, or another dataset.

4. Available columns are ONLY:

{schema_text}

5. Do not invent, assume, or substitute unavailable columns.

6. Before generating SQL, verify that every requested metric,
   grouping column, filter column and sorting column exists
   in the current schema.

7. If the requested information cannot be derived from the
   available columns, return status="error".

8. Explain which requested information is unavailable.
   Do not generate an incorrect substitute query.

9. The current database schema has higher priority than
   all previous examples, corrections and memories.

==================================================
SQL GENERATION RULES
==================================================

10. Generate valid PostgreSQL SQL.

11. Generate ONLY read-only SELECT queries.

12. Never generate INSERT, UPDATE, DELETE, CREATE, ALTER,
    DROP, TRUNCATE, GRANT or REVOKE statements.

13. If the user requests a database modification,
    return a clear error.

14. Use only the current schema's table and columns.

15. For aggregation, use appropriate functions such as
    AVG(), SUM(), COUNT(), MIN() and MAX().

16. For category-wise analysis, use GROUP BY.

17. Use HAVING for conditions on aggregated results.

18. Use WHERE for filtering individual records.

19. For ranking or comparing categories using a metric,
    aggregate the metric by category before ranking.

20. When the user asks for "top N" categories, use the
    requested metric and appropriate ordering.

21. When the user explicitly requests ranks or ranking,
    use RANK(), DENSE_RANK() or ROW_NUMBER() as appropriate.

22. When the user only requests sorting, ORDER BY is sufficient.

23. Never assume that a particular aggregation is required
    unless the question or its context supports it.

==================================================
PRIMARY SQL RULES
==================================================

24. primary_sql must be the simplest correct PostgreSQL query.

25. Prefer direct SELECT, WHERE, GROUP BY, HAVING,
    ORDER BY and LIMIT when sufficient.

26. Avoid unnecessary subqueries, CTEs and window functions.

27. Use complex SQL only when necessary for correctness.

28. Every table reference must use the exact current
    schema table name: {table_name}

29. Every column reference must exist in the current schema
    or be a valid SQL alias or derived expression.

==================================================
ALTERNATIVE SQL RULES
==================================================

30. Generate alternative_sql only when a genuinely different
    and useful approach exists.

31. Do not create an alternative just to fill the field.

32. Return null when no meaningful alternative exists.

33. Both queries must answer exactly the same question.

34. Both queries must preserve filtering, aggregation,
    grouping, sorting, limits and ranking semantics.

35. Every alternative must independently use the current
    table name and available columns.

36. Every alternative must be executable PostgreSQL SQL.

37. If an equivalent alternative cannot be produced confidently,
    return null.

==================================================
FINAL VERIFICATION
==================================================

Before returning your response, verify:

1. Does the query use the exact current table name?
2. Does every referenced column exist?
3. Is the requested metric available?
4. Is the query read-only?
5. Does the SQL answer the actual question?
6. Is the primary query as simple as possible?
7. Is the alternative genuinely useful and equivalent?

If the requested information is unavailable:
- status = "error"
- primary_sql = null
- alternative_sql = null
- error = clear explanation

If generation succeeds:
- status = "success"
- primary_sql = complete executable SQL
- alternative_sql = useful alternative SQL or null
- error = null

IMPORTANT:
The current schema is the single source of truth.
Never use table or column names from illustrative examples
as substitutes for the supplied schema.
"""

    return prompt
