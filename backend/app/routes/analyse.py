from fastapi import APIRouter, HTTPException, Query, Path
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import os
from pathlib import Path as FilePath

from ..services.analyse_service import get_directory_stats, analyse_file_types
from ..utils.path_utils import is_valid_directory, sanitize_path

router = APIRouter(
    prefix="/api/v1/analyse",
    tags=["Analyse"],
    responses={404: {"description": "Non trouvé"}},
)


class AnalyseRequest(BaseModel):
    directory_path: str = Field(..., description="Chemin du répertoire à analyser")
    include_hidden: bool = Field(False, description="Inclure les fichiers cachés")
    recursive: bool = Field(False, description="Analyse récursive des sous-dossiers")


class AnalyseResponse(BaseModel):
    total_size: int = Field(..., description="Taille totale en octets")
    total_size_human: str = Field(..., description="Taille totale formatée")
    file_count: int = Field(..., description="Nombre de fichiers")
    dir_count: int = Field(..., description="Nombre de dossiers")
    file_types: Dict[str, int] = Field(..., description="Types de fichiers et leur nombre")
    largest_files: List[Dict[str, Any]] = Field(..., description="Les plus grands fichiers")
    newest_files: List[Dict[str, Any]] = Field(..., description="Les fichiers les plus récents")


@router.post("/directory", response_model=AnalyseResponse)
async def analyse_directory(request: AnalyseRequest):
    """
    Analyse un répertoire et retourne des statistiques détaillées
    """
    directory = sanitize_path(request.directory_path)
    
    if not is_valid_directory(directory):
        raise HTTPException(status_code=404, detail=f"Le répertoire {directory} n'existe pas ou n'est pas accessible")
        
    try:
        stats = get_directory_stats(directory, request.include_hidden, request.recursive)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'analyse: {str(e)}")


@router.get("/extensions/{directory_path:path}")
async def get_extension_stats(
    directory_path: str = Path(..., description="Chemin du répertoire à analyser"),
    recursive: bool = Query(False, description="Analyse récursive des sous-dossiers")
):
    """
    Retourne des statistiques sur les extensions de fichiers dans un répertoire
    """
    directory = sanitize_path(directory_path)
    
    if not is_valid_directory(directory):
        raise HTTPException(status_code=404, detail=f"Le répertoire {directory} n'existe pas ou n'est pas accessible")
        
    try:
        stats = analyse_file_types(directory, recursive)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'analyse: {str(e)}")


@router.get("/health")
async def health_check():
    """
    Vérifie l'état de l'API d'analyse
    """
    return {"status": "ok", "service": "analyse"} 