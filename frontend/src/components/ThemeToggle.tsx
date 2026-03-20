import { Moon, Sun } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

import type { ColorScheme } from "../hooks/useColorScheme";

type ThemeToggleProps = {
  value: ColorScheme;
  onChange: (scheme: ColorScheme) => void;
};

export function ThemeToggle({ value, onChange }: ThemeToggleProps) {
  return (
    <div className="inline-flex items-center gap-1 rounded-full border bg-card/90 p-1 shadow-subtle backdrop-blur-sm">
      <Button
        type="button"
        variant="ghost"
        size="icon"
        onClick={() => onChange("light")}
        className={cn(
          "h-9 w-9 rounded-full transition-all duration-150",
          value === "light"
            ? "bg-primary text-primary-foreground shadow-card scale-105"
            : "hover:scale-105 active:scale-95",
        )}
        aria-label="Use light theme"
        aria-pressed={value === "light"}
      >
        <Sun className="h-4 w-4" aria-hidden />
      </Button>
      <Button
        type="button"
        variant="ghost"
        size="icon"
        onClick={() => onChange("dark")}
        className={cn(
          "h-9 w-9 rounded-full transition-all duration-150",
          value === "dark"
            ? "bg-primary text-primary-foreground shadow-card scale-105"
            : "hover:scale-105 active:scale-95",
        )}
        aria-label="Use dark theme"
        aria-pressed={value === "dark"}
      >
        <Moon className="h-4 w-4" aria-hidden />
      </Button>
    </div>
  );
}
