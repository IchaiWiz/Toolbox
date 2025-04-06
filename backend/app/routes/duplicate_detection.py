from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from ..services.duplicate_detection_service import find_duplicates, get_scan_status
from ..utils.path_utils import is_valid_directory, sanitize_path

router = APIRouter(
    prefix="/api/v1/duplicate",
    tags=["Duplicate Detection"],
    responses={404: {"description": "Non trouvé"}},
)


class ScanRequest(BaseModel):
    directory_path: str = Field(..., description="Chemin du répertoire à analyser")
    recursive: bool = Field(True, description="Analyse récursive des sous-dossiers")
    include_hidden: bool = Field(False, description="Inclure les fichiers cachés")
    min_size: int = Field(1024, description="Taille minimale des fichiers à considérer (octets)")
    methods: List[str] = Field(["size", "hash"], description="Méthodes de détection (size, hash, content)")


class ScanResponse(BaseModel):
    scan_id: str = Field(..., description="Identifiant unique de l'analyse")
    status: str = Field(..., description="État de l'analyse (en cours, terminée, erreur)")
    message: str = Field(..., description="Message informatif")


@router.post("/scan", response_model=ScanResponse)
async def start_duplicate_scan(background_tasks: BackgroundTasks, request: ScanRequest):
    """
    Démarre une analyse pour trouver des fichiers en double
    """
    directory = sanitize_path(request.directory_path)
    
    if not is_valid_directory(directory):
        raise HTTPException(status_code=404, detail=f"Le répertoire {directory} n'existe pas ou n'est pas accessible")
    
    # Valider les méthodes de détection
    valid_methods = ["size", "hash", "content"]
    for method in request.methods:
        if method not in valid_methods:
            raise HTTPException(
                status_code=400, 
                detail=f"Méthode de détection '{method}' non valide. Valeurs acceptées: {valid_methods}"
            )
    
    # Démarrer l'analyse en arrière-plan
    scan_id = find_duplicates(
        directory,
        request.recursive,
        request.include_hidden,
        request.min_size,
        request.methods,
        background=True
    )
    
    return {
        "scan_id": scan_id,
        "status": "en_cours",
        "message": f"Analyse démarrée sur {directory}"
    }


@router.get("/status/{scan_id}")
async def check_scan_status(scan_id: str):
    """
    Vérifie l'état d'une analyse en cours ou terminée
    """
    status = get_scan_status(scan_id)
    if status is None:
        raise HTTPException(status_code=404, detail=f"Analyse avec ID {scan_id} non trouvée")
    
    return status


@router.post("/quick_scan")
async def quick_duplicate_scan(
    directory_path: str = Query(..., description="Chemin du répertoire à analyser"),
    recursive: bool = Query(True),
    min_size: int = Query(1024 * 10)  # 10KB par défaut
):
    """
    Effectue une analyse rapide pour trouver les doublons (synchrone, pour petits dossiers)
    """
    directory = sanitize_path(directory_path)
    
    if not is_valid_directory(directory):
        raise HTTPException(status_code=404, detail=f"Le répertoire {directory} n'existe pas ou n'est pas accessible")
    
    # Exécuter l'analyse de manière synchrone (pourrait être un problème pour les grands dossiers)
    scan_id = find_duplicates(
        directory,
        recursive,
        False,  # Ne pas inclure les fichiers cachés
        min_size,
        ["size", "hash"],  # Méthodes rapides
        background=False
    )
    
    # Récupérer les résultats
    results = get_scan_status(scan_id)
    
    return results


@router.get("/health")
async def health_check():
    """
    Vérifie l'état de l'API de détection de doublons
    """
    return {"status": "ok", "service": "duplicate_detection"} 