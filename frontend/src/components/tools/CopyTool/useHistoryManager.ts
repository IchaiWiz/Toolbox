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
    
    // Ajouter à l'historique et limiter à MAX_HISTORY_ITEMS éléments
    const newHistory = [
      configWithTimestamp, 
      ...history.filter(item => item.id !== configToSave.id)
    ].slice(0, MAX_HISTORY_ITEMS);
    
    setHistory(newHistory);
  };

  /**
   * Vider l'historique
   */
  const clearHistory = () => setHistory([]);

  return {
    history,
    saveToHistory,
    clearHistory
  };
} 