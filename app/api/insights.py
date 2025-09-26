from fastapi import APIRouter, HTTPException
from typing import Dict
from app.models.metadata import Dashboard
from app.core.metadata_extractor import fetch_dashboard_metadata, build_training_documents
from app.core.training_pack import build_training_pack
from app.core.schema_analyzer import analyze_schema
from app.llm.vector_store import VectorStore
from app.llm.langchain_agent import RAGAgent
from app.llm.embeddings import get_embedding
from app.sql.executor import execute_sql_dynamic
from app.config import settings

router = APIRouter()

# Initialize VectorStore & RAGAgent once (singleton)
vector_store = VectorStore(persist_path=settings.VECTOR_STORE_PATH)
rag_agent = RAGAgent(vector_store=vector_store)


@router.get("/insights/{dashboard_id}", response_model=Dict)
def get_dashboard_insights(dashboard_id: int):
    """
    Fetch dashboard metadata, build training pack, run RAG agent,
    execute SQL dynamically, and return results + natural-language insight.
    """
    # -----------------------------
    # Step 1: Fetch metadata from Superset
    # -----------------------------
    try:
        metadata_dict = fetch_dashboard_metadata(dashboard_id)
        dashboard = Dashboard(**metadata_dict)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error fetching dashboard metadata: {str(e)}")

    # -----------------------------
    # Step 2: Build training pack & schema analysis
    # -----------------------------
    training_pack = build_training_pack(metadata_dict)
    schema_analysis = analyze_schema(dashboard.datasets)

    # -----------------------------
    # Step 3: Add training pack documents to Vector Store
    # -----------------------------
    for chart_sql in training_pack.get("chart_sqls", []):
        doc_text = chart_sql.get("sql", "")
        doc_id = f"chart_{chart_sql['chart_id']}"
        embedding = get_embedding(doc_text)
        vector_store.add_document(doc_id=doc_id, text=doc_text, embedding=embedding)
    vector_store.persist()

    # -----------------------------
    # Step 4: Generate insight using RAG agent
    # -----------------------------
    try:
        sql_query, insight_text = rag_agent.generate_insight(metadata_dict)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating insight: {str(e)}")

    # -----------------------------
    # Step 5: Execute SQL dynamically using dataset's DB URI
    # -----------------------------
    dataset_doc = next((d for d in build_training_documents(dashboard_id) if d.get("sqlalchemy_uri")), None)
    if not dataset_doc:
        raise HTTPException(status_code=400, detail="No dataset with database connection found")

    dataset_uri = dataset_doc["sqlalchemy_uri"]

    try:
        query_results = execute_sql_dynamic(sql_query, sqlalchemy_uri=dataset_uri, limit=50, timeout=15)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing SQL: {str(e)}")

    return {
        "dashboard_id": dashboard_id,
        "sql": sql_query,
        "insight": insight_text,
        "rows": query_results
    }
