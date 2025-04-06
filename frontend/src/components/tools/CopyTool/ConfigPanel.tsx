import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { useContext } from "react";
import { Accordion, AccordionItem, AccordionTrigger, AccordionContent } from "@/components/ui/accordion";

import { useCopyTool, CopyToolProvider, CopyToolContext } from "./CopyToolContext";
import { 
  CollapsibleSection, 
  HistoryDialog, 
  InputWithButton, 
  ItemList 
} from "./components";

/**
 * Panneau de configuration pour l'outil de copie
 */
export function ConfigPanel() {
  // Vérifier si nous sommes déjà dans un contexte CopyTool
  const contextExists = useContext(CopyToolContext) !== undefined;

  // Si le contexte existe déjà, on utilise directement le contenu
  // Sinon, on encapsule le contenu dans un CopyToolProvider
  if (contextExists) {
    return <ConfigPanelContent />;
  } else {
    return (
      <CopyToolProvider>
        <ConfigPanelContent />
      </CopyToolProvider>
    );
  }
}

/**
 * Contenu du panneau de configuration
 * Ce composant interne utilise le hook useCopyTool
 */
function ConfigPanelContent() {
  const { 
    config,
    history,
    directoryInput,
    fileInput,
    extensionInput,
    patternInput,
    excludeDirectoryInput,
    setDirectoryInput,
    setFileInput,
    setExtensionInput,
    setPatternInput,
    setExcludeDirectoryInput,
    addDirectory,
    addFile,
    addExcludeExtension,
    addExcludePattern,
    addExcludeDirectory,
    removeItem,
    editItem,
    toggleRecursive,
    resetConfig,
    loadFromHistory,
    clearHistory,
    toggleFavorite
  } = useCopyTool();
  
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-medium">Configuration</h3>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={resetConfig}>
            Réinitialiser
          </Button>
          
          <HistoryDialog 
            history={history} 
            onApplyConfig={loadFromHistory} 
            onClearHistory={clearHistory}
            onToggleFavorite={toggleFavorite} 
          />
        </div>
      </div>
      
      {/* Section des répertoires */}
      <CollapsibleSection 
        title="Répertoires" 
        description="Dossiers à inclure dans la recherche" 
        isOpen={true}
      >
        <div className="space-y-4">
          <InputWithButton 
            value={directoryInput}
            onChange={setDirectoryInput}
            onAdd={addDirectory}
            placeholder="Chemin du dossier"
            buttonLabel="Ajouter"
          />
          
          <div>
            <Label className="text-xs mb-1 block">Dossiers sélectionnés</Label>
            <ItemList 
              items={config.directories} 
              onRemove={(index) => removeItem("directories", index)} 
              emptyMessage="Aucun dossier sélectionné"
              onEdit={(index, newValue) => editItem("directories", index, newValue)}
            />
          </div>
          
          <div className="flex items-center space-x-2">
            <Checkbox 
              id="recursive" 
              checked={config.recursive} 
              onCheckedChange={toggleRecursive}
            />
            <Label htmlFor="recursive" className="text-sm">
              Inclure les sous-dossiers
            </Label>
          </div>
        </div>
      </CollapsibleSection>
      
      {/* Section des fichiers */}
      <CollapsibleSection 
        title="Fichiers spécifiques" 
        description="Fichiers individuels à copier"
      >
        <div className="space-y-4">
          <InputWithButton 
            value={fileInput}
            onChange={setFileInput}
            onAdd={addFile}
            placeholder="Chemin du fichier"
            buttonLabel="Ajouter"
          />
          
          <div>
            <Label className="text-xs mb-1 block">Fichiers sélectionnés</Label>
            <ItemList 
              items={config.files} 
              onRemove={(index) => removeItem("files", index)} 
              emptyMessage="Aucun fichier sélectionné"
              onEdit={(index, newValue) => editItem("files", index, newValue)}
            />
          </div>
        </div>
      </CollapsibleSection>
      
      {/* Section des exclusions */}
      <CollapsibleSection 
        title="Exclusions" 
        description="Éléments à exclure de la recherche"
        isOpen={false}
      >
        <div className="space-y-4">
          {/* Extensions à exclure */}
          <div>
            <Label htmlFor="extension-input" className="text-sm mb-1 block">Extensions à exclure</Label>
            <InputWithButton 
              value={extensionInput}
              onChange={setExtensionInput}
              onAdd={addExcludeExtension}
              placeholder="Ex: log, tmp, cache"
              buttonLabel="Exclure"
            />
            
            <Accordion type="single" collapsible className="mt-2" defaultValue="">
              <AccordionItem value="excludeExtensions">
                <AccordionTrigger className="py-2 text-xs">
                  Voir les extensions ({config.excludeExtensions.length})
                </AccordionTrigger>
                <AccordionContent>
                  <ItemList 
                    items={config.excludeExtensions} 
                    onRemove={(index) => removeItem("excludeExtensions", index)} 
                    maxHeight="100px"
                    onEdit={(index, newValue) => editItem("excludeExtensions", index, newValue)}
                  />
                </AccordionContent>
              </AccordionItem>
            </Accordion>
          </div>
          
          {/* Motifs à exclure */}
          <div>
            <Label htmlFor="pattern-input" className="text-sm mb-1 block">Motifs à exclure</Label>
            <InputWithButton 
              value={patternInput}
              onChange={setPatternInput}
              onAdd={addExcludePattern}
              placeholder="Ex: .env, package-lock.json"
              buttonLabel="Exclure"
            />
            
            <Accordion type="single" collapsible className="mt-2" defaultValue="">
              <AccordionItem value="excludePatterns">
                <AccordionTrigger className="py-2 text-xs">
                  Voir les motifs ({config.excludePatterns.length})
                </AccordionTrigger>
                <AccordionContent>
                  <ItemList 
                    items={config.excludePatterns} 
                    onRemove={(index) => removeItem("excludePatterns", index)} 
                    maxHeight="100px"
                    onEdit={(index, newValue) => editItem("excludePatterns", index, newValue)}
                  />
                </AccordionContent>
              </AccordionItem>
            </Accordion>
          </div>
          
          {/* Dossiers à exclure */}
          <div>
            <Label htmlFor="exclude-directory-input" className="text-sm mb-1 block">Dossiers à exclure</Label>
            <InputWithButton 
              value={excludeDirectoryInput}
              onChange={setExcludeDirectoryInput}
              onAdd={addExcludeDirectory}
              placeholder="Ex: node_modules, .git"
              buttonLabel="Exclure"
            />
            
            <Accordion type="single" collapsible className="mt-2" defaultValue="">
              <AccordionItem value="excludeDirectories">
                <AccordionTrigger className="py-2 text-xs">
                  Voir les dossiers ({config.excludeDirectories.length})
                </AccordionTrigger>
                <AccordionContent>
                  <ItemList 
                    items={config.excludeDirectories} 
                    onRemove={(index) => removeItem("excludeDirectories", index)} 
                    maxHeight="100px"
                    onEdit={(index, newValue) => editItem("excludeDirectories", index, newValue)}
                  />
                </AccordionContent>
              </AccordionItem>
            </Accordion>
          </div>
        </div>
      </CollapsibleSection>
    </div>
  );
} 