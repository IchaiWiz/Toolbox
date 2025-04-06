import { Sun, Moon, Palette, Leaf, Waves, Sunset, TreePine, Flower } from "lucide-react";
import { Button } from "@/components/ui/button";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { useTheme } from "@/contexts/ThemeContext";
import { useEffect, useState } from "react";

export function ThemeSwitcher() {
  const { theme, setTheme } = useTheme();
  const [menuOpen, setMenuOpen] = useState(false);

  const handleThemeChange = (newTheme: string) => {
    // Forcer la fermeture du menu avant de changer le thème
    setMenuOpen(false);
    // Petit délai pour s'assurer que le menu a eu le temps de se fermer
    setTimeout(() => {
      setTheme(newTheme as any);
    }, 50);
  };

  return (
    <DropdownMenu open={menuOpen} onOpenChange={setMenuOpen}>
      <DropdownMenuTrigger asChild>
        <Button 
          variant="outline" 
          size="icon" 
          className="transition-all duration-200 hover:bg-secondary"
        >
          {theme === "light" && <Sun className="h-5 w-5" />}
          {theme === "dark" && <Moon className="h-5 w-5" />}
          {theme === "fancy" && <Palette className="h-5 w-5" />}
          {theme === "nature" && <Leaf className="h-5 w-5" />}
          {theme === "ocean" && <Waves className="h-5 w-5" />}
          {theme === "sunset" && <Sunset className="h-5 w-5" />}
          {theme === "forest" && <TreePine className="h-5 w-5" />}
          {theme === "lavender" && <Flower className="h-5 w-5" />}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="animate-in slide-in-from-top-2 duration-200">
        <DropdownMenuItem 
          onClick={() => handleThemeChange("light")}
          className="flex items-center gap-2 cursor-pointer"
        >
          <Sun className="h-4 w-4" />
          <span>Clair</span>
        </DropdownMenuItem>
        <DropdownMenuItem 
          onClick={() => handleThemeChange("dark")}
          className="flex items-center gap-2 cursor-pointer"
        >
          <Moon className="h-4 w-4" />
          <span>Sombre</span>
        </DropdownMenuItem>
        <DropdownMenuItem 
          onClick={() => handleThemeChange("fancy")}
          className="flex items-center gap-2 cursor-pointer"
        >
          <Palette className="h-4 w-4" />
          <span>Fantaisie</span>
        </DropdownMenuItem>
        <DropdownMenuItem 
          onClick={() => handleThemeChange("nature")}
          className="flex items-center gap-2 cursor-pointer"
        >
          <Leaf className="h-4 w-4" />
          <span>Nature</span>
        </DropdownMenuItem>
        <DropdownMenuItem 
          onClick={() => handleThemeChange("ocean")}
          className="flex items-center gap-2 cursor-pointer"
        >
          <Waves className="h-4 w-4" />
          <span>Océan</span>
        </DropdownMenuItem>
        <DropdownMenuItem 
          onClick={() => handleThemeChange("sunset")}
          className="flex items-center gap-2 cursor-pointer"
        >
          <Sunset className="h-4 w-4" />
          <span>Coucher de soleil</span>
        </DropdownMenuItem>
        <DropdownMenuItem 
          onClick={() => handleThemeChange("forest")}
          className="flex items-center gap-2 cursor-pointer"
        >
          <TreePine className="h-4 w-4" />
          <span>Forêt</span>
        </DropdownMenuItem>
        <DropdownMenuItem 
          onClick={() => handleThemeChange("lavender")}
          className="flex items-center gap-2 cursor-pointer"
        >
          <Flower className="h-4 w-4" />
          <span>Lavande</span>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
} 