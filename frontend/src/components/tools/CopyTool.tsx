// import { Split } from "@/components/ui/split";
import { ConfigPanel } from "./CopyTool/ConfigPanel";
import { ResultsPanel } from "./CopyTool/ResultsPanel";
import { CopyToolProvider } from "./CopyTool/CopyToolContext";

/**
 * Outil de copie de fichiers avec fonctionnalités avancées
 */
export function CopyTool() {
  return (
    <CopyToolProvider>
      <div className="h-full flex flex-col">
        <div className="px-6 py-3">
          <h2 className="text-xl font-semibold">Copie Avancée</h2>
          <p className="text-sm text-muted-foreground">
            Copiez le contenu des fichiers et dossiers dans le presse-papier
          </p>
        </div>
        
        <div className="flex-1 px-6 pb-6 overflow-hidden">
          <div className="h-full flex flex-row">
            <div className="w-1/2 overflow-auto pr-4">
              <ConfigPanel />
            </div>
            <div className="w-1/2 overflow-auto pl-4">
              <ResultsPanel />
            </div>
          </div>
        </div>
      </div>
    </CopyToolProvider>
  );
} 