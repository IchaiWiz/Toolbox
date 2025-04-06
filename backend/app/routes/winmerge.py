from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import os
import subprocess
import platform
from pathlib import Path

from ..utils.path_utils import sanitize_path, is_valid_directory
from ..services.winmerge_service import compare_directories, compare_files

router = APIRouter(
    prefix="/api/v1/winmerge",
    tags=["WinMerge"],
    responses={404: {"description": "Non trouvé"}},
)


class CompareRequest(BaseModel):
    left_path: str = Field(..., description="Chemin du fichier ou dossier gauche")
    right_path: str = Field(..., description="Chemin du fichier ou dossier droit")
    recursive: bool = Field(True, description="Comparer les sous-dossiers (uniquement pour les dossiers)")
    show_identical: bool = Field(False, description="Afficher les fichiers identiques")


class CompareResult(BaseModel):
    differences: int = Field(..., description="Nombre de différences trouvées")
    identical: int = Field(..., description="Nombre de fichiers identiques")
    left_only: int = Field(..., description="Nombre de fichiers uniquement à gauche")
    right_only: int = Field(..., description="Nombre de fichiers uniquement à droite")
    details: List[Dict[str, Any]] = Field(..., description="Détails des différences")


@router.post("/compare", response_model=CompareResult)
async def compare_paths(request: CompareRequest):
    """
    Compare deux fichiers ou dossiers et retourne un rapport détaillé
    """
    left = sanitize_path(request.left_path)
    right = sanitize_path(request.right_path)
    
    left_path = Path(left)
    right_path = Path(right)
    
    if not left_path.exists():
        raise HTTPException(status_code=404, detail=f"Le chemin gauche {left} n'existe pas")
        
    if not right_path.exists():
        raise HTTPException(status_code=404, detail=f"Le chemin droit {right} n'existe pas")
    
    # Vérifier si ce sont des fichiers ou des répertoires
    if left_path.is_file() and right_path.is_file():
        # Comparer des fichiers
        result = compare_files(left, right)
    elif left_path.is_dir() and right_path.is_dir():
        # Comparer des répertoires
        result = compare_directories(left, right, request.recursive, request.show_identical)
    else:
        raise HTTPException(
            status_code=400, 
            detail="Les deux chemins doivent être du même type (deux fichiers ou deux dossiers)"
        )
    
    return result


@router.post("/launch")
async def launch_winmerge(
    left_path: str = Body(..., embed=True),
    right_path: str = Body(..., embed=True)
):
    """
    Lance WinMerge pour comparer deux fichiers ou dossiers (uniquement sous Windows).
    
    Cette fonction tente de lancer l'application WinMerge si elle est installée.
    """
    if platform.system() != "Windows":
        raise HTTPException(
            status_code=400,
            detail="Cette fonctionnalité n'est disponible que sous Windows"
        )
    
    left = sanitize_path(left_path)
    right = sanitize_path(right_path)
    
    # Chemins possibles pour WinMerge
    winmerge_paths = [
        "C:\\Program Files\\WinMerge\\WinMergeU.exe",
        "C:\\Program Files (x86)\\WinMerge\\WinMergeU.exe",
    ]
    
    winmerge_exe = None
    for path in winmerge_paths:
        if os.path.exists(path):
            winmerge_exe = path
            break
    
    if not winmerge_exe:
        return {
            "success": False,
            "message": "WinMerge n'est pas installé ou n'a pas été trouvé dans les emplacements standards"
        }
    
    try:
        # Lancer WinMerge avec les deux chemins
        subprocess.Popen([winmerge_exe, left, right])
        return {
            "success": True,
            "message": f"WinMerge a été lancé pour comparer {left} et {right}"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Erreur lors du lancement de WinMerge: {str(e)}"
        }


@router.get("/health")
async def health_check():
    """
    Vérifie l'état de l'API WinMerge
    """
    return {"status": "ok", "service": "winmerge"} 