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
 * Service API pour interagir avec le backend
 */
export const copyToolApi = {
  /**
   * Scanner les fichiers selon les critères spécifiés
   */
  async scanFiles(payload: ScanRequestPayload): Promise<{ matches: FileMatch[]; totalMatches: number; totalSubdirectories: number }> {
    const response = await fetch(`${API_BASE_URL}/scan`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "Erreur lors du scan des fichiers");
    }
    
    const data = await response.json();
    return {
      matches: data.matches || [],
      totalMatches: data.total_matches || 0,
      totalSubdirectories: data.total_subdirectories || 0
    };
  },
  
  /**
   * Récupérer et formater le contenu des fichiers
   */
  async formatContent(payload: ScanRequestPayload): Promise<string> {
    const response = await fetch(`${API_BASE_URL}/format-content`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "Erreur lors de la récupération du contenu");
    }
    
    const data = await response.json();
    if (!data.formatted_content) {
      throw new Error("Aucun contenu formaté disponible");
    }
    
    return data.formatted_content;
  },
  
  /**
   * Analyse complète pour obtenir à la fois les fichiers correspondants et leur contenu formaté
   */
  async analyzeFiles(payload: ScanRequestPayload): Promise<CopyResult> {
    // 1. Obtenir la liste des fichiers correspondants
    const scanResult = await this.scanFiles(payload);
    
    // Calculer la taille totale et les statistiques par extension
    let totalSize = 0;
    const extensionCount: Record<string, number> = {};
    
    if (scanResult.matches.length > 0) {
      totalSize = scanResult.matches.reduce((sum, file) => sum + file.size, 0);
      
      scanResult.matches.forEach(file => {
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
        const formattedContent = await this.formatContent(payload);
        
        // Calculer les statistiques textuelles
        const textStats = calculateTextStats(formattedContent);
        stats.totalLines = textStats.lines;
        stats.totalWords = textStats.words;
        stats.totalChars = textStats.chars;
        
        return {
          matches: scanResult.matches,
          totalMatches: scanResult.totalMatches,
          formattedContent,
          stats
        };
      } catch (error) {
        console.error("Erreur lors de la récupération du contenu formaté:", error);
        // En cas d'erreur, retourner un résultat sans contenu formaté
        return {
          matches: scanResult.matches,
          totalMatches: scanResult.totalMatches,
          formattedContent: "",
          stats
        };
      }
    }
    
    // Aucun fichier trouvé
    return {
      matches: [],
      totalMatches: 0,
      formattedContent: "",
      stats
    };
  }
}; 