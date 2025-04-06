import { useState, useRef, useEffect } from 'react';
import { X, BarChart3, Copy, Save, FolderTree, SplitSquareVertical, Plus, Pin, Edit, Pencil, Trash2, RefreshCw, Search, Settings, FilesIcon } from 'lucide-react';
import { useTabs, ToolType } from '@/contexts/TabsContext';
import { Button } from '@/components/ui/button';
import { 
  Tooltip, 
  TooltipContent, 
  TooltipProvider, 
  TooltipTrigger 
} from '@/components/ui/tooltip';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger
} from '@/components/ui/dropdown-menu';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogTrigger
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";

// Définir les icônes pour chaque type d'outil
const toolIcons: Record<ToolType, React.ReactNode> = {
  Dashboard: <BarChart3 className="w-4 h-4" />,
  CopyTool: <Copy className="w-4 h-4" />,
  BackupTool: <Save className="w-4 h-4" />,
  AnalyseTool: <BarChart3 className="w-4 h-4" />,
  AiStructureTool: <FolderTree className="w-4 h-4" />,
  DuplicateDetectionTool: <FilesIcon className="w-4 h-4" />,
  WinMergeTool: <SplitSquareVertical className="w-4 h-4" />
};

export function TabBar() {
  const { tabs, activeTab, addTab, closeTab, setActiveTab, reorderTabs, renameTab, togglePinTab, closeAllUnpinnedTabs } = useTabs();
  const [draggedTab, setDraggedTab] = useState<string | null>(null);
  const tabRefs = useRef<Record<string, HTMLDivElement | null>>({});
  
  // État pour le dialogue de renommage
  const [isRenameDialogOpen, setIsRenameDialogOpen] = useState(false);
  const [tabToRename, setTabToRename] = useState<string | null>(null);
  const [newTabName, setNewTabName] = useState("");

  // Vérifier s'il y a des onglets non épinglés
  const hasUnpinnedTabs = tabs.some(tab => !tab.pinned && tab.closable);

  // Gestionnaire de début de glisser-déposer
  const handleDragStart = (e: React.DragEvent<HTMLDivElement>, id: string) => {
    setDraggedTab(id);
    e.dataTransfer.effectAllowed = 'move';
    // Pour cacher l'image fantôme par défaut
    const img = new Image();
    img.src = 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7';
    e.dataTransfer.setDragImage(img, 0, 0);
    
    if (tabRefs.current[id]) {
      tabRefs.current[id]?.classList.add('opacity-50', 'scale-95');
    }
  };

  // Gestionnaire de fin de glisser-déposer
  const handleDragEnd = (e: React.DragEvent<HTMLDivElement>, id: string) => {
    setDraggedTab(null);
    if (tabRefs.current[id]) {
      tabRefs.current[id]?.classList.remove('opacity-50', 'scale-95');
    }
  };

  // Gestionnaire d'entrée dans la zone de dépôt
  const handleDragOver = (e: React.DragEvent<HTMLDivElement>, id: string) => {
    e.preventDefault();
    if (draggedTab && draggedTab !== id) {
      const draggedIndex = tabs.findIndex(tab => tab.id === draggedTab);
      const hoverIndex = tabs.findIndex(tab => tab.id === id);
      
      // Ne pas permettre le déplacement du Dashboard (toujours en premier)
      if (draggedIndex === 0 || hoverIndex === 0) return;
      
      reorderTabs(draggedIndex, hoverIndex);
    }
  };

  // Ouvrir le dialogue de renommage
  const openRenameDialog = (id: string) => {
    const tab = tabs.find(tab => tab.id === id);
    if (tab) {
      setTabToRename(id);
      setNewTabName(tab.title);
      setIsRenameDialogOpen(true);
    }
  };

  // Confirmer le renommage
  const confirmRename = () => {
    if (tabToRename && newTabName.trim()) {
      renameTab(tabToRename, newTabName.trim());
      setIsRenameDialogOpen(false);
      setTabToRename(null);
      setNewTabName("");
    }
  };

  return (
    <>
      <div className="flex items-center bg-card border-b border-border overflow-x-auto overflow-y-hidden">
        <div className="flex-1 flex items-center">
          {tabs.map((tab, index) => (
            <div
              key={tab.id}
              ref={el => tabRefs.current[tab.id] = el}
              draggable={tab.type !== 'Dashboard'}
              onDragStart={e => handleDragStart(e, tab.id)}
              onDragEnd={e => handleDragEnd(e, tab.id)}
              onDragOver={e => handleDragOver(e, tab.id)}
              className={`
                flex items-center h-11 px-4 border-r border-border cursor-pointer
                transition-all duration-150 ease-in-out
                ${activeTab === tab.id 
                  ? 'bg-background text-foreground border-b-2 border-b-primary' 
                  : 'text-muted-foreground hover:bg-secondary/10'
                }
                ${tab.pinned ? 'border-l-2 border-l-primary/50' : ''}
              `}
              onClick={() => setActiveTab(tab.id)}
            >
              <div className="flex items-center gap-2">
                {toolIcons[tab.type]}
                <span className="text-sm font-medium">{tab.title}</span>
              </div>
              
              <div className="flex ml-2 items-center">
                {tab.type !== 'Dashboard' && (
                  <>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        togglePinTab(tab.id);
                      }}
                      className={`
                        p-1 rounded-full transition-colors
                        ${tab.pinned 
                          ? 'text-primary hover:bg-secondary/20' 
                          : 'text-muted-foreground hover:bg-secondary/20'
                        }
                      `}
                      title={tab.pinned ? "Désépingler" : "Épingler"}
                    >
                      <Pin className="h-3 w-3" />
                    </button>
                    
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        openRenameDialog(tab.id);
                      }}
                      className="p-1 rounded-full text-muted-foreground hover:bg-secondary/20 transition-colors"
                      title="Renommer"
                    >
                      <Pencil className="h-3 w-3" />
                    </button>
                  </>
                )}
                
                {tab.closable && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      closeTab(tab.id);
                    }}
                    className="p-1 rounded-full hover:bg-secondary/20 transition-colors"
                    title="Fermer"
                  >
                    <X className="h-3 w-3" />
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
        
        <div className="flex items-center mr-2">
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button 
                  variant="ghost" 
                  size="icon" 
                  className="h-8 w-8 mr-2"
                  onClick={closeAllUnpinnedTabs}
                  disabled={!hasUnpinnedTabs}
                >
                  <Trash2 className={`h-4 w-4 ${!hasUnpinnedTabs ? 'opacity-50' : ''}`} />
                </Button>
              </TooltipTrigger>
              <TooltipContent side="bottom">
                <p>Fermer tous les onglets non épinglés</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
          
          <TooltipProvider>
            <DropdownMenu>
              <Tooltip>
                <TooltipTrigger asChild>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" size="icon" className="h-8 w-8">
                      <Plus className="h-4 w-4" />
                    </Button>
                  </DropdownMenuTrigger>
                </TooltipTrigger>
                <TooltipContent side="bottom">
                  <p>Ajouter un outil</p>
                </TooltipContent>
              </Tooltip>
              
              <DropdownMenuContent align="end" className="animate-in slide-in-from-top-2 duration-200">
                <DropdownMenuItem 
                  onClick={() => addTab('CopyTool')}
                  className="flex items-center gap-2 cursor-pointer"
                >
                  <Copy className="h-4 w-4" />
                  <span>Outil de Copie</span>
                </DropdownMenuItem>
                <DropdownMenuItem 
                  onClick={() => addTab('BackupTool')}
                  className="flex items-center gap-2 cursor-pointer"
                >
                  <Save className="h-4 w-4" />
                  <span>Outil de Sauvegarde</span>
                </DropdownMenuItem>
                <DropdownMenuItem 
                  onClick={() => addTab('AnalyseTool')}
                  className="flex items-center gap-2 cursor-pointer"
                >
                  <BarChart3 className="h-4 w-4" />
                  <span>Analyse de Dossiers</span>
                </DropdownMenuItem>
                <DropdownMenuItem 
                  onClick={() => addTab('AiStructureTool')}
                  className="flex items-center gap-2 cursor-pointer"
                >
                  <FolderTree className="h-4 w-4" />
                  <span>Génération d'Arborescence IA</span>
                </DropdownMenuItem>
                <DropdownMenuItem 
                  onClick={() => addTab('DuplicateDetectionTool')}
                  className="flex items-center gap-2 cursor-pointer"
                >
                  <FilesIcon className="h-4 w-4" />
                  <span>Détection de Doublons</span>
                </DropdownMenuItem>
                <DropdownMenuItem 
                  onClick={() => addTab('WinMergeTool')}
                  className="flex items-center gap-2 cursor-pointer"
                >
                  <SplitSquareVertical className="h-4 w-4" />
                  <span>Comparaison de Dossiers</span>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </TooltipProvider>
        </div>
      </div>

      {/* Dialogue de renommage */}
      <Dialog open={isRenameDialogOpen} onOpenChange={setIsRenameDialogOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Renommer l'onglet</DialogTitle>
          </DialogHeader>
          <div className="py-4">
            <Input
              value={newTabName}
              onChange={(e) => setNewTabName(e.target.value)}
              placeholder="Nouveau nom de l'onglet"
              className="w-full"
              autoFocus
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  confirmRename();
                }
              }}
            />
          </div>
          <DialogFooter>
            <Button
              type="button"
              variant="secondary"
              onClick={() => setIsRenameDialogOpen(false)}
            >
              Annuler
            </Button>
            <Button type="button" onClick={confirmRename}>
              Renommer
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
} 