import { createContext, useContext, useState, useEffect, ReactNode } from 'react';

type Theme = 'light' | 'dark' | 'fancy' | 'nature' | 'ocean' | 'sunset' | 'forest' | 'lavender';

interface ThemeContextType {
  theme: Theme;
  setTheme: (theme: Theme) => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

// Vérifier si localStorage est disponible
const isLocalStorageAvailable = () => {
  try {
    const testKey = '__test__';
    localStorage.setItem(testKey, testKey);
    localStorage.removeItem(testKey);
    return true;
  } catch (e) {
    return false;
  }
};

// Récupérer le thème depuis localStorage de façon sécurisée
const getStoredTheme = (): Theme | null => {
  if (!isLocalStorageAvailable()) return null;
  
  try {
    const storedTheme = localStorage.getItem('toolbox-theme') as Theme;
    return storedTheme;
  } catch (error) {
    return null;
  }
};

// Enregistrer le thème dans localStorage de façon sécurisée
const storeTheme = (theme: Theme): void => {
  if (!isLocalStorageAvailable()) return;
  
  try {
    localStorage.setItem('toolbox-theme', theme);
  } catch (error) {
    // Silencieux en cas d'erreur
  }
};

export function ThemeProvider({ children }: { children: ReactNode }) {
  const allThemes: Theme[] = ['light', 'dark', 'fancy', 'nature', 'ocean', 'sunset', 'forest', 'lavender'];
  
  // Initialiser avec le thème stocké ou par défaut
  const initialTheme = (() => {
    const stored = getStoredTheme();
    if (stored && allThemes.includes(stored)) {
      return stored;
    }
    
    if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return 'dark' as Theme;
    }
    
    return 'light' as Theme;
  })();
  
  const [theme, setTheme] = useState<Theme>(initialTheme);

  // Effet pour appliquer le thème initial au DOM
  useEffect(() => {
    applyThemeToDOM(theme);
    
    // Fonction pour détecter les changements de thème dans d'autres onglets
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'toolbox-theme' && e.newValue) {
        if (allThemes.includes(e.newValue as Theme)) {
          setTheme(e.newValue as Theme);
        }
      }
    };
    
    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  // Effet pour réagir aux changements de thème
  useEffect(() => {
    storeTheme(theme);
    applyThemeToDOM(theme);
  }, [theme]);
  
  // Fonction pour appliquer le thème au DOM
  const applyThemeToDOM = (currentTheme: Theme) => {
    const root = document.documentElement;
    
    // Supprimer toutes les classes de thème
    allThemes.forEach(t => root.classList.remove(t));
    
    // Ajouter la classe du thème actuel
    root.classList.add(currentTheme);
  };

  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
} 