from typing import Dict, List
from app.llm.vector_store import VectorStore
from app.llm.embeddings import get_embedding
from app.config import settings
import requests
import json

SUPSERSET_API_BASE = settings.SUPERSET_BASE_URL + "/api/v1"  # e.g., http://localhost:8088/api/v1
SUPERSET_API_KEY = settings.SUPERSET_API_KEY    # Bearer token

vector_store = VectorStore(persist_path=settings.VECTOR_STORE_PATH)


def fetch_dashboard_metadata(dashboard_id: int) -> Dict:
    """
    Fetch dashboard metadata from Superset API
    """
    headers = {"Authorization": f"Bearer {SUPERSET_API_KEY}"}
    url = f"{SUPSERSET_API_BASE}/dashboard/{dashboard_id}"
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        raise Exception(f"Failed to fetch dashboard {dashboard_id}: {resp.text}")
    return resp.json()


def fetch_dataset_details(dataset_id: int) -> Dict:
    """
    Fetch dataset metadata from Superset API
    Includes database connection info for dynamic SQL execution
    """
    headers = {"Authorization": f"Bearer {SUPERSET_API_KEY}"}
    url = f"{SUPSERSET_API_BASE}/dataset/{dataset_id}"
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        raise Exception(f"Failed to fetch dataset {dataset_id}: {resp.text}")
    data = resp.json()
    # Extract SQLAlchemy URI for execution
    sqlalchemy_uri = data.get("database", {}).get("sqlalchemy_uri")
    data["sqlalchemy_uri"] = sqlalchemy_uri
    return data


def build_training_documents(dashboard_metadata: Dict) -> List[Dict]:
    """
    Build training documents from dashboard metadata for Vector Store
    Each document is a dict: {"id": str, "text": str, "embedding": List[float]}
    Also attach sqlalchemy_uri to dataset docs for executor
    """
    docs = []
    dashboard_id = dashboard_metadata.get("id")
    charts = dashboard_metadata.get("charts", [])
    datasets = dashboard_metadata.get("datasets", [])

    # Add dashboard-level doc
    dashboard_text = json.dumps({"dashboard_id": dashboard_id, "charts": [c["id"] for c in charts]})
    docs.append({
        "id": f"dashboard-{dashboard_id}",
        "text": dashboard_text,
        "embedding": get_embedding(dashboard_text)
    })

    # Add charts
    for chart in charts:
        chart_text = json.dumps(chart)
        docs.append({
            "id": f"chart-{chart['id']}",
            "text": chart_text,
            "embedding": get_embedding(chart_text)
        })

    # Add datasets with sqlalchemy_uri
    for dataset in datasets:
        dataset_id = dataset["id"]
        dataset_details = fetch_dataset_details(dataset_id)
        dataset_text = json.dumps(dataset_details)
        docs.append({
            "id": f"dataset-{dataset_id}",
            "text": dataset_text,
            "embedding": get_embedding(dataset_text),
            "sqlalchemy_uri": dataset_details.get("sqlalchemy_uri")
        })

    return docs


def ingest_dashboard(dashboard_id: int):
    """
    Full ingestion pipeline: fetch metadata → build docs → store embeddings
    """
    metadata = fetch_dashboard_metadata(dashboard_id)
    docs = build_training_documents(metadata)
    for doc in docs:
        vector_store.add_document(doc["id"], doc["text"], doc["embedding"])
    vector_store.persist()
    print(f"Ingested {len(docs)} documents for dashboard {dashboard_id}")
