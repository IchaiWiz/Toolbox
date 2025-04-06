"""
Routes de l'API
"""
# Ne pas importer automatiquement les modules pour les tests

# Permet d'importer tous les routers plus facilement
# Par exemple: from app.routes import analyse, backup, copy
# au lieu de: from app.routes.analyse import router as analyse_router

# On garde seulement copy
# from .analyse import router as analyse
# from .backup import router as backup 
from .copy import router as copy
# from .winmerge import router as winmerge
# from .duplicate_detection import router as duplicate_detection
# from .ai_structure import router as ai_structure
