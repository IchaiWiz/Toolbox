import os
import re
from pathlib import Path
from typing import Dict, Any, List, Tuple

from ..config import MAX_FILE_SIZE


def scan_directory(
    directory: str,
    include_extensions: List[str] = [],
    exclude_extensions: List[str] = [],
    include_patterns: List[str] = [],
    exclude_patterns: List[str] = [],
    exclude_directories: List[str] = [],
    recursive: bool = True
) -> List[Dict[str, Any]]:
    """
    Scanne un dossier et retourne les fichiers correspondant aux critères.
    
    Args:
        directory: Chemin du dossier à scanner
        include_extensions: Liste des extensions à inclure (sans le point) - DÉPRÉCIÉ
        exclude_extensions: Liste des extensions à exclure (sans le point)
        include_patterns: Liste des motifs regex à inclure dans les noms de fichiers - DÉPRÉCIÉ
        exclude_patterns: Liste des motifs regex à exclure dans les noms de fichiers
        exclude_directories: Liste des sous-dossiers à exclure
        recursive: Chercher dans les sous-dossiers
        
    Returns:
        Liste des fichiers correspondant aux critères
    """
    results = []
    dir_path = Path(directory)
    
    if not dir_path.exists() or not dir_path.is_dir():
        return results
    
    # Déterminer la méthode de parcours
    walk_method = os.walk if recursive else lambda d: [(d, [], [f.name for f in Path(d).iterdir() if f.is_file()])]
    
    for root, dirs, files in walk_method(directory):
        # Convertir le chemin absolu en chemin relatif pour faciliter les comparaisons
        relative_path = os.path.relpath(root, directory)
        should_skip_dir = False
        
        # Filtrer les sous-dossiers à exclure (avant exploration)
        if exclude_directories:
            # Vérifier si ce dossier est à exclure
            should_skip_dir = os.path.basename(root) in exclude_directories or any(
                f"/{excluded_dir}/" in f"{root}/" 
                for excluded_dir in exclude_directories
            )
            
            # Filtrer aussi les sous-dossiers pour les prochaines itérations
            if not should_skip_dir:
                dirs[:] = [d for d in dirs if d not in exclude_directories]
        
        # Si on doit sauter ce dossier, passer au suivant
        if should_skip_dir:
            dirs[:] = []  # Vider la liste pour éviter de parcourir les sous-dossiers
            continue
        
        for filename in files:
            file_path = os.path.join(root, filename)
            file = Path(file_path)
            
            # Ignorer les fichiers trop gros
            if file.stat().st_size > MAX_FILE_SIZE:
                continue
                
            # Vérifier l'extension
            extension = file.suffix[1:] if file.suffix else ""
            if extension in exclude_extensions:
                continue
                
            # Vérifier les motifs d'exclusion
            exclude_match = False
            if exclude_patterns:
                exclude_match = any(re.search(pattern, filename) for pattern in exclude_patterns)
            if exclude_match:
                continue
                
            # Ajouter le fichier aux résultats
            results.append({
                "path": str(file).replace("\\", "/"),
                "name": filename,
                "size": file.stat().st_size,
                "extension": extension
            })
    
    return results


def read_file_content(file_path: str) -> str:
    """
    Lit le contenu d'un fichier de manière sécurisée.
    
    Args:
        file_path: Chemin du fichier à lire
        
    Returns:
        Contenu du fichier
    """
    path = Path(file_path)
    
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"Le fichier {file_path} n'existe pas ou n'est pas un fichier")
        
    if path.stat().st_size > MAX_FILE_SIZE:
        raise ValueError(f"Le fichier {file_path} est trop volumineux")
    
    # Déterminer l'encodage (en fonction de l'extension)
    encoding = "utf-8"  # Par défaut
    
    # Essayons de lire avec l'encodage déterminé
    try:
        with open(path, "r", encoding=encoding) as f:
            return f.read()
    except UnicodeDecodeError:
        # En cas d'erreur, on essaie avec un autre encodage
        try:
            with open(path, "r", encoding="latin-1") as f:
                return f.read()
        except Exception:
            # Si ça ne fonctionne toujours pas, on considère que c'est un fichier binaire
            return f"[Contenu binaire - Taille: {path.stat().st_size} octets]"
    except Exception as e:
        raise IOError(f"Erreur lors de la lecture: {str(e)}")


def format_file_for_copy(file_path: str, content: str, size_human: str = "") -> str:
    """
    Formate le contenu d'un fichier pour la copie.
    
    Args:
        file_path: Chemin du fichier
        content: Contenu du fichier
        size_human: Taille du fichier formatée (optionnel)
        
    Returns:
        Contenu formaté
    """
    if size_human:
        return f"=== {file_path} ({size_human}) ===\n\n{content}\n\n---\n\n"
    else:
        return f"=== {file_path} ===\n\n{content}\n\n---\n\n"


def get_file_stats(file_path: str) -> Dict[str, Any]:
    """
    Calcule les statistiques d'un fichier texte.
    
    Args:
        file_path: Chemin du fichier à analyser
        
    Returns:
        Dictionnaire contenant les statistiques du fichier
    """
    path = Path(file_path)
    
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"Le fichier {file_path} n'existe pas ou n'est pas un fichier")
        
    stats = {
        "totalLines": 0,
        "totalWords": 0,
        "totalChars": 0,
        "extension": path.suffix[1:] if path.suffix else "sans extension"
    }
    
    try:
        content = read_file_content(file_path)
        
        # Calcul des statistiques
        stats["totalChars"] = len(content)
        stats["totalLines"] = len(content.splitlines())
        stats["totalWords"] = len(re.findall(r'\w+', content))
        
        return stats
    except Exception as e:
        # En cas d'erreur, retourner les statistiques de base
        return {
            **stats,
            "error": str(e)
        } 