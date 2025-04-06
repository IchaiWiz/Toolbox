import os
import hashlib
import time
import datetime
import threading
from pathlib import Path
from typing import Dict, Any, List, Set, Optional, Tuple
from collections import defaultdict

# Stockage des résultats d'analyse (dans un vrai projet, utiliser une BD)
SCAN_RESULTS = {}


def find_duplicates(
    directory_path: str,
    recursive: bool = True,
    include_hidden: bool = False,
    min_size: int = 1024,  # 1KB minimum par défaut
    methods: List[str] = ["size", "hash"],
    background: bool = True
) -> str:
    """
    Trouve les fichiers en double dans un répertoire.
    
    Args:
        directory_path: Chemin du répertoire à analyser
        recursive: Analyser récursivement les sous-dossiers
        include_hidden: Inclure les fichiers cachés
        min_size: Taille minimale des fichiers à considérer (en octets)
        methods: Méthodes de détection à utiliser
        background: Exécuter en arrière-plan
        
    Returns:
        ID de l'analyse
    """
    # Générer un identifiant unique pour cette analyse
    scan_id = f"scan_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Initialiser le statut
    SCAN_RESULTS[scan_id] = {
        "id": scan_id,
        "directory": directory_path,
        "start_time": time.time(),
        "end_time": None,
        "status": "en_cours",
        "progress": 0,
        "message": "Initialisation de l'analyse",
        "error": None,
        "duplicates": [],
        "stats": {
            "total_files": 0,
            "processed_files": 0,
            "duplicate_sets": 0,
            "duplicate_files": 0,
            "wasted_space": 0
        }
    }
    
    # Fonction pour exécuter l'analyse
    def run_scan():
        try:
            # Préparation
            path = Path(directory_path)
            if not path.exists() or not path.is_dir():
                raise ValueError(f"Le répertoire {directory_path} n'existe pas ou n'est pas un dossier")
            
            # Compter les fichiers pour calculer la progression
            SCAN_RESULTS[scan_id]["message"] = "Comptage des fichiers..."
            file_list = []
            
            if recursive:
                for root, dirs, files in os.walk(path):
                    # Ignorer les dossiers cachés si nécessaire
                    if not include_hidden:
                        dirs[:] = [d for d in dirs if not d.startswith('.')]
                    
                    for file in files:
                        # Ignorer les fichiers cachés si nécessaire
                        if not include_hidden and file.startswith('.'):
                            continue
                            
                        file_path = Path(root) / file
                        if file_path.is_file() and file_path.stat().st_size >= min_size:
                            file_list.append(file_path)
            else:
                for item in path.iterdir():
                    if not include_hidden and item.name.startswith('.'):
                        continue
                        
                    if item.is_file() and item.stat().st_size >= min_size:
                        file_list.append(item)
            
            # Mettre à jour les statistiques
            total_files = len(file_list)
            SCAN_RESULTS[scan_id]["stats"]["total_files"] = total_files
            SCAN_RESULTS[scan_id]["message"] = f"Analyse de {total_files} fichiers..."
            
            # Étape 1: Regrouper par taille si la méthode est demandée
            size_groups = defaultdict(list)
            
            for i, file_path in enumerate(file_list):
                # Mettre à jour la progression
                progress = min(int((i / total_files) * 100), 99) if total_files > 0 else 0
                SCAN_RESULTS[scan_id]["progress"] = progress
                SCAN_RESULTS[scan_id]["stats"]["processed_files"] = i
                
                if "size" in methods:
                    # Regrouper par taille
                    size = file_path.stat().st_size
                    size_groups[size].append(file_path)
                else:
                    # Si on ne regroupe pas par taille, tout va dans le même groupe
                    size_groups["all"].append(file_path)
            
            # Mettre à jour le statut
            SCAN_RESULTS[scan_id]["message"] = "Analyse des doublons potentiels..."
            
            # Étape 2: Vérifier les doublons avec le hash MD5
            duplicates = []
            
            if "hash" in methods:
                for size, files in size_groups.items():
                    # Ne considérer que les groupes avec au moins 2 fichiers
                    if len(files) < 2:
                        continue
                        
                    # Regrouper par hash
                    hash_groups = defaultdict(list)
                    for file_path in files:
                        file_hash = get_file_hash(file_path)
                        hash_groups[file_hash].append(file_path)
                    
                    # Ajouter aux résultats les groupes avec doublons
                    for hash_val, hash_files in hash_groups.items():
                        if len(hash_files) >= 2:
                            duplicates.append({
                                "size": size,
                                "hash": hash_val,
                                "count": len(hash_files),
                                "wasted_space": size * (len(hash_files) - 1),
                                "files": [str(f) for f in hash_files]
                            })
            else:
                # Si pas de vérification par hash, considérer que les fichiers de même taille sont des doublons
                for size, files in size_groups.items():
                    if len(files) >= 2:
                        duplicates.append({
                            "size": size,
                            "count": len(files),
                            "wasted_space": size * (len(files) - 1),
                            "files": [str(f) for f in files]
                        })
            
            # Étape 3: Vérification supplémentaire du contenu bit à bit (si demandé)
            if "content" in methods:
                refined_duplicates = []
                
                for dup_group in duplicates:
                    files = [Path(f) for f in dup_group["files"]]
                    
                    # Regrouper par contenu bit à bit
                    content_groups = defaultdict(list)
                    for file_path in files:
                        # Utiliser le chemin comme identifiant du groupe
                        content_id = str(file_path)
                        content_groups[content_id].append(file_path)
                        
                        # Comparer ce fichier avec tous les autres du groupe
                        for other_file in files:
                            if file_path != other_file and are_files_identical(file_path, other_file):
                                content_groups[content_id].append(other_file)
                    
                    # Éliminer les doublons dans chaque groupe
                    for content_id, content_files in content_groups.items():
                        unique_files = list(set([str(f) for f in content_files]))
                        if len(unique_files) >= 2:
                            refined_duplicates.append({
                                "size": dup_group["size"],
                                "count": len(unique_files),
                                "wasted_space": dup_group["size"] * (len(unique_files) - 1),
                                "files": unique_files
                            })
                
                duplicates = refined_duplicates
            
            # Calculer les statistiques finales
            duplicate_files = sum(group["count"] for group in duplicates)
            duplicate_sets = len(duplicates)
            wasted_space = sum(group["wasted_space"] for group in duplicates)
            
            # Mettre à jour les résultats
            SCAN_RESULTS[scan_id].update({
                "duplicates": duplicates,
                "status": "terminé",
                "progress": 100,
                "end_time": time.time(),
                "message": f"Analyse terminée: {duplicate_sets} groupes de doublons trouvés",
                "stats": {
                    "total_files": total_files,
                    "processed_files": total_files,
                    "duplicate_sets": duplicate_sets,
                    "duplicate_files": duplicate_files,
                    "wasted_space": wasted_space
                }
            })
            
        except Exception as e:
            # Gérer les erreurs
            SCAN_RESULTS[scan_id].update({
                "status": "erreur",
                "end_time": time.time(),
                "error": str(e),
                "message": f"Erreur: {str(e)}"
            })
    
    # Lancer l'analyse en arrière-plan ou immédiatement
    if background:
        thread = threading.Thread(target=run_scan)
        thread.daemon = True
        thread.start()
    else:
        run_scan()
    
    return scan_id


def get_scan_status(scan_id: str) -> Optional[Dict[str, Any]]:
    """
    Récupère l'état d'une analyse.
    
    Args:
        scan_id: ID de l'analyse
        
    Returns:
        Dictionnaire avec les résultats ou None si non trouvé
    """
    return SCAN_RESULTS.get(scan_id)


def get_file_hash(file_path: Path) -> str:
    """
    Calcule le hash MD5 d'un fichier.
    """
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        # Lire le fichier par morceaux pour économiser la mémoire
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def are_files_identical(file1: Path, file2: Path) -> bool:
    """
    Compare deux fichiers octet par octet pour vérifier s'ils sont identiques.
    """
    # Vérifier d'abord la taille
    if file1.stat().st_size != file2.stat().st_size:
        return False
    
    # Comparer le contenu par morceaux
    with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
        while True:
            chunk1 = f1.read(4096)
            chunk2 = f2.read(4096)
            
            if chunk1 != chunk2:
                return False
                
            if not chunk1:  # Fin de fichier
                break
    
    return True 