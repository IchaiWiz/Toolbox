from fastapi import APIRouter, HTTPException, Body, BackgroundTasks
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import datetime

from ..services.backup_service import create_backup, get_backup_status, get_backup_list, restore_backup
from ..utils.path_utils import is_valid_directory, sanitize_path

router = APIRouter(
    prefix="/api/v1/backup",
    tags=["Backup"],
    responses={404: {"description": "Non trouvé"}},
)


class BackupRequest(BaseModel):
    source_directory: str = Field(..., description="Chemin du répertoire source à sauvegarder")
    destination_directory: str = Field(..., description="Chemin du répertoire de destination pour la sauvegarde")
    backup_name: Optional[str] = Field(None, description="Nom de la sauvegarde (sinon généré automatiquement)")
    include_hidden: bool = Field(False, description="Inclure les fichiers cachés")
    compression: bool = Field(True, description="Compresser la sauvegarde")


class BackupResponse(BaseModel):
    backup_id: str = Field(..., description="Identifiant unique de la sauvegarde")
    status: str = Field(..., description="État de la sauvegarde (en cours, terminée, erreur)")
    message: str = Field(..., description="Message informatif")


@router.post("/create", response_model=BackupResponse)
async def start_backup(background_tasks: BackgroundTasks, request: BackupRequest):
    """
    Démarre une sauvegarde en arrière-plan
    """
    source = sanitize_path(request.source_directory)
    destination = sanitize_path(request.destination_directory)
    
    if not is_valid_directory(source):
        raise HTTPException(status_code=404, detail=f"Le répertoire source {source} n'existe pas ou n'est pas accessible")
        
    if not is_valid_directory(destination):
        raise HTTPException(status_code=404, detail=f"Le répertoire de destination {destination} n'existe pas ou n'est pas accessible")
    
    # Générer un nom de sauvegarde si non fourni
    backup_name = request.backup_name
    if not backup_name:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        folder_name = source.rstrip("/\\").split("/")[-1]
        backup_name = f"backup_{folder_name}_{timestamp}"
    
    # Lancer la sauvegarde en arrière-plan
    backup_id = f"bkp_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    background_tasks.add_task(
        create_backup,
        backup_id,
        source,
        destination,
        backup_name,
        request.include_hidden,
        request.compression
    )
    
    return {
        "backup_id": backup_id,
        "status": "en_cours",
        "message": f"Sauvegarde {backup_name} démarrée"
    }


@router.get("/status/{backup_id}")
async def check_backup_status(backup_id: str):
    """
    Vérifie l'état d'une sauvegarde en cours ou terminée
    """
    status = get_backup_status(backup_id)
    if status is None:
        raise HTTPException(status_code=404, detail=f"Sauvegarde avec ID {backup_id} non trouvée")
    
    return status


@router.get("/list/{directory_path:path}")
async def list_backups(directory_path: str):
    """
    Liste les sauvegardes disponibles dans un répertoire
    """
    directory = sanitize_path(directory_path)
    
    if not is_valid_directory(directory):
        raise HTTPException(status_code=404, detail=f"Le répertoire {directory} n'existe pas ou n'est pas accessible")
        
    try:
        backups = get_backup_list(directory)
        return {"backups": backups}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des sauvegardes: {str(e)}")


@router.post("/restore")
async def start_restore(
    background_tasks: BackgroundTasks,
    backup_path: str = Body(..., embed=True),
    destination: str = Body(..., embed=True),
    overwrite: bool = Body(False, embed=True)
):
    """
    Restaure une sauvegarde vers une destination
    """
    backup_path = sanitize_path(backup_path)
    destination = sanitize_path(destination)
    
    if not is_valid_directory(destination):
        raise HTTPException(status_code=404, detail=f"Le répertoire de destination {destination} n'existe pas ou n'est pas accessible")
    
    restore_id = f"restore_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    background_tasks.add_task(
        restore_backup,
        restore_id,
        backup_path,
        destination,
        overwrite
    )
    
    return {
        "restore_id": restore_id,
        "status": "en_cours",
        "message": "Restauration démarrée"
    }


@router.get("/health")
async def health_check():
    """
    Vérifie l'état de l'API de sauvegarde
    """
    return {"status": "ok", "service": "backup"} 