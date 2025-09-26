from fastapi import FastAPI, HTTPException
from app.models.insights import InsightsRequest, InsightsResponse, SQLResultRow
from app.llm.vector_store import VectorStore
from app.llm.langchain_agent import RAGAgent
from app.sql.validator import validate_sql
from app.sql.executor import execute_sql
from app.config import settings

# Initialize FastAPI
app = FastAPI(
    title="Superset Insights Service",
    description="Generates SQL and natural-language insights for Superset dashboards",
    version="1.0.0"
)

# Initialize Vector Store and RAG Agent
vector_store = VectorStore(persist_path=settings.VECTOR_STORE_PATH)
rag_agent = RAGAgent(vector_store=vector_store)


@app.post("/insights", response_model=InsightsResponse)
def generate_insights(request: InsightsRequest):
    """
    Generate SQL and insight for a given Superset dashboard ID.
    """
    dashboard_id = request.dashboard_id

    # Step 1: Retrieve dashboard metadata from vector store
    # (Assumes metadata already ingested)
    top_docs = vector_store.query(f"Dashboard ID: {dashboard_id}", top_k=5)
    if not top_docs:
        raise HTTPException(status_code=404, detail=f"No metadata found for dashboard {dashboard_id}")

    dashboard_metadata = {
        "dashboard": {"id": dashboard_id},
        "charts": [eval(doc["text"]) for doc in top_docs if "chart" in doc["id"]],
        "datasets": [eval(doc["text"]) for doc in top_docs if "dataset" in doc["id"]]
    }

    # Step 2: Generate SQL + insight via RAG agent
    try:
        sql, insight = rag_agent.generate_insight(dashboard_metadata)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM generation error: {str(e)}")

    # Step 3: Validate SQL
    is_valid, message = validate_sql(sql)
    if not is_valid:
        raise HTTPException(status_code=400, detail=f"SQL validation failed: {message}")

    # Step 4: Execute SQL in Postgres
    try:
        results_raw = execute_sql(sql)
        results = [SQLResultRow(data=row) for row in results_raw]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SQL execution error: {str(e)}")

    return InsightsResponse(
        dashboard_id=dashboard_id,
        sql=sql,
        insight=insight,
        results=results
    )


@app.get("/health")
def health_check():
    """
    Health check endpoint
    """
    return {"status": "ok"}
