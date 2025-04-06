from fastapi import APIRouter, HTTPException, Body, Query
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field
import os
import re
from pathlib import Path

from ..utils.file_utils import scan_directory, read_file_content, format_file_for_copy
from ..utils.path_utils import is_valid_directory, sanitize_path

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


class AdvancedCopyResult(BaseModel):
    matches: List[FileMatch] = Field(..., description="Fichiers correspondant aux critères")
    total_matches: int = Field(..., description="Nombre total de fichiers correspondants")
    formatted_content: str = Field(default="", description="Contenu formaté des fichiers")
    total_subdirectories: int = Field(default=0, description="Nombre total de sous-dossiers")


@router.post("/advanced/scan", response_model=AdvancedCopyResult)
async def scan_for_files(request: AdvancedCopyRequest):
    """
    Scanne les fichiers selon les critères spécifiés
    """
    matches = []
    total_subdirectories = 0
    
    # Vérifier si les répertoires existent
    valid_directories_found = False
    
    # Analyser les dossiers spécifiés
    for directory in request.directories:
        dir_path = sanitize_path(directory)
        if not is_valid_directory(dir_path):
            continue
            
        valid_directories_found = True
        try:
            # Calculer le nombre total de sous-dossiers
            if request.recursive:
                for root, dirs, _ in os.walk(dir_path):
                    # Filtrer les sous-dossiers exclus
                    if request.rules.exclude_directories:
                        dirs[:] = [d for d in dirs if d not in request.rules.exclude_directories 
                                  and not any(Path(os.path.join(root, d)).match(f"**/{excluded}/**") 
                                             for excluded in request.rules.exclude_directories)]
                    
                    total_subdirectories += len(dirs)
                
            # Rechercher les fichiers correspondants
            dir_matches = scan_directory(
                directory=dir_path,
                exclude_extensions=request.rules.exclude_extensions,
                exclude_patterns=request.rules.exclude_patterns,
                exclude_directories=request.rules.exclude_directories,
                recursive=request.recursive
            )
            
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
            # Ignorer les erreurs et continuer avec les autres dossiers
            print(f"Erreur lors de l'analyse du dossier {dir_path}: {str(e)}")
    
    # Si aucun répertoire valide n'a été trouvé et qu'il y a des répertoires spécifiés
    if not valid_directories_found and request.directories and not request.files:
        raise HTTPException(status_code=404, detail="Le répertoire spécifié n'existe pas ou n'est pas accessible")
    
    # Ajouter les fichiers spécifiques s'ils respectent les règles
    for file_path in request.files:
        file = Path(sanitize_path(file_path))
        if not file.exists() or not file.is_file():
            continue
            
        # Vérifier si le fichier correspond aux règles
        extension = file.suffix[1:] if file.suffix else ""
        filename = file.name
        
        # Vérification des extensions
        if extension in request.rules.exclude_extensions:
            continue
            
        # Vérification des motifs
        exclude_match = False
        if request.rules.exclude_patterns:
            exclude_match = any(re.search(pattern, filename) for pattern in request.rules.exclude_patterns)
        if exclude_match:
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
            continue
            
        # Calculer la taille formatée pour ce fichier spécifique
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
    
    return {
        "matches": matches,
        "total_matches": len(matches),
        "formatted_content": "",
        "total_subdirectories": total_subdirectories
    }


@router.post("/advanced/format-content", response_model=AdvancedCopyResult)
async def format_files_content(request: AdvancedCopyRequest):
    """
    Récupère et formate le contenu des fichiers sélectionnés selon les critères
    """
    # D'abord, on obtient les fichiers correspondants
    scan_result = await scan_for_files(request)
    matches = scan_result["matches"]
    total_subdirectories = scan_result["total_subdirectories"]
    
    # Ensuite, on récupère et formate le contenu
    formatted_content = ""
    for file_match in matches:
        file_path = file_match["path"]
        try:
            content = read_file_content(file_path)
            formatted_content += format_file_for_copy(file_path, content, file_match["size_human"])
        except Exception as e:
            # En cas d'erreur, on mentionne le fichier qu'on n'a pas pu lire
            formatted_content += f"=== {file_path} ({file_match['size_human']}) ===\nErreur lors de la lecture: {str(e)}\n\n---\n\n"
    
    return {
        "matches": matches,
        "total_matches": len(matches),
        "formatted_content": formatted_content,
        "total_subdirectories": total_subdirectories
    }


@router.get("/health")
async def health_check():
    """
    Vérifie l'état de l'API de copie
    """
    return {"status": "ok", "service": "copy"} 