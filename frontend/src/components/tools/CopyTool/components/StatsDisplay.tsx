import { FileStats } from "../types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface StatsDisplayProps {
  stats: FileStats;
}

/**
 * Composant pour afficher les statistiques des fichiers
 */
export function StatsDisplay({ stats }: StatsDisplayProps) {
  if (!stats) return null;
  
  return (
    <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
      <Card>
        <CardHeader className="py-2">
          <CardTitle className="text-sm">Fichiers</CardTitle>
        </CardHeader>
        <CardContent className="py-2">
          <div className="text-2xl font-bold">{stats.fileCount}</div>
          <div className="text-xs text-muted-foreground space-y-1">
            <p>{stats.totalSubdirectories || 0} sous-dossier(s)</p>
            <p className="font-medium">{stats.totalSizeFormatted || "0 Ko"}</p>
          </div>
        </CardContent>
      </Card>
      
      <Card>
        <CardHeader className="py-2">
          <CardTitle className="text-sm">Lignes</CardTitle>
        </CardHeader>
        <CardContent className="py-2">
          <div className="text-2xl font-bold">{stats.totalLines.toLocaleString()}</div>
          <p className="text-xs text-muted-foreground">
            {stats.totalChars.toLocaleString()} caractères
          </p>
        </CardContent>
      </Card>
      
      <Card>
        <CardHeader className="py-2">
          <CardTitle className="text-sm">Mots</CardTitle>
        </CardHeader>
        <CardContent className="py-2">
          <div className="text-2xl font-bold">{stats.totalWords.toLocaleString()}</div>
          <p className="text-xs text-muted-foreground">
            {Math.round(stats.totalWords / stats.totalLines || 0)} mots/ligne
          </p>
        </CardContent>
      </Card>
    </div>
  );
} 