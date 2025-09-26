import os
from typing import List, Dict, Any
from chromadb import Client
from chromadb.config import Settings
from app.llm.embeddings import get_embedding  # We'll implement this separately

class VectorStore:
    """
    Chroma vector database wrapper for storing embeddings of dashboard metadata.
    """

    def __init__(self, persist_path: str = "./data/vector_db"):
        os.makedirs(persist_path, exist_ok=True)
        self.client = Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=persist_path
        ))
        # Collection name
        self.collection_name = "dashboard_metadata"
        self.collection = self._get_or_create_collection(self.collection_name)

    def _get_or_create_collection(self, name: str):
        if self.client.get_collection(name) is None:
            return self.client.create_collection(name)
        return self.client.get_collection(name)

    def ingest_dashboard_metadata(self, metadata: Dict[str, Any]):
        """
        Convert dashboard metadata into embeddings and store in vector DB.
        Each chart/dataset is treated as a separate document.
        """
        documents = []
        ids = []

        dashboard_id = metadata.get("dashboard", {}).get("id")
        if not dashboard_id:
            raise ValueError("Dashboard metadata missing 'id'")

        # Process charts
        for chart in metadata.get("charts", []):
            doc_text = str(chart)
            doc_id = f"dashboard_{dashboard_id}_chart_{chart.get('id')}"
            embedding = get_embedding(doc_text)
            documents.append({
                "id": doc_id,
                "text": doc_text,
                "embedding": embedding
            })
            ids.append(doc_id)

        # Process datasets
        for dataset in metadata.get("datasets", []):
            doc_text = str(dataset)
            doc_id = f"dashboard_{dashboard_id}_dataset_{dataset.get('id')}"
            embedding = get_embedding(doc_text)
            documents.append({
                "id": doc_id,
                "text": doc_text,
                "embedding": embedding
            })
            ids.append(doc_id)

        # Add to collection
        self.collection.add(
            ids=[d["id"] for d in documents],
            documents=[d["text"] for d in documents],
            embeddings=[d["embedding"] for d in documents]
        )

    def query(self, query_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve top-k relevant metadata entries for a query.
        """
        embedding = get_embedding(query_text)
        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=top_k
        )
        hits = []
        for idx, doc_id in enumerate(results['ids'][0]):
            hits.append({
                "id": doc_id,
                "text": results['documents'][0][idx],
                "distance": results['distances'][0][idx]
            })
        return hits
