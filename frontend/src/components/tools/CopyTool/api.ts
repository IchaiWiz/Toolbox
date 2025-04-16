import { CopyResult, FileMatch, FileStats, ScanRequestPayload, API_BASE_URL } from './types';

/**
 * Formater la taille des fichiers en unités lisibles
 */
export const formatFileSize = (bytes: number): string => {
  if (bytes < 1024) {
    return `${bytes} octets`;
  } else if (bytes < 1024 * 1024) {
    return `${(bytes / 1024).toFixed(1)} Ko`;
  } else {
    return `${(bytes / (1024 * 1024)).toFixed(1)} Mo`;
  }
};

/**
 * Calculer les statistiques textuelles d'un contenu formaté
 */
export const calculateTextStats = (formattedContent: string): { lines: number; words: number; chars: number } => {
  const lines = formattedContent.split('\n').length;
  const words = formattedContent.split(/\s+/).filter(Boolean).length;
  const chars = formattedContent.length;
  
  return { lines, words, chars };
};

/**
 * Activer les logs détaillés pour le débogage
 */
const ENABLE_DEBUG_LOGGING = import.meta.env.VITE_DEBUG_MODE === 'true';

/**
 * Logger personnalisé pour l'API
 */
const apiLogger = {
  info: (message: string) => {
    if (ENABLE_DEBUG_LOGGING) {
      console.info(`[CopyTool API] ${message}`);
    }
  },
  error: (message: string, error?: any) => {
    console.error(`[CopyTool API ERROR] ${message}`, error || '');
  },
  warn: (message: string) => {
    if (ENABLE_DEBUG_LOGGING) {
      console.warn(`[CopyTool API] ${message}`);
    }
  },
  debug: (message: string, data?: any) => {
    if (ENABLE_DEBUG_LOGGING) {
      console.debug(`[CopyTool API] ${message}`, data || '');
    }
  }
};

/**
 * Service API pour interagir avec le backend
 */
export const copyToolApi = {
  /**
   * Scanner les fichiers selon les critères spécifiés
   */
  async scanFiles(payload: ScanRequestPayload): Promise<{ matches: FileMatch[]; totalMatches: number; totalSubdirectories: number }> {
    apiLogger.info(`Début du scan des fichiers: ${payload.directories.length} dossiers, ${payload.files.length} fichiers`);
    apiLogger.debug('Payload de requête:', payload);
    
    const startTime = performance.now();
    
    try {
      const response = await fetch(`${API_BASE_URL}/scan`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        const errorMessage = errorData.detail || "Erreur lors du scan des fichiers";
        apiLogger.error(`Erreur HTTP ${response.status}: ${errorMessage}`);
        throw new Error(errorMessage);
      }
      
      const data = await response.json();
      const endTime = performance.now();
      
      apiLogger.info(`Scan terminé en ${(endTime - startTime).toFixed(2)}ms: ${data.total_matches || 0} fichiers trouvés`);
      
      if (data.invalid_paths && data.invalid_paths.length > 0) {
        apiLogger.warn(`${data.invalid_paths.length} chemins avec des erreurs d'accès`);
      }
      
      return {
        matches: data.matches || [],
        totalMatches: data.total_matches || 0,
        totalSubdirectories: data.total_subdirectories || 0
      };
    } catch (error) {
      const endTime = performance.now();
      apiLogger.error(`Échec du scan après ${(endTime - startTime).toFixed(2)}ms`, error);
      throw error;
    }
  },
  
  /**
   * Récupérer et formater le contenu des fichiers
   */
  async formatContent(payload: ScanRequestPayload): Promise<string> {
    apiLogger.info(`Début du formatage du contenu: ${payload.directories.length} dossiers, ${payload.files.length} fichiers`);
    
    const startTime = performance.now();
    
    try {
      const response = await fetch(`${API_BASE_URL}/format-content`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        const errorMessage = errorData.detail || "Erreur lors de la récupération du contenu";
        apiLogger.error(`Erreur HTTP ${response.status}: ${errorMessage}`);
        throw new Error(errorMessage);
      }
      
      const data = await response.json();
      const endTime = performance.now();
      
      if (!data.formatted_content) {
        apiLogger.error("Aucun contenu formaté n'a été retourné");
        throw new Error("Aucun contenu formaté disponible");
      }
      
      const contentStats = calculateTextStats(data.formatted_content);
      apiLogger.info(`Formatage terminé en ${(endTime - startTime).toFixed(2)}ms: ${contentStats.lines} lignes`);
      
      if (data.invalid_paths && data.invalid_paths.length > 0) {
        apiLogger.warn(`${data.invalid_paths.length} chemins avec des erreurs d'accès`);
      }
      
      return data.formatted_content;
    } catch (error) {
      const endTime = performance.now();
      apiLogger.error(`Échec du formatage après ${(endTime - startTime).toFixed(2)}ms`, error);
      throw error;
    }
  },
  
  /**
   * Analyse complète pour obtenir à la fois les fichiers correspondants et leur contenu formaté
   */
  async analyzeFiles(payload: ScanRequestPayload): Promise<CopyResult> {
    apiLogger.info(`Début de l'analyse complète: ${payload.directories.length} dossiers, ${payload.files.length} fichiers`);
    apiLogger.debug(`Dossiers: ${payload.directories.join(', ')}`);
    
    const startTime = performance.now();
    
    try {
      // 1. Obtenir la liste des fichiers correspondants
      apiLogger.info("Étape 1: Scan des fichiers");
      const response = await fetch(`${API_BASE_URL}/scan`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        const errorMessage = errorData.detail || "Erreur lors du scan des fichiers";
        apiLogger.error(`Erreur HTTP ${response.status}: ${errorMessage}`);
        throw new Error(errorMessage);
      }
      
      const data = await response.json();
      const scanTime = performance.now();
      apiLogger.info(`Scan terminé en ${(scanTime - startTime).toFixed(2)}ms: ${data.total_matches || 0} fichiers trouvés`);
      
      const scanResult = {
        matches: data.matches || [],
        totalMatches: data.total_matches || 0,
        totalSubdirectories: data.total_subdirectories || 0,
        invalid_paths: data.invalid_paths || []
      };
      
      if (scanResult.invalid_paths.length > 0) {
        apiLogger.warn(`${scanResult.invalid_paths.length} chemins avec des erreurs d'accès pendant le scan`);
        apiLogger.debug("Chemins problématiques:", scanResult.invalid_paths);
      }
      
      // Calculer la taille totale et les statistiques par extension
      let totalSize = 0;
      const extensionCount: Record<string, number> = {};
      
      if (scanResult.matches.length > 0) {
        totalSize = scanResult.matches.reduce((sum: number, file: FileMatch) => sum + file.size, 0);
        
        scanResult.matches.forEach((file: FileMatch) => {
          const ext = file.extension || "sans extension";
          extensionCount[ext] = (extensionCount[ext] || 0) + 1;
        });
      }
      
      // Stats de base avec les informations disponibles
      const stats: FileStats = {
        totalLines: 0,
        totalWords: 0,
        totalChars: 0,
        fileCount: scanResult.totalMatches,
        folderCount: payload.directories.length,
        totalSubdirectories: scanResult.totalSubdirectories,
        totalSize,
        totalSizeFormatted: formatFileSize(totalSize),
        byExtension: extensionCount
      };
      
      // 2. Obtenir le contenu formaté si des fichiers ont été trouvés
      if (scanResult.matches.length > 0) {
        try {
          apiLogger.info("Étape 2: Formatage du contenu");
          const formatResponse = await fetch(`${API_BASE_URL}/format-content`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
          });
          
          if (!formatResponse.ok) {
            const errorData = await formatResponse.json();
            apiLogger.error(`Erreur HTTP ${formatResponse.status} lors du formatage: ${errorData.detail || "Erreur inconnue"}`);
            
            // Même en cas d'erreur, on retourne les fichiers trouvés
            apiLogger.info("Retour des fichiers sans contenu formaté");
            const endTime = performance.now();
            apiLogger.info(`Analyse terminée en ${(endTime - startTime).toFixed(2)}ms avec erreur de formatage`);
            
            return {
              matches: scanResult.matches,
              totalMatches: scanResult.totalMatches,
              formattedContent: "",
              stats,
              invalid_paths: scanResult.invalid_paths
            };
          }
          
          const formatData = await formatResponse.json();
          const formattedContent = formatData.formatted_content || "";
          const formatTime = performance.now();
          apiLogger.info(`Formatage terminé en ${(formatTime - scanTime).toFixed(2)}ms`);
          
          // Ajouter les erreurs de chemin supplémentaires
          if (formatData.invalid_paths && formatData.invalid_paths.length > 0) {
            apiLogger.warn(`${formatData.invalid_paths.length} chemins avec des erreurs d'accès pendant le formatage`);
            
            // Fusionner les chemins invalides, en évitant les doublons
            const existingPaths = new Set(scanResult.invalid_paths.map((p: any) => p.original_path));
            
            for (const invalidPath of formatData.invalid_paths) {
              if (!existingPaths.has(invalidPath.original_path)) {
                scanResult.invalid_paths.push(invalidPath);
                existingPaths.add(invalidPath.original_path);
              }
            }
          }
          
          // Calculer les statistiques textuelles
          const textStats = calculateTextStats(formattedContent);
          stats.totalLines = textStats.lines;
          stats.totalWords = textStats.words;
          stats.totalChars = textStats.chars;
          
          const endTime = performance.now();
          apiLogger.info(`Analyse complète terminée en ${(endTime - startTime).toFixed(2)}ms`);
          
          return {
            matches: scanResult.matches,
            totalMatches: scanResult.totalMatches,
            formattedContent,
            stats,
            invalid_paths: scanResult.invalid_paths
          };
        } catch (error) {
          apiLogger.error("Erreur lors de la récupération du contenu formaté:", error);
          
          // En cas d'erreur, retourner un résultat sans contenu formaté
          const endTime = performance.now();
          apiLogger.info(`Analyse terminée en ${(endTime - startTime).toFixed(2)}ms avec exception de formatage`);
          
          return {
            matches: scanResult.matches,
            totalMatches: scanResult.totalMatches,
            formattedContent: "",
            stats,
            invalid_paths: scanResult.invalid_paths
          };
        }
      }
      
      // Aucun fichier trouvé
      const endTime = performance.now();
      apiLogger.info(`Analyse terminée en ${(endTime - startTime).toFixed(2)}ms: aucun fichier trouvé`);
      
      return {
        matches: [],
        totalMatches: 0,
        formattedContent: "",
        stats,
        invalid_paths: scanResult.invalid_paths
      };
    } catch (error) {
      apiLogger.error("Erreur lors de l'analyse des fichiers:", error);
      
      const endTime = performance.now();
      apiLogger.error(`Échec de l'analyse après ${(endTime - startTime).toFixed(2)}ms`, error);
      
      // En cas d'erreur globale, retourner un résultat vide mais ne pas bloquer l'interface
      return {
        matches: [],
        totalMatches: 0,
        formattedContent: "",
        stats: {
          totalLines: 0,
          totalWords: 0,
          totalChars: 0,
          fileCount: 0,
          folderCount: payload.directories.length,
          totalSubdirectories: 0,
          totalSize: 0,
          totalSizeFormatted: "0 octets",
          byExtension: {}
        },
        invalid_paths: [{
          original_path: "Analyse globale",
          clean_path: "",
          error_type: "error",
          message: error instanceof Error ? error.message : "Erreur inconnue lors de l'analyse"
        }]
      };
    }
  }
}; 