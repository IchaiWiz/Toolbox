import { SplitSquareVertical } from "lucide-react";

export function WinMergeTool() {
  return (
    <div className="p-6 rounded-lg bg-card text-card-foreground shadow-sm animate-in slide-in-from-bottom-4 duration-300">
      <header className="flex items-center gap-2 mb-6">
        <SplitSquareVertical className="w-6 h-6 text-primary" />
        <h2 className="text-2xl font-semibold">Comparaison de Dossiers</h2>
      </header>
      
      <div className="flex items-center justify-center p-10 rounded-lg bg-muted/30 border border-dashed border-border h-[300px]">
        <div className="text-center flex flex-col items-center gap-3">
          <SplitSquareVertical className="w-12 h-12 text-muted-foreground opacity-50" />
          <p className="text-muted-foreground font-medium">Placeholder pour l'outil de comparaison</p>
          <p className="text-sm text-muted-foreground/70">Comparaison visuelle de deux dossiers à la façon de WinMerge</p>
        </div>
      </div>
    </div>
  );
} 