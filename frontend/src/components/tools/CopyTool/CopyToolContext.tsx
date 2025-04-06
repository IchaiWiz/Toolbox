import { createContext, useState, useEffect, useContext, ReactNode } from "react";
import { CopyConfig, CopyResult, createEmptyConfig } from "./types";
import { useHistoryManager } from "./useHistoryManager";
import { copyToolApi } from "./api";
import { createApiPayload } from "./utils";
import { useTabs } from "@/contexts/TabsContext";

// Clés de stockage local pour l'état de l'outil
const STORAGE_KEY_CONFIG = "copy-tool-current-config";
const STORAGE_KEY_RESULTS = "copy-tool-current-results";
const STORAGE_KEY_TAB_CONFIG = "copy-tool-tab-configs"; // Pour stocker les configs par onglet
const STORAGE_KEY_TAB_RESULTS = "copy-tool-tab-results"; // Pour stocker les résultats par onglet
const STORAGE_KEY_EXISTING_TABS = "copy-tool-existing-tabs"; // Pour suivre les onglets qui existent déjà

interface CopyToolContextType {
  // État
  config: CopyConfig;
  history: CopyConfig[];
  results: CopyResult | null;
  isLoading: boolean;
  error: string | null;
  copied: boolean;
  
  // Entrées de formulaire
  directoryInput: string;
  fileInput: string;
  extensionInput: string;
  patternInput: string;
  excludeDirectoryInput: string;
  
  // Setters
  setConfig: (config: CopyConfig) => void;
  setDirectoryInput: (value: string) => void;
  setFileInput: (value: string) => void;
  setExtensionInput: (value: string) => void;
  setPatternInput: (value: string) => void;
  setExcludeDirectoryInput: (value: string) => void;
  
  // Actions
  addDirectory: () => void;
  addFile: () => void;
  addExcludeExtension: () => void;
  addExcludePattern: () => void;
  addExcludeDirectory: () => void;
  removeItem: (list: keyof CopyConfig, index: number) => void;
  editItem: (list: keyof CopyConfig, index: number, newValue: string) => void;
  toggleRecursive: (checked: boolean) => void;
  resetConfig: () => void;
  loadFromHistory: (config: CopyConfig) => void;
  clearHistory: () => void;
  toggleFavorite: (id: string) => void;
  scanFiles: () => Promise<void>;
  copyToClipboard: () => Promise<void>;
}

// Exporter le contexte pour qu'il puisse être vérifié dans d'autres composants
export const CopyToolContext = createContext<CopyToolContextType | undefined>(undefined);

export function useCopyTool() {
  const context = useContext(CopyToolContext);
  if (!context) {
    throw new Error("useCopyTool doit être utilisé dans un CopyToolProvider");
  }
  return context;
}

interface CopyToolProviderProps {
  children: ReactNode;
}

export function CopyToolProvider({ children }: CopyToolProviderProps) {
  // Obtenir l'onglet actif pour suivre les changements
  const { activeTab } = useTabs();

  // État local
  const [config, setConfig] = useState<CopyConfig>(createEmptyConfig());
  const [results, setResults] = useState<CopyResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const [initialized, setInitialized] = useState(false); // État pour suivre l'initialisation
  const [existingTabs, setExistingTabs] = useState<string[]>([]);

  // Entrées de formulaire
  const [directoryInput, setDirectoryInput] = useState("");
  const [fileInput, setFileInput] = useState("");
  const [extensionInput, setExtensionInput] = useState("");
  const [patternInput, setPatternInput] = useState("");
  const [excludeDirectoryInput, setExcludeDirectoryInput] = useState("");

  // Utiliser le hook de gestion d'historique
  const { history, saveToHistory, clearHistory, toggleFavorite } = useHistoryManager();

  // Charger la liste des onglets existants
  useEffect(() => {
    try {
      const savedExistingTabs = localStorage.getItem(STORAGE_KEY_EXISTING_TABS);
      if (savedExistingTabs) {
        setExistingTabs(JSON.parse(savedExistingTabs));
      }
      setInitialized(true);
    } catch (error) {
      console.error("Erreur lors du chargement des onglets existants:", error);
      setInitialized(true);
    }
  }, []);

  // Sauvegarder la liste des onglets existants
  useEffect(() => {
    if (!initialized) return;
    
    try {
      localStorage.setItem(STORAGE_KEY_EXISTING_TABS, JSON.stringify(existingTabs));
    } catch (error) {
      console.error("Erreur lors de la sauvegarde des onglets existants:", error);
    }
  }, [existingTabs, initialized]);

  // Charger la configuration depuis le stockage local ou utiliser une configuration vide
  useEffect(() => {
    if (!initialized || !activeTab) return;
    
    try {
      // Vérifier si l'onglet actif existe déjà dans notre liste
      const isNewTab = !existingTabs.includes(activeTab);
      
      // Charger les configurations par onglet
      const tabConfigs = JSON.parse(localStorage.getItem(STORAGE_KEY_TAB_CONFIG) || '{}');
      const tabResults = JSON.parse(localStorage.getItem(STORAGE_KEY_TAB_RESULTS) || '{}');
      
      if (isNewTab) {
        // Pour un nouvel onglet, utiliser une configuration vide et aucun résultat
        setConfig(createEmptyConfig());
        setResults(null);
        
        // Ajouter l'onglet à la liste des onglets existants
        setExistingTabs(prev => [...prev, activeTab]);
      } else if (tabConfigs[activeTab]) {
        // Pour un onglet existant, charger sa configuration spécifique
        setConfig(tabConfigs[activeTab]);
        
        // Charger les résultats spécifiques à l'onglet, s'ils existent
        if (tabResults[activeTab]) {
          setResults(tabResults[activeTab]);
        } else {
          setResults(null);
        }
      }
    } catch (error) {
      console.error("Erreur lors du chargement de la configuration:", error);
    }
  }, [activeTab, initialized, existingTabs]);

  // Sauvegarder les résultats dans le stockage local quand ils changent
  useEffect(() => {
    if (!initialized || !activeTab) return;
    
    try {
      // Sauvegarder les résultats globalement (pour compatibilité)
      if (results) {
        localStorage.setItem(STORAGE_KEY_RESULTS, JSON.stringify(results));
      } else {
        localStorage.removeItem(STORAGE_KEY_RESULTS);
      }
      
      // Sauvegarder les résultats spécifiques à l'onglet
      const tabResults = JSON.parse(localStorage.getItem(STORAGE_KEY_TAB_RESULTS) || '{}');
      if (results) {
        tabResults[activeTab] = results;
      } else {
        delete tabResults[activeTab];
      }
      localStorage.setItem(STORAGE_KEY_TAB_RESULTS, JSON.stringify(tabResults));
    } catch (error) {
      console.error("Erreur lors de la sauvegarde des résultats:", error);
    }
  }, [results, activeTab, initialized]);
  
  // Sauvegarder la configuration dans le stockage local quand elle change
  useEffect(() => {
    if (!initialized || !activeTab) return;
    
    try {
      // Sauvegarder comme configuration globale
      localStorage.setItem(STORAGE_KEY_CONFIG, JSON.stringify(config));
      
      // Sauvegarder aussi comme configuration spécifique à l'onglet
      const tabConfigs = JSON.parse(localStorage.getItem(STORAGE_KEY_TAB_CONFIG) || '{}');
      tabConfigs[activeTab] = config;
      localStorage.setItem(STORAGE_KEY_TAB_CONFIG, JSON.stringify(tabConfigs));
    } catch (error) {
      console.error("Erreur lors de la sauvegarde de la configuration:", error);
    }
  }, [config, activeTab, initialized]);

  // Réinitialiser le statut de copie après un délai
  useEffect(() => {
    if (copied) {
      const timer = setTimeout(() => setCopied(false), 2000);
      return () => clearTimeout(timer);
    }
  }, [copied]);

  // Ajouter un répertoire à la configuration
  const addDirectory = () => {
    if (!directoryInput.trim()) return;
    
    if (!config.directories.includes(directoryInput)) {
      setConfig({
        ...config,
        directories: [...config.directories, directoryInput]
      });
    }
    
    setDirectoryInput("");
  };

  // Ajouter un fichier à la configuration
  const addFile = () => {
    if (!fileInput.trim()) return;
    
    if (!config.files.includes(fileInput)) {
      setConfig({
        ...config,
        files: [...config.files, fileInput]
      });
    }
    
    setFileInput("");
  };

  // Ajouter une extension à exclure
  const addExcludeExtension = () => {
    if (!extensionInput.trim()) return;
    
    // Nettoyer l'extension (enlever le . au début si présent)
    const extension = extensionInput.trim().startsWith(".") 
      ? extensionInput.trim().substring(1) 
      : extensionInput.trim();
      
    if (!config.excludeExtensions.includes(extension)) {
      setConfig({
        ...config,
        excludeExtensions: [...config.excludeExtensions, extension]
      });
    }
    
    setExtensionInput("");
  };

  // Ajouter un motif à exclure
  const addExcludePattern = () => {
    if (!patternInput.trim()) return;
    
    if (!config.excludePatterns.includes(patternInput)) {
      setConfig({
        ...config,
        excludePatterns: [...config.excludePatterns, patternInput]
      });
    }
    
    setPatternInput("");
  };

  // Ajouter un dossier à exclure
  const addExcludeDirectory = () => {
    if (!excludeDirectoryInput.trim()) return;
    
    if (!config.excludeDirectories.includes(excludeDirectoryInput)) {
      setConfig({
        ...config,
        excludeDirectories: [...config.excludeDirectories, excludeDirectoryInput]
      });
    }
    
    setExcludeDirectoryInput("");
  };

  // Supprimer un élément d'une liste
  const removeItem = (list: keyof CopyConfig, index: number) => {
    if (Array.isArray(config[list])) {
      const newList = [...(config[list] as string[])];
      newList.splice(index, 1);
      setConfig({
        ...config,
        [list]: newList
      });
    }
  };

  // Éditer un élément dans une liste
  const editItem = (list: keyof CopyConfig, index: number, newValue: string) => {
    if (Array.isArray(config[list]) && newValue.trim()) {
      const newList = [...(config[list] as string[])];
      newList[index] = newValue.trim();
      setConfig({
        ...config,
        [list]: newList
      });
    }
  };

  // Mettre à jour la valeur du champ récursif
  const toggleRecursive = (checked: boolean) => {
    setConfig({
      ...config,
      recursive: checked
    });
  };

  // Réinitialiser la configuration
  const resetConfig = () => {
    const newConfig = createEmptyConfig();
    setConfig(newConfig);
    setResults(null);
    setError(null);
    
    // Mettre à jour la configuration pour l'onglet actuel dans le stockage local
    if (activeTab) {
      try {
        // Mettre à jour la configuration
        const tabConfigs = JSON.parse(localStorage.getItem(STORAGE_KEY_TAB_CONFIG) || '{}');
        tabConfigs[activeTab] = newConfig;
        localStorage.setItem(STORAGE_KEY_TAB_CONFIG, JSON.stringify(tabConfigs));
        
        // Supprimer les résultats
        const tabResults = JSON.parse(localStorage.getItem(STORAGE_KEY_TAB_RESULTS) || '{}');
        delete tabResults[activeTab];
        localStorage.setItem(STORAGE_KEY_TAB_RESULTS, JSON.stringify(tabResults));
      } catch (error) {
        console.error("Erreur lors de la mise à jour de la configuration pour l'onglet:", error);
      }
    }
  };

  // Charger une configuration depuis l'historique
  const loadFromHistory = (historicConfig: CopyConfig) => {
    // S'assurer que tous les champs sont présents, même les nouveaux champs
    const completeConfig = {
      ...createEmptyConfig(), // Commence avec une configuration complète
      ...historicConfig,      // Écrase avec les valeurs historiques
      // S'assurer que le champ excludeDirectories existe
      excludeDirectories: historicConfig.excludeDirectories || []
    };
    
    setConfig(completeConfig);
    
    // Sauvegarder explicitement pour l'onglet actuel
    if (activeTab) {
      try {
        const tabConfigs = JSON.parse(localStorage.getItem(STORAGE_KEY_TAB_CONFIG) || '{}');
        tabConfigs[activeTab] = completeConfig;
        localStorage.setItem(STORAGE_KEY_TAB_CONFIG, JSON.stringify(tabConfigs));
      } catch (error) {
        console.error("Erreur lors de la sauvegarde de la configuration pour l'onglet:", error);
      }
    }
  };

  // Scanner les fichiers selon la configuration
  const scanFiles = async () => {
    setIsLoading(true);
    setError(null);
    setResults(null);
    
    try {
      // Créer le payload pour l'API
      const payload = createApiPayload(config);
      
      // Utiliser le service API pour scanner et formater les fichiers
      const result = await copyToolApi.analyzeFiles(payload);
      
      // Mettre à jour les résultats
      setResults(result);
      
      // Sauvegarder la configuration dans l'historique
      saveToHistory(config);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erreur inconnue");
    } finally {
      setIsLoading(false);
    }
  };

  // Copier le contenu formaté dans le presse-papier
  const copyToClipboard = async () => {
    // Si le contenu formaté existe déjà, le copier directement
    if (results?.formattedContent) {
      try {
        await navigator.clipboard.writeText(results.formattedContent);
        setCopied(true);
        return;
      } catch (err) {
        setError("Impossible de copier dans le presse-papier");
        return;
      }
    }
    
    // Si on arrive ici, c'est qu'on n'a pas encore le contenu formaté
    setIsLoading(true);
    setError(null);
    
    try {
      // Créer le payload pour l'API
      const payload = createApiPayload(config);
      
      // Obtenir le contenu formaté
      const formattedContent = await copyToolApi.formatContent(payload);
      
      // Mettre à jour les résultats avec le contenu formaté
      if (results) {
        const updatedResults = {
          ...results,
          formattedContent
        };
        setResults(updatedResults);
      } else {
        setResults({
          matches: [],
          totalMatches: 0,
          formattedContent,
          stats: {
            totalLines: 0,
            totalWords: 0,
            totalChars: 0,
            fileCount: 0,
            folderCount: 0,
            totalSubdirectories: 0,
            totalSize: 0,
            totalSizeFormatted: "0 octets",
            byExtension: {}
          }
        });
      }
      
      // Copier dans le presse-papier
      await navigator.clipboard.writeText(formattedContent);
      setCopied(true);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erreur inconnue");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <CopyToolContext.Provider 
      value={{ 
        config, 
        history, 
        results, 
        isLoading, 
        error, 
        copied,
        directoryInput,
        fileInput,
        extensionInput,
        patternInput,
        excludeDirectoryInput,
        setConfig,
        setDirectoryInput,
        setFileInput,
        setExtensionInput,
        setPatternInput,
        setExcludeDirectoryInput,
        addDirectory,
        addFile,
        addExcludeExtension,
        addExcludePattern,
        addExcludeDirectory,
        removeItem,
        editItem,
        toggleRecursive,
        resetConfig,
        loadFromHistory,
        clearHistory,
        toggleFavorite,
        scanFiles,
        copyToClipboard
      }}
    >
      {children}
    </CopyToolContext.Provider>
  );
} 