import os
import re
import json
import pandas as pd
import sqlglot
from sqlglot import exp
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
MAX_RETRIES = 2


def validate_sql(sql, df, table_name):
    """Validate SQL syntax, tables, columns and safety."""

    if not sql:
        raise ValueError("AI returned an empty SQL query.")

    if "--" in sql or "/*" in sql:
        raise ValueError("SQL comments are not allowed.")

    try:
        statements = sqlglot.parse(sql, read="postgres")
    except sqlglot.errors.ParseError as error:
        raise ValueError(f"Invalid SQL syntax: {error}")

    statements = [s for s in statements if s is not None]

    if len(statements) != 1:
        raise ValueError("Only one SQL statement is allowed.")

    tree = statements[0]

    if not isinstance(tree, exp.Select):
        raise ValueError("Only SELECT queries are allowed.")
    
    forbidden = (
        exp.Insert,
        exp.Update,
        exp.Delete,
        exp.Create,
        exp.Drop,
        exp.Alter,
        exp.Truncate,
        exp.Grant,
        exp.Revoke
    )

    for operation in forbidden:
      if next(tree.find_all(operation), None) is not None:
         raise ValueError("Unsafe SQL operation detected.")
    
    allowed_table = table_name.lower()

    cte_names = {
        cte.alias_or_name.lower()
        for cte in tree.find_all(exp.CTE)
    }

    for table in tree.find_all(exp.Table):
        if table.name.lower() not in cte_names:
            if table.name.lower() != allowed_table:
                raise ValueError(
                    f"Table '{table.name}' is not allowed."
                )

        if table.db or table.catalog:
            raise ValueError("Schema-qualified tables are not allowed.")

    valid_columns = {
        str(column).lower() for column in df.columns
    }

    aliases = {
        projection.alias.lower()
        for projection in tree.expressions
        if isinstance(projection, exp.Alias)
    }

    for column in tree.find_all(exp.Column):
        name = column.name.lower()

        if name == "*":
            continue

        if name not in valid_columns and name not in aliases:
            raise ValueError(
                f"Unknown column '{column.name}'."
            )

    return sql.strip().rstrip(";")


def review_sql(client, question, sql, df):
    """Ask a separate AI call to review SQL against user intent."""

    schema = "\n".join(
        f"- {column}: {dtype}"
        for column, dtype in df.dtypes.items()
    )

    prompt = f"""
Review whether this SQL correctly answers the user's question.

USER QUESTION:
{question}

AVAILABLE TABLE: test_data

AVAILABLE COLUMNS:
{schema}

GENERATED SQL:
{sql}

Check:
1. Does the SQL answer the exact question?
2. Is the correct aggregation used: SUM, AVG, COUNT, MIN or MAX?
3. Is GROUP BY used where necessary?
4. Is ASC or DESC correct?
5. Is LIMIT used when a single highest or lowest result is requested?
6. Does SELECT include the requested category and calculated metric?
7. Are unnecessary filters or assumptions introduced?

Return JSON only, using this structure:
{{
  "status": "PASS" or "FAIL",
  "reason": "Brief explanation",
  "corrected_sql": "Corrected SQL if FAIL, otherwise empty"
}}

Do not approve SQL merely because its syntax is valid.
"""

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a strict PostgreSQL SQL reviewer."
            },
            {"role": "user", "content": prompt}
        ],
        temperature=0,
        max_completion_tokens=500,
        response_format={"type": "json_object"}
    )

    result = json.loads(response.choices[0].message.content)

    if result.get("status") not in ["PASS", "FAIL"]:
        raise ValueError("AI reviewer returned an invalid status.")

    return result


def generate_sql(question, df, table_name="test_data"):
    """Generate, validate and review SQL with up to two retries."""

    if not question or not question.strip():
        raise ValueError("Please enter a question.")

    if not isinstance(df, pd.DataFrame) or df.empty:
        raise ValueError("A non-empty DataFrame is required.")

    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", table_name):
        raise ValueError("Invalid table name.")

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError("GROQ_API_KEY is missing from .env.")

    client = Groq(api_key=api_key)

    schema = "\n".join(
        f"- {column}: {dtype}"
        for column, dtype in df.dtypes.items()
    )

    prompt = f"""
Convert the user's question into ONE PostgreSQL SELECT query.

TABLE: {table_name}

SCHEMA:
{schema}

QUESTION:
{question}

RULES:
1. Use only the supplied table and columns.
2. Generate only SELECT queries.
3. Use SUM for totals, AVG for averages and COUNT for counts.
4. Use GROUP BY when calculating metrics by category.
5. Use DESC for highest and ASC for lowest.
6. Use LIMIT 1 for a single highest or lowest category.
7. Return both the category and its calculated metric.
8. Never confuse individual records with category aggregates.
9. Never invent columns.
10. Return only SQL without Markdown or explanations.

Example:
Question: Which city has the highest average revenue?

SELECT city, AVG(revenue) AS average_revenue
FROM {table_name}
GROUP BY city
ORDER BY average_revenue DESC
LIMIT 1;
"""

    last_error = "Unknown validation error."

    for attempt in range(MAX_RETRIES + 1):

        try:
            if attempt == 0:
                messages = [
                    {
                        "role": "system",
                        "content": "You are an expert PostgreSQL query generator."
                    },
                    {"role": "user", "content": prompt}
                ]
            else:
                messages = [
                    {
                        "role": "system",
                        "content": "Correct PostgreSQL SQL based on the feedback."
                    },
                    {
                        "role": "user",
                        "content": f"""
Original question: {question}

Available schema:
{schema}

Previous SQL:
{sql}

Reason for rejection:
{last_error}

Generate a corrected SELECT query.
Return SQL only.
"""
                    }
                ]

            response = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=messages,
                temperature=0,
                max_completion_tokens=500
            )

            sql = response.choices[0].message.content.strip()

            sql = re.sub(
                r"^```(?:sql)?\s*",
                "",
                sql,
                flags=re.IGNORECASE
            )
            sql = re.sub(r"\s*```$", "", sql).strip()

            # First validate SQL structure and safety
            validate_sql(sql, df, table_name)

            # Then review whether it answers the question
            review = review_sql(client, question, sql, df)

            if review["status"] == "PASS":
                return sql.rstrip(";").strip()

            last_error = review.get(
                "reason",
                "The SQL does not correctly answer the question."
            )

            corrected_sql = review.get("corrected_sql", "").strip()

            if corrected_sql:
                sql = corrected_sql

                try:
                    validate_sql(sql, df, table_name)
                    second_review = review_sql(
                        client, question, sql, df
                    )

                    if second_review["status"] == "PASS":
                        return sql.rstrip(";").strip()

                    last_error = second_review.get(
                        "reason", last_error
                    )

                except ValueError as error:
                    last_error = str(error)

        except ValueError as error:
            last_error = str(error)

        except Exception as error:
            raise RuntimeError(
                f"SQL generation/review failed: {error}"
            ) from error

    raise ValueError(
        f"SQL could not pass validation after "
        f"{MAX_RETRIES} retries. Last issue: {last_error}"
    )

