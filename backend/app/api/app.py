"""
Configuration de l'application FastAPI
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import httpx
from fastapi.responses import JSONResponse

from ..routes import analyse, backup, copy, winmerge, duplicate_detection, ai_structure
from .endpoints import health_router


def create_app() -> FastAPI:
    """
    Crée et configure l'application FastAPI
    
    Returns:
        Application FastAPI configurée
    """
    app = FastAPI(
        title="ToolBox API",
        description="API pour l'application ToolBox",
        version="0.1.0"
    )

    # Configuration CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # En production, spécifiez les origines exactes
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Inclure les routeurs sans le préfixe /api car ils ont déjà leurs propres préfixes
    app.include_router(analyse)
    app.include_router(backup)
    app.include_router(copy)
    app.include_router(winmerge)
    app.include_router(duplicate_detection)
    app.include_router(ai_structure)
    
    # Ajouter le router de santé
    app.include_router(health_router)

    @app.get("/")
    async def root():
        return {"message": "ToolBox API est en ligne!"}

    @app.get("/api/test-all")
    async def test_all_services():
        """
        Teste toutes les routes health des différents services
        """
        base_url = "http://localhost:8000"
        services = [
            "/api/v1/analyse/health",
            "/api/v1/backup/health", 
            "/api/v1/copy/health",
            "/api/v1/winmerge/health",
            "/api/v1/duplicate/health",
            "/api/v1/ai-structure/health"
        ]
        
        results = {}
        
        async with httpx.AsyncClient() as client:
            for service_path in services:
                try:
                    response = await client.get(f"{base_url}{service_path}")
                    results[service_path] = {
                        "status": "ok" if response.status_code == 200 else "error",
                        "status_code": response.status_code,
                        "response": response.json() if response.status_code == 200 else str(response.content)
                    }
                except Exception as e:
                    results[service_path] = {
                        "status": "error",
                        "error": str(e)
                    }
        
        return JSONResponse(content=results)
    
    return app 