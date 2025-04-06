import { FileText, FolderOpen } from "lucide-react";
import { CopyConfig } from "../types";
import { formatDate, truncateText } from "../utils";
import { Badge } from "@/components/ui/badge";
import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Button } from "@/components/ui/button";

interface HistoryItemProps {
  item: CopyConfig;
  onApply: (config: CopyConfig) => void;
}

/**
 * Composant pour afficher un élément d'historique
 */
export function HistoryItem({ item, onApply }: HistoryItemProps) {
  return (
    <Card key={item.id} className="border border-muted">
      <CardHeader className="p-3 pb-0">
        <CardTitle className="text-sm font-medium">
          {item.name || formatDate(item.timestamp)}
        </CardTitle>
        <CardDescription className="text-xs flex flex-wrap gap-1">
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
          {item.excludePatterns.length > 0 && (
            <Badge variant="destructive" className="flex items-center gap-1">
              {item.excludePatterns.length} excl.
            </Badge>
          )}
        </CardDescription>
        {item.directories.length > 0 && (
          <div className="mt-2 text-xs text-muted-foreground truncate flex items-center">
            <FolderOpen className="h-3 w-3 mr-1 inline-block flex-shrink-0" /> 
            {truncateText(item.directories[0])}
            {item.directories.length > 1 && <span className="ml-1">+ {item.directories.length - 1} autres</span>}
          </div>
        )}
      </CardHeader>
      
      <Accordion type="single" collapsible className="px-3">
        <AccordionItem value="details" className="border-b-0">
          <AccordionTrigger className="py-2 text-xs">
            Voir détails
          </AccordionTrigger>
          <AccordionContent>
            {item.directories.length > 0 && (
              <div className="mb-2">
                <p className="text-xs font-medium mb-1">Dossiers:</p>
                <div className="text-xs space-y-1 ml-2">
                  {item.directories.slice(0, 3).map((dir, i) => (
                    <p key={i} className="truncate">{dir}</p>
                  ))}
                  {item.directories.length > 3 && (
                    <p className="text-muted-foreground">
                      + {item.directories.length - 3} autres...
                    </p>
                  )}
                </div>
              </div>
            )}
            
            {item.files.length > 0 && (
              <div className="mb-2">
                <p className="text-xs font-medium mb-1">Fichiers:</p>
                <div className="text-xs space-y-1 ml-2">
                  {item.files.slice(0, 3).map((file, i) => (
                    <p key={i} className="truncate">{file}</p>
                  ))}
                  {item.files.length > 3 && (
                    <p className="text-muted-foreground">
                      + {item.files.length - 3} autres...
                    </p>
                  )}
                </div>
              </div>
            )}
            
            <div className="flex justify-end mt-3">
              <Button 
                variant="default" 
                size="sm" 
                onClick={() => onApply(item)}
              >
                Appliquer
              </Button>
            </div>
          </AccordionContent>
        </AccordionItem>
      </Accordion>
    </Card>
  );
} 