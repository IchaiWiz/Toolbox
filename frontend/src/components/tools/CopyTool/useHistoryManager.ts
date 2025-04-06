import { useState, useEffect } from 'react';
import { CopyConfig, MAX_HISTORY_ITEMS, STORAGE_KEY } from './types';

/**
 * Hook pour gérer l'historique des configurations de copie
 */
export function useHistoryManager() {
  const [history, setHistory] = useState<CopyConfig[]>([]);

  // Charger l'historique au montage du composant
  useEffect(() => {
    try {
      const storedHistory = localStorage.getItem(STORAGE_KEY);
      if (storedHistory) {
        setHistory(JSON.parse(storedHistory));
      }
    } catch (e) {
      console.error("Erreur lors du chargement de l'historique:", e);
    }
  }, []);

  // Sauvegarder l'historique quand il change
  useEffect(() => {
    if (history.length > 0) {
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(history));
      } catch (e) {
        console.error("Erreur lors de la sauvegarde de l'historique:", e);
      }
    }
  }, [history]);

  /**
   * Ajouter ou mettre à jour une configuration dans l'historique
   */
  const saveToHistory = (configToSave: CopyConfig) => {
    // Ne sauvegarder que si la configuration contient au moins des dossiers ou des fichiers
    if (configToSave.directories.length === 0 && configToSave.files.length === 0) {
      return;
    }
    
    // Mettre à jour le timestamp
    const configWithTimestamp = {
      ...configToSave,
      timestamp: Date.now()
    };
    
    // Conserver l'état favori si la configuration existe déjà
    const existingConfig = history.find(item => item.id === configToSave.id);
    if (existingConfig && existingConfig.isFavorite) {
      configWithTimestamp.isFavorite = existingConfig.isFavorite;
    }
    
    // Ajouter à l'historique et limiter à MAX_HISTORY_ITEMS éléments
    // Les favoris sont toujours conservés en premier
    const nonFavorites = history
      .filter(item => item.id !== configToSave.id && !item.isFavorite)
      .sort((a, b) => b.timestamp - a.timestamp);
    
    const favorites = history
      .filter(item => item.id !== configToSave.id && item.isFavorite)
      .sort((a, b) => b.timestamp - a.timestamp);
    
    let newHistory = [configWithTimestamp];
    
    // Ajouter d'abord les favoris puis les non-favoris
    newHistory = [...newHistory, ...favorites, ...nonFavorites];
    
    // Limiter le nombre total d'éléments
    newHistory = newHistory.slice(0, MAX_HISTORY_ITEMS);
    
    setHistory(newHistory);
  };

  /**
   * Marquer/démarquer une configuration comme favorite
   */
  const toggleFavorite = (id: string) => {
    const newHistory = history.map(item => {
      if (item.id === id) {
        return {
          ...item,
          isFavorite: !item.isFavorite
        };
      }
      return item;
    });
    
    // Réordonner pour que les favoris apparaissent en premier
    const favorites = newHistory.filter(item => item.isFavorite);
    const nonFavorites = newHistory.filter(item => !item.isFavorite);
    
    setHistory([...favorites, ...nonFavorites]);
  };

  /**
   * Vider l'historique
   */
  const clearHistory = () => setHistory([]);

  return {
    history,
    saveToHistory,
    toggleFavorite,
    clearHistory
  };
} 