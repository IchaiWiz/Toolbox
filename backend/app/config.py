import os
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env si présent
load_dotenv()

# Taille maximale des fichiers (10 MB par défaut)
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 10 * 1024 * 1024))

# Racine du projet
ROOT_DIR = Path(__file__).parent.parent

# Répertoires de base
BASE_DIR = Path(__file__).resolve().parent.parent
APP_DIR = BASE_DIR / "app"

# Configuration de l'API
API_PREFIX = "/api/v1"
DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "t")
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 8000))

# Répertoires temporaires et de travail
TEMP_DIR = BASE_DIR / "temp"
TEMP_DIR.mkdir(exist_ok=True)

# Autres configurations
# La variable MAX_FILE_SIZE est déjà définie plus haut 