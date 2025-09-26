from app.db.cache import redis_client
from app.llm.vector_store import VectorStore
from app.config import settings

# Singleton VectorStore instance
vector_store_instance = VectorStore(persist_path=settings.VECTOR_STORE_PATH)

def get_vector_store():
    return vector_store_instance

def get_redis_client():
    return redis_client
