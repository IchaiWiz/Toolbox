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
    # Ne pas remplacer les backslashes par des forward slashes sous Windows
    # Pour assurer une meilleure compatibilité avec les chemins Windows
    
    # Normaliser le chemin (résoudre .., . et les slashes dupliqués)
    # Utiliser Path pour une meilleure gestion cross-platform
    normalized = str(Path(path))
    
    # Retirer les caractères potentiellement dangereux sauf ":" pour Windows
    # Cette liste peut être ajustée selon les besoins
    unsafe_chars = re.compile(r'[<>"|?*]')
    sanitized = unsafe_chars.sub('_', normalized)
    
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