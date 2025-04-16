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
    # Si le chemin est None ou vide, retourner une chaîne vide
    if not path:
        return ""
        
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
    
    # Pour les chemins Windows avec espaces, essayer de préserver le format exact
    windows_path = False
    if re.match(r'^[a-zA-Z]:\\', path):
        windows_path = True
    
    try:
        # Normaliser le chemin (résoudre .., . et les slashes dupliqués)
        # Pour Windows, préserver le format original si possible
        if windows_path:
            # Utiliser os.path.normpath pour les chemins Windows
            normalized = os.path.normpath(path)
        else:
            # Utiliser Path pour une meilleure gestion cross-platform
            normalized = str(Path(path))
        
        # Retirer les caractères potentiellement dangereux sauf ":" pour Windows
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
    # Essayer avec différentes variantes du chemin
    paths_to_try = [
        directory,
        directory.strip('"\''),  # Sans guillemets
        str(Path(directory)) if not isinstance(directory, Path) else str(directory),  # Normalisé par Path
        os.path.normpath(directory)  # Normalisé par os.path
    ]
    
    for path in paths_to_try:
        try:
            path_obj = Path(path)
            if path_obj.exists() and path_obj.is_dir() and os.access(str(path_obj), os.R_OK):
                return True
        except Exception:
            # Ignorer les erreurs et continuer avec la prochaine variante
            continue
    
    return False


def format_path_error(path: str, error_type: str) -> Dict[str, Any]:
    """
    Formate une erreur liée à un chemin de fichier.
    
    Args:
        path: Chemin qui a causé l'erreur
        error_type: Type d'erreur (not_found, permission, etc.)
        
    Returns:
        Dictionnaire contenant les détails de l'erreur
    """
    # Si le chemin est None ou vide
    if not path:
        error_message = "Chemin vide ou non spécifié"
        return {
            "original_path": "",
            "clean_path": "",
            "error_type": error_type,
            "message": error_message
        }
    
    # Utiliser la fonction sanitize_path pour nettoyer le chemin de manière cohérente
    # avec le reste de l'application
    clean_path = sanitize_path(path)
    
    # Pour les chemins Windows spécifiquement, s'assurer que les backslashes sont correctement gérés
    if re.match(r'^[a-zA-Z]:\\', clean_path):
        # Remplacer les doubles backslashes par un seul (utiliser r'\' pour éviter les problèmes d'échappement)
        clean_path = re.sub(r'\\+', r'\\', clean_path)
    
    # Gérer les chemins avec caractères d'échappement
    if '%3A' in clean_path:
        clean_path = clean_path.replace('%3A', ':')
    
    # Gérer les chemins avec formatage spécial (ex: /c%3A/Users/...)
    if clean_path.startswith('/') and re.search(r'/[a-zA-Z]%3A/', clean_path):
        match = re.search(r'/([a-zA-Z])%3A/', clean_path)
        if match:
            drive_letter = match.group(1)
            clean_path = re.sub(r'/[a-zA-Z]%3A/', f'{drive_letter}:/', clean_path)
    
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