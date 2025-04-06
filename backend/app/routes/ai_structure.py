from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import json

from ..services.ai_structure_service import analyze_directory_structure, get_analysis_status
from ..utils.path_utils import is_valid_directory, sanitize_path

router = APIRouter(
    prefix="/api/v1/ai-structure",
    tags=["AI Structure"],
    responses={404: {"description": "Non trouvé"}},
)


class AnalyzeRequest(BaseModel):
    directory_path: str = Field(..., description="Chemin du répertoire à analyser")
    recursive: bool = Field(True, description="Analyse récursive des sous-dossiers")
    include_hidden: bool = Field(False, description="Inclure les fichiers et dossiers cachés")
    max_depth: int = Field(5, description="Profondeur maximale d'analyse (0 = illimité)")


class AnalyzeResponse(BaseModel):
    analysis_id: str = Field(..., description="Identifiant unique de l'analyse")
    status: str = Field(..., description="État de l'analyse")
    message: str = Field(..., description="Message informatif")


@router.post("/analyze", response_model=AnalyzeResponse)
async def start_structure_analysis(background_tasks: BackgroundTasks, request: AnalyzeRequest):
    """
    Démarre une analyse de structure de répertoire avec IA
    """
    directory = sanitize_path(request.directory_path)
    
    if not is_valid_directory(directory):
        raise HTTPException(status_code=404, detail=f"Le répertoire {directory} n'existe pas ou n'est pas accessible")
    
    # Valider les paramètres
    if request.max_depth < 0:
        raise HTTPException(status_code=400, detail="La profondeur maximale ne peut pas être négative")
    
    # Lancer l'analyse en arrière-plan
    analysis_id = analyze_directory_structure(
        directory,
        request.recursive,
        request.include_hidden,
        request.max_depth,
        background=True
    )
    
    return {
        "analysis_id": analysis_id,
        "status": "en_cours",
        "message": f"Analyse démarrée sur {directory}"
    }


@router.get("/status/{analysis_id}")
async def check_analysis_status(analysis_id: str):
    """
    Vérifie l'état d'une analyse en cours ou terminée
    """
    status = get_analysis_status(analysis_id)
    if status is None:
        raise HTTPException(status_code=404, detail=f"Analyse avec ID {analysis_id} non trouvée")
    
    return status


@router.post("/suggest-improvements/{analysis_id}")
async def suggest_improvements(analysis_id: str):
    """
    Génère des suggestions d'amélioration pour une structure de répertoire 
    basées sur l'analyse précédente.
    """
    status = get_analysis_status(analysis_id)
    if status is None:
        raise HTTPException(status_code=404, detail=f"Analyse avec ID {analysis_id} non trouvée")
    
    if status["status"] != "terminé":
        raise HTTPException(status_code=400, detail="L'analyse n'est pas encore terminée")
    
    # Dans une version réelle, nous utiliserions une IA pour analyser la structure
    # et faire des recommandations. Pour cet exemple, nous retournons des suggestions fictives.
    
    # On simule des suggestions basées sur quelques règles simples
    structure = status.get("structure", {})
    file_count = status.get("stats", {}).get("file_count", 0)
    dir_count = status.get("stats", {}).get("dir_count", 0)
    
    suggestions = []
    
    # Quelques règles de base pour générer des suggestions
    if file_count > 100 and dir_count < 5:
        suggestions.append({
            "type": "organization",
            "severity": "high",
            "message": "Le répertoire contient beaucoup de fichiers mais peu de dossiers. Considérez regrouper les fichiers par catégorie."
        })
    
    if "node_modules" in json.dumps(structure) or "vendor" in json.dumps(structure):
        suggestions.append({
            "type": "dependencies",
            "severity": "medium",
            "message": "Des répertoires de dépendances ont été détectés. Assurez-vous qu'ils sont exclus des sauvegardes et du contrôle de version."
        })
    
    if file_count > 0:
        suggestions.append({
            "type": "generic",
            "severity": "low",
            "message": "Envisagez d'ajouter un fichier README.md pour documenter la structure du projet."
        })
    
    return {
        "analysis_id": analysis_id,
        "suggestions": suggestions,
        "message": f"Généré {len(suggestions)} suggestions d'amélioration"
    }


@router.get("/health")
async def health_check():
    """
    Vérifie l'état de l'API d'analyse de structure
    """
    return {"status": "ok", "service": "ai_structure"} 