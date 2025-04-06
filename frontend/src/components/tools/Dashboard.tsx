import { BarChart3, Copy, Save, FolderTree, FilesIcon, SplitSquareVertical, LayoutDashboard } from "lucide-react";
import { useTabs, ToolType } from '@/contexts/TabsContext';
import { Button } from "@/components/ui/button";
import { useState } from "react";

// Définir les informations pour chaque type d'outil
const toolsInfo = [
  {
    type: 'CopyTool' as ToolType,
    title: 'Outil de Copie',
    description: 'Copie de dossiers avec options avancées',
    icon: <Copy className="h-10 w-10 text-primary" />,
    color: 'bg-primary/10'
  },
  {
    type: 'BackupTool' as ToolType,
    title: 'Outil de Sauvegarde',
    description: 'Sauvegarde avec exclusions (ignorer certains dossiers ou fichiers)',
    icon: <Save className="h-10 w-10 text-primary" />,
    color: 'bg-primary/10'
  },
  {
    type: 'AiStructureTool' as ToolType,
    title: 'Arborescence IA',
    description: 'Génération d\'arborescence de fichiers/dossiers par IA',
    icon: <FolderTree className="h-10 w-10 text-primary" />,
    color: 'bg-primary/10'
  },
  {
    type: 'AnalyseTool' as ToolType,
    title: 'Analyse de Dossiers',
    description: 'Statistiques sur les dossiers (poids, nombre de fichiers, extensions, etc.)',
    icon: <BarChart3 className="h-10 w-10 text-primary" />,
    color: 'bg-primary/10'
  },
  {
    type: 'DuplicateDetectionTool' as ToolType,
    title: 'Détection de Doublons',
    description: 'Détection de fichiers similaires ou identiques',
    icon: <FilesIcon className="h-10 w-10 text-primary" />,
    color: 'bg-primary/10'
  },
  {
    type: 'WinMergeTool' as ToolType,
    title: 'Comparaison de Dossiers',
    description: 'Comparaison visuelle de deux dossiers (à la façon de WinMerge)',
    icon: <SplitSquareVertical className="h-10 w-10 text-primary" />,
    color: 'bg-primary/10'
  }
];

export function Dashboard() {
  const { addTab } = useTabs();

  return (
    <div className="p-6 rounded-lg bg-card text-card-foreground shadow-sm flex flex-col gap-6 animate-in slide-in-from-bottom-4 duration-300">
      <header className="flex items-center gap-2">
        <LayoutDashboard className="w-6 h-6 text-primary" />
        <h2 className="text-2xl font-semibold">Dashboard</h2>
      </header>
      
      <div className="bg-secondary/10 rounded-lg p-4 border border-border mb-4">
        <h3 className="font-medium mb-2">Bienvenue dans Toolbox</h3>
        <p className="text-muted-foreground">
          Cette interface vous permet d'accéder à différents outils via les onglets.
          Vous pouvez ouvrir de nouveaux outils, les fermer, les renommer et les épingler selon vos besoins.
        </p>
      </div>
      
      <div>
        <h3 className="text-lg font-medium mb-4">Outils disponibles</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {toolsInfo.map((tool) => (
            <div 
              key={tool.type}
              className="flex flex-col p-5 rounded-lg border border-border hover:border-primary/50 transition-all duration-200 cursor-pointer shadow-sm hover:shadow-md"
              onClick={() => addTab(tool.type)}
            >
              <div className={`p-4 rounded-full ${tool.color} w-fit mb-4`}>
                {tool.icon}
              </div>
              <h4 className="text-lg font-medium mb-2">{tool.title}</h4>
              <p className="text-muted-foreground mb-4 flex-grow">{tool.description}</p>
              <Button variant="outline" className="w-full justify-start gap-2">
                {tool.type === 'CopyTool' && <Copy className="h-4 w-4" />}
                {tool.type === 'BackupTool' && <Save className="h-4 w-4" />}
                {tool.type === 'AiStructureTool' && <FolderTree className="h-4 w-4" />}
                {tool.type === 'AnalyseTool' && <BarChart3 className="h-4 w-4" />}
                {tool.type === 'DuplicateDetectionTool' && <FilesIcon className="h-4 w-4" />}
                {tool.type === 'WinMergeTool' && <SplitSquareVertical className="h-4 w-4" />}
                Ouvrir l'outil
              </Button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
} 