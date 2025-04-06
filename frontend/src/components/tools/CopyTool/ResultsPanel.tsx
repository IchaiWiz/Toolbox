import { useState, useContext } from "react";
import { Filter, Clipboard, Check, AlertCircle, Loader2, ArrowDown, ArrowUp } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

import { useCopyTool, CopyToolProvider, CopyToolContext } from "./CopyToolContext";
import { StatsDisplay, ExtensionStats, FileList } from "./components";
import { FileMatch } from "./types";

// Type pour les options de tri
type SortField = "extension" | "size";
type SortDirection = "asc" | "desc";

/**
 * Panneau d'affichage des résultats de recherche
 */
export function ResultsPanel() {
  // Vérifier si nous sommes déjà dans un contexte CopyTool
  const contextExists = useContext(CopyToolContext) !== undefined;

  // Si le contexte existe déjà, on utilise directement le contenu
  // Sinon, on encapsule le contenu dans un CopyToolProvider
  if (contextExists) {
    return <ResultsPanelContent />;
  } else {
    return (
      <CopyToolProvider>
        <ResultsPanelContent />
      </CopyToolProvider>
    );
  }
}

/**
 * Contenu du panneau de résultats qui utilise le hook useCopyTool
 * Ce composant est utilisé à l'intérieur d'un CopyToolProvider
 */
function ResultsPanelContent() {
  const { 
    config,
    results,
    isLoading,
    error,
    copied,
    scanFiles,
    copyToClipboard
  } = useCopyTool();
  
  // État pour le tri
  const [sortField, setSortField] = useState<SortField>("extension");
  const [sortDirection, setSortDirection] = useState<SortDirection>("asc");
  
  // Vérifier si un scan peut être effectué
  const canScan = config.directories.length > 0 || config.files.length > 0;
  
  // Vérifier si une copie peut être effectuée
  const canCopy = !isLoading && results && results.matches.length > 0;
  
  // Fonction pour changer le champ de tri
  const toggleSort = (field: SortField) => {
    if (sortField === field) {
      // Si on clique sur le même champ, on inverse la direction
      setSortDirection(sortDirection === "asc" ? "desc" : "asc");
    } else {
      // Si on change de champ, on commence par ordre ascendant
      setSortField(field);
      setSortDirection("asc");
    }
  };
  
  // Fonction pour trier les fichiers
  const sortFiles = (files: FileMatch[]): FileMatch[] => {
    if (!files) return [];
    
    return [...files].sort((a, b) => {
      if (sortField === "extension") {
        const extA = a.extension || "";
        const extB = b.extension || "";
        return sortDirection === "asc" 
          ? extA.localeCompare(extB)
          : extB.localeCompare(extA);
      } else if (sortField === "size") {
        return sortDirection === "asc" 
          ? a.size - b.size
          : b.size - a.size;
      }
      return 0;
    });
  };
  
  // Obtenir les fichiers triés
  const sortedFiles = results?.matches ? sortFiles(results.matches) : [];
  
  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle className="flex justify-between items-center">
          <span>Résultats de la recherche</span>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              disabled={isLoading || !canScan}
              onClick={scanFiles}
            >
              {isLoading ? (
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <Filter className="h-4 w-4 mr-2" />
              )}
              Rechercher
            </Button>
            
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant="default"
                    size="sm"
                    onClick={copyToClipboard}
                    disabled={!canCopy}
                  >
                    {copied ? (
                      <Check className="h-4 w-4 mr-2" />
                    ) : (
                      <Clipboard className="h-4 w-4 mr-2" />
                    )}
                    {copied ? "Copié!" : "Copier"}
                  </Button>
                </TooltipTrigger>
                <TooltipContent>
                  <p>Copier le contenu des fichiers dans le presse-papier</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </div>
        </CardTitle>
        <CardDescription>
          Fichiers correspondant à vos critères
        </CardDescription>
      </CardHeader>
      <CardContent>
        {/* Affichage des erreurs */}
        {error && (
          <div className="bg-destructive/20 border border-destructive p-3 mb-4 rounded-md flex items-start gap-2">
            <AlertCircle className="h-5 w-5 text-destructive shrink-0 mt-0.5" />
            <div>
              <p className="font-medium text-destructive">Erreur</p>
              <p className="text-sm">{error}</p>
            </div>
          </div>
        )}
        
        {/* Affichage pendant le chargement */}
        {isLoading ? (
          <div className="flex justify-center items-center h-[calc(100vh-300px)]">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
          </div>
        ) : !results ? (
          /* Aucune recherche effectuée */
          <div className="flex flex-col items-center justify-center h-[calc(100vh-300px)] text-center">
            <Filter className="h-12 w-12 text-muted-foreground opacity-50 mb-3" />
            <p className="text-muted-foreground">
              Lancez une recherche pour voir les résultats
            </p>
            <p className="text-xs text-muted-foreground">
              Configurez vos critères dans le panneau de gauche, puis cliquez sur Rechercher
            </p>
          </div>
        ) : results.matches.length === 0 ? (
          /* Aucun résultat trouvé */
          <div className="flex flex-col items-center justify-center h-[calc(100vh-300px)] text-center">
            <AlertCircle className="h-12 w-12 text-muted-foreground opacity-50 mb-3" />
            <p className="text-muted-foreground">
              Aucun fichier ne correspond à vos critères
            </p>
          </div>
        ) : (
          /* Affichage des résultats */
          <div>
            {/* Statistiques générales */}
            {results.stats && <StatsDisplay stats={results.stats} />}
            
            {/* Statistiques par extension */}
            {results.stats && <ExtensionStats stats={results.stats} />}
            
            {/* Nombre de fichiers trouvés et boutons de tri */}
            <div className="mb-4 flex justify-between items-center">
              <p className="text-sm text-muted-foreground">
                {results.totalMatches} fichier(s) trouvé(s)
              </p>
              
              <div className="flex gap-2">
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <Button
                        variant="ghost"
                        size="sm"
                        className={`px-2 ${sortField === 'extension' ? 'bg-secondary/50' : ''}`}
                        onClick={() => toggleSort('extension')}
                      >
                        Extension
                        {sortField === 'extension' && (
                          sortDirection === 'asc' ? 
                            <ArrowUp className="h-3 w-3 ml-1" /> : 
                            <ArrowDown className="h-3 w-3 ml-1" />
                        )}
                      </Button>
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>Trier par extension</p>
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>
                
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <Button
                        variant="ghost"
                        size="sm"
                        className={`px-2 ${sortField === 'size' ? 'bg-secondary/50' : ''}`}
                        onClick={() => toggleSort('size')}
                      >
                        Taille
                        {sortField === 'size' && (
                          sortDirection === 'asc' ? 
                            <ArrowUp className="h-3 w-3 ml-1" /> : 
                            <ArrowDown className="h-3 w-3 ml-1" />
                        )}
                      </Button>
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>Trier par taille</p>
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>
              </div>
            </div>
            
            {/* Liste des fichiers */}
            <FileList files={sortedFiles} />
          </div>
        )}
      </CardContent>
    </Card>
  );
} 