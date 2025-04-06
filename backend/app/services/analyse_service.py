import os
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from collections import defaultdict

from ..utils.file_utils import get_file_stats


def get_directory_stats(directory_path: str, include_hidden: bool = False, recursive: bool = False) -> Dict[str, Any]:
    """
    Analyse un répertoire et génère des statistiques complètes.
    
    Args:
        directory_path: Chemin du répertoire à analyser
        include_hidden: Inclure les fichiers cachés
        recursive: Analyser les sous-dossiers
        
    Returns:
        Dictionnaire avec les statistiques du répertoire
    """
    path = Path(directory_path)
    if not path.exists() or not path.is_dir():
        raise ValueError(f"Le répertoire {directory_path} n'existe pas ou n'est pas un dossier")
    
    total_size = 0
    file_count = 0
    dir_count = 0
    file_types = defaultdict(int)
    all_files = []
    
    # Fonction pour traiter un seul fichier
    def process_file(file_path):
        nonlocal total_size, file_count
        
        stats = file_path.stat()
        total_size += stats.st_size
        file_count += 1
        
        extension = file_path.suffix.lower()[1:] if file_path.suffix else "sans extension"
        file_types[extension] += 1
        
        file_info = {
            "name": file_path.name,
            "path": str(file_path),
            "size": stats.st_size,
            "size_human": f"{stats.st_size / 1024:.1f} KB" if stats.st_size < 1024 * 1024 else f"{stats.st_size / (1024 * 1024):.1f} MB",
            "modified": stats.st_mtime,
            "modified_date": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stats.st_mtime)),
        }
        all_files.append(file_info)
    
    # Pour l'analyse récursive
    if recursive:
        for root, dirs, files in os.walk(path):
            root_path = Path(root)
            
            # Ignorer les dossiers cachés si demandé
            if not include_hidden and any(p.startswith('.') for p in root_path.parts):
                continue
                
            # Compter les dossiers
            for d in dirs:
                if include_hidden or not d.startswith('.'):
                    dir_count += 1
            
            # Traiter les fichiers
            for file in files:
                file_path = root_path / file
                if include_hidden or not file.startswith('.'):
                    process_file(file_path)
    else:
        # Analyse non récursive
        for item in path.iterdir():
            if not include_hidden and item.name.startswith('.'):
                continue
                
            if item.is_dir():
                dir_count += 1
            else:
                process_file(item)
    
    # Trier les fichiers pour trouver les plus grands et les plus récents
    largest_files = sorted(all_files, key=lambda x: x["size"], reverse=True)[:10]
    newest_files = sorted(all_files, key=lambda x: x["modified"], reverse=True)[:10]
    
    # Préparer la réponse
    total_size_human = f"{total_size / (1024 * 1024):.2f} MB" if total_size > 1024 * 1024 else f"{total_size / 1024:.2f} KB"
    
    return {
        "total_size": total_size,
        "total_size_human": total_size_human,
        "file_count": file_count,
        "dir_count": dir_count,
        "file_types": dict(file_types),
        "largest_files": largest_files,
        "newest_files": newest_files
    }


def analyse_file_types(directory_path: str, recursive: bool = False) -> Dict[str, Any]:
    """
    Analyse les types de fichiers dans un répertoire.
    
    Args:
        directory_path: Chemin du répertoire à analyser
        recursive: Analyser les sous-dossiers
        
    Returns:
        Statistiques sur les extensions de fichiers
    """
    path = Path(directory_path)
    if not path.exists() or not path.is_dir():
        raise ValueError(f"Le répertoire {directory_path} n'existe pas ou n'est pas un dossier")
    
    extension_count = defaultdict(int)
    extension_size = defaultdict(int)
    
    def process_file(file_path):
        stats = file_path.stat()
        extension = file_path.suffix.lower()[1:] if file_path.suffix else "sans extension"
        extension_count[extension] += 1
        extension_size[extension] += stats.st_size
    
    if recursive:
        for root, _, files in os.walk(path):
            for file in files:
                process_file(Path(root) / file)
    else:
        for item in path.iterdir():
            if item.is_file():
                process_file(item)
    
    # Préparer la réponse avec les tailles formatées
    result = {
        "extensions": {}
    }
    
    for ext in extension_count.keys():
        size = extension_size[ext]
        size_human = f"{size / (1024 * 1024):.2f} MB" if size > 1024 * 1024 else f"{size / 1024:.2f} KB"
        
        result["extensions"][ext] = {
            "count": extension_count[ext],
            "total_size": size,
            "total_size_human": size_human,
            "percentage": f"{extension_count[ext] / sum(extension_count.values()) * 100:.1f}%"
        }
    
    return result 