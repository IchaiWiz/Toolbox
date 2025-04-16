export interface CopyConfig {
  id: string;
  directories: string[];
  files: string[];
  excludeExtensions: string[];
  excludePatterns: string[];
  excludeDirectories: string[];
  recursive: boolean;
  timestamp: number;
  name?: string;
  isFavorite?: boolean;
}

export interface FileMatch {
  path: string;
  name: string;
  size: number;
  extension: string;
}

export interface PathError {
  original_path: string;
  clean_path: string;
  error_type: string;
  message: string;
}

export interface FileStats {
  totalLines: number;
  totalWords: number;
  totalChars: number;
  fileCount: number;
  folderCount: number;
  totalSubdirectories: number;
  totalSize: number;
  totalSizeFormatted: string;
  byExtension: Record<string, number>;
}

export interface CopyResult {
  matches: FileMatch[];
  totalMatches: number;
  formattedContent: string;
  stats: FileStats;
  invalid_paths?: PathError[];
}

// API payload types
export interface ScanRequestPayload {
  directories: string[];
  files: string[];
  rules: {
    include_extensions: string[];
    exclude_extensions: string[];
    include_patterns: string[];
    exclude_patterns: string[];
    exclude_directories: string[];
  };
  recursive: boolean;
}

// Constants
export const MAX_HISTORY_ITEMS = 20;
export const STORAGE_KEY = "copy-tool-history";
export const API_BASE_URL = "http://localhost:8000/api/v1/copy/advanced";

// Dossiers communs à exclure par défaut
export const DEFAULT_EXCLUDED_DIRECTORIES = [
  "node_modules",
  "__pycache__",
  ".git",
  ".venv",
  "venv",
  "env",
  "dist",
  "build",
  ".cache",
  ".idea",
  ".vs",
  ".vscode",
  "coverage",
  "tmp",
  "temp",
  ".vite",
  "vendor"
];

// Motifs communs à exclure par défaut
export const DEFAULT_EXCLUDED_PATTERNS = [
  "package-lock.json",
  "yarn.lock",
  "pnpm-lock.yaml",
  ".DS_Store",
  "Thumbs.db",
  ".pyc$",
  ".pyo$",
  ".log$",
  ".bak$",
  ".swp$",
  "~$",
  ".tmp$",
  ".gitignore",
  "components.json",
  "eslint.config.js",
  "vite-env.d.ts"
];

// Fonction pour créer une configuration vide
export const createEmptyConfig = (): CopyConfig => ({
  id: crypto.randomUUID(),
  directories: [],
  files: [],
  excludeExtensions: [],
  excludePatterns: [...DEFAULT_EXCLUDED_PATTERNS],
  excludeDirectories: [...DEFAULT_EXCLUDED_DIRECTORIES],
  recursive: true,
  timestamp: Date.now(),
  isFavorite: false
}); 