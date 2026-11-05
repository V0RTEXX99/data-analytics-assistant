import sqlparse
import sqlglot
from sqlglot import exp


def clean_sql_response(sql_query):
    """
    Cleans common formatting returned by an LLM.
    """

    if not sql_query:
        return ""

    sql_query = sql_query.strip()

    # Remove markdown code fences if present
    if sql_query.startswith("```"):
        lines = sql_query.splitlines()

        if lines and lines[0].startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        sql_query = "\n".join(lines).strip()

    return sql_query


def classify_sql(sql_query):
    """
    Allows only a single read-only SELECT query.
    Rejects write operations, DDL and multiple statements.
    """

    if not sql_query or not sql_query.strip():
        return "UNKNOWN"

    try:
        statements = sqlglot.parse(sql_query, read="postgres")
    except Exception:
        return "UNKNOWN"

    # Reject empty or multiple statements
    if len(statements) != 1 or statements[0] is None:
        return "UNKNOWN"

    expression = statements[0]

    # Only SELECT statements are allowed.
    # WITH queries containing SELECT are represented as SELECT
    # with CTEs in SQLGlot.
    if not isinstance(expression, exp.Select):
        # Reject SELECT INTO because it creates a new table
        if expression.args.get("into") is not None:
            return "UNKNOWN"

    # Reject write operations anywhere inside the query,
    # including CTEs and nested expressions.
    forbidden_nodes = (
        exp.Insert,
        exp.Update,
        exp.Delete,
        exp.Create,
        exp.Drop,
        exp.Alter,
        exp.TruncateTable,
        exp.Command,
    )

    for node in expression.walk():
        if isinstance(node, forbidden_nodes):
            return "UNKNOWN"

    return "READ"


def validate_sql_syntax(sql_query):
    """
    Checks whether the SQL can be parsed as PostgreSQL SQL.
    """

    try:
        sqlglot.parse_one(sql_query, read="postgres")

        return True, None

    except Exception as error:
        return False, str(error)


def validate_schema(sql_query, schema):
    """
    Checks whether referenced tables and columns exist
    in the provided schema.

    Currently designed for a single-table schema.
    """

    try:
        expression = sqlglot.parse_one(sql_query, read="postgres")
    except Exception:
        return False, "SQL could not be parsed."

    table_name = schema["table_name"]
    valid_columns = set(schema["columns"].keys())

    # Identify CTE names
    cte_names = {cte.alias_or_name.lower() for cte in expression.find_all(exp.CTE)}

    # Check table references
    for table in expression.find_all(exp.Table):

        referenced_table = table.name.lower()

        # Allow the actual database table and defined CTEs
        if referenced_table != table_name.lower() and referenced_table not in cte_names:
            return (False, f"Unknown table referenced: {referenced_table}")

    # Collect aliases defined in SELECT statements
    valid_aliases = set()

    for select in expression.find_all(exp.Select):
        for projection in select.expressions:
            if isinstance(projection, exp.Alias):
                valid_aliases.add(projection.alias)

    # Check column references
    for column in expression.find_all(exp.Column):

        column_name = column.name

        # Ignore wildcard
        if column_name == "*":
            continue

        # Ignore valid SELECT aliases
        if column_name in valid_aliases:
            continue

        if column_name not in valid_columns:
            return (False, f"Unknown column referenced: {column_name}")

    return True, None


def validate_sql(sql_query, schema):
    """
    Performs complete SQL validation.
    """

    sql_query = clean_sql_response(sql_query)

    if not sql_query:
        return {
            "valid": False,
            "query_type": "UNKNOWN",
            "syntax_valid": False,
            "schema_valid": False,
            "message": "No SQL query was generated.",
        }

    query_type = classify_sql(sql_query)

    if query_type == "UNKNOWN":
        return {
            "valid": False,
            "query_type": "UNKNOWN",
            "syntax_valid": False,
            "schema_valid": False,
            "message": "Only a single read-only SELECT query is allowed.",
        }

    syntax_valid, syntax_error = validate_sql_syntax(sql_query)

    if not syntax_valid:
        return {
            "valid": False,
            "query_type": query_type,
            "syntax_valid": False,
            "schema_valid": False,
            "message": f"Invalid SQL syntax: {syntax_error}",
        }

    schema_valid, schema_error = validate_schema(sql_query, schema)

    if not schema_valid:
        return {
            "valid": False,
            "query_type": query_type,
            "syntax_valid": True,
            "schema_valid": False,
            "message": schema_error,
        }

    return {
        "valid": True,
        "query_type": query_type,
        "syntax_valid": True,
        "schema_valid": True,
        "message": "SQL query is valid.",
    }
