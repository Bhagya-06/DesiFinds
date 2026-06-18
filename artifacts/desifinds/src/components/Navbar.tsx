import { useState } from "react";
import { useLocation } from "wouter";
import { useTheme } from "next-themes";
import { Sun, Moon, Search, Menu, X, Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";

export default function Navbar() {
  const [location, navigate] = useLocation();
  const { theme, setTheme } = useTheme();
  const [menuOpen, setMenuOpen] = useState(false);

  const links = [
    { href: "/", label: "Home" },
    { href: "/explore", label: "Explore" },
    { href: "/workflow", label: "Workflow" },
  ];

  return (
    <nav className="sticky top-0 z-50 border-b border-border/60 bg-background/80 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <button onClick={() => navigate("/")} className="flex items-center gap-2 group">
            <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center shadow-sm">
              <Sparkles className="w-4 h-4 text-white" />
            </div>
            <span className="text-xl font-bold tracking-tight">
              <span className="text-primary">Desi</span>
              <span className="text-foreground">Finds</span>
            </span>
          </button>

          {/* Desktop nav */}
          <div className="hidden md:flex items-center gap-1">
            {links.map((link) => (
              <button
                key={link.href}
                onClick={() => navigate(link.href)}
                className={cn(
                  "px-4 py-2 text-sm font-medium rounded-md transition-colors",
                  location === link.href
                    ? "text-primary bg-primary/10"
                    : "text-muted-foreground hover:text-foreground hover:bg-muted"
                )}
              >
                {link.label}
              </button>
            ))}
          </div>

          {/* Actions */}
          <div className="flex items-center gap-2">
            <button
              onClick={() => navigate("/search")}
              className="hidden sm:flex items-center gap-2 px-3 py-2 text-sm text-muted-foreground border border-border rounded-lg hover:bg-muted transition-colors"
            >
              <Search className="w-4 h-4" />
              <span>Search products</span>
              <kbd className="hidden lg:inline-flex items-center px-1.5 py-0.5 text-xs bg-muted rounded border border-border">⌘K</kbd>
            </button>

            <button
              onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
              className="p-2 rounded-lg text-muted-foreground hover:text-foreground hover:bg-muted transition-colors"
              aria-label="Toggle theme"
            >
              {theme === "dark" ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
            </button>

            <button
              onClick={() => setMenuOpen(!menuOpen)}
              className="md:hidden p-2 rounded-lg text-muted-foreground hover:bg-muted transition-colors"
            >
              {menuOpen ? <X className="w-4 h-4" /> : <Menu className="w-4 h-4" />}
            </button>
          </div>
        </div>

        {/* Mobile menu */}
        {menuOpen && (
          <div className="md:hidden border-t border-border py-2 pb-3 space-y-1">
            {links.map((link) => (
              <button
                key={link.href}
                onClick={() => { navigate(link.href); setMenuOpen(false); }}
                className={cn(
                  "w-full text-left px-4 py-2.5 text-sm font-medium rounded-md transition-colors",
                  location === link.href
                    ? "text-primary bg-primary/10"
                    : "text-muted-foreground hover:text-foreground hover:bg-muted"
                )}
              >
                {link.label}
              </button>
            ))}
          </div>
        )}
      </div>
    </nav>
  );
}
