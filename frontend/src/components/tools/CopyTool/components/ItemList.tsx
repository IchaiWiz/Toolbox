import { X, Edit, Check } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useState } from "react";
import { Input } from "@/components/ui/input";

interface ItemListProps {
  items: string[];
  onRemove: (index: number) => void;
  emptyMessage?: string;
  maxHeight?: string;
  onEdit?: (index: number, newValue: string) => void;
}

/**
 * Composant pour afficher une liste d'éléments avec possibilité de les supprimer et éditer
 */
export function ItemList({ 
  items, 
  onRemove, 
  emptyMessage = "Aucun élément", 
  maxHeight = "150px",
  onEdit
}: ItemListProps) {
  const [editIndex, setEditIndex] = useState<number | null>(null);
  const [editValue, setEditValue] = useState<string>("");

  const handleEditClick = (index: number, value: string) => {
    setEditIndex(index);
    setEditValue(value);
  };

  const handleSaveEdit = (index: number) => {
    if (onEdit && editValue.trim()) {
      onEdit(index, editValue);
    }
    setEditIndex(null);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>, index: number) => {
    if (e.key === 'Enter') {
      handleSaveEdit(index);
    } else if (e.key === 'Escape') {
      setEditIndex(null);
    }
  };

  if (items.length === 0) {
    return (
      <p className="text-center text-sm text-muted-foreground py-2">
        {emptyMessage}
      </p>
    );
  }

  return (
    <ScrollArea className={`w-full max-h-[${maxHeight}]`}>
      <div className="flex flex-wrap gap-2 p-1">
        {items.map((item, index) => (
          <Badge 
            key={index} 
            variant="secondary"
            className={`flex items-center gap-1.5 py-1.5 pl-2.5 pr-1.5 group ${editIndex === index ? 'w-full' : ''}`}
          >
            {editIndex === index ? (
              <div className="flex w-full items-center gap-1">
                <Input
                  value={editValue}
                  onChange={(e) => setEditValue(e.target.value)}
                  onKeyDown={(e) => handleKeyDown(e, index)}
                  className="h-6 py-0 px-1 text-xs"
                  autoFocus
                />
                <button
                  onClick={() => handleSaveEdit(index)}
                  className="p-0.5 rounded-full bg-green-100 hover:bg-green-200"
                  aria-label="Sauvegarder"
                >
                  <Check className="h-3 w-3" />
                </button>
              </div>
            ) : (
              <>
                <span className="overflow-x-auto max-w-[300px]" title={item}>{item}</span>
                {onEdit && (
                  <button
                    onClick={() => handleEditClick(index, item)}
                    className="p-0.5 rounded-full bg-muted/20 hover:bg-muted/60"
                    aria-label={`Éditer ${item}`}
                  >
                    <Edit className="h-3 w-3" />
                  </button>
                )}
                <button
                  onClick={() => onRemove(index)}
                  className="p-0.5 rounded-full bg-muted/20 hover:bg-muted/60"
                  aria-label={`Supprimer ${item}`}
                >
                  <X className="h-3 w-3" />
                </button>
              </>
            )}
          </Badge>
        ))}
      </div>
    </ScrollArea>
  );
} 