import os
import time
import datetime
import threading
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from collections import defaultdict

# Stockage des résultats d'analyse (dans un vrai projet, utiliser une BD)
ANALYSIS_RESULTS = {}


def analyze_directory_structure(
    directory_path: str,
    recursive: bool = True,
    include_hidden: bool = False,
    max_depth: int = 5,
    background: bool = True
) -> str:
    """
    Analyse la structure d'un répertoire et génère des informations.
    
    Args:
        directory_path: Chemin du répertoire à analyser
        recursive: Analyser récursivement les sous-dossiers
        include_hidden: Inclure les fichiers et dossiers cachés
        max_depth: Profondeur maximale d'analyse (0 = illimité)
        background: Exécuter en arrière-plan
        
    Returns:
        ID de l'analyse
    """
    # Générer un identifiant unique pour cette analyse
    analysis_id = f"analysis_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Initialiser le statut
    ANALYSIS_RESULTS[analysis_id] = {
        "id": analysis_id,
        "directory": directory_path,
        "start_time": time.time(),
        "end_time": None,
        "status": "en_cours",
        "progress": 0,
        "message": "Initialisation de l'analyse",
        "error": None,
        "structure": {},
        "stats": {
            "file_count": 0,
            "dir_count": 0,
            "extension_stats": {},
            "avg_files_per_dir": 0,
            "max_depth": 0
        }
    }
    
    # Fonction pour exécuter l'analyse
    def run_analysis():
        try:
            # Préparation
            path = Path(directory_path)
            if not path.exists() or not path.is_dir():
                raise ValueError(f"Le répertoire {directory_path} n'existe pas ou n'est pas un dossier")
            
            # Analyser la structure
            ANALYSIS_RESULTS[analysis_id]["message"] = "Analyse de la structure..."
            
            structure = {}
            file_count = 0
            dir_count = 0
            extension_count = defaultdict(int)
            max_depth_found = 0
            
            # Fonction pour analyser un répertoire récursivement
            def analyze_dir(dir_path: Path, parent_dict: Dict, current_depth: int = 0):
                nonlocal file_count, dir_count, max_depth_found
                
                if max_depth > 0 and current_depth > max_depth:
                    return
                
                if current_depth > max_depth_found:
                    max_depth_found = current_depth
                
                for item in dir_path.iterdir():
                    # Ignorer les éléments cachés si nécessaire
                    if not include_hidden and item.name.startswith('.'):
                        continue
                    
                    # Mettre à jour la progression (approximative)
                    ANALYSIS_RESULTS[analysis_id]["progress"] = min(
                        ANALYSIS_RESULTS[analysis_id]["progress"] + 1, 
                        99
                    )
                    
                    if item.is_dir():
                        dir_count += 1
                        # Créer un sous-dictionnaire pour ce dossier
                        parent_dict[item.name] = {}
                        
                        # Continuer récursivement si demandé
                        if recursive:
                            analyze_dir(item, parent_dict[item.name], current_depth + 1)
                    else:
                        file_count += 1
                        # Stocker le fichier
                        parent_dict[item.name] = {
                            "type": "file",
                            "size": item.stat().st_size,
                            "extension": item.suffix.lower()[1:] if item.suffix else ""
                        }
                        
                        # Compter l'extension
                        extension = item.suffix.lower()[1:] if item.suffix else "sans extension"
                        extension_count[extension] += 1
            
            # Démarrer l'analyse récursive
            structure[path.name] = {}
            analyze_dir(path, structure[path.name])
            
            # Calculer des statistiques additionnelles
            avg_files_per_dir = file_count / max(dir_count, 1)
            
            # Identifier les patterns dans la structure
            patterns = identify_patterns(structure)
            
            # Mettre à jour les résultats
            ANALYSIS_RESULTS[analysis_id].update({
                "structure": structure,
                "status": "terminé",
                "progress": 100,
                "end_time": time.time(),
                "message": f"Analyse terminée: {file_count} fichiers, {dir_count} dossiers",
                "stats": {
                    "file_count": file_count,
                    "dir_count": dir_count,
                    "extension_stats": dict(extension_count),
                    "avg_files_per_dir": avg_files_per_dir,
                    "max_depth": max_depth_found
                },
                "patterns": patterns
            })
            
        except Exception as e:
            # Gérer les erreurs
            ANALYSIS_RESULTS[analysis_id].update({
                "status": "erreur",
                "end_time": time.time(),
                "error": str(e),
                "message": f"Erreur: {str(e)}"
            })
    
    # Lancer l'analyse en arrière-plan ou immédiatement
    if background:
        thread = threading.Thread(target=run_analysis)
        thread.daemon = True
        thread.start()
    else:
        run_analysis()
    
    return analysis_id


def get_analysis_status(analysis_id: str) -> Optional[Dict[str, Any]]:
    """
    Récupère l'état d'une analyse.
    
    Args:
        analysis_id: ID de l'analyse
        
    Returns:
        Dictionnaire avec les résultats ou None si non trouvé
    """
    return ANALYSIS_RESULTS.get(analysis_id)


def identify_patterns(structure: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Identifie des patterns dans la structure de fichiers.
    Dans une version réelle, cela utiliserait des algorithmes plus sophistiqués
    ou de l'IA pour détecter des patterns et faire des recommandations.
    
    Args:
        structure: Dictionnaire représentant la structure du répertoire
        
    Returns:
        Liste des patterns identifiés
    """
    patterns = []
    
    # Convertir la structure en texte pour des recherches simples
    structure_str = str(structure)
    
    # Détecter des patterns courants
    
    # 1. Projet Web
    if any(x in structure_str for x in ['html', 'css', 'js', 'index.html']):
        patterns.append({
            "name": "Projet Web",
            "confidence": 0.8,
            "description": "Structure typique d'un projet web avec HTML, CSS et JavaScript"
        })
    
    # 2. Projet Node.js
    if 'node_modules' in structure_str or 'package.json' in structure_str:
        patterns.append({
            "name": "Projet Node.js",
            "confidence": 0.9,
            "description": "Projet utilisant Node.js avec des dépendances"
        })
    
    # 3. Projet Python
    if '.py' in structure_str or 'requirements.txt' in structure_str:
        patterns.append({
            "name": "Projet Python",
            "confidence": 0.8,
            "description": "Projet Python avec des scripts et potentiellement des dépendances"
        })
    
    # 4. Projet de documentation
    if '.md' in structure_str or 'docs' in structure_str:
        patterns.append({
            "name": "Documentation",
            "confidence": 0.7,
            "description": "Structure contenant de la documentation (Markdown, docs, etc.)"
        })
    
    # 5. Collection médias
    media_exts = ['jpg', 'jpeg', 'png', 'gif', 'mp4', 'avi', 'mp3', 'wav']
    if any(f".{ext}" in structure_str for ext in media_exts):
        patterns.append({
            "name": "Collection média",
            "confidence": 0.6,
            "description": "Collection de fichiers médias (images, vidéos, audio)"
        })
    
    # Si aucun pattern n'est détecté, ajouter un pattern générique
    if not patterns:
        patterns.append({
            "name": "Structure générique",
            "confidence": 0.5,
            "description": "Aucun pattern spécifique détecté dans cette structure de répertoires"
        })
    
    return patterns 