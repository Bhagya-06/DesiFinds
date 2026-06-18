import { useState, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { SlidersHorizontal, X, Sparkles, AlertCircle, ChevronDown, ChevronUp, Key } from "lucide-react";
import { useSearchProducts } from "@workspace/api-client-react";
import type { SearchResult, ProductMatch } from "@workspace/api-client-react";
import Navbar from "@/components/Navbar";
import SearchBar from "@/components/SearchBar";
import ProductCard from "@/components/ProductCard";
import Footer from "@/components/Footer";
import { Skeleton } from "@/components/ui/skeleton";
import { formatPrice, getApiKey, setApiKey } from "@/lib/utils";
import { cn } from "@/lib/utils";

const SORT_OPTIONS = ["Best Match", "Price: Low to High", "Price: High to Low", "Highest Rated"];
const CATEGORIES = ["All", "Apparel", "Footwear", "Electronics", "Audio", "Watches", "Skincare", "Bags", "Jewelry", "Furniture", "Home Decor", "Kitchen", "Fitness", "Perfumes", "Eyewear"];

function ProductSkeleton() {
  return (
    <div className="bg-card border border-card-border rounded-2xl overflow-hidden">
      <Skeleton className="aspect-[4/3] w-full" />
      <div className="p-4 space-y-3">
        <Skeleton className="h-3 w-20" />
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-3 w-3/4" />
        <Skeleton className="h-8 w-full" />
      </div>
    </div>
  );
}

function AnalysisCard({ analysis }: { analysis: SearchResult["analysis"] }) {
  const [expanded, setExpanded] = useState(false);
  return (
    <div className="bg-card border border-border rounded-2xl p-5 mb-6">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-primary" />
          <span className="text-sm font-semibold text-foreground">AI Product Analysis</span>
        </div>
        <button onClick={() => setExpanded(!expanded)} className="text-muted-foreground hover:text-foreground transition-colors">
          {expanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>
      </div>
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-sm">
        <div><span className="text-muted-foreground text-xs">Category</span><p className="font-medium text-foreground mt-0.5">{analysis.category}</p></div>
        <div><span className="text-muted-foreground text-xs">Original Brand</span><p className="font-medium text-foreground mt-0.5">{analysis.originalBrand}</p></div>
        <div><span className="text-muted-foreground text-xs">Price Range</span><p className="font-medium text-foreground mt-0.5">{analysis.priceRange}</p></div>
      </div>
      <AnimatePresence>
        {expanded && (
          <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: "auto", opacity: 1 }} exit={{ height: 0, opacity: 0 }} className="overflow-hidden">
            <div className="pt-4 mt-4 border-t border-border grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-muted-foreground text-xs">Aesthetic Style</span>
                <p className="font-medium text-foreground mt-0.5">{analysis.aestheticStyle}</p>
              </div>
              {analysis.features.length > 0 && (
                <div>
                  <span className="text-muted-foreground text-xs">Key Features</span>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {analysis.features.map((f) => (
                      <span key={f} className="px-2 py-0.5 rounded-md bg-primary/10 text-primary text-xs">{f}</span>
                    ))}
                  </div>
                </div>
              )}
              {analysis.materials.length > 0 && (
                <div>
                  <span className="text-muted-foreground text-xs">Materials</span>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {analysis.materials.map((m) => (
                      <span key={m} className="px-2 py-0.5 rounded-md bg-secondary/10 text-secondary text-xs">{m}</span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default function SearchPage() {
  // wouter useLocation() doesn't include query params — use window.location.search
  const initialQuery = new URLSearchParams(typeof window !== "undefined" ? window.location.search : "").get("q") || "";

  const [query, setQuery] = useState(initialQuery);
  const [apiKey, setApiKeyState] = useState(getApiKey);
  const [showApiKey, setShowApiKey] = useState(false);
  const [results, setResults] = useState<SearchResult | null>(null);
  const [sortBy, setSortBy] = useState("Best Match");
  const [categoryFilter, setCategoryFilter] = useState("All");
  const [showFilters, setShowFilters] = useState(false);
  const [priceRange, setPriceRange] = useState<[number, number]>([0, 50000]);
  const [minRating, setMinRating] = useState(0);

  const { mutate: search, isPending, error } = useSearchProducts({
    mutation: {
      onSuccess: (data) => setResults(data),
    },
  });

  const doSearch = useCallback((q: string) => {
    if (!q.trim()) return;
    setQuery(q);
    search({ data: { query: q, apiKey: apiKey || undefined } });
  }, [search, apiKey]);

  useEffect(() => {
    if (initialQuery) doSearch(initialQuery);
  }, []);

  const handleSearch = (q: string) => {
    history.pushState(null, "", `?q=${encodeURIComponent(q)}`);
    doSearch(q);
  };

  const filteredMatches = (results?.matches || []).filter((m: ProductMatch) => {
    if (categoryFilter !== "All" && m.product.category !== categoryFilter) return false;
    if (m.product.price < priceRange[0] || m.product.price > priceRange[1]) return false;
    if (m.product.rating < minRating) return false;
    return true;
  }).sort((a: ProductMatch, b: ProductMatch) => {
    if (sortBy === "Price: Low to High") return a.product.price - b.product.price;
    if (sortBy === "Price: High to Low") return b.product.price - a.product.price;
    if (sortBy === "Highest Rated") return b.product.rating - a.product.rating;
    return b.matchScore - a.matchScore;
  });

  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Search bar */}
        <div className="mb-8">
          <SearchBar defaultValue={query} onSearch={handleSearch} />
        </div>

        {/* API key toggle */}
        <div className="mb-6">
          <button
            onClick={() => setShowApiKey(!showApiKey)}
            className="flex items-center gap-2 text-xs text-muted-foreground hover:text-foreground transition-colors"
          >
            <Key className="w-3.5 h-3.5" />
            {showApiKey ? "Hide" : "Add OpenAI API Key"} for AI-powered matching
          </button>
          <AnimatePresence>
            {showApiKey && (
              <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: "auto", opacity: 1 }} exit={{ height: 0, opacity: 0 }} className="overflow-hidden">
                <div className="flex items-center gap-2 mt-2">
                  <input
                    type="password"
                    value={apiKey}
                    onChange={(e) => { setApiKeyState(e.target.value); setApiKey(e.target.value); }}
                    placeholder="sk-..."
                    className="flex-1 px-3 py-2 rounded-lg border border-border bg-card text-sm text-foreground placeholder:text-muted-foreground outline-none focus:border-primary"
                  />
                  <span className="text-xs text-muted-foreground">Optional — enables AI matching</span>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        <div className="flex gap-6">
          {/* Filters sidebar */}
          <AnimatePresence>
            {showFilters && (
              <motion.aside
                initial={{ width: 0, opacity: 0 }}
                animate={{ width: 220, opacity: 1 }}
                exit={{ width: 0, opacity: 0 }}
                className="shrink-0 overflow-hidden"
              >
                <div className="bg-card border border-border rounded-2xl p-4 space-y-5">
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-sm">Filters</span>
                    <button onClick={() => setShowFilters(false)} className="text-muted-foreground hover:text-foreground">
                      <X className="w-4 h-4" />
                    </button>
                  </div>

                  {/* Category */}
                  <div>
                    <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-2">Category</p>
                    <div className="space-y-1">
                      {CATEGORIES.map((cat) => (
                        <button
                          key={cat}
                          onClick={() => setCategoryFilter(cat)}
                          className={cn(
                            "w-full text-left text-xs px-2.5 py-1.5 rounded-lg transition-colors",
                            categoryFilter === cat ? "bg-primary/10 text-primary font-medium" : "text-foreground hover:bg-muted"
                          )}
                        >
                          {cat}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Min Rating */}
                  <div>
                    <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-2">Min Rating: {minRating > 0 ? `${minRating}+` : "Any"}</p>
                    <input
                      type="range" min={0} max={4.5} step={0.5} value={minRating}
                      onChange={(e) => setMinRating(Number(e.target.value))}
                      className="w-full accent-primary"
                    />
                    <div className="flex justify-between text-xs text-muted-foreground mt-1">
                      <span>Any</span><span>4.5+</span>
                    </div>
                  </div>

                  {/* Reset */}
                  <button
                    onClick={() => { setCategoryFilter("All"); setMinRating(0); setPriceRange([0, 50000]); }}
                    className="w-full text-xs text-center text-primary hover:underline"
                  >
                    Reset filters
                  </button>
                </div>
              </motion.aside>
            )}
          </AnimatePresence>

          {/* Main content */}
          <div className="flex-1 min-w-0">
            {/* Toolbar */}
            {(results || isPending) && (
              <div className="flex items-center gap-3 mb-5">
                <button
                  onClick={() => setShowFilters(!showFilters)}
                  className={cn(
                    "flex items-center gap-2 px-3.5 py-2 rounded-xl border text-sm font-medium transition-colors",
                    showFilters ? "border-primary bg-primary/10 text-primary" : "border-border text-foreground hover:bg-muted"
                  )}
                >
                  <SlidersHorizontal className="w-4 h-4" />
                  Filters
                </button>

                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                  className="px-3 py-2 rounded-xl border border-border bg-card text-sm text-foreground outline-none cursor-pointer"
                >
                  {SORT_OPTIONS.map((o) => <option key={o}>{o}</option>)}
                </select>

                {results && (
                  <span className="text-sm text-muted-foreground ml-auto">
                    {filteredMatches.length} result{filteredMatches.length !== 1 ? "s" : ""} for "{query}"
                    {results.aiPowered && <span className="ml-2 px-2 py-0.5 rounded-full bg-primary/10 text-primary text-xs font-medium">AI-Powered</span>}
                  </span>
                )}
              </div>
            )}

            {/* Loading */}
            {isPending && (
              <div>
                <div className="h-24 bg-card border border-border rounded-2xl mb-6 animate-pulse" />
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                  {[...Array(6)].map((_, i) => <ProductSkeleton key={i} />)}
                </div>
              </div>
            )}

            {/* Error */}
            {error && !isPending && (
              <div className="flex items-start gap-3 p-5 bg-destructive/10 border border-destructive/20 rounded-2xl text-destructive">
                <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
                <div>
                  <p className="font-semibold text-sm">Search failed</p>
                  <p className="text-sm mt-1 opacity-80">Please try again. If you're using AI matching, verify your API key.</p>
                </div>
              </div>
            )}

            {/* Results */}
            {results && !isPending && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                <AnalysisCard analysis={results.analysis} />

                {filteredMatches.length === 0 ? (
                  <div className="text-center py-12">
                    <p className="text-muted-foreground">No products match your filters.</p>
                    <button onClick={() => { setCategoryFilter("All"); setMinRating(0); }} className="mt-3 text-sm text-primary hover:underline">Reset filters</button>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                    {filteredMatches.map((match: ProductMatch, i: number) => (
                      <motion.div
                        key={match.product.id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: i * 0.08 }}
                      >
                        <ProductCard
                          product={match.product}
                          matchScore={match.matchScore}
                          matchReason={match.matchReason}
                          valueProp={match.valueProp}
                          priceSavings={match.priceSavings ?? undefined}
                          index={i}
                        />
                      </motion.div>
                    ))}
                  </div>
                )}
              </motion.div>
            )}

            {/* Empty state */}
            {!results && !isPending && !error && (
              <div className="text-center py-20">
                <div className="w-20 h-20 rounded-full bg-primary/10 flex items-center justify-center mx-auto mb-5">
                  <span className="text-4xl">🔍</span>
                </div>
                <h2 className="text-xl font-semibold text-foreground mb-2">Find your Indian alternative</h2>
                <p className="text-muted-foreground max-w-md mx-auto text-sm">
                  Type any product name, brand, or URL above. Our AI will find the best Indian alternatives for you.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>

      <Footer />
    </div>
  );
}
