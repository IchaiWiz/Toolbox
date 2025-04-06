"""
Fichier de compatibilité pour les anciennes importations.
Ce fichier réexporte les fonctions du module backup refactorisé.
"""
# Re-exporter les fonctions depuis le nouveau module
from .backup import create_backup, get_backup_status, get_backup_list, restore_backup

__all__ = ["create_backup", "get_backup_status", "get_backup_list", "restore_backup"]

import os
import shutil
import zipfile
import time
import datetime
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Union

from ..config import TEMP_DIR

# Stockage en mémoire des statuts des sauvegardes (dans un vrai projet, utiliser une BD)
BACKUP_STATUS = {}


def create_backup(
    backup_id: str,
    source_dir: str,
    destination_dir: str,
    backup_name: str,
    include_hidden: bool = False,
    compression: bool = True
) -> None:
    """
    Crée une sauvegarde d'un répertoire source vers une destination.
    Cette fonction est prévue pour être exécutée en arrière-plan.
    
    Args:
        backup_id: Identifiant unique de la sauvegarde
        source_dir: Répertoire source à sauvegarder
        destination_dir: Répertoire où placer la sauvegarde
        backup_name: Nom de la sauvegarde
        include_hidden: Inclure les fichiers cachés
        compression: Compresser la sauvegarde dans un ZIP
    """
    # Mettre à jour le statut
    BACKUP_STATUS[backup_id] = {
        "id": backup_id,
        "source": source_dir,
        "destination": destination_dir,
        "name": backup_name,
        "start_time": time.time(),
        "end_time": None,
        "status": "en_cours",
        "progress": 0,
        "message": "Initialisation de la sauvegarde",
        "error": None
    }
    
    try:
        src_path = Path(source_dir)
        dest_path = Path(destination_dir)
        
        # Vérifier les dossiers
        if not src_path.exists() or not src_path.is_dir():
            raise ValueError(f"Le répertoire source {source_dir} n'existe pas")
            
        if not dest_path.exists() or not dest_path.is_dir():
            raise ValueError(f"Le répertoire de destination {destination_dir} n'existe pas")
        
        # Créer un dossier temporaire de travail
        temp_backup_dir = TEMP_DIR / f"backup_{backup_id}"
        temp_backup_dir.mkdir(exist_ok=True)
            
        if compression:
            # Mise à jour statut
            BACKUP_STATUS[backup_id]["message"] = "Création de l'archive ZIP"
            
            # Chemin du fichier ZIP final
            zip_path = dest_path / f"{backup_name}.zip"
            
            # Créer l'archive ZIP
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                file_count = sum(len(files) for _, _, files in os.walk(src_path))
                processed = 0
                
                for root, dirs, files in os.walk(src_path):
                    # Ignorer les dossiers cachés si nécessaire
                    if not include_hidden and any(d.startswith('.') for d in Path(root).parts):
                        continue
                            
                    # Filtrer les dossiers cachés
                    if not include_hidden:
                        dirs[:] = [d for d in dirs if not d.startswith('.')]
                        
                    for file in files:
                        # Ignorer les fichiers cachés si nécessaire
                        if not include_hidden and file.startswith('.'):
                            continue
                            
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, src_path)
                        
                        zipf.write(file_path, arcname)
                        
                        # Mettre à jour la progression
                        processed += 1
                        progress = min(int((processed / file_count) * 100), 99)
                        BACKUP_STATUS[backup_id]["progress"] = progress
                        BACKUP_STATUS[backup_id]["message"] = f"Compression en cours ({progress}%)"
        else:
            # Sauvegarde simple (copie de fichiers)
            BACKUP_STATUS[backup_id]["message"] = "Copie des fichiers"
            
            # Créer le dossier de destination
            backup_dir = dest_path / backup_name
            backup_dir.mkdir(exist_ok=True)
            
            # Copier les fichiers
            file_count = sum(len(files) for _, _, files in os.walk(src_path))
            processed = 0
            
            for root, dirs, files in os.walk(src_path):
                # Ignorer les dossiers cachés si nécessaire
                if not include_hidden and any(d.startswith('.') for d in Path(root).parts):
                    continue
                        
                # Filtrer les dossiers cachés
                if not include_hidden:
                    dirs[:] = [d for d in dirs if not d.startswith('.')]
                    
                # Créer la structure de dossiers
                rel_dir = os.path.relpath(root, src_path)
                if rel_dir != '.':
                    os.makedirs(backup_dir / rel_dir, exist_ok=True)
                    
                for file in files:
                    # Ignorer les fichiers cachés si nécessaire
                    if not include_hidden and file.startswith('.'):
                        continue
                        
                    src_file = os.path.join(root, file)
                    dst_file = backup_dir / rel_dir / file
                    
                    shutil.copy2(src_file, dst_file)
                    
                    # Mettre à jour la progression
                    processed += 1
                    progress = min(int((processed / file_count) * 100), 99)
                    BACKUP_STATUS[backup_id]["progress"] = progress
                    BACKUP_STATUS[backup_id]["message"] = f"Copie en cours ({progress}%)"
                    
        # Créer un fichier de métadonnées
        metadata = {
            "backup_id": backup_id,
            "name": backup_name,
            "source": str(src_path),
            "created_at": datetime.datetime.now().isoformat(),
            "compression": compression,
            "include_hidden": include_hidden
        }
        
        # Enregistrer les métadonnées
        if compression:
            metadata_path = dest_path / f"{backup_name}.meta.json"
        else:
            metadata_path = backup_dir / "backup.meta.json"
            
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Finaliser
        BACKUP_STATUS[backup_id]["status"] = "terminé"
        BACKUP_STATUS[backup_id]["progress"] = 100
        BACKUP_STATUS[backup_id]["end_time"] = time.time()
        BACKUP_STATUS[backup_id]["message"] = "Sauvegarde terminée avec succès"
        
    except Exception as e:
        # Gérer les erreurs
        BACKUP_STATUS[backup_id]["status"] = "erreur"
        BACKUP_STATUS[backup_id]["end_time"] = time.time()
        BACKUP_STATUS[backup_id]["error"] = str(e)
        BACKUP_STATUS[backup_id]["message"] = f"Erreur: {str(e)}"
    finally:
        # Nettoyer les fichiers temporaires
        if 'temp_backup_dir' in locals() and temp_backup_dir.exists():
            shutil.rmtree(temp_backup_dir, ignore_errors=True)


def get_backup_status(backup_id: str) -> Optional[Dict[str, Any]]:
    """
    Récupère le statut d'une sauvegarde.
    
    Args:
        backup_id: Identifiant de la sauvegarde
        
    Returns:
        Dictionnaire avec le statut ou None si non trouvé
    """
    return BACKUP_STATUS.get(backup_id)


def get_backup_list(directory: str) -> List[Dict[str, Any]]:
    """
    Liste les sauvegardes dans un répertoire.
    
    Args:
        directory: Répertoire à scanner
        
    Returns:
        Liste des sauvegardes trouvées avec leurs métadonnées
    """
    backups = []
    dir_path = Path(directory)
    
    if not dir_path.exists() or not dir_path.is_dir():
        return []
    
    # Rechercher les archives ZIP et les dossiers de sauvegarde
    for item in dir_path.iterdir():
        # Cas 1: Archive ZIP avec fichier de métadonnées
        if item.is_file() and item.suffix.lower() == '.zip':
            meta_path = dir_path / f"{item.stem}.meta.json"
            if meta_path.exists():
                try:
                    with open(meta_path, 'r') as f:
                        metadata = json.load(f)
                    metadata['path'] = str(item)
                    metadata['size'] = item.stat().st_size
                    metadata['type'] = 'zip'
                    backups.append(metadata)
                except json.JSONDecodeError:
                    pass
        
        # Cas 2: Dossier de sauvegarde avec fichier de métadonnées
        elif item.is_dir():
            meta_path = item / "backup.meta.json"
            if meta_path.exists():
                try:
                    with open(meta_path, 'r') as f:
                        metadata = json.load(f)
                    metadata['path'] = str(item)
                    
                    # Calculer la taille totale
                    total_size = sum(f.stat().st_size for f in item.glob('**/*') if f.is_file())
                    metadata['size'] = total_size
                    metadata['type'] = 'directory'
                    backups.append(metadata)
                except json.JSONDecodeError:
                    pass
    
    return backups


def restore_backup(
    restore_id: str,
    backup_path: str,
    destination: str,
    overwrite: bool = False
) -> None:
    """
    Restaure une sauvegarde vers une destination.
    Cette fonction est prévue pour être exécutée en arrière-plan.
    
    Args:
        restore_id: Identifiant de restauration
        backup_path: Chemin vers la sauvegarde (ZIP ou dossier)
        destination: Destination pour la restauration
        overwrite: Écraser les fichiers existants
    """
    # Stocker le statut (comme pour les sauvegardes)
    BACKUP_STATUS[restore_id] = {
        "id": restore_id,
        "source": backup_path,
        "destination": destination,
        "start_time": time.time(),
        "end_time": None,
        "status": "en_cours",
        "progress": 0,
        "message": "Initialisation de la restauration",
        "error": None
    }
    
    try:
        backup = Path(backup_path)
        dest = Path(destination)
        
        if not backup.exists():
            raise ValueError(f"La sauvegarde {backup_path} n'existe pas")
            
        if not dest.exists() or not dest.is_dir():
            raise ValueError(f"La destination {destination} n'existe pas ou n'est pas un dossier")
        
        # Restauration d'une archive ZIP
        if backup.is_file() and backup.suffix.lower() == '.zip':
            BACKUP_STATUS[restore_id]["message"] = "Extraction de l'archive"
            
            with zipfile.ZipFile(backup, 'r') as zipf:
                file_list = zipf.infolist()
                total_files = len(file_list)
                
                for i, file_info in enumerate(file_list):
                    # Vérifier si le fichier existe déjà
                    target_path = dest / file_info.filename
                    if target_path.exists() and not overwrite:
                        continue
                        
                    # Extraire
                    zipf.extract(file_info, dest)
                    
                    # Mise à jour progression
                    progress = min(int((i + 1) / total_files * 100), 99)
                    BACKUP_STATUS[restore_id]["progress"] = progress
                    BACKUP_STATUS[restore_id]["message"] = f"Extraction en cours ({progress}%)"
        
        # Restauration d'un dossier
        elif backup.is_dir():
            BACKUP_STATUS[restore_id]["message"] = "Copie des fichiers"
            
            # Vérifier si c'est bien une sauvegarde
            if not (backup / "backup.meta.json").exists():
                raise ValueError(f"Le dossier {backup_path} ne semble pas être une sauvegarde valide")
            
            # Compter les fichiers à copier
            file_count = sum(1 for _ in backup.glob('**/*') if _.is_file() and _.name != 'backup.meta.json')
            processed = 0
            
            for src_file in backup.glob('**/*'):
                if src_file.is_file() and src_file.name != 'backup.meta.json':
                    # Chemin relatif par rapport à la sauvegarde
                    rel_path = src_file.relative_to(backup)
                    
                    # Destination
                    dst_file = dest / rel_path
                    
                    # Vérifier si le fichier existe déjà
                    if dst_file.exists() and not overwrite:
                        processed += 1
                        continue
                        
                    # Créer le dossier parent si nécessaire
                    dst_file.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Copier le fichier
                    shutil.copy2(src_file, dst_file)
                    
                    # Mise à jour progression
                    processed += 1
                    progress = min(int(processed / file_count * 100), 99)
                    BACKUP_STATUS[restore_id]["progress"] = progress
                    BACKUP_STATUS[restore_id]["message"] = f"Copie en cours ({progress}%)"
        
        else:
            raise ValueError(f"Le chemin {backup_path} n'est ni un fichier ZIP ni un dossier de sauvegarde")
        
        # Finaliser
        BACKUP_STATUS[restore_id]["status"] = "terminé"
        BACKUP_STATUS[restore_id]["progress"] = 100
        BACKUP_STATUS[restore_id]["end_time"] = time.time()
        BACKUP_STATUS[restore_id]["message"] = "Restauration terminée avec succès"
        
    except Exception as e:
        # Gérer les erreurs
        BACKUP_STATUS[restore_id]["status"] = "erreur"
        BACKUP_STATUS[restore_id]["end_time"] = time.time()
        BACKUP_STATUS[restore_id]["error"] = str(e)
        BACKUP_STATUS[restore_id]["message"] = f"Erreur: {str(e)}" 