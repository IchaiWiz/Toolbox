# Toolbox

This repository contains a fullstack project with a React frontend and a Python backend that provides a toolbox for various file operations. These tools are particularly relevant for working with language models (LLMs) like ChatGPT or Claude, facilitating data preparation and organization.

> **Important note:** Currently, only the advanced copy tool is implemented and functional. Other tools (backup, analysis, WinMerge, duplicate detection, AI structuring) are under development.

## Prerequisites

### Node.js

1. Download and install Node.js from [the official website](https://nodejs.org/)
2. Verify the installation with the commands:
   ```
   node --version
   npm --version
   ```

### Python

1. Download and install Python from [the official website](https://www.python.org/downloads/)
   - On Linux, you can use your package manager (apt, yum, etc.)
2. Verify the installation with the command:
   ```
   python --version   # On Windows
   python3 --version  # On Linux/macOS (depending on configuration)
   ```

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/IchaiWiz/Toolbox
   ```

2. Navigate to the project folder:
   ```
   cd toolbox
   ```

3. Install frontend dependencies:
   ```
   cd frontend
   npm install
   cd ..
   ```

4. Configure the Python environment for the backend:
   
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

## Starting the project

To launch both the frontend and backend simultaneously:

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

This command will:
- Start the frontend server (Vite)
- Activate the Python virtual environment
- Start the backend server (FastAPI with Uvicorn)

> **Note:** On Linux/macOS, you may need to modify the script in `package.json` to use the correct virtual environment activation command. Replace `call venv/Scripts/activate` with `source venv/bin/activate` in the `dev` script.

The frontend will be accessible at: http://localhost:5173
The backend will be accessible at: http://localhost:8000

## Tests

To run the Python backend tests:

```
cd backend
python -m pytest
```

The tests verify the proper functioning of API routes and utilities.

## Features

### Advanced Copy Tool (Available)

The copy tool allows you to:
- Select files and folders to copy
- Exclude certain files based on extensions or patterns
- Copy content to the clipboard
- Manage a history of copy operations
- Get statistics on copied files

These features are particularly useful for preparing data to submit to LLMs like ChatGPT or Claude, by allowing precise selection of source code files.

## Tools in development

The following features are planned but not yet implemented:
- File backup
- File analysis
- WinMerge integration
- Duplicate file detection
- AI-assisted file structuring 