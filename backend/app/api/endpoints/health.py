"""
Routes pour vérifier l'état de santé de l'API.
"""
from fastapi import APIRouter

router = APIRouter(
    prefix="/api/health",
    tags=["Health"],
)

@router.get("/")
async def health_check():
    """
    Vérifie l'état de santé général de l'API.
    """
    return {"status": "ok", "service": "api"} 