import os
import re
import logging
from pathlib import Path
from typing import Dict, Any, List, Tuple

from ..config import MAX_FILE_SIZE

# Configuration du logger
logger = logging.getLogger("toolbox.file_utils")


def scan_directory(
    directory: str,
    include_extensions: List[str] = [],
    exclude_extensions: List[str] = [],
    include_patterns: List[str] = [],
    exclude_patterns: List[str] = [],
    exclude_directories: List[str] = [],
    recursive: bool = True
) -> Dict[str, Any]:
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
        Dictionnaire contenant la liste des fichiers correspondant aux critères et les erreurs rencontrées
    """
    logger.info(f"Début du scan du dossier {directory} (récursif={recursive})")
    
    results = []
    errors = []  # Liste pour stocker les fichiers et dossiers en erreur
    dir_path = Path(directory)
    
    if not dir_path.exists() or not dir_path.is_dir():
        err_msg = f"Le dossier {directory} n'existe pas ou n'est pas accessible"
        logger.error(err_msg)
        return {"files": results, "errors": [err_msg]}
    
    # Fonction pour parcourir le répertoire de manière sécurisée
    def safe_walk(directory):
        try:
            # Pour les dossiers non récursifs, utiliser un itérateur personnalisé
            if not recursive:
                try:
                    logger.debug(f"Scan non récursif de {directory}")
                    # Liste des fichiers dans le dossier courant uniquement
                    files = []
                    dirs = []
                    try:
                        for f in Path(directory).iterdir():
                            try:
                                if f.is_file():
                                    files.append(f.name)
                                elif f.is_dir():
                                    dirs.append(f.name)
                            except (PermissionError, OSError) as e:
                                err_msg = f"Accès refusé à '{f}': {str(e)}"
                                logger.warning(err_msg)
                                errors.append(err_msg)
                    except (PermissionError, OSError) as e:
                        err_msg = f"Erreur d'accès au dossier '{directory}': {str(e)}"
                        logger.error(err_msg)
                        errors.append(err_msg)
                    
                    logger.debug(f"Dossier {directory}: {len(files)} fichiers, {len(dirs)} sous-dossiers")
                    # Retourner un seul tuple pour ce dossier
                    yield (directory, dirs, files)
                except (PermissionError, OSError) as e:
                    # En cas d'erreur d'accès, noter l'erreur et retourner un tuple vide
                    err_msg = f"Erreur d'accès au dossier '{directory}': {str(e)}"
                    logger.error(err_msg)
                    errors.append(err_msg)
                    yield (directory, [], [])
            else:
                # Pour la récursion, utiliser os.walk avec gestion d'erreur
                logger.debug(f"Démarrage du scan récursif de {directory}")
                
                def onerror(e):
                    err_msg = f"Erreur lors du parcours de '{e.filename}': {str(e.exception)}"
                    logger.error(err_msg)
                    errors.append(err_msg)
                
                for root, dirs, files in os.walk(directory, onerror=onerror):
                    # Filtrer les sous-dossiers que nous ne pouvons pas accéder immédiatement
                    filtered_dirs = []
                    for d in dirs[:]:
                        try:
                            dir_path = os.path.join(root, d)
                            # Essayer d'accéder au dossier
                            os.listdir(dir_path)
                            filtered_dirs.append(d)
                        except (PermissionError, OSError) as e:
                            # Signaler l'erreur et passer au suivant
                            err_msg = f"Accès refusé au dossier '{dir_path}': {str(e)}"
                            logger.warning(err_msg)
                            errors.append(err_msg)
                            dirs.remove(d)  # Ne pas continuer avec ce dossier
                    
                    logger.debug(f"Traitement de {root}: {len(files)} fichiers, {len(dirs)} sous-dossiers")
                    yield (root, dirs, files)
        except Exception as e:
            # Gestion globale des erreurs (fallback)
            err_msg = f"Erreur générale lors du parcours de '{directory}': {str(e)}"
            logger.error(err_msg)
            errors.append(err_msg)
            yield (directory, [], [])
    
    # Utiliser notre fonction de parcours sécurisée
    logger.info(f"Début du parcours de {directory}")
    
    file_counter = 0
    error_counter = 0
    dir_counter = 0
    
    for root, dirs, files in safe_walk(directory):
        dir_counter += 1
        # Convertir le chemin absolu en chemin relatif pour faciliter les comparaisons
        try:
            relative_path = os.path.relpath(root, directory)
            if relative_path != '.':
                logger.debug(f"Traitement du sous-dossier: {relative_path}")
        except ValueError:
            # Gérer les erreurs de calcul de chemin relatif
            err_msg = f"Erreur de calcul du chemin relatif pour '{root}'"
            logger.error(err_msg)
            errors.append(err_msg)
            error_counter += 1
            continue
            
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
                excluded_count = len(dirs)
                dirs[:] = [d for d in dirs if d not in exclude_directories]
                excluded_count -= len(dirs)
                if excluded_count > 0:
                    logger.debug(f"Exclusion de {excluded_count} sous-dossiers dans {root}")
        
        # Si on doit sauter ce dossier, passer au suivant
        if should_skip_dir:
            logger.debug(f"Dossier exclu: {root}")
            dirs[:] = []  # Vider la liste pour éviter de parcourir les sous-dossiers
            continue
        
        for filename in files:
            try:
                file_path = os.path.join(root, filename)
                file = Path(file_path)
                
                # Vérifier si le fichier existe et est accessible
                try:
                    if not file.exists() or not file.is_file():
                        logger.debug(f"Fichier inexistant ou non reconnu: {file_path}")
                        continue
                except (PermissionError, OSError) as e:
                    err_msg = f"Erreur d'accès au fichier '{file_path}': {str(e)}"
                    logger.warning(err_msg)
                    errors.append(err_msg)
                    error_counter += 1
                    continue
                
                # Obtenir les stats du fichier avec gestion d'erreur
                try:
                    file_size = file.stat().st_size
                except (PermissionError, OSError) as e:
                    # Noter l'erreur et passer au fichier suivant
                    err_msg = f"Erreur d'accès au fichier '{file_path}': {str(e)}"
                    logger.warning(err_msg)
                    errors.append(err_msg)
                    error_counter += 1
                    continue
                
                # Ignorer les fichiers trop gros
                if file_size > MAX_FILE_SIZE:
                    logger.debug(f"Fichier trop volumineux ignoré: {file_path} ({file_size} octets > {MAX_FILE_SIZE})")
                    continue
                    
                # Vérifier l'extension
                extension = file.suffix[1:] if file.suffix else ""
                if extension in exclude_extensions:
                    logger.debug(f"Fichier exclu par extension: {file_path} (extension: {extension})")
                    continue
                    
                # Vérifier les motifs d'exclusion
                exclude_match = False
                if exclude_patterns:
                    exclude_match = any(re.search(pattern, filename) for pattern in exclude_patterns)
                if exclude_match:
                    logger.debug(f"Fichier exclu par motif: {file_path}")
                    continue
                    
                # Ajouter le fichier aux résultats
                results.append({
                    "path": str(file).replace("\\", "/"),
                    "name": filename,
                    "size": file_size,
                    "extension": extension
                })
                file_counter += 1
                
                if file_counter % 100 == 0:  # Log tous les 100 fichiers
                    logger.info(f"Progression: {file_counter} fichiers trouvés, {error_counter} erreurs")
                
            except Exception as e:
                # Capturer et noter l'erreur mais continuer avec les autres fichiers
                err_msg = f"Erreur lors du traitement du fichier '{os.path.join(root, filename)}': {str(e)}"
                logger.error(err_msg)
                errors.append(err_msg)
                error_counter += 1
                continue
    
    logger.info(f"Scan terminé pour {directory}: {file_counter} fichiers trouvés, {dir_counter} dossiers traités, {error_counter} erreurs")
    return {"files": results, "errors": errors}


def read_file_content(file_path: str) -> str:
    """
    Lit le contenu d'un fichier de manière sécurisée.
    
    Args:
        file_path: Chemin du fichier à lire
        
    Returns:
        Contenu du fichier
    """
    logger.debug(f"Lecture du fichier: {file_path}")
    path = Path(file_path)
    
    try:
        try:
            if not path.exists() or not path.is_file():
                err_msg = f"Le fichier {file_path} n'existe pas ou n'est pas un fichier"
                logger.warning(err_msg)
                raise FileNotFoundError(err_msg)
        except (PermissionError, OSError) as e:
            err_msg = f"[Erreur d'accès - {str(e)}]"
            logger.error(f"Erreur d'accès au fichier {file_path}: {str(e)}")
            return err_msg
            
        try:
            if path.stat().st_size > MAX_FILE_SIZE:
                err_msg = f"Le fichier {file_path} est trop volumineux"
                logger.warning(err_msg)
                raise ValueError(err_msg)
        except (PermissionError, OSError) as e:
            err_msg = f"[Erreur d'accès - {str(e)}]"
            logger.error(f"Erreur lors de l'obtention de la taille de {file_path}: {str(e)}")
            return err_msg
        
        # Déterminer l'encodage (en fonction de l'extension)
        encoding = "utf-8"  # Par défaut
        
        # Essayons de lire avec l'encodage déterminé
        try:
            with open(path, "r", encoding=encoding) as f:
                content = f.read()
                logger.debug(f"Fichier lu avec succès: {file_path} (utf-8)")
                return content
        except UnicodeDecodeError:
            # En cas d'erreur, on essaie avec un autre encodage
            logger.debug(f"Tentative de lecture avec encodage latin-1: {file_path}")
            try:
                with open(path, "r", encoding="latin-1") as f:
                    content = f.read()
                    logger.debug(f"Fichier lu avec succès: {file_path} (latin-1)")
                    return content
            except Exception:
                # Si ça ne fonctionne toujours pas, on considère que c'est un fichier binaire
                err_msg = f"[Contenu binaire - Taille: {path.stat().st_size} octets]"
                logger.warning(f"Fichier binaire détecté: {file_path}")
                return err_msg
        except PermissionError as e:
            err_msg = f"[Erreur d'accès - {str(e)}]"
            logger.error(f"Erreur de permission lors de la lecture de {file_path}: {str(e)}")
            return err_msg
        except FileNotFoundError as e:
            err_msg = f"[Fichier non trouvé - {str(e)}]"
            logger.error(f"Fichier non trouvé: {file_path}")
            return err_msg
        except ValueError as e:
            err_msg = f"[Erreur de valeur - {str(e)}]"
            logger.error(f"Erreur de valeur lors de la lecture de {file_path}: {str(e)}")
            return err_msg
        except Exception as e:
            err_msg = f"[Erreur de lecture - {str(e)}]"
            logger.error(f"Erreur générale lors de la lecture de {file_path}: {str(e)}")
            return err_msg
            
    except PermissionError as e:
        err_msg = f"[Erreur d'accès - {str(e)}]"
        logger.error(f"Erreur d'accès au fichier {file_path}: {str(e)}")
        return err_msg
    except FileNotFoundError as e:
        err_msg = f"[Fichier non trouvé - {str(e)}]"
        logger.error(f"Fichier non trouvé: {file_path}")
        return err_msg
    except ValueError as e:
        err_msg = f"[Erreur de valeur - {str(e)}]"
        logger.error(f"Erreur de valeur: {file_path} - {str(e)}")
        return err_msg
    except Exception as e:
        err_msg = f"[Erreur de lecture - {str(e)}]"
        logger.error(f"Erreur générale lors de la lecture de {file_path}: {str(e)}")
        return err_msg


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