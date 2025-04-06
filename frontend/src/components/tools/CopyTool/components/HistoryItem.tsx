import { Check, Clock, Eye, FileText, FolderOpen, Star, StarOff } from "lucide-react";
import { CopyConfig } from "../types";
import { formatDate, formatTime } from "../utils";
import { Badge } from "@/components/ui/badge";
import { 
  Card, 
  CardHeader, 
  CardContent, 
  CardFooter 
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { 
  Dialog, 
  DialogContent, 
  DialogHeader, 
  DialogTitle
} from "@/components/ui/dialog";
import { useState } from "react";

interface HistoryItemProps {
  item: CopyConfig;
  onApply: (config: CopyConfig) => void;
  onToggleFavorite?: (id: string) => void;
}

/**
 * Composant pour afficher un élément d'historique
 */
export function HistoryItem({ item, onApply, onToggleFavorite }: HistoryItemProps) {
  const isFavorite = !!item.isFavorite;
  const [showDetailsDialog, setShowDetailsDialog] = useState(false);
  
  const toggleFavorite = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (onToggleFavorite) {
      onToggleFavorite(item.id);
    }
  };
  
  const handleApply = () => {
    onApply(item);
  };
  
  const openDetails = (e: React.MouseEvent) => {
    e.stopPropagation();
    setShowDetailsDialog(true);
  };
  
  return (
    <>
      <Card 
        key={item.id} 
        className="border border-muted transition-all hover:border-primary/50 hover:shadow-sm cursor-pointer group"
        onClick={handleApply}
      >
        <CardHeader className="p-3 pb-0 flex flex-row items-start justify-between space-y-0">
          <div>
            <div className="flex items-center gap-1">
              <span className="text-sm font-medium truncate max-w-[200px]">
                {item.name || formatDate(item.timestamp)}
              </span>
              <div className="flex items-center text-muted-foreground">
                <Clock className="h-3 w-3 ml-1" />
                <span className="text-xs ml-1">{formatTime(item.timestamp)}</span>
              </div>
            </div>
            
            <div className="flex flex-wrap gap-1 mt-1">
              <Badge variant="outline" className="flex items-center gap-1">
                <FolderOpen className="h-3 w-3" />
                {item.directories.length}
              </Badge>
              <Badge variant="outline" className="flex items-center gap-1">
                <FileText className="h-3 w-3" />
                {item.files.length}
              </Badge>
              {item.excludeExtensions.length > 0 && (
                <Badge variant="secondary" className="flex items-center gap-1">
                  {item.excludeExtensions.length} ext.
                </Badge>
              )}
              {(item.excludePatterns.length > 0 && item.excludePatterns.length !== 2) && (
                <Badge variant="destructive" className="flex items-center gap-1">
                  {item.excludePatterns.length} excl.
                </Badge>
              )}
            </div>
          </div>
          
          <Button 
            variant="ghost" 
            size="icon" 
            className="h-7 w-7"
            onClick={toggleFavorite}
          >
            {isFavorite ? (
              <Star className="h-3.5 w-3.5 text-yellow-500 fill-yellow-500" />
            ) : (
              <StarOff className="h-3.5 w-3.5 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity" />
            )}
          </Button>
        </CardHeader>
        
        <CardContent className="p-3 pt-2">
          {item.directories.length > 0 && (
            <div className="text-xs text-muted-foreground mt-1 space-y-1">
              {item.directories.slice(0, 2).map((dir, index) => (
                <div key={index} className="flex items-start">
                  <FolderOpen className="h-3 w-3 mr-1 mt-0.5 flex-shrink-0" /> 
                  <div className="break-all">{dir}</div>
                </div>
              ))}
              {item.directories.length > 2 && (
                <div className="text-xs text-muted-foreground">+{item.directories.length - 2} autres dossiers</div>
              )}
            </div>
          )}
          
          {item.files.length > 0 && item.directories.length === 0 && (
            <div className="text-xs text-muted-foreground mt-1 space-y-1">
              {item.files.slice(0, 2).map((file, index) => (
                <div key={index} className="flex items-start">
                  <FileText className="h-3 w-3 mr-1 mt-0.5 flex-shrink-0" /> 
                  <div className="break-all">{file}</div>
                </div>
              ))}
              {item.files.length > 2 && (
                <div className="text-xs text-muted-foreground">+{item.files.length - 2} autres fichiers</div>
              )}
            </div>
          )}
        </CardContent>
        
        <CardFooter className="p-2 pt-0 flex justify-between gap-4">
          <Button 
            variant="ghost" 
            size="sm"
            className="text-xs h-7 opacity-0 group-hover:opacity-100 transition-opacity"
            onClick={openDetails}
          >
            <Eye className="h-3 w-3 mr-1" />
            Détails
          </Button>
          
          <Button 
            variant="default" 
            size="sm" 
            className="text-xs h-7 opacity-0 group-hover:opacity-100 transition-opacity"
            onClick={(e) => {
              e.stopPropagation();
              handleApply();
            }}
          >
            <Check className="h-3 w-3 mr-1" />
            Appliquer
          </Button>
        </CardFooter>
      </Card>
      
      <Dialog open={showDetailsDialog} onOpenChange={setShowDetailsDialog}>
        <DialogContent onClick={(e) => e.stopPropagation()} className="max-w-xl">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              {item.name || `Configuration du ${formatDate(item.timestamp)}`}
              <span className="text-muted-foreground text-sm font-normal">
                {formatTime(item.timestamp)}
              </span>
            </DialogTitle>
          </DialogHeader>
          
          <div className="space-y-4 py-4">
            {/* Dossiers */}
            <div>
              <h3 className="text-sm font-medium mb-1 flex items-center">
                <FolderOpen className="h-4 w-4 mr-1" /> 
                Dossiers ({item.directories.length})
              </h3>
              {item.directories.length > 0 ? (
                <div className="border rounded-md p-2 text-sm max-h-[150px] overflow-y-auto space-y-1">
                  {item.directories.map((dir, i) => (
                    <div key={i} className="break-all">{dir}</div>
                  ))}
                </div>
              ) : (
                <div className="text-sm text-muted-foreground">Aucun dossier</div>
              )}
            </div>
            
            {/* Fichiers */}
            <div>
              <h3 className="text-sm font-medium mb-1 flex items-center">
                <FileText className="h-4 w-4 mr-1" /> 
                Fichiers ({item.files.length})
              </h3>
              {item.files.length > 0 ? (
                <div className="border rounded-md p-2 text-sm max-h-[150px] overflow-y-auto space-y-1">
                  {item.files.map((file, i) => (
                    <div key={i} className="break-all">{file}</div>
                  ))}
                </div>
              ) : (
                <div className="text-sm text-muted-foreground">Aucun fichier</div>
              )}
            </div>
            
            {/* Extensions exclues */}
            <div>
              <h3 className="text-sm font-medium mb-1">Extensions exclues ({item.excludeExtensions.length})</h3>
              {item.excludeExtensions.length > 0 ? (
                <div className="flex flex-wrap gap-1">
                  {item.excludeExtensions.map((ext, i) => (
                    <Badge key={i} variant="secondary">{ext}</Badge>
                  ))}
                </div>
              ) : (
                <div className="text-sm text-muted-foreground">Aucune extension exclue</div>
              )}
            </div>
            
            {/* Motifs exclus */}
            <div>
              <h3 className="text-sm font-medium mb-1">Motifs exclus ({item.excludePatterns.length})</h3>
              {item.excludePatterns.length > 0 ? (
                <div className="border rounded-md p-2 text-sm max-h-[100px] overflow-y-auto space-y-1">
                  {item.excludePatterns.map((pattern, i) => (
                    <div key={i} className="break-all">{pattern}</div>
                  ))}
                </div>
              ) : (
                <div className="text-sm text-muted-foreground">Aucun motif exclu</div>
              )}
            </div>
            
            {/* Dossiers exclus */}
            <div>
              <h3 className="text-sm font-medium mb-1">Dossiers exclus ({item.excludeDirectories.length})</h3>
              {item.excludeDirectories.length > 0 ? (
                <div className="border rounded-md p-2 text-sm max-h-[100px] overflow-y-auto space-y-1">
                  {item.excludeDirectories.map((dir, i) => (
                    <div key={i} className="break-all">{dir}</div>
                  ))}
                </div>
              ) : (
                <div className="text-sm text-muted-foreground">Aucun dossier exclu</div>
              )}
            </div>
            
            <div className="flex items-center space-x-2 pt-2">
              <Button 
                variant="default" 
                onClick={() => {
                  handleApply();
                  setShowDetailsDialog(false);
                }}
              >
                <Check className="h-4 w-4 mr-2" />
                Appliquer cette configuration
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
} 