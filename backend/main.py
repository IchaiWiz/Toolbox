"""
Point d'entrée principal de l'application ToolBox API.
"""
import os
import logging
import sys

# Obtenir le niveau de log depuis la variable d'environnement ou utiliser WARNING par défaut
log_level_name = os.getenv("TOOLBOX_LOG_LEVEL", "WARNING").upper()
log_level = getattr(logging, log_level_name, logging.WARNING)

# Configuration du logging avec console handler pour s'assurer que les logs sont visibles
logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("toolbox")
logger.setLevel(log_level)

# Log de confirmation du niveau de logging seulement en mode debug
if log_level_name != "WARNING":
    logger.info(f"Niveau de logging configuré à {log_level_name}")
if log_level_name == "DEBUG":
    logger.debug("==== MODE DEBUG ACTIVÉ - Les logs détaillés seront affichés ====")

from app.api import create_app

# Création de l'application FastAPI
app = create_app()

if __name__ == "__main__":
    # Récupérer le port depuis les variables d'environnement ou utiliser 8000 par défaut
    port = int(os.getenv("PORT", 8000))
    
    # Log de démarrage seulement en mode debug
    if log_level_name != "WARNING":
        logger.info(f"Démarrage du serveur sur le port {port}")
    
    # Lancer le serveur
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True, log_level=log_level_name.lower()) 