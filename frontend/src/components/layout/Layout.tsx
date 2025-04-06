import { ReactNode, useState } from 'react';
import { useTabs } from '@/contexts/TabsContext';
import { Activity, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { TabBar } from './TabBar';
import { ThemeSwitcher } from './ThemeSwitcher';
import { Dashboard } from '@/components/tools/Dashboard';
import { CopyTool } from '@/components/tools/CopyTool';
import { BackupTool } from '@/components/tools/BackupTool';
import { AnalyseTool } from '@/components/tools/AnalyseTool';
import { AiStructureTool } from '@/components/tools/AiStructureTool';
import { DuplicateDetectionTool } from '@/components/tools/DuplicateDetectionTool';
import { WinMergeTool } from '@/components/tools/WinMergeTool';

interface LayoutProps {
  children?: ReactNode;
}

// Mapping entre les types d'outils et leurs composants
const toolComponents = {
  Dashboard,
  CopyTool,
  BackupTool,
  AnalyseTool,
  AiStructureTool,
  DuplicateDetectionTool,
  WinMergeTool
};

export function Layout({ children }: LayoutProps) {
  const { tabs, activeTab } = useTabs();
  const [isLoading, setIsLoading] = useState(false);
  const [showTestResults, setShowTestResults] = useState(false);
  const [testResults, setTestResults] = useState<Record<string, any> | null>(null);
  
  // Trouver l'onglet actif
  const currentTab = tabs.find(tab => tab.id === activeTab);
  
  // Déterminer quel composant afficher
  const ActiveComponent = currentTab ? toolComponents[currentTab.type] : Dashboard;

  // Fonction pour tester toutes les APIs
  const testAllApis = async () => {
    setIsLoading(true);
    setTestResults(null);
    setShowTestResults(true);
    
    try {
      const response = await fetch(`http://localhost:8000/api/test-all`);
      const data = await response.json();
      setTestResults(data);
    } catch (error) {
      setTestResults({
        error: {
          status: "error",
          message: `Erreur lors de l'appel au test global des APIs: ${error}`
        }
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-background text-foreground">
      {/* En-tête avec le logo et les actions */}
      <header className="h-14 px-4 border-b border-border flex items-center justify-between bg-card">
        <div className="w-32">
          {/* Espace réservé à gauche pour équilibrer */}
        </div>
        
        <h1 className="text-xl font-bold">Toolbox</h1>
        
        <div className="flex items-center space-x-2 w-32 justify-end">
          <Button
            variant="ghost"
            size="icon"
            onClick={testAllApis}
            disabled={isLoading}
            title="Tester les APIs"
            className="relative transition-all duration-200 hover:bg-secondary"
          >
            <Activity className="h-4 w-4" />
            {isLoading && (
              <span className="absolute inset-0 flex items-center justify-center">
                <span className="animate-spin h-3 w-3 border-2 border-current border-t-transparent rounded-full" />
              </span>
            )}
          </Button>
          <ThemeSwitcher />
        </div>
      </header>
      
      {/* Barre d'onglets */}
      <TabBar />
      
      {/* Contenu principal */}
      <main className="flex-1 p-4 overflow-auto">
        <ActiveComponent />
      </main>
      
      {/* Popup de résultats des tests d'APIs */}
      {showTestResults && (
        <div className="fixed top-16 right-4 w-80 bg-popover border border-border rounded-lg shadow-lg z-50 max-h-[80vh] overflow-auto">
          <div className="p-3 border-b border-border flex items-center justify-between">
            <h3 className="font-medium text-sm">Résultats des tests d'API</h3>
            <Button 
              variant="ghost" 
              size="icon" 
              onClick={() => setShowTestResults(false)}
              className="h-6 w-6"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
          
          <div className="p-2">
            {isLoading ? (
              <div className="p-3 text-center">
                <span className="inline-block animate-spin h-4 w-4 border-2 border-current border-t-transparent rounded-full mr-2" />
                Test en cours...
              </div>
            ) : testResults ? (
              <div className="space-y-2 text-sm">
                {Object.entries(testResults).map(([service, result]) => (
                  <div key={service} className={`p-2 rounded ${result.status === 'ok' ? 'bg-green-100 dark:bg-green-900/20' : 'bg-red-100 dark:bg-red-900/20'}`}>
                    <p className="font-medium text-xs">{service}</p>
                    <div className="flex gap-1 items-center text-xs">
                      <span>Status: {result.status}</span>
                      {result.status_code && <span>({result.status_code})</span>}
                    </div>
                    {result.error && (
                      <p className="text-red-500 text-xs mt-1">{result.error}</p>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-center text-muted-foreground">Aucun résultat</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
} 