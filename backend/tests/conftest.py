"""
Configuration globale pour les tests
"""
import sys
import os
from pathlib import Path

# Ajouter le répertoire parent (backend) au chemin de recherche des modules
# pour que les importations comme 'from app.xxx' fonctionnent
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir)) 