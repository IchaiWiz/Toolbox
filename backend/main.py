"""
Point d'entrée principal de l'application ToolBox API.
"""
import os
from app.api import create_app

# Création de l'application FastAPI
app = create_app()

if __name__ == "__main__":
    # Récupérer le port depuis les variables d'environnement ou utiliser 8000 par défaut
    port = int(os.getenv("PORT", 8000))
    
    # Lancer le serveur
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True) 