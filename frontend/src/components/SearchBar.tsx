import { useState, useRef, useEffect } from "react";
import { useLocation } from "wouter";
import { Search, X, ArrowRight } from "lucide-react";
import { cn, addRecentSearch } from "@/lib/utils";

interface SearchBarProps {
  large?: boolean;
  defaultValue?: string;
  onSearch?: (q: string) => void;
  placeholder?: string;
}

const EXAMPLE_SEARCHES = [
  "Zara Linen Shirt",
  "AirPods Pro",
  "Logitech MX Master Mouse",
  "CeraVe Moisturizer",
  "Nike Sneakers",
  "Dyson Air Purifier",
  "Ray-Ban Sunglasses",
];

export default function SearchBar({ large, defaultValue = "", onSearch, placeholder }: SearchBarProps) {
  const [, navigate] = useLocation();
  const [value, setValue] = useState(defaultValue);
  const [focused, setFocused] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => { setValue(defaultValue); }, [defaultValue]);

  const handleSearch = (q: string = value) => {
    const trimmed = q.trim();
    if (!trimmed) return;
    addRecentSearch(trimmed);
    if (onSearch) {
      onSearch(trimmed);
    } else {
      navigate(`/search?q=${encodeURIComponent(trimmed)}`);
    }
    setFocused(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") handleSearch();
    if (e.key === "Escape") { setFocused(false); inputRef.current?.blur(); }
  };

  return (
    <div className={cn("relative w-full", large && "max-w-2xl mx-auto")}>
      <div className={cn(
        "flex items-center gap-3 rounded-2xl border bg-card transition-all duration-200",
        large ? "px-5 py-4" : "px-4 py-3",
        focused ? "border-primary shadow-lg shadow-primary/10 ring-2 ring-primary/20" : "border-border shadow-sm hover:border-primary/40"
      )}>
        <Search className={cn("shrink-0 text-muted-foreground", large ? "w-5 h-5" : "w-4 h-4")} />
        <input
          ref={inputRef}
          type="text"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onFocus={() => setFocused(true)}
          onBlur={() => setTimeout(() => setFocused(false), 150)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder || "Search for a product (e.g. Zara Linen Shirt, AirPods Pro)..."}
          className={cn(
            "flex-1 bg-transparent outline-none text-foreground placeholder:text-muted-foreground min-w-0",
            large ? "text-base" : "text-sm"
          )}
        />
        {value && (
          <button onClick={() => setValue("")} className="shrink-0 text-muted-foreground hover:text-foreground transition-colors">
            <X className="w-4 h-4" />
          </button>
        )}
        <button
          onClick={() => handleSearch()}
          className={cn(
            "shrink-0 flex items-center gap-2 rounded-xl font-semibold bg-primary text-primary-foreground hover:opacity-90 transition-opacity",
            large ? "px-5 py-2.5 text-sm" : "px-3 py-1.5 text-xs"
          )}
        >
          {large ? (
            <>Find Indian <ArrowRight className="w-4 h-4" /></>
          ) : (
            <Search className="w-3.5 h-3.5" />
          )}
        </button>
      </div>

      {/* Dropdown suggestions */}
      {focused && !value && (
        <div className="absolute top-full left-0 right-0 mt-2 bg-card border border-border rounded-2xl shadow-xl overflow-hidden z-50">
          <div className="p-3">
            <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2 px-2">Try searching</p>
            {EXAMPLE_SEARCHES.map((example) => (
              <button
                key={example}
                onMouseDown={() => { setValue(example); handleSearch(example); }}
                className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-muted transition-colors text-left group"
              >
                <Search className="w-4 h-4 text-muted-foreground shrink-0" />
                <span className="text-sm text-foreground flex-1">{example}</span>
                <ArrowRight className="w-4 h-4 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity" />
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
