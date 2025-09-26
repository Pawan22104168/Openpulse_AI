import redis
import pickle
from app.config import settings
from typing import Any, Optional

# Initialize Redis client
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    password=settings.REDIS_PASSWORD,
    decode_responses=False
)


def set_cache(key: str, value: Any, expire_seconds: int = 3600):
    """
    Store a Python object in Redis with optional expiration (default 1 hour)
    """
    serialized = pickle.dumps(value)
    redis_client.set(name=key, value=serialized, ex=expire_seconds)


def get_cache(key: str) -> Optional[Any]:
    """
    Retrieve a Python object from Redis
    """
    data = redis_client.get(key)
    if data is None:
        return None
    return pickle.loads(data)


def get_cached_query_result(query: str) -> Optional[Any]:
    """
    Convenience function for caching SQL query results
    """
    key = f"sql_cache:{hash(query)}"
    return get_cache(key)


def set_cached_query_result(query: str, result: Any, expire_seconds: int = 3600):
    """
    Store SQL query results in cache
    """
    key = f"sql_cache:{hash(query)}"
    set_cache(key, result, expire_seconds)
