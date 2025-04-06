import { Clock, History, Search, TagIcon, Star } from "lucide-react";
import { useState, useMemo } from "react";
import { CopyConfig } from "../types";
import { HistoryItem } from "./HistoryItem";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogFooter,
  DialogClose
} from "@/components/ui/dialog";
import { formatDate } from "../utils";

interface HistoryDialogProps {
  history: CopyConfig[];
  onApplyConfig: (config: CopyConfig) => void;
  onClearHistory: () => void;
  onToggleFavorite?: (id: string) => void;
}

/**
 * Dialogue pour afficher et gérer l'historique des configurations
 */
export function HistoryDialog({ history, onApplyConfig, onClearHistory, onToggleFavorite }: HistoryDialogProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [currentView, setCurrentView] = useState<"all" | "recent" | "favorites">("all");
  
  const handleApplyConfig = (config: CopyConfig) => {
    onApplyConfig(config);
    setIsOpen(false);
  };
  
  // Filtrer l'historique en fonction du terme de recherche
  const filteredHistory = useMemo(() => {
    if (!searchTerm.trim()) return history;
    
    const term = searchTerm.toLowerCase();
    return history.filter(item => {
      // Chercher dans les dossiers
      const foundInDirectories = item.directories.some(dir => 
        dir.toLowerCase().includes(term)
      );
      
      // Chercher dans les fichiers
      const foundInFiles = item.files.some(file => 
        file.toLowerCase().includes(term)
      );
      
      // Chercher dans le nom (si présent)
      const foundInName = item.name ? item.name.toLowerCase().includes(term) : false;
      
      return foundInDirectories || foundInFiles || foundInName;
    });
  }, [history, searchTerm]);
  
  // Les configurations favorites
  const favoriteHistory = useMemo(() => {
    return filteredHistory.filter(item => item.isFavorite);
  }, [filteredHistory]);
  
  // Les 5 configurations les plus récentes
  const recentHistory = useMemo(() => {
    return filteredHistory.slice(0, 5);
  }, [filteredHistory]);
  
  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm">
          <History className="h-4 w-4 mr-2" />
          Historique
        </Button>
      </DialogTrigger>
      
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Historique des configurations</DialogTitle>
          <DialogDescription>
            Vos configurations de copie sauvegardées
          </DialogDescription>
        </DialogHeader>
        
        <div className="pt-4">
          <div className="flex items-center space-x-2 mb-4">
            <div className="relative flex-1">
              <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Rechercher un dossier ou fichier..."
                className="pl-8"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
          </div>
          
          {history.length === 0 ? (
            <div className="text-center text-muted-foreground py-12 border rounded-md">
              <History className="h-12 w-12 mx-auto mb-2 opacity-20" />
              <p className="text-lg">Aucun historique disponible</p>
              <p className="text-sm">Les configurations seront enregistrées après avoir lancé une opération de copie</p>
            </div>
          ) : filteredHistory.length === 0 ? (
            <div className="text-center text-muted-foreground py-12 border rounded-md">
              <Search className="h-12 w-12 mx-auto mb-2 opacity-20" />
              <p className="text-lg">Aucun résultat</p>
              <p className="text-sm">Aucune configuration ne correspond à votre recherche</p>
            </div>
          ) : (
            <Tabs defaultValue="all" value={currentView} onValueChange={(v) => setCurrentView(v as any)}>
              <TabsList className="mb-4">
                <TabsTrigger value="all">
                  <TagIcon className="h-4 w-4 mr-2" />
                  Tout
                </TabsTrigger>
                <TabsTrigger value="favorites">
                  <Star className="h-4 w-4 mr-2" />
                  Favoris
                </TabsTrigger>
                <TabsTrigger value="recent">
                  <Clock className="h-4 w-4 mr-2" />
                  Récents
                </TabsTrigger>
              </TabsList>

              <TabsContent value="favorites" className="m-0">
                <ScrollArea className="h-[400px] pr-4">
                  {favoriteHistory.length === 0 ? (
                    <div className="text-center text-muted-foreground py-12 border rounded-md">
                      <Star className="h-12 w-12 mx-auto mb-2 opacity-20" />
                      <p className="text-lg">Aucun favori</p>
                      <p className="text-sm">Marquez vos configurations préférées en cliquant sur l'étoile</p>
                    </div>
                  ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {favoriteHistory.map((item) => (
                        <HistoryItem 
                          key={item.id} 
                          item={item} 
                          onApply={handleApplyConfig}
                          onToggleFavorite={onToggleFavorite}
                        />
                      ))}
                    </div>
                  )}
                </ScrollArea>
              </TabsContent>
              
              <TabsContent value="all" className="m-0">
                <ScrollArea className="h-[400px] pr-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {filteredHistory.map((item) => (
                      <HistoryItem 
                        key={item.id} 
                        item={item} 
                        onApply={handleApplyConfig}
                        onToggleFavorite={onToggleFavorite}
                      />
                    ))}
                  </div>
                </ScrollArea>
              </TabsContent>
              
              <TabsContent value="recent" className="m-0">
                <ScrollArea className="h-[400px] pr-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {recentHistory.map((item) => (
                      <HistoryItem 
                        key={item.id} 
                        item={item} 
                        onApply={handleApplyConfig}
                        onToggleFavorite={onToggleFavorite}
                      />
                    ))}
                  </div>
                </ScrollArea>
              </TabsContent>
            </Tabs>
          )}
        </div>
        
        <DialogFooter>
          <DialogClose asChild>
            <Button variant="outline" size="sm">Fermer</Button>
          </DialogClose>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
} 