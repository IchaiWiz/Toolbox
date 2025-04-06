import os
import pytest
import tempfile
import shutil
from pathlib import Path
from fastapi.testclient import TestClient
from fastapi import FastAPI

# Créer une application FastAPI minimale pour les tests
from app.routes.copy import router as copy_router
from app.config import MAX_FILE_SIZE

# Créer une application FastAPI simplifiée pour les tests uniquement
app = FastAPI(title="Toolbox API Test", version="1.0.0")
app.include_router(copy_router)
client = TestClient(app)


class TestCopyRoutes:
    """Tests pour les routes de l'API de copie"""
    
    @pytest.fixture
    def test_directory(self):
        """Crée une structure de fichiers pour les tests"""
        temp_dir = tempfile.mkdtemp()
        
        # Créer quelques fichiers de test
        files = {
            'file1.txt': 'Contenu du fichier 1',
            'file2.py': 'print("Hello world")',
            'file3.md': '# Titre markdown',
            'hidden.txt': 'Fichier caché',
            'subdir/nested.txt': 'Fichier dans sous-dossier',
            'subdir/code.py': 'def test(): pass',
        }
        
        for file_path, content in files.items():
            full_path = os.path.join(temp_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w') as f:
                f.write(content)
        
        yield temp_dir
        
        # Nettoyage
        shutil.rmtree(temp_dir)
    
    def test_health_check(self):
        """Test de la route health check"""
        response = client.get("/api/v1/copy/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok", "service": "copy"}
    
    def test_scan_files_no_directory(self):
        """Test de scan avec un répertoire inexistant"""
        request_data = {
            "directories": ["/chemin/non/existant"],
            "files": [],
            "rules": {
                "include_extensions": [],
                "exclude_extensions": [],
                "include_patterns": [],
                "exclude_patterns": []
            },
            "recursive": True
        }
        
        response = client.post("/api/v1/copy/advanced/scan", json=request_data)
        assert response.status_code == 404
        assert "n'existe pas" in response.json()["detail"]
    
    def test_scan_files_valid(self, test_directory):
        """Test de scan avec un répertoire valide"""
        request_data = {
            "directories": [test_directory],
            "files": [],
            "rules": {
                "include_extensions": [],
                "exclude_extensions": [],
                "include_patterns": [],
                "exclude_patterns": []
            },
            "recursive": True
        }
        
        response = client.post("/api/v1/copy/advanced/scan", json=request_data)
        assert response.status_code == 200
        data = response.json()
        
        assert "matches" in data
        assert "total_matches" in data
        assert "formatted_content" in data
        assert data["total_matches"] == 6
        assert len(data["matches"]) == 6
    
    def test_scan_files_with_filters(self, test_directory):
        """Test de scan avec des filtres"""
        request_data = {
            "directories": [test_directory],
            "files": [],
            "rules": {
                "exclude_extensions": ["txt"],
                "exclude_patterns": [],
                "exclude_directories": []
            },
            "recursive": True
        }
        
        response = client.post("/api/v1/copy/advanced/scan", json=request_data)
        assert response.status_code == 200
        data = response.json()
        
        # Les fichiers .txt devraient être exclus
        assert all(match["extension"] != "txt" for match in data["matches"])
        
        # Il devrait rester les fichiers .py et autres
        assert data["total_matches"] > 0
        assert any(match["extension"] == "py" for match in data["matches"])
    
    def test_scan_files_with_specific_file(self, test_directory):
        """Test de scan avec un fichier spécifique"""
        specific_file = os.path.join(test_directory, "file1.txt")
        
        request_data = {
            "directories": [],
            "files": [specific_file],
            "rules": {
                "include_extensions": [],
                "exclude_extensions": [],
                "include_patterns": [],
                "exclude_patterns": []
            },
            "recursive": True
        }
        
        response = client.post("/api/v1/copy/advanced/scan", json=request_data)
        assert response.status_code == 200
        data = response.json()
        
        assert data["total_matches"] == 1
        assert data["matches"][0]["name"] == "file1.txt"
    
    def test_format_content(self, test_directory):
        """Test de formatage du contenu"""
        request_data = {
            "directories": [],
            "files": [os.path.join(test_directory, "file1.txt")],
            "rules": {
                "include_extensions": [],
                "exclude_extensions": [],
                "include_patterns": [],
                "exclude_patterns": []
            },
            "recursive": True
        }
        
        response = client.post("/api/v1/copy/advanced/format-content", json=request_data)
        assert response.status_code == 200
        data = response.json()
        
        assert data["total_matches"] == 1
        assert "=== " in data["formatted_content"]
        assert "Contenu du fichier 1" in data["formatted_content"]
        assert "---" in data["formatted_content"]
        assert "total_subdirectories" in data
        assert "(" in data["formatted_content"]  # Vérifier que la taille formatée apparaît entre parenthèses
    
    def test_format_content_multiple_files(self, test_directory):
        """Test de formatage avec plusieurs fichiers"""
        request_data = {
            "directories": [test_directory],
            "files": [],
            "rules": {
                "exclude_extensions": ["md", "json", "xml"],  # On exclut tout sauf les .txt
                "exclude_patterns": [],
                "exclude_directories": []
            },
            "recursive": True
        }
        
        response = client.post("/api/v1/copy/advanced/format-content", json=request_data)
        assert response.status_code == 200
        data = response.json()
        
        # Vérifier que le contenu formaté contient bien les fichiers .txt
        assert "file1.txt" in data["formatted_content"]
        assert "hidden.txt" in data["formatted_content"] 
        assert "nested.txt" in data["formatted_content"]
        assert "Contenu du fichier 1" in data["formatted_content"]
        assert "Fichier caché" in data["formatted_content"]
        assert "Fichier dans sous-dossier" in data["formatted_content"]
        
        # Vérifier les nouvelles fonctionnalités
        assert "total_subdirectories" in data
        assert isinstance(data["total_subdirectories"], int)
        
        # Vérifier que la taille est formatée pour au moins un fichier
        assert "Ko" in data["formatted_content"] or "Mo" in data["formatted_content"] or "octets" in data["formatted_content"]
        
        # Vérifier que chaque fichier a size_human
        for match in data["matches"]:
            assert "size_human" in match
            assert isinstance(match["size_human"], str)
    
    def test_scan_with_excluded_directories(self, test_directory):
        """Test de scan avec exclusion de sous-dossiers"""
        # Créer la structure de test avec un sous-dossier supplémentaire contenant des fichiers
        nested_dir = os.path.join(test_directory, "subdir")
        if not os.path.exists(nested_dir):
            os.makedirs(nested_dir)
            
        # Créer un fichier dans le sous-dossier
        with open(os.path.join(nested_dir, "nested.txt"), "w") as f:
            f.write("Fichier dans sous-dossier")
            
        # Créer un autre sous-dossier à exclure
        excluded_dir = os.path.join(test_directory, "excluded")
        if not os.path.exists(excluded_dir):
            os.makedirs(excluded_dir)
            
        # Créer un fichier dans le sous-dossier à exclure
        with open(os.path.join(excluded_dir, "excluded.txt"), "w") as f:
            f.write("Ce fichier ne devrait pas être inclus")
            
        request_data = {
            "directories": [test_directory],
            "files": [],
            "rules": {
                "include_extensions": [],
                "exclude_extensions": [],
                "include_patterns": [],
                "exclude_patterns": [],
                "exclude_directories": ["excluded"]
            },
            "recursive": True
        }
        
        response = client.post("/api/v1/copy/advanced/scan", json=request_data)
        assert response.status_code == 200
        data = response.json()
        
        # Vérifier que les résultats n'incluent aucun fichier du sous-dossier exclu
        excluded_paths = [match["path"] for match in data["matches"]]
        assert not any("excluded" in path for path in excluded_paths)
        
        # Vérifier que les fichiers des autres sous-dossiers sont toujours inclus
        assert any("subdir" in path for path in excluded_paths)
        
        # Vérifier que le nombre total de fichiers est correct
        # Tous les fichiers sauf ceux dans "excluded"
        assert data["total_matches"] > 0
        
    def test_scan_with_multiple_excluded_directories(self, test_directory):
        """Test de scan avec plusieurs sous-dossiers exclus"""
        # Créer des sous-dossiers supplémentaires
        dirs_to_exclude = ["node_modules", "dist", ".git"]
        
        for dir_name in dirs_to_exclude:
            excluded_dir = os.path.join(test_directory, dir_name)
            if not os.path.exists(excluded_dir):
                os.makedirs(excluded_dir)
                
            # Créer un fichier dans chaque sous-dossier à exclure
            with open(os.path.join(excluded_dir, f"{dir_name}.txt"), "w") as f:
                f.write(f"Fichier dans {dir_name}")
        
        # Créer un sous-dossier qui ne sera pas exclu
        included_dir = os.path.join(test_directory, "src")
        if not os.path.exists(included_dir):
            os.makedirs(included_dir)
            
        # Créer un fichier dans le sous-dossier inclus
        with open(os.path.join(included_dir, "included.txt"), "w") as f:
            f.write("Ce fichier devrait être inclus")
        
        request_data = {
            "directories": [test_directory],
            "files": [],
            "rules": {
                "include_extensions": [],
                "exclude_extensions": [],
                "include_patterns": [],
                "exclude_patterns": [],
                "exclude_directories": dirs_to_exclude
            },
            "recursive": True
        }
        
        response = client.post("/api/v1/copy/advanced/scan", json=request_data)
        assert response.status_code == 200
        data = response.json()
        
        # Vérifier que les résultats n'incluent aucun fichier des sous-dossiers exclus
        paths = [match["path"] for match in data["matches"]]
        for excluded_dir in dirs_to_exclude:
            assert not any(f"/{excluded_dir}/" in path for path in paths)
            
        # Vérifier que le fichier du répertoire inclus est présent
        assert any("src/included.txt" in path for path in paths)
        
    def test_format_content_with_excluded_directories(self, test_directory):
        """Test de formatage du contenu avec exclusion de sous-dossiers"""
        # Préparer la structure de test
        test_dirs = {
            "include": ["src", "app"],
            "exclude": ["node_modules", "dist"]
        }
        
        # Créer les sous-dossiers et ajouter des fichiers
        for dir_type, dirs in test_dirs.items():
            for dir_name in dirs:
                dir_path = os.path.join(test_directory, dir_name)
                if not os.path.exists(dir_path):
                    os.makedirs(dir_path)
                
                # Ajouter un fichier texte dans chaque dossier
                with open(os.path.join(dir_path, f"{dir_name}.txt"), "w") as f:
                    f.write(f"Contenu du fichier dans {dir_name}")
        
        request_data = {
            "directories": [test_directory],
            "files": [],
            "rules": {
                "include_extensions": ["txt"],
                "exclude_extensions": [],
                "include_patterns": [],
                "exclude_patterns": [],
                "exclude_directories": test_dirs["exclude"]
            },
            "recursive": True
        }
        
        response = client.post("/api/v1/copy/advanced/format-content", json=request_data)
        assert response.status_code == 200
        data = response.json()
        
        # Vérifier que les fichiers des dossiers inclus sont présents
        for dir_name in test_dirs["include"]:
            assert f"{dir_name}.txt" in data["formatted_content"]
            assert f"Contenu du fichier dans {dir_name}" in data["formatted_content"]
            
        # Vérifier que les fichiers des dossiers exclus sont absents
        for dir_name in test_dirs["exclude"]:
            assert f"{dir_name}.txt" not in data["formatted_content"]
            assert f"Contenu du fichier dans {dir_name}" not in data["formatted_content"] 