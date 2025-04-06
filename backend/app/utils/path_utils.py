import os
import re
from pathlib import Path
from typing import List, Optional, Dict, Any


def sanitize_path(path: str) -> str:
    """
    Nettoie et normalise un chemin d'accès.
    
    Args:
        path: Chemin à nettoyer
        
    Returns:
        Chemin normalisé et sécurisé
    """
    # Supprimer les guillemets au début et à la fin du chemin
    if path.startswith('"') and path.endswith('"'):
        path = path[1:-1]
    elif path.startswith("'") and path.endswith("'"):
        path = path[1:-1]
        
    # Vérifier si le chemin est entouré de guillemets avec des espaces
    path = path.strip()
    if path.startswith('"') and path.endswith('"'):
        path = path[1:-1]
    elif path.startswith("'") and path.endswith("'"):
        path = path[1:-1]
    
    try:
        # Normaliser le chemin (résoudre .., . et les slashes dupliqués)
        # Utiliser Path pour une meilleure gestion cross-platform
        normalized = str(Path(path))
        
        # Retirer les caractères potentiellement dangereux sauf ":" pour Windows
        # Cette liste peut être ajustée selon les besoins
        unsafe_chars = re.compile(r'[<>"|?*]')
        sanitized = unsafe_chars.sub('_', normalized)
        
        return sanitized
    except Exception:
        # Si Path échoue (par ex. avec des chemins mal formés), 
        # retourner le chemin nettoyé manuellement
        # Supprimer les caractères de contrôle et les caractères dangereux
        unsafe_chars = re.compile(r'[<>"|?*\x00-\x1F]')
        sanitized = unsafe_chars.sub('_', path)
        return sanitized


def is_valid_directory(directory: str) -> bool:
    """
    Vérifie si un répertoire existe et est accessible.
    
    Args:
        directory: Chemin du répertoire à vérifier
        
    Returns:
        True si le répertoire est valide, False sinon
    """
    path = Path(directory)
    return path.exists() and path.is_dir() and os.access(directory, os.R_OK)


def format_path_error(path: str, error_type: str) -> Dict[str, Any]:
    """
    Formate une erreur liée à un chemin de fichier.
    
    Args:
        path: Chemin qui a causé l'erreur
        error_type: Type d'erreur (not_found, permission, etc.)
        
    Returns:
        Dictionnaire contenant les détails de l'erreur
    """
    # Nettoyer le chemin des caractères problématiques et des notations spéciales
    clean_path = path
    
    # Supprimer les guillemets au début et à la fin du chemin
    if clean_path.startswith('"') and clean_path.endswith('"'):
        clean_path = clean_path[1:-1]
    elif clean_path.startswith("'") and clean_path.endswith("'"):
        clean_path = clean_path[1:-1]
    
    # Supprimer les espaces inutiles
    clean_path = clean_path.strip()
    
    # Gérer les chemins Windows avec C: ou autre lettre de lecteur
    if re.match(r'^[a-zA-Z]:\\', clean_path):
        # Remplacer les doubles backslashes par un seul
        clean_path = re.sub(r'\\+', '\\', clean_path)
        
    # Gérer les chemins avec caractères d'échappement
    if '%3A' in clean_path:
        clean_path = clean_path.replace('%3A', ':')
        
    # Gérer les chemins avec formatage spécial (ex: /c%3A/Users/...)
    if clean_path.startswith('/') and re.search(r'/[a-zA-Z]%3A/', clean_path):
        match = re.search(r'/([a-zA-Z])%3A/', clean_path)
        if match:
            drive_letter = match.group(1)
            clean_path = re.sub(r'/[a-zA-Z]%3A/', f'{drive_letter}:/', clean_path)
    
    # Nettoyer les doubles slashes
    if '/' in clean_path:
        clean_path = re.sub(r'/+', '/', clean_path)
    if '\\' in clean_path:
        clean_path = re.sub(r'\\+', r'\\', clean_path)
    
    # Essayer de normaliser le chemin avec Path si possible
    try:
        clean_path = str(Path(clean_path))
    except Exception:
        # Si la normalisation échoue, garder le chemin tel quel
        pass
    
    # Créer le message d'erreur approprié
    error_message = ""
    if error_type == "not_found":
        error_message = f"Le chemin '{clean_path}' n'existe pas"
    elif error_type == "permission":
        error_message = f"Accès refusé au chemin '{clean_path}'"
    else:
        error_message = f"Erreur avec le chemin '{clean_path}': {error_type}"
    
    return {
        "original_path": path,
        "clean_path": clean_path,
        "error_type": error_type,
        "message": error_message
    } 