"""
Fixtures partagées pour les tests de l'outil de copie
"""
import os
import pytest
import tempfile
import shutil
from pathlib import Path


@pytest.fixture(scope="session")
def test_files_structure():
    """
    Crée une structure de fichiers pour les tests et la partage entre les différents tests.
    Cette fixture a une portée de session pour éviter de recréer les fichiers pour chaque test.
    """
    temp_dir = tempfile.mkdtemp()
    
    # Créer quelques fichiers de test
    files = {
        'file1.txt': 'Contenu du fichier 1',
        'file2.py': 'print("Hello world")',
        'file3.md': '# Titre markdown',
        'hidden.txt': 'Fichier caché',
        'subdir/nested.txt': 'Fichier dans sous-dossier',
        'subdir/code.py': 'def test(): pass',
        'subdir/data.json': '{"test": true}',
        'empty.txt': '',
    }
    
    # Créer les fichiers
    for file_path, content in files.items():
        full_path = os.path.join(temp_dir, file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w') as f:
            f.write(content)
    
    yield temp_dir
    
    # Nettoyage à la fin de la session de test
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_max_file_size(monkeypatch):
    """
    Modifie temporairement la valeur de MAX_FILE_SIZE pour les tests
    """
    # Une valeur plus petite pour faciliter les tests
    monkeypatch.setattr("app.config.MAX_FILE_SIZE", 1024)  # 1 KB
    return 1024 