import { Copy, FilesIcon } from "lucide-react";

export function DuplicateDetectionTool() {
  return (
    <div className="p-6 rounded-lg bg-card text-card-foreground shadow-sm animate-in slide-in-from-bottom-4 duration-300">
      <header className="flex items-center gap-2 mb-6">
        <Copy className="w-6 h-6 text-primary" />
        <h2 className="text-2xl font-semibold">Détection de Doublons</h2>
      </header>
      
      <div className="flex items-center justify-center p-10 rounded-lg bg-muted/30 border border-dashed border-border h-[300px]">
        <div className="text-center flex flex-col items-center gap-3">
          <div className="relative">
            <FilesIcon className="w-12 h-12 text-muted-foreground opacity-50" />
            <Copy className="w-6 h-6 text-muted-foreground opacity-70 absolute -top-1 -right-1" />
          </div>
          <p className="text-muted-foreground font-medium">Placeholder pour l'outil de détection de doublons</p>
          <p className="text-sm text-muted-foreground/70">Détection de fichiers similaires ou identiques</p>
        </div>
      </div>
    </div>
  );
} 