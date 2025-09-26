from typing import Dict, Tuple
from app.llm.vector_store import VectorStore
from app.llm.embeddings import get_embedding
from app.config import settings
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch

class RAGAgent:
    """
    Retriever-Augmented Generation agent.
    Combines Vector Store retrieval with local LLM to generate SQL + insights.
    """

    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store
        self.model_name = settings.LLM_MODEL_NAME
        self.tokenizer, self.model = self._load_llm()
        # HuggingFace pipeline for text generation
        self.generator = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            device=0 if torch.cuda.is_available() else -1
        )

    def _load_llm(self):
        tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        model = AutoModelForCausalLM.from_pretrained(self.model_name)
        model.eval()
        return tokenizer, model

    def generate_insight(self, dashboard_metadata: Dict) -> Tuple[str, str]:
        """
        Generate a SQL candidate and natural-language insight for a dashboard.
        Steps:
        1. Retrieve relevant charts/datasets from vector store
        2. Construct prompt
        3. Use LLM to generate SQL + insight
        """
        dashboard_id = dashboard_metadata.get("dashboard", {}).get("id")
        if not dashboard_id:
            raise ValueError("Dashboard metadata missing 'id'")

        # --- Step 1: Retrieve relevant docs
        query_text = f"Generate SQL and insight for dashboard {dashboard_id}"
        top_docs = self.vector_store.query(query_text, top_k=5)
        context_text = "\n".join([doc["text"] for doc in top_docs])

        # --- Step 2: Construct prompt
        prompt = f"""
        You are a SQL expert and data analyst.
        Based on the following dashboard metadata, generate:
        1. A single SQL query that could answer key metrics.
        2. A brief natural-language insight.
        Only produce syntactically correct SQL and a short insight.

        Context:
        {context_text}

        Response format:
        SQL:
        <your SQL here>

        Insight:
        <short insight here>
        """

        # --- Step 3: Generate using LLM
        response = self.generator(prompt, max_length=1024, do_sample=False)[0]["generated_text"]

        # --- Step 4: Parse response
        sql = ""
        insight = ""
        if "SQL:" in response and "Insight:" in response:
            try:
                sql = response.split("SQL:")[1].split("Insight:")[0].strip()
                insight = response.split("Insight:")[1].strip()
            except Exception:
                sql = response.strip()
                insight = "Insight could not be extracted."
        else:
            sql = response.strip()
            insight = "Insight could not be extracted."

        return sql, insight
