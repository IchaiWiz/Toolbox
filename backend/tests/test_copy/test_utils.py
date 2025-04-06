import os
import pytest
import tempfile
import shutil
from pathlib import Path

from app.utils.file_utils import scan_directory, read_file_content, format_file_for_copy
from app.utils.path_utils import sanitize_path, is_valid_directory
from app.config import MAX_FILE_SIZE


class TestPathUtils:
    """Tests pour les utilitaires de chemins"""

    def test_sanitize_path(self):
        # Tester les chemins avec des caractères spéciaux
        assert sanitize_path(r'C:\test<>|?*.txt') == r'C:\test_____.txt'
        
        # Utiliser os.path.normpath pour gérer la différence Windows/Unix
        assert os.path.normpath(sanitize_path('/test/file<>|?*.txt')) == os.path.normpath('/test/file_____.txt')
        
        # Tester le cas basique (avec normpath pour compatibilité cross-platform)
        assert os.path.normpath(sanitize_path('/test/file.txt')) == os.path.normpath('/test/file.txt')
        
        # Tester les chemins relatifs
        assert sanitize_path('./file.txt') == str(Path('./file.txt'))
        
        # Tester les cas de normalisation
        input_path = '/test/../file.txt'
        expected = os.path.normpath('/file.txt')
        assert os.path.normpath(sanitize_path(input_path)) == expected

    def test_is_valid_directory(self):
        # Créer un répertoire temporaire pour le test
        with tempfile.TemporaryDirectory() as temp_dir:
            # Tester un répertoire valide
            assert is_valid_directory(temp_dir) is True
            
            # Tester un répertoire qui n'existe pas
            assert is_valid_directory(os.path.join(temp_dir, 'nonexistent')) is False
            
            # Tester un fichier (pas un répertoire)
            temp_file = os.path.join(temp_dir, 'test.txt')
            with open(temp_file, 'w') as f:
                f.write('test')
            assert is_valid_directory(temp_file) is False


class TestFileUtils:
    """Tests pour les utilitaires de fichiers"""
    
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
    
    def test_scan_directory_basic(self, test_directory):
        # Test de base sans filtres
        results = scan_directory(test_directory)
        
        # 6 fichiers au total dans notre structure
        assert len(results) == 6
        
        # Vérifier qu'ils ont tous les propriétés attendues
        for file in results:
            assert "path" in file
            assert "name" in file
            assert "size" in file
            assert "extension" in file
    
    def test_scan_directory_with_extensions(self, test_directory):
        """Test de la fonction scan_directory avec filtrage par extension"""
        # Exclure les fichiers .txt
        results = scan_directory(
            test_directory,
            exclude_extensions=["txt"],
            recursive=True
        )
        
        # Vérifier que les fichiers .txt sont exclus
        assert all(file["extension"] != "txt" for file in results)
        
        # Vérifier que les autres types de fichiers sont inclus
        assert any(file["extension"] == "py" for file in results)
    
    def test_scan_directory_with_patterns(self, test_directory):
        """Test de la fonction scan_directory avec filtrage par motifs"""
        # Exclure les fichiers contenant 'hidden'
        results = scan_directory(
            test_directory,
            exclude_patterns=["hidden"],
            recursive=True
        )
        
        # Vérifier que les fichiers contenant 'hidden' sont exclus
        assert all("hidden" not in file["name"] for file in results)
        
        # Vérifier que les autres fichiers sont inclus
        assert any("file1" in file["name"] for file in results)
    
    def test_scan_directory_non_recursive(self, test_directory):
        # Test sans récursion
        results = scan_directory(
            test_directory,
            recursive=False
        )
        
        # 4 fichiers au niveau racine
        assert len(results) == 4
        assert all("subdir" not in file["path"] for file in results)
    
    def test_read_file_content(self, test_directory):
        # Tester la lecture d'un fichier existant
        file_path = os.path.join(test_directory, "file1.txt")
        content = read_file_content(file_path)
        assert content == "Contenu du fichier 1"
        
        # Tester la lecture d'un fichier qui n'existe pas
        with pytest.raises(FileNotFoundError):
            read_file_content(os.path.join(test_directory, "nonexistent.txt"))
        
        # Créer un fichier qui dépasse MAX_FILE_SIZE
        large_file = os.path.join(test_directory, "large_file.txt")
        with open(large_file, 'w') as f:
            f.write('x' * (MAX_FILE_SIZE + 1))
        
        # Tester la lecture d'un fichier trop volumineux
        with pytest.raises(ValueError):
            read_file_content(large_file)
    
    def test_format_file_for_copy(self):
        # Tester le formatage du contenu
        formatted = format_file_for_copy("/path/to/file.txt", "Content")
        assert formatted == "=== /path/to/file.txt ===\n\nContent\n\n---\n\n"
        
        # Tester avec un contenu vide
        formatted = format_file_for_copy("/path/to/empty.txt", "")
        assert formatted == "=== /path/to/empty.txt ===\n\n\n\n---\n\n" 