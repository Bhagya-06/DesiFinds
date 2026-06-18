import { useState, useEffect } from "react";
import { useLocation } from "wouter";
import { motion } from "framer-motion";
import { ArrowRight, Zap, Shield, Heart, ChevronRight } from "lucide-react";
import { useListCategories, useListBrands, useGetTrending } from "@workspace/api-client-react";
import Navbar from "@/components/Navbar";
import SearchBar from "@/components/SearchBar";
import Footer from "@/components/Footer";
import ProductCard from "@/components/ProductCard";
import { getRecentSearches, formatPrice } from "@/lib/utils";

const CATEGORY_ICONS: Record<string, string> = {
  Apparel: "👔", Footwear: "👟", Electronics: "💻", Audio: "🎧",
  Watches: "⌚", Skincare: "✨", Bags: "👜", Jewelry: "💍",
  Furniture: "🛋️", "Home Decor": "🏮", Kitchen: "🍳", Fitness: "🏋️",
  Perfumes: "🌸", Eyewear: "👓",
};

const BRAND_COLORS = [
  "from-amber-400 to-orange-500",
  "from-teal-400 to-cyan-500",
  "from-violet-400 to-purple-500",
  "from-rose-400 to-pink-500",
  "from-emerald-400 to-green-500",
  "from-blue-400 to-indigo-500",
];

export default function HomePage() {
  const [, navigate] = useLocation();
  const [recentSearches, setRecentSearches] = useState<string[]>([]);
  const { data: categories } = useListCategories();
  const { data: brands } = useListBrands();
  const { data: trending } = useGetTrending();

  useEffect(() => {
    setRecentSearches(getRecentSearches());
  }, []);

  const handleSearch = (q: string) => {
    navigate(`/search?q=${encodeURIComponent(q)}`);
  };

  return (
    <div className="min-h-screen bg-background paisley-bg">
      <Navbar />

      {/* Hero */}
      <section className="relative overflow-hidden pt-20 pb-24 px-4">
        {/* Decorative blobs */}
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-primary/8 rounded-full blur-3xl -translate-x-1/2 -translate-y-1/2 pointer-events-none" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-secondary/8 rounded-full blur-3xl translate-x-1/2 translate-y-1/2 pointer-events-none" />

        <div className="max-w-4xl mx-auto text-center relative">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            {/* Badge */}
            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-primary/30 bg-primary/5 text-primary text-sm font-medium mb-6">
              <Zap className="w-3.5 h-3.5" />
              <span>AI-Powered Indian Product Discovery</span>
            </div>

            {/* Heading */}
            <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold tracking-tight mb-4 leading-none">
              <span className="text-foreground">Desi</span>
              <span className="text-gradient">Finds</span>
            </h1>
            <p className="text-2xl sm:text-3xl font-light text-muted-foreground mb-3">
              Find Better. <span className="text-primary font-medium">Find Indian.</span>
            </p>
            <p className="text-base sm:text-lg text-muted-foreground max-w-xl mx-auto mb-10">
              Search any international product and discover premium Indian alternatives with similar quality, materials, and aesthetics — at better value.
            </p>

            {/* Search bar */}
            <SearchBar large onSearch={handleSearch} />

            {/* Example chips */}
            <div className="flex flex-wrap justify-center gap-2 mt-5">
              {["Zara Linen Shirt", "AirPods Pro", "Logitech MX Master", "CeraVe Moisturizer", "Nike Sneakers"].map((ex) => (
                <button
                  key={ex}
                  onClick={() => handleSearch(ex)}
                  className="px-3.5 py-1.5 rounded-full border border-border bg-card text-xs text-muted-foreground hover:border-primary hover:text-primary hover:bg-primary/5 transition-all"
                >
                  {ex}
                </button>
              ))}
            </div>
          </motion.div>
        </div>
      </section>

      {/* Recent searches */}
      {recentSearches.length > 0 && (
        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mb-12">
          <div className="flex items-center gap-3 mb-3">
            <p className="text-sm font-semibold text-muted-foreground">Recent Searches</p>
          </div>
          <div className="flex flex-wrap gap-2">
            {recentSearches.map((s) => (
              <button
                key={s}
                onClick={() => handleSearch(s)}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-muted border border-border text-xs text-foreground hover:border-primary hover:text-primary transition-all"
              >
                {s}
                <ArrowRight className="w-3 h-3" />
              </button>
            ))}
          </div>
        </section>
      )}

      <div className="lotus-divider max-w-7xl mx-auto px-4 mb-16" />

      {/* Category strip */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mb-16">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-foreground">Browse by Category</h2>
          <button onClick={() => navigate("/explore")} className="flex items-center gap-1 text-sm text-primary hover:underline">
            See all <ChevronRight className="w-4 h-4" />
          </button>
        </div>
        <div className="flex gap-3 overflow-x-auto pb-2 scrollbar-none" style={{ scrollbarWidth: "none" }}>
          {(categories && categories.length > 0
            ? categories
            : Object.entries(CATEGORY_ICONS).map(([name, icon]) => ({ name, count: 0, icon }))
          ).map((cat) => (
            <button
              key={cat.name}
              onClick={() => navigate(`/explore?category=${cat.name}`)}
              className="shrink-0 flex flex-col items-center gap-2 px-5 py-4 rounded-2xl border border-border bg-card hover:border-primary hover:bg-primary/5 transition-all group min-w-[90px]"
            >
              <span className="text-2xl">{cat.icon || CATEGORY_ICONS[cat.name] || "🛍️"}</span>
              <span className="text-xs font-medium text-foreground whitespace-nowrap">{cat.name}</span>
              {cat.count > 0 && <span className="text-xs text-muted-foreground">{cat.count}</span>}
            </button>
          ))}
        </div>
      </section>

      {/* Why DesiFinds */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mb-16">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[
            { icon: Zap, title: "AI-Powered Matching", desc: "Our AI analyzes materials, features, and aesthetics to find the most relevant Indian alternatives.", color: "text-primary bg-primary/10" },
            { icon: Shield, title: "Quality Verified", desc: "Every recommendation is curated from established Indian brands with verified quality and real customer reviews.", color: "text-secondary bg-secondary/10" },
            { icon: Heart, title: "Made in India", desc: "Support Indian craftsmanship and entrepreneurship while getting premium products at better value.", color: "text-accent bg-accent/10" },
          ].map(({ icon: Icon, title, desc, color }) => (
            <div key={title} className="rounded-2xl border border-border bg-card p-6">
              <div className={`w-10 h-10 rounded-xl flex items-center justify-center mb-4 ${color}`}>
                <Icon className="w-5 h-5" />
              </div>
              <h3 className="font-semibold text-foreground mb-2">{title}</h3>
              <p className="text-sm text-muted-foreground leading-relaxed">{desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Trending Brands */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mb-16">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-foreground">Trending Indian Brands</h2>
          <button onClick={() => navigate("/explore")} className="flex items-center gap-1 text-sm text-primary hover:underline">
            See all <ChevronRight className="w-4 h-4" />
          </button>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
          {(brands || []).slice(0, 10).map((brand, i) => (
            <button
              key={brand.name}
              onClick={() => navigate(`/explore?brand=${brand.name}`)}
              className="group relative overflow-hidden rounded-2xl border border-border bg-card p-4 text-center hover:border-primary/40 transition-all"
            >
              <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${BRAND_COLORS[i % BRAND_COLORS.length]} flex items-center justify-center mx-auto mb-3 text-white text-xl font-bold shadow-sm`}>
                {brand.name[0]}
              </div>
              <p className="text-sm font-semibold text-foreground line-clamp-1">{brand.name}</p>
              <p className="text-xs text-muted-foreground line-clamp-1 mt-0.5">{brand.categories[0]}</p>
            </button>
          ))}
        </div>
      </section>

      {/* Trending Products */}
      {trending && trending.topProducts.length > 0 && (
        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mb-16">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-foreground">Top Products</h2>
            <button onClick={() => navigate("/explore")} className="flex items-center gap-1 text-sm text-primary hover:underline">
              See all <ChevronRight className="w-4 h-4" />
            </button>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {trending.topProducts.slice(0, 4).map((product, i) => (
              <motion.div key={product.id} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }}>
                <ProductCard product={product} index={i} />
              </motion.div>
            ))}
          </div>
        </section>
      )}

      <Footer />
    </div>
  );
}
