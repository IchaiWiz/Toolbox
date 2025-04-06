import { History } from "lucide-react";
import { useState } from "react";
import { CopyConfig } from "../types";
import { HistoryItem } from "./HistoryItem";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
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

interface HistoryDialogProps {
  history: CopyConfig[];
  onApplyConfig: (config: CopyConfig) => void;
  onClearHistory: () => void;
}

/**
 * Dialogue pour afficher et gérer l'historique des configurations
 */
export function HistoryDialog({ history, onApplyConfig, onClearHistory }: HistoryDialogProps) {
  const [isOpen, setIsOpen] = useState(false);
  
  const handleApplyConfig = (config: CopyConfig) => {
    onApplyConfig(config);
    setIsOpen(false);
  };
  
  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm">
          <History className="h-4 w-4 mr-2" />
          Historique
        </Button>
      </DialogTrigger>
      
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Historique des configurations</DialogTitle>
          <DialogDescription>
            Vos 10 dernières opérations de copie
          </DialogDescription>
        </DialogHeader>
        
        <div className="py-4">
          {history.length === 0 ? (
            <p className="text-center text-muted-foreground py-4">
              Aucun historique disponible
            </p>
          ) : (
            <ScrollArea className="h-[400px]">
              <div className="space-y-3">
                {history.map((item) => (
                  <HistoryItem 
                    key={item.id} 
                    item={item} 
                    onApply={handleApplyConfig} 
                  />
                ))}
              </div>
            </ScrollArea>
          )}
        </div>
        
        <DialogFooter>
          {history.length > 0 && (
            <Button 
              variant="destructive" 
              size="sm" 
              onClick={onClearHistory}
            >
              Effacer l'historique
            </Button>
          )}
          <DialogClose asChild>
            <Button variant="outline" size="sm">Fermer</Button>
          </DialogClose>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
} 