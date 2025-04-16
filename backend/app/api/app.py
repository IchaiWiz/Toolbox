"""
Configuration de l'application FastAPI
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import httpx
from fastapi.responses import JSONResponse
import logging
import time

# Importer les routeurs spécifiquement
from ..routes.copy import router as copy_router
from ..routes.duplicate_detection import router as duplicate_detection_router
from ..routes.winmerge import router as winmerge_router
from ..routes.ai_structure import router as ai_structure_router
from ..routes.analyse import router as analyse_router
from ..routes.backup import router as backup_router
from .endpoints import health_router

# Configuration du logger
logger = logging.getLogger("toolbox.api")

def create_app() -> FastAPI:
    """
    Crée et configure l'application FastAPI
    
    Returns:
        Application FastAPI configurée
    """
    logger.info("Création de l'application FastAPI")
    
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

    # Middleware pour logger les requêtes
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start_time = time.time()
        
        # Générer un ID unique pour la requête
        request_id = f"{int(start_time * 1000)}"
        
        # Logger le début de la requête
        logger.info(f"[{request_id}] Début de la requête {request.method} {request.url.path}")
        
        try:
            # Exécuter la requête
            response = await call_next(request)
            
            # Calculer la durée
            process_time = (time.time() - start_time) * 1000
            logger.info(f"[{request_id}] Fin de la requête {request.method} {request.url.path} - Status: {response.status_code} - Durée: {process_time:.2f}ms")
            
            return response
        except Exception as e:
            # En cas d'erreur pendant le traitement
            process_time = (time.time() - start_time) * 1000
            logger.error(f"[{request_id}] Erreur lors de la requête {request.method} {request.url.path} - Durée: {process_time:.2f}ms - {str(e)}")
            
            return JSONResponse(
                status_code=500,
                content={"detail": "Erreur interne du serveur"}
            )
    
    # Gestion globale des exceptions non gérées
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Exception non gérée: {request.method} {request.url.path} - {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": f"Erreur interne du serveur: {str(exc)}"}
        )

    # Inclure les routeurs
    app.include_router(copy_router)
    app.include_router(duplicate_detection_router)
    app.include_router(winmerge_router)
    app.include_router(ai_structure_router)
    app.include_router(analyse_router)
    app.include_router(backup_router)
    
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
            # "/api/v1/analyse/health",
            # "/api/v1/backup/health", 
            "/api/v1/copy/health",
            # "/api/v1/winmerge/health",
            # "/api/v1/duplicate/health",
            # "/api/v1/ai-structure/health"
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
    
    logger.info("Application FastAPI créée et configurée")
    return app 