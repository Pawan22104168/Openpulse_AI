from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

@router.get("/health", tags=["health"])
def health_check():
    """
    Simple health check endpoint.
    Returns OK status and timestamp.
    """
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
