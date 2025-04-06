import os
import filecmp
import difflib
import hashlib
from pathlib import Path
from typing import Dict, Any, List


def compare_files(left_path: str, right_path: str) -> Dict[str, Any]:
    """
    Compare deux fichiers et retourne un rapport détaillé de leurs différences.
    
    Args:
        left_path: Chemin du fichier gauche
        right_path: Chemin du fichier droit
        
    Returns:
        Dictionnaire contenant les informations sur la comparaison
    """
    left = Path(left_path)
    right = Path(right_path)
    
    if not left.exists():
        raise FileNotFoundError(f"Le fichier {left_path} n'existe pas")
        
    if not right.exists():
        raise FileNotFoundError(f"Le fichier {right_path} n'existe pas")
    
    # Comparaison simple avec filecmp
    are_identical = filecmp.cmp(left, right, shallow=False)
    
    # Obtenir les hachages pour une comparaison supplémentaire
    left_hash = get_file_hash(left)
    right_hash = get_file_hash(right)
    
    details = []
    
    # Si les fichiers sont différents, calculer une diff ligne par ligne
    # mais seulement pour les fichiers texte de taille raisonnable
    if not are_identical and is_text_file(left) and is_text_file(right) and \
       left.stat().st_size < 5 * 1024 * 1024 and right.stat().st_size < 5 * 1024 * 1024:
        with open(left, 'r', encoding='utf-8', errors='ignore') as left_file:
            left_lines = left_file.readlines()
            
        with open(right, 'r', encoding='utf-8', errors='ignore') as right_file:
            right_lines = right_file.readlines()
            
        # Générer un diff
        diff = list(difflib.unified_diff(
            left_lines, 
            right_lines,
            fromfile=str(left),
            tofile=str(right),
            lineterm=''
        ))
        
        # Limiter à 100 lignes pour éviter des résultats trop volumineux
        diff_text = '\n'.join(diff[:100])
        if len(diff) > 100:
            diff_text += f"\n... et {len(diff) - 100} lignes supplémentaires"
    else:
        diff_text = None
    
    # Préparer le résultat
    result = {
        "differences": 0 if are_identical else 1,
        "identical": 1 if are_identical else 0,
        "left_only": 0,
        "right_only": 0,
        "details": [
            {
                "name": left.name,
                "left_path": str(left),
                "right_path": str(right),
                "status": "identical" if are_identical else "different",
                "left_size": left.stat().st_size,
                "right_size": right.stat().st_size,
                "left_hash": left_hash,
                "right_hash": right_hash,
                "diff": diff_text
            }
        ]
    }
    
    return result


def compare_directories(
    left_dir: str, 
    right_dir: str, 
    recursive: bool = True,
    show_identical: bool = False
) -> Dict[str, Any]:
    """
    Compare deux répertoires et retourne un rapport détaillé.
    
    Args:
        left_dir: Chemin du répertoire gauche
        right_dir: Chemin du répertoire droit
        recursive: Si True, compare aussi les sous-répertoires
        show_identical: Si True, inclut aussi les fichiers identiques dans les détails
        
    Returns:
        Dictionnaire contenant les informations sur la comparaison
    """
    left_path = Path(left_dir)
    right_path = Path(right_dir)
    
    if not left_path.exists() or not left_path.is_dir():
        raise ValueError(f"Le répertoire {left_dir} n'existe pas ou n'est pas un dossier")
        
    if not right_path.exists() or not right_path.is_dir():
        raise ValueError(f"Le répertoire {right_dir} n'existe pas ou n'est pas un dossier")
    
    # Utiliser filecmp pour comparer les répertoires
    comparison = filecmp.dircmp(left_path, right_path)
    
    # Initialiser les compteurs
    differences = 0
    identical = 0
    left_only_count = len(comparison.left_only)
    right_only_count = len(comparison.right_only)
    details = []
    
    # Ajouter les détails des fichiers seulement présents dans le premier répertoire
    for name in comparison.left_only:
        left_file_path = left_path / name
        details.append({
            "name": name,
            "left_path": str(left_file_path),
            "right_path": None,
            "status": "left_only",
            "left_size": left_file_path.stat().st_size if left_file_path.is_file() else None,
            "right_size": None,
            "is_dir": left_file_path.is_dir()
        })
    
    # Ajouter les détails des fichiers seulement présents dans le second répertoire
    for name in comparison.right_only:
        right_file_path = right_path / name
        details.append({
            "name": name,
            "left_path": None,
            "right_path": str(right_file_path),
            "status": "right_only",
            "left_size": None,
            "right_size": right_file_path.stat().st_size if right_file_path.is_file() else None,
            "is_dir": right_file_path.is_dir()
        })
    
    # Fichiers présents dans les deux répertoires mais différents
    for name in comparison.diff_files:
        differences += 1
        left_file_path = left_path / name
        right_file_path = right_path / name
        
        details.append({
            "name": name,
            "left_path": str(left_file_path),
            "right_path": str(right_file_path),
            "status": "different",
            "left_size": left_file_path.stat().st_size,
            "right_size": right_file_path.stat().st_size,
            "is_dir": False
        })
    
    # Fichiers identiques
    if show_identical:
        for name in comparison.same_files:
            identical += 1
            left_file_path = left_path / name
            right_file_path = right_path / name
            
            details.append({
                "name": name,
                "left_path": str(left_file_path),
                "right_path": str(right_file_path),
                "status": "identical",
                "left_size": left_file_path.stat().st_size,
                "right_size": right_file_path.stat().st_size,
                "is_dir": False
            })
    else:
        identical = len(comparison.same_files)
    
    # Traiter récursivement les sous-répertoires si demandé
    if recursive:
        for subdir in comparison.common_dirs:
            left_subdir = left_path / subdir
            right_subdir = right_path / subdir
            
            # Comparer récursivement
            subdir_result = compare_directories(
                str(left_subdir),
                str(right_subdir),
                recursive,
                show_identical
            )
            
            # Ajouter aux compteurs
            differences += subdir_result["differences"]
            identical += subdir_result["identical"]
            left_only_count += subdir_result["left_only"]
            right_only_count += subdir_result["right_only"]
            
            # Ajouter les détails
            details.extend(subdir_result["details"])
    else:
        # Si non récursif, compter juste les sous-répertoires communs
        for subdir in comparison.common_dirs:
            left_subdir = left_path / subdir
            right_subdir = right_path / subdir
            
            details.append({
                "name": subdir,
                "left_path": str(left_subdir),
                "right_path": str(right_subdir),
                "status": "directory",
                "left_size": None,
                "right_size": None,
                "is_dir": True
            })
    
    # Préparer le résultat
    result = {
        "differences": differences,
        "identical": identical,
        "left_only": left_only_count,
        "right_only": right_only_count,
        "details": details
    }
    
    return result


def get_file_hash(file_path: Path) -> str:
    """
    Calcule le hash MD5 d'un fichier.
    """
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def is_text_file(file_path: Path) -> bool:
    """
    Détermine si un fichier est probablement un fichier texte.
    """
    if file_path.suffix.lower() in ('.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.xml', '.csv'):
        return True
        
    # Vérification basique du contenu (échantillon)
    try:
        with open(file_path, 'rb') as f:
            sample = f.read(1024)
            
        # Si l'échantillon contient des caractères nuls, c'est probablement un fichier binaire
        if b'' in sample:
            return False
            
        # Essayer de décoder en UTF-8
        try:
            sample.decode('utf-8')
            return True
        except UnicodeDecodeError:
            return False
    except:
        return False 