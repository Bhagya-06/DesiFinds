import { useState } from "react";
import { useLocation } from "wouter";
import { useTheme } from "next-themes";
import { Sun, Moon, Search, Menu, X, Sparkles, User, LogOut, Heart } from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuth } from "@/context/AuthContext";

export default function Navbar() {
  const [location, navigate] = useLocation();
  const { theme, setTheme } = useTheme();
  const [menuOpen, setMenuOpen] = useState(false);
  const { currentUser, logout, setAuthModalOpen } = useAuth();

  const links = [
    { href: "/", label: "Home" },
    { href: "/explore", label: "Explore" },
    { href: "/chat", label: "AI Assistant" },
    { href: "/workflow", label: "Workflow" },
  ];

  return (
    <nav className="sticky top-0 z-50 border-b border-border/60 bg-background/80 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <button onClick={() => navigate("/")} className="flex items-center gap-2 group">
            <img src="/favicon.svg" alt="DesiFinds Logo" className="w-8 h-8 object-contain rounded-lg shadow-sm bg-primary/10 p-0.5" />
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

            {/* Auth section */}
            {currentUser ? (
              <div className="hidden md:flex items-center gap-2 border-l border-border pl-2 ml-1">
                <button
                  onClick={() => navigate("/wishlist")}
                  className={cn(
                    "flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold border transition-all",
                    location === "/wishlist"
                      ? "border-primary bg-primary/10 text-primary"
                      : "border-border text-muted-foreground hover:text-foreground hover:bg-muted"
                  )}
                >
                  <Heart className="w-3.5 h-3.5 fill-current" />
                  Wishlist
                </button>
                <div className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-muted text-xs text-foreground font-semibold">
                  <User className="w-3.5 h-3.5 text-primary" />
                  {currentUser.username}
                </div>
                <button
                  onClick={logout}
                  className="p-2 rounded-lg text-muted-foreground hover:text-destructive hover:bg-destructive/10 transition-colors"
                  title="Logout"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <button
                onClick={() => setAuthModalOpen(true)}
                className="hidden md:flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-primary text-primary-foreground text-xs font-semibold hover:opacity-90 transition-opacity ml-1"
              >
                <User className="w-3.5 h-3.5" />
                Sign In
              </button>
            )}

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
            
            {/* Mobile Auth options */}
            <div className="border-t border-border mt-2 pt-2 px-4 space-y-2">
              {currentUser ? (
                <>
                  <div className="flex items-center gap-2 py-1.5 text-sm font-semibold text-foreground">
                    <User className="w-4 h-4 text-primary" />
                    <span>Logged in as: {currentUser.username}</span>
                  </div>
                  <button
                    onClick={() => { navigate("/wishlist"); setMenuOpen(false); }}
                    className="w-full flex items-center gap-2 py-2 text-sm font-medium text-muted-foreground hover:text-foreground"
                  >
                    <Heart className="w-4 h-4 text-red-500 fill-current" />
                    My Wishlist
                  </button>
                  <button
                    onClick={() => { logout(); setMenuOpen(false); }}
                    className="w-full flex items-center gap-2 py-2 text-sm font-medium text-destructive"
                  >
                    <LogOut className="w-4 h-4" />
                    Log Out
                  </button>
                </>
              ) : (
                <button
                  onClick={() => { setAuthModalOpen(true); setMenuOpen(false); }}
                  className="w-full flex items-center justify-center gap-1.5 py-2.5 bg-primary text-primary-foreground font-semibold rounded-lg text-sm"
                >
                  <User className="w-4 h-4" />
                  Sign In
                </button>
              )}
            </div>
          </div>
        )}
      </div>
    </nav>
  );
}
