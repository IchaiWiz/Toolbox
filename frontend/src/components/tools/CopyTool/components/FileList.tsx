import { FileMatch } from "../types";
import { ScrollArea } from "@/components/ui/scroll-area";

interface FileListProps {
  files: FileMatch[];
}

/**
 * Composant pour afficher la liste des fichiers trouvés
 */
export function FileList({ files }: FileListProps) {
  if (!files || files.length === 0) return null;
  
  return (
    <ScrollArea className="h-[calc(100vh-500px)] border rounded-md">
      <div className="p-2 space-y-2">
        {files.map((file, index) => (
          <div key={index} className="flex justify-between p-2 bg-secondary/10 rounded text-sm">
            <div className="overflow-x-auto flex-1">
              <span className="font-mono text-xs bg-secondary/30 rounded px-1.5 py-0.5 mr-2">
                {file.extension || "?"}
              </span>
              <span className="text-xs text-muted-foreground mr-2">
                {(file.size / 1024).toFixed(1)} KB
              </span>
              {file.path}
            </div>
          </div>
        ))}
      </div>
    </ScrollArea>
  );
} 