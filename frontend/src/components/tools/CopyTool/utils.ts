import { CopyConfig, ScanRequestPayload } from './types';

/**
 * Convertir une configuration CopyConfig en payload pour les requêtes API
 */
export const createApiPayload = (config: CopyConfig): ScanRequestPayload => ({
  directories: config.directories,
  files: config.files,
  rules: {
    include_extensions: [], // Non utilisé dans la configuration actuelle
    exclude_extensions: config.excludeExtensions,
    include_patterns: [], // Non utilisé dans la configuration actuelle
    exclude_patterns: config.excludePatterns,
    exclude_directories: config.excludeDirectories
  },
  recursive: config.recursive
});

/**
 * Retourne un aperçu tronqué d'un texte
 */
export const truncateText = (text: string, maxLength: number = 50): string => {
  if (!text || text.length <= maxLength) return text;
  return `${text.substring(0, maxLength)}...`;
};

/**
 * Formate la date de manière lisible (sans l'heure)
 */
export const formatDate = (timestamp: number): string => {
  return new Date(timestamp).toLocaleString('fr-FR', {
    day: '2-digit',
    month: '2-digit',
    year: '2-digit'
  });
};

/**
 * Formate l'heure de manière lisible
 */
export const formatTime = (timestamp: number): string => {
  return new Date(timestamp).toLocaleString('fr-FR', {
    hour: '2-digit',
    minute: '2-digit'
  });
}; 