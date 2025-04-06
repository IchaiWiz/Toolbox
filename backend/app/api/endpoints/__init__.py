"""
Endpoints communs de l'API.
"""
from .health import router as health_router

__all__ = ["health_router"] 