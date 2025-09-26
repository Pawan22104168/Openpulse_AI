import sqlparse
from sqlparse.sql import IdentifierList, Identifier
from sqlparse.tokens import Keyword, DML
from typing import List

def extract_tables(sql_query: str) -> List[str]:
    """
    Extract table names from a SQL query.
    """
    parsed = sqlparse.parse(sql_query)
    tables = []

    for stmt in parsed:
        for token in stmt.tokens:
            if token.ttype is DML and token.value.upper() == "SELECT":
                # Look for identifiers after SELECT
                from_seen = False
                for t in stmt.tokens:
                    if from_seen:
                        if isinstance(t, IdentifierList):
                            for identifier in t.get_identifiers():
                                tables.append(identifier.get_real_name())
                        elif isinstance(t, Identifier):
                            tables.append(t.get_real_name())
                        break
                    if t.ttype is Keyword and t.value.upper() == "FROM":
                        from_seen = True
    return list(set(tables))


def is_select_query(sql_query: str) -> bool:
    """
    Check if the query is a SELECT statement.
    """
    parsed = sqlparse.parse(sql_query)
    if not parsed:
        return False
    stmt = parsed[0]
    return stmt.get_type() == "SELECT"


def clean_query(sql_query: str) -> str:
    """
    Remove extra whitespace and semicolons.
    """
    return sqlparse.format(sql_query, strip_comments=True, reindent=True).strip().rstrip(";")
