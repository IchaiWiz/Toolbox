from fastapi import APIRouter, HTTPException, Body, Query
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field
import os
import re
import logging
from pathlib import Path

from ..utils.file_utils import scan_directory, read_file_content, format_file_for_copy
from ..utils.path_utils import is_valid_directory, sanitize_path, format_path_error

# Configuration du logger
logger = logging.getLogger("toolbox.copy")

router = APIRouter(
    prefix="/api/v1/copy",
    tags=["Copy"],
    responses={404: {"description": "Non trouvé"}},
)


class AdvancedCopyRule(BaseModel):
    exclude_extensions: List[str] = Field(default=[], description="Extensions à exclure")
    exclude_patterns: List[str] = Field(default=[], description="Motifs à exclure dans les noms de fichiers")
    exclude_directories: List[str] = Field(default=[], description="Sous-dossiers à exclure")


class AdvancedCopyRequest(BaseModel):
    directories: List[str] = Field(default=[], description="Liste des dossiers à analyser")
    files: List[str] = Field(default=[], description="Liste des fichiers spécifiques")
    rules: AdvancedCopyRule = Field(default_factory=AdvancedCopyRule, description="Règles de filtrage")
    recursive: bool = Field(default=True, description="Chercher dans les sous-dossiers")


class FileMatch(BaseModel):
    path: str = Field(..., description="Chemin du fichier")
    name: str = Field(..., description="Nom du fichier")
    size: int = Field(..., description="Taille du fichier en octets")
    size_human: str = Field(default="", description="Taille du fichier formatée (Ko ou Mo)")
    extension: str = Field(..., description="Extension du fichier (sans le point)")


class PathError(BaseModel):
    original_path: str = Field(..., description="Chemin original qui a causé l'erreur")
    clean_path: str = Field(..., description="Chemin nettoyé")
    error_type: str = Field(..., description="Type d'erreur (not_found, permission, etc.)")
    message: str = Field(..., description="Message d'erreur détaillé")


class AdvancedCopyResult(BaseModel):
    matches: List[FileMatch] = Field(..., description="Fichiers correspondant aux critères")
    total_matches: int = Field(..., description="Nombre total de fichiers correspondants")
    formatted_content: str = Field(default="", description="Contenu formaté des fichiers")
    total_subdirectories: int = Field(default=0, description="Nombre total de sous-dossiers")
    invalid_paths: Optional[List[PathError]] = Field(default=None, description="Chemins invalides avec détails d'erreur")


@router.post("/advanced/scan", response_model=AdvancedCopyResult)
async def scan_for_files(request: AdvancedCopyRequest):
    """
    Scanne les fichiers selon les critères spécifiés
    """
    logger.info(f"Démarrage du scan avec {len(request.directories)} dossiers et {len(request.files)} fichiers")
    
    matches = []
    total_subdirectories = 0
    invalid_paths = []
    
    # Analyser les dossiers spécifiés
    for directory in request.directories:
        dir_path = sanitize_path(directory)
        logger.info(f"Traitement du dossier: {dir_path}")
        
        try:
            if not is_valid_directory(dir_path):
                logger.warning(f"Dossier non valide: {dir_path}")
                invalid_paths.append(format_path_error(directory, "not_found"))
                continue
                
            # Calculer le nombre total de sous-dossiers
            if request.recursive:
                try:
                    for root, dirs, _ in os.walk(dir_path, onerror=lambda e: None):
                        # Filtrer les sous-dossiers exclus
                        if request.rules.exclude_directories:
                            dirs[:] = [d for d in dirs if d not in request.rules.exclude_directories 
                                    and not any(Path(os.path.join(root, d)).match(f"**/{excluded}/**") 
                                                for excluded in request.rules.exclude_directories)]
                        
                        total_subdirectories += len(dirs)
                except Exception as walk_error:
                    # Ajouter l'erreur mais continuer l'analyse
                    logger.error(f"Erreur lors du parcours de {dir_path}: {str(walk_error)}")
                    invalid_paths.append(format_path_error(directory, f"Erreur lors du parcours: {str(walk_error)}"))
                
            # Rechercher les fichiers correspondants
            logger.info(f"Scan du dossier: {dir_path} (récursif={request.recursive})")
            scan_result = scan_directory(
                directory=dir_path,
                exclude_extensions=request.rules.exclude_extensions,
                exclude_patterns=request.rules.exclude_patterns,
                exclude_directories=request.rules.exclude_directories,
                recursive=request.recursive
            )
            
            # Récupérer les fichiers trouvés et les erreurs
            dir_matches = scan_result["files"]
            
            # Ajouter les erreurs de scan aux chemins invalides
            for error_msg in scan_result.get("errors", []):
                logger.warning(f"Erreur pendant le scan: {error_msg}")
                invalid_paths.append(format_path_error(directory, error_msg))
            
            logger.info(f"Trouvé {len(dir_matches)} fichiers dans {dir_path}")
            
            # Ajouter la taille formatée pour chaque fichier
            for match in dir_matches:
                size = match["size"]
                if size < 1024:
                    size_human = f"{size} octets"
                elif size < 1024 * 1024:
                    size_human = f"{size / 1024:.1f} Ko"
                else:
                    size_human = f"{size / (1024 * 1024):.1f} Mo"
                
                match["size_human"] = size_human
                
            matches.extend(dir_matches)
        except Exception as e:
            # Ajouter l'erreur avec le chemin formaté mais continuer avec les autres dossiers
            logger.error(f"Erreur générale lors du traitement de {dir_path}: {str(e)}")
            invalid_paths.append(format_path_error(directory, str(e)))
    
    # Ajouter les fichiers spécifiques s'ils respectent les règles
    for file_path in request.files:
        try:
            file_path = sanitize_path(file_path)
            logger.info(f"Traitement du fichier: {file_path}")
            
            file = Path(file_path)
            try:
                if not file.exists() or not file.is_file():
                    logger.warning(f"Fichier non trouvé: {file_path}")
                    invalid_paths.append(format_path_error(file_path, "not_found"))
                    continue
            except (PermissionError, OSError) as e:
                logger.error(f"Erreur d'accès au fichier {file_path}: {str(e)}")
                invalid_paths.append(format_path_error(file_path, f"Erreur d'accès: {str(e)}"))
                continue
                
            # Vérifier si le fichier correspond aux règles
            extension = file.suffix[1:] if file.suffix else ""
            filename = file.name
            
            # Vérification des extensions
            if extension in request.rules.exclude_extensions:
                logger.info(f"Fichier exclu (extension): {file_path}")
                continue
                
            # Vérification des motifs
            exclude_match = False
            if request.rules.exclude_patterns:
                exclude_match = any(re.search(pattern, filename) for pattern in request.rules.exclude_patterns)
            if exclude_match:
                logger.info(f"Fichier exclu (motif): {file_path}")
                continue
            
            # Vérification des sous-dossiers exclus
            file_is_excluded = False
            if request.rules.exclude_directories:
                file_dir = os.path.dirname(str(file))
                for excluded_dir in request.rules.exclude_directories:
                    if os.path.basename(file_dir) == excluded_dir or f"/{excluded_dir}/" in f"{file_dir}/":
                        file_is_excluded = True
                        break
            if file_is_excluded:
                logger.info(f"Fichier exclu (dossier parent): {file_path}")
                continue
                
            # Calculer la taille formatée pour ce fichier spécifique
            try:
                file_size = file.stat().st_size
                if file_size < 1024:
                    file_size_human = f"{file_size} octets"
                elif file_size < 1024 * 1024:
                    file_size_human = f"{file_size / 1024:.1f} Ko"
                else:
                    file_size_human = f"{file_size / (1024 * 1024):.1f} Mo"
                    
                # Ajouter le fichier aux résultats
                matches.append({
                    "path": str(file).replace("\\", "/"),
                    "name": filename,
                    "size": file_size,
                    "size_human": file_size_human,
                    "extension": extension
                })
                logger.info(f"Fichier ajouté aux résultats: {file_path}")
            except (PermissionError, OSError) as e:
                logger.error(f"Erreur d'accès au fichier {file_path}: {str(e)}")
                invalid_paths.append(format_path_error(file_path, f"Erreur d'accès: {str(e)}"))
        except Exception as e:
            logger.error(f"Erreur générale lors du traitement du fichier {file_path}: {str(e)}")
            invalid_paths.append(format_path_error(file_path, str(e)))
    
    logger.info(f"Scan terminé: {len(matches)} fichiers trouvés, {len(invalid_paths)} chemins invalides")
    
    result = {
        "matches": matches,
        "total_matches": len(matches),
        "formatted_content": "",
        "total_subdirectories": total_subdirectories
    }
    
    # Ajouter les erreurs de chemin s'il y en a
    if invalid_paths:
        result["invalid_paths"] = invalid_paths
    
    return result


@router.post("/advanced/format-content", response_model=AdvancedCopyResult)
async def format_files_content(request: AdvancedCopyRequest):
    """
    Récupère et formate le contenu des fichiers sélectionnés selon les critères
    """
    logger.info("Début du formatage du contenu des fichiers")
    
    # D'abord, on obtient les fichiers correspondants
    scan_result = await scan_for_files(request)
    matches = scan_result["matches"]
    total_subdirectories = scan_result["total_subdirectories"]
    invalid_paths = scan_result.get("invalid_paths", [])
    
    logger.info(f"Formatage du contenu pour {len(matches)} fichiers")
    
    # Ensuite, on récupère et formate le contenu
    formatted_content = ""
    for file_match in matches:
        file_path = file_match["path"]
        try:
            logger.info(f"Lecture du fichier: {file_path}")
            content = read_file_content(file_path)
            
            # Si le contenu commence par "[Erreur", c'est une erreur de lecture
            if content.startswith("[Erreur") or content.startswith("[Fichier non") or content.startswith("[Contenu binaire"):
                logger.warning(f"Problème lors de la lecture de {file_path}: {content}")
                formatted_content += f"=== {file_path} ({file_match['size_human']}) ===\n{content}\n\n---\n\n"
                
                # Ajouter aux chemins invalides si c'est une erreur
                if not content.startswith("[Contenu binaire"):
                    invalid_paths.append(format_path_error(file_path, content))
            else:
                formatted_content += format_file_for_copy(file_path, content, file_match["size_human"])
        except Exception as e:
            # En cas d'erreur, on mentionne le fichier qu'on n'a pas pu lire
            error_msg = f"Erreur lors de la lecture: {str(e)}"
            logger.error(f"Erreur lors de la lecture de {file_path}: {str(e)}")
            formatted_content += f"=== {file_path} ({file_match['size_human']}) ===\n{error_msg}\n\n---\n\n"
            # Ajouter aux chemins invalides
            invalid_paths.append(format_path_error(file_path, error_msg))
    
    logger.info("Formatage du contenu terminé")
    
    result = {
        "matches": matches,
        "total_matches": len(matches),
        "formatted_content": formatted_content,
        "total_subdirectories": total_subdirectories
    }
    
    # Ajouter les erreurs de chemin s'il y en a
    if invalid_paths:
        result["invalid_paths"] = invalid_paths
        
    return result


@router.get("/health")
async def health_check():
    """
    Vérifie l'état de l'API de copie
    """
    return {"status": "ok", "service": "copy"} 