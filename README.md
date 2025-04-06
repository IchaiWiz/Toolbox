# Toolbox

Ce dépôt contient un projet fullstack avec un frontend React et un backend Python qui fournit une boîte à outils pour diverses opérations sur les fichiers. Ces outils sont particulièrement pertinents pour travailler avec des modèles de langage (LLM) comme ChatGPT ou Claude, facilitant la préparation et l'organisation des données.

> **Note importante:** Actuellement, seul l'outil de copie avancée est implémenté et fonctionnel. Les autres outils (sauvegarde, analyse, WinMerge, détection de doublons, structuration par IA) sont en cours de développement.

## Prérequis

### Node.js

1. Téléchargez et installez Node.js depuis [le site officiel](https://nodejs.org/)
2. Vérifiez l'installation avec les commandes:
   ```
   node --version
   npm --version
   ```

### Python

1. Téléchargez et installez Python depuis [le site officiel](https://www.python.org/downloads/)
   - Sur Linux, vous pouvez utiliser votre gestionnaire de paquets (apt, yum, etc.)
2. Vérifiez l'installation avec la commande:
   ```
   python --version   # Sur Windows
   python3 --version  # Sur Linux/macOS (selon la configuration)
   ```

## Installation

1. Clonez le dépôt:
   ```
   git clone https://github.com/IchaiWiz/Toolbox
   ```

2. Accédez au dossier du projet:
   ```
   cd toolbox
   ```

3. Installez les dépendances du frontend:
   ```
   cd frontend
   npm install
   cd ..
   ```

4. Configurez l'environnement Python pour le backend:
   
   **Windows:**
   ```
   cd backend
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   cd ..
   ```
   
   **Linux/macOS:**
   ```
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   cd ..
   ```

## Lancement du projet

Pour lancer simultanément le frontend et le backend:

**Windows:**
```
cd frontend
npm run dev
```

**Linux/macOS:**
```
cd frontend
npm run dev
```

Cette commande va:
- Démarrer le serveur frontend (Vite)
- Activer l'environnement virtuel Python
- Démarrer le serveur backend (FastAPI avec Uvicorn)

> **Note:** Sur Linux/macOS, vous devrez peut-être modifier le script dans `package.json` pour utiliser la bonne commande d'activation de l'environnement virtuel. Remplacez `call venv/Scripts/activate` par `source venv/bin/activate` dans le script `backend`.

Le frontend sera accessible à l'adresse: http://localhost:5173
Le backend sera accessible à l'adresse: http://localhost:8000

## Tests

Pour exécuter les tests du backend Python:

```
cd backend
python -m pytest
```

Les tests vérifient le bon fonctionnement des routes API et des utilitaires.

## Fonctionnalités

### Outil de Copie Avancée (Disponible)

L'outil de copie permet de:
- Sélectionner des fichiers et dossiers à copier
- Exclure certains fichiers selon des extensions ou motifs
- Copier le contenu dans le presse-papier
- Gérer un historique des opérations de copie
- Obtenir des statistiques sur les fichiers copiés

Ces fonctionnalités sont particulièrement utiles pour préparer des données à soumettre aux LLM comme ChatGPT ou Claude, en permettant une sélection précise des fichiers de code source.

## Outils en développement

Les fonctionnalités suivantes sont prévues mais non encore implémentées:
- Sauvegarde de fichiers
- Analyse de fichiers
- Intégration avec WinMerge
- Détection de fichiers en double
- Structuration de fichiers assistée par IA 