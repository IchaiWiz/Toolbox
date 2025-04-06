import { Plus } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

interface InputWithButtonProps {
  value: string;
  onChange: (value: string) => void;
  onAdd: () => void;
  placeholder?: string;
  buttonLabel?: string;
}

/**
 * Composant d'entrée avec bouton d'ajout
 */
export function InputWithButton({
  value,
  onChange,
  onAdd,
  placeholder = "Entrer une valeur",
  buttonLabel = "Ajouter"
}: InputWithButtonProps) {
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && value.trim()) {
      e.preventDefault();
      onAdd();
    }
  };

  return (
    <div className="flex items-stretch gap-2">
      <Input
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        className="flex-1"
      />
      <Button 
        onClick={onAdd} 
        disabled={!value.trim()}
        type="button"
        size="sm"
      >
        <Plus className="h-4 w-4 mr-1" />
        {buttonLabel}
      </Button>
    </div>
  );
} 