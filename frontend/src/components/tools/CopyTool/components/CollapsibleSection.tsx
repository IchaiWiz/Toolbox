import { useState } from "react";
import { ChevronDown, ChevronRight } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

interface CollapsibleSectionProps { 
  title: string; 
  description?: string; 
  isOpen?: boolean; 
  children: React.ReactNode;
}

/**
 * Composant pour une section pliable/dépliable
 */
export function CollapsibleSection({ 
  title, 
  description, 
  isOpen: defaultOpen = false, 
  children 
}: CollapsibleSectionProps) {
  const [isOpen, setIsOpen] = useState(defaultOpen);
  
  return (
    <Card className="overflow-hidden">
      <CardHeader 
        className="py-3 cursor-pointer"
        onClick={() => setIsOpen(!isOpen)}
      >
        <div className="flex items-center">
          {isOpen ? (
            <ChevronDown className="h-4 w-4 mr-2 text-muted-foreground" />
          ) : (
            <ChevronRight className="h-4 w-4 mr-2 text-muted-foreground" />
          )}
          <CardTitle className="text-base">{title}</CardTitle>
        </div>
        {description && <CardDescription>{description}</CardDescription>}
      </CardHeader>
      {isOpen && <CardContent>{children}</CardContent>}
    </Card>
  );
} 