import sqlparse
from sqlparse.sql import IdentifierList, Identifier
from sqlparse.tokens import Keyword, DML

READ_ONLY_COMMANDS = {"SELECT", "WITH"}

FORBIDDEN_COMMANDS = {"INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE", "CREATE"}


def validate_sql(sql: str) -> tuple[bool, str]:
    """
    Validate SQL query:
    1. Must be read-only
    2. No forbidden commands
    3. Returns (is_valid: bool, message: str)
    """
    if not sql or not sql.strip():
        return False, "SQL query is empty"

    statements = sqlparse.parse(sql)
    for stmt in statements:
        # Identify the first keyword
        first_token = stmt.token_first(skip_cm=True)
        if first_token is None:
            continue

        if first_token.ttype is Keyword or first_token.ttype is DML:
            command = first_token.value.upper()
            if command in FORBIDDEN_COMMANDS:
                return False, f"Forbidden SQL command detected: {command}"
            if command not in READ_ONLY_COMMANDS:
                return False, f"Only read-only SQL allowed. Found: {command}"

    # Optional: enforce LIMIT clause
    if "LIMIT" not in sql.upper():
        return False, "SQL query missing LIMIT clause"

    return True, "SQL is valid"
