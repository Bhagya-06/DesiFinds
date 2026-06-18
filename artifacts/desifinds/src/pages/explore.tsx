import { useState, useEffect } from "react";
import { useLocation } from "wouter";
import { motion } from "framer-motion";
import { SlidersHorizontal, X, Search } from "lucide-react";
import { useListProducts, getListProductsQueryKey, useListCategories } from "@workspace/api-client-react";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import ProductCard from "@/components/ProductCard";
import SearchBar from "@/components/SearchBar";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";

const CATEGORY_ICONS: Record<string, string> = {
  Apparel: "👔", Footwear: "👟", Electronics: "💻", Audio: "🎧",
  Watches: "⌚", Skincare: "✨", Bags: "👜", Jewelry: "💍",
  Furniture: "🛋️", "Home Decor": "🏮", Kitchen: "🍳", Fitness: "🏋️",
  Perfumes: "🌸", Eyewear: "👓",
};

const SORT_OPTIONS = [
  { label: "Best Match", value: "" },
  { label: "Price: Low to High", value: "price_asc" },
  { label: "Price: High to Low", value: "price_desc" },
  { label: "Highest Rated", value: "rating_desc" },
];

function ProductSkeleton() {
  return (
    <div className="bg-card border border-card-border rounded-2xl overflow-hidden">
      <Skeleton className="aspect-[4/3] w-full" />
      <div className="p-4 space-y-3">
        <Skeleton className="h-3 w-20" /><Skeleton className="h-4 w-full" />
        <Skeleton className="h-3 w-3/4" /><Skeleton className="h-8 w-full" />
      </div>
    </div>
  );
}

export default function ExplorePage() {
  // wouter useLocation() doesn't include query params — use window.location.search
  const searchParams = new URLSearchParams(typeof window !== "undefined" ? window.location.search : "");

  const [category, setCategory] = useState(searchParams.get("category") || "");
  const [brand, setBrand] = useState(searchParams.get("brand") || "");
  const [q, setQ] = useState("");
  const [minPrice, setMinPrice] = useState<number | undefined>(undefined);
  const [maxPrice, setMaxPrice] = useState<number | undefined>(undefined);
  const [minRating, setMinRating] = useState<number | undefined>(undefined);
  const [page, setPage] = useState(0);
  const [showFilters, setShowFilters] = useState(false);
  const limit = 24;

  const { data: categories } = useListCategories();

  const queryParams = {
    category: category || undefined,
    brand: brand || undefined,
    q: q || undefined,
    minPrice,
    maxPrice,
    minRating,
    limit,
    offset: page * limit,
  };

  const { data, isLoading } = useListProducts(queryParams, {
    query: { queryKey: getListProductsQueryKey(queryParams) },
  });

  useEffect(() => {
    setPage(0);
  }, [category, brand, q, minPrice, maxPrice, minRating]);

  const activeFiltersCount = [category, brand, q, minPrice, maxPrice, minRating].filter(Boolean).length;

  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-foreground mb-1">Explore Indian Products</h1>
          <p className="text-muted-foreground text-sm">
            Browse {data?.total?.toLocaleString("en-IN") || "5,000+"} premium Indian products across all categories
          </p>
        </div>

        {/* Search */}
        <div className="mb-6">
          <SearchBar onSearch={setQ} placeholder="Search within Indian products..." />
        </div>

        {/* Category pills */}
        <div className="flex gap-2 overflow-x-auto pb-2 mb-6" style={{ scrollbarWidth: "none" }}>
          <button
            onClick={() => setCategory("")}
            className={cn("shrink-0 flex items-center gap-1.5 px-4 py-2 rounded-full border text-sm font-medium transition-all",
              !category ? "border-primary bg-primary/10 text-primary" : "border-border text-foreground hover:border-primary/40")}
          >
            All
          </button>
          {(categories || Object.keys(CATEGORY_ICONS).map((name) => ({ name, count: 0, icon: CATEGORY_ICONS[name] }))).map((cat) => (
            <button
              key={cat.name}
              onClick={() => setCategory(cat.name === category ? "" : cat.name)}
              className={cn("shrink-0 flex items-center gap-1.5 px-4 py-2 rounded-full border text-sm font-medium transition-all",
                category === cat.name ? "border-primary bg-primary/10 text-primary" : "border-border text-foreground hover:border-primary/40")}
            >
              <span>{cat.icon || CATEGORY_ICONS[cat.name]}</span>
              {cat.name}
            </button>
          ))}
        </div>

        {/* Toolbar */}
        <div className="flex items-center gap-3 mb-6">
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={cn(
              "flex items-center gap-2 px-3.5 py-2 rounded-xl border text-sm font-medium transition-colors",
              showFilters ? "border-primary bg-primary/10 text-primary" : "border-border text-foreground hover:bg-muted"
            )}
          >
            <SlidersHorizontal className="w-4 h-4" />
            Filters
            {activeFiltersCount > 0 && (
              <span className="w-5 h-5 rounded-full bg-primary text-primary-foreground text-xs flex items-center justify-center">{activeFiltersCount}</span>
            )}
          </button>

          {brand && (
            <div className="flex items-center gap-1.5 px-3 py-2 rounded-xl border border-secondary/40 bg-secondary/5 text-secondary text-sm">
              {brand}
              <button onClick={() => setBrand("")}><X className="w-3 h-3" /></button>
            </div>
          )}

          {data && (
            <span className="text-sm text-muted-foreground ml-auto">
              {data.total.toLocaleString("en-IN")} products
            </span>
          )}
        </div>

        {/* Filters panel */}
        {showFilters && (
          <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="bg-card border border-border rounded-2xl p-5 mb-6 grid grid-cols-1 sm:grid-cols-3 gap-5">
            <div>
              <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2">Min Price</p>
              <input type="number" placeholder="e.g. 500" value={minPrice || ""} onChange={(e) => setMinPrice(e.target.value ? Number(e.target.value) : undefined)}
                className="w-full px-3 py-2 rounded-lg border border-border bg-background text-sm text-foreground outline-none focus:border-primary" />
            </div>
            <div>
              <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2">Max Price</p>
              <input type="number" placeholder="e.g. 5000" value={maxPrice || ""} onChange={(e) => setMaxPrice(e.target.value ? Number(e.target.value) : undefined)}
                className="w-full px-3 py-2 rounded-lg border border-border bg-background text-sm text-foreground outline-none focus:border-primary" />
            </div>
            <div>
              <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2">Min Rating: {minRating || "Any"}</p>
              <input type="range" min={0} max={4.5} step={0.5} value={minRating || 0} onChange={(e) => setMinRating(Number(e.target.value) || undefined)} className="w-full accent-primary" />
              <div className="flex justify-between text-xs text-muted-foreground mt-1"><span>Any</span><span>4.5+</span></div>
            </div>
          </motion.div>
        )}

        {/* Products grid */}
        {isLoading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {[...Array(12)].map((_, i) => <ProductSkeleton key={i} />)}
          </div>
        ) : data && data.products.length > 0 ? (
          <>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {data.products.map((product, i) => (
                <motion.div key={product.id} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.03 }}>
                  <ProductCard product={product} index={i} />
                </motion.div>
              ))}
            </div>

            {/* Pagination */}
            {data.total > limit && (
              <div className="flex items-center justify-center gap-3 mt-10">
                <button
                  disabled={page === 0}
                  onClick={() => setPage(page - 1)}
                  className="px-4 py-2 rounded-xl border border-border text-sm font-medium text-foreground hover:bg-muted disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                >
                  Previous
                </button>
                <span className="text-sm text-muted-foreground">
                  Page {page + 1} of {Math.ceil(data.total / limit)}
                </span>
                <button
                  disabled={(page + 1) * limit >= data.total}
                  onClick={() => setPage(page + 1)}
                  className="px-4 py-2 rounded-xl border border-border text-sm font-medium text-foreground hover:bg-muted disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                >
                  Next
                </button>
              </div>
            )}
          </>
        ) : (
          <div className="text-center py-20">
            <div className="w-16 h-16 rounded-full bg-muted flex items-center justify-center mx-auto mb-4">
              <Search className="w-8 h-8 text-muted-foreground" />
            </div>
            <h3 className="font-semibold text-foreground mb-2">No products found</h3>
            <p className="text-sm text-muted-foreground">Try adjusting your filters or search terms.</p>
            <button onClick={() => { setCategory(""); setBrand(""); setQ(""); setMinPrice(undefined); setMaxPrice(undefined); setMinRating(undefined); }}
              className="mt-4 text-sm text-primary hover:underline">Reset all filters</button>
          </div>
        )}
      </div>

      <Footer />
    </div>
  );
}
