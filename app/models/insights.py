from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

# ------------------------------
# Request models
# ------------------------------

class InsightsRequest(BaseModel):
    dashboard_id: int = Field(..., description="Superset dashboard ID for which insights are requested")
    query_context: Optional[str] = Field(None, description="Optional user query or context for insights generation")

# ------------------------------
# Response models
# ------------------------------

class SQLResultRow(BaseModel):
    """
    Represents a single row returned from SQL execution.
    """
    data: Dict[str, Any]

class InsightsResponse(BaseModel):
    dashboard_id: int
    sql: str = Field(..., description="Generated SQL query for the dashboard")
    insight: str = Field(..., description="Generated natural-language insight")
    results: Optional[List[SQLResultRow]] = Field(None, description="Optional SQL execution results")
