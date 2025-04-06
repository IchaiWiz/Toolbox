import { Save } from "lucide-react";

export function BackupTool() {
  return (
    <div className="p-6 rounded-lg bg-card text-card-foreground shadow-sm animate-in slide-in-from-bottom-4 duration-300">
      <header className="flex items-center gap-2 mb-6">
        <Save className="w-6 h-6 text-primary" />
        <h2 className="text-2xl font-semibold">Outil de Sauvegarde</h2>
      </header>
      
      <div className="flex items-center justify-center p-10 rounded-lg bg-muted/30 border border-dashed border-border h-[300px]">
        <div className="text-center flex flex-col items-center gap-3">
          <Save className="w-12 h-12 text-muted-foreground opacity-50" />
          <p className="text-muted-foreground font-medium">Placeholder pour l'outil de sauvegarde</p>
          <p className="text-sm text-muted-foreground/70">Sauvegarde avec exclusions (ignorer certains dossiers ou fichiers)</p>
        </div>
      </div>
    </div>
  );
} 