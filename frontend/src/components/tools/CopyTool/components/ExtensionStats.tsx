import { BarChart } from "lucide-react";
import { FileStats } from "../types";

interface ExtensionStatsProps {
  stats: FileStats;
}

/**
 * Composant pour afficher la répartition des fichiers par extension
 */
export function ExtensionStats({ stats }: ExtensionStatsProps) {
  if (!stats || !stats.byExtension || Object.keys(stats.byExtension).length === 0) {
    return null;
  }
  
  // Trier les extensions par nombre décroissant
  const sortedExtensions = Object.entries(stats.byExtension)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5); // Limiter aux 5 principales extensions
  
  return (
    <div className="mb-6">
      <h4 className="text-sm font-medium mb-2 flex items-center">
        <BarChart className="h-4 w-4 mr-1 text-muted-foreground" />
        Extensions
      </h4>
      <div className="flex flex-wrap gap-2">
        {sortedExtensions.map(([ext, count]) => (
          <span 
            key={ext} 
            className="px-2 py-1 text-xs rounded-full bg-secondary"
          >
            {ext || "Sans extension"}: {count}
          </span>
        ))}
      </div>
    </div>
  );
} 