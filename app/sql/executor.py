from typing import List, Dict, Any
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError


def execute_sql_dynamic(query: str, sqlalchemy_uri: str, limit: int = 100, timeout: int = 10) -> List[Dict[str, Any]]:
    """
    Execute a SQL query safely against the given database URI.
    - Enforces LIMIT if not present
    - Enforces statement timeout
    - Returns list of rows as dictionaries
    """
    # Add LIMIT if not present
    if "limit" not in query.lower():
        query = f"{query.rstrip(';')} LIMIT {limit}"

    results: List[Dict[str, Any]] = []
    engine = create_engine(sqlalchemy_uri, connect_args={"options": f"-c statement_timeout={timeout*1000}"})

    try:
        with engine.connect() as conn:
            result_proxy = conn.execute(text(query))
            results = [dict(row) for row in result_proxy]
    except SQLAlchemyError as e:
        raise RuntimeError(f"SQL execution error: {str(e)}")
    finally:
        engine.dispose()

    return results
