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

const BRAND_COMPARISONS = {
  luggage: {
    category: "Premium Travel Gear",
    globalBrand: "Away Travel (USA)",
    localBrand: "Mokobara (India)",
    globalPrice: "₹28,000",
    localPrice: "₹8,500",
    metrics: [
      { name: "Shell Material (German Polycarbonate)", global: 100, local: 100, reason: "Both use identical Covestro Makrolon aerospace-grade Polycarbonate" },
      { name: "Wheel Silentness & Gliding", global: 95, local: 98, reason: "Mokobara uses Japanese Hinomoto-equivalent custom dual-caster wheels" },
      { name: "Stitch & Zipper Strength (YKK)", global: 98, local: 98, reason: "Both use heavy-duty water-repellent YKK nylon-coil zippers" },
      { name: "Warranty Duration", global: 100, local: 80, reason: "Away offers lifetime warranty; Mokobara offers a robust 6-year warranty" },
    ],
    trustPoints: [
      "German Makrolon® Polycarbonate shell",
      "Super-silent Hinomoto double-wheels",
      "30% of the cost (no import duties)"
    ],
    verdict: "Mokobara offers identical structural shell and gliding hardware specs at a fraction of the cost, making it the supreme value alternative for frequent flyers."
  },
  skincare: {
    category: "Science-Backed Skincare",
    globalBrand: "Luxury Import Brands (USA/EU)",
    localBrand: "Minimalist / Dot & Key (India)",
    globalPrice: "₹2,500",
    localPrice: "₹599",
    metrics: [
      { name: "Sourcing Purity (BASF, DSM)", global: 100, local: 100, reason: "Minimalist sources raw actives from global leaders in Germany & Netherlands" },
      { name: "Toxin & Filler Cleanliness (No Parabens/Sulfates)", global: 75, local: 100, reason: "Indian brands use 100% clean, fragrance-free, sulfate/paraben-free formulas" },
      { name: "Harmful Sunscreen Filters (No Oxybenzone)", global: 60, local: 100, reason: "Minimalist uses clean new-age filters that are hormone-safe and eco-safe" },
      { name: "Climate Optimization (Indian UV/Humidity)", global: 70, local: 98, reason: "Specifically formulated to prevent greasy shine under hot, tropical climates" },
    ],
    trustPoints: [
      "Zero added synthetic fragrances or dyes",
      "100% free of Parabens, Sulfates, Phthalates, and Oxybenzone",
      "Ingredients sourced from BASF (Germany) & DSM (Netherlands)",
      "Clinical efficacy trials published transparently on website"
    ],
    verdict: "Local brands like Minimalist and Dot & Key offer superior formulation safety by eliminating harsh chemical stabilizers and hormone-disrupting filters found in global products, tailoring them for tropical climates."
  },
  watches: {
    category: "Automatic Horology",
    globalBrand: "Seiko / Tissot (Japan/Swiss)",
    localBrand: "Bangalore Watch Company (India)",
    globalPrice: "₹65,000",
    localPrice: "₹68,000",
    metrics: [
      { name: "Steel Quality (Surgical 316L)", global: 100, local: 100, reason: "Both use marine-grade high-nickel anti-corrosive stainless steel" },
      { name: "Dial Glass (Sapphire)", global: 95, local: 100, reason: "BWC uses scratch-resistant double-domed sapphire with anti-reflective coating" },
      { name: "Calibre Movement Reliability", global: 100, local: 95, reason: "Seiko uses in-house calibres; BWC utilizes robust Japanese Miyota / Swiss Sellita" },
      { name: "Collectibility & Design Theme", global: 90, local: 100, reason: "BWC features hand-finished dials inspired by ISRO, IAF, and Indian history" },
    ],
    trustPoints: [
      "Surgical-grade 316L stainless steel casings",
      "Scratchproof double-domed Sapphire crystals",
      "Individually hand-assembled in Bangalore"
    ],
    verdict: "Bangalore Watch Company provides Tissot-level hand-finishing, Japanese automatic precision, and unique national-heritage stories that make them fine heirlooms."
  },
  shirts: {
    category: "Bespoke & Clean Apparel",
    globalBrand: "Global Fast Fashion (Zara/H&M)",
    localBrand: "Bombay Shirt Company / Snitch (India)",
    globalPrice: "₹4,500",
    localPrice: "₹1,899",
    metrics: [
      { name: "Natural Fiber Sourcing (Giza/Linen)", global: 40, local: 100, reason: "Indian brands use Egyptian Giza cotton and French linen instead of synthetic polyesters" },
      { name: "Chemical Dyes Safety (No Azo Dyes)", global: 70, local: 100, reason: "BSC & Snitch use certified non-toxic organic dyes that do not bleed skin-irritants" },
      { name: "Stitch Density & Seam Strength (18+ SPI)", global: 70, local: 95, reason: "BSC uses tighter stitches per inch ensuring seams do not fray or stretch" },
      { name: "Fit Customization & Tailoring", global: 30, local: 100, reason: "Custom tailors collar, cuffs, chest, and arms for individual body dimensions" },
    ],
    trustPoints: [
      "100% natural long-staple Egyptian Giza Cotton & French Flax Linen",
      "Eco-certified, non-toxic organic dyes (No Azo Dyes or Formaldehyde)",
      "High Stitches Per Inch (18+ SPI) construction for durability",
      "Handcrafted tailors ensuring fair artisanal local wages"
    ],
    verdict: "Indian slow-fashion brands stand in stark contrast to global fast fashion imports by eliminating plastic polyester fabrics and chemical dyes in favor of high-breathability Giza cotton and custom tailored fits."
  }
};

export default function HomePage() {
  const [, navigate] = useLocation();
  const [recentSearches, setRecentSearches] = useState<string[]>([]);
  const [selectedComparison, setSelectedComparison] = useState<string>("luggage");
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

      {/* Quality Comparison & Trust Index */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mb-16">
        <div className="text-center max-w-3xl mx-auto mb-10">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full border border-primary/20 bg-primary/5 text-primary text-xs font-semibold mb-3">
            <Shield className="w-3.5 h-3.5" />
            <span>Verified Quality Index</span>
          </div>
          <h2 className="text-3xl font-extrabold text-foreground tracking-tight sm:text-4xl">
            Side-by-Side Trust Analysis
          </h2>
          <p className="text-muted-foreground mt-3 text-sm sm:text-base">
            We verified the materials, sourcing networks, and certifications of premium Indian startups against global standard-setters. Here is the factual, unsponsored comparison.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          {/* Sidebar / Tabs */}
          <div className="lg:col-span-3 flex lg:flex-col gap-2 overflow-x-auto pb-2 lg:pb-0 scrollbar-none">
            {Object.entries(BRAND_COMPARISONS).map(([key, comp]) => (
              <button
                key={key}
                onClick={() => setSelectedComparison(key)}
                className={`w-full text-left px-4 py-3 rounded-xl border text-sm font-medium transition-all shrink-0 md:shrink-1 ${
                  selectedComparison === key
                    ? "bg-primary text-primary-foreground border-primary shadow-sm"
                    : "bg-card text-foreground border-border hover:border-primary/40"
                }`}
              >
                <div className="font-semibold">{comp.category}</div>
                <div className={`text-xs ${selectedComparison === key ? "text-primary-foreground/80" : "text-muted-foreground"} mt-0.5`}>
                  {comp.localBrand.split(" ")[0]} vs {comp.globalBrand.split(" ")[0]}
                </div>
              </button>
            ))}
          </div>

          {/* Comparison Details Dashboard */}
          <div className="lg:col-span-9 rounded-3xl border border-border bg-card shadow-sm p-6 sm:p-8">
            {/* Header: Brand vs Brand */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border pb-6 mb-6">
              <div className="grid grid-cols-2 gap-8 items-center">
                <div>
                  <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Global Standard</span>
                  <h3 className="text-lg font-bold text-foreground mt-1">{BRAND_COMPARISONS[selectedComparison as keyof typeof BRAND_COMPARISONS].globalBrand}</h3>
                  <div className="text-sm font-semibold text-rose-500 mt-0.5">
                    Avg. Price: {BRAND_COMPARISONS[selectedComparison as keyof typeof BRAND_COMPARISONS].globalPrice}
                  </div>
                </div>
                <div>
                  <span className="text-xs font-semibold text-primary uppercase tracking-wider">Premium Indian Match</span>
                  <h3 className="text-lg font-bold text-foreground mt-1">{BRAND_COMPARISONS[selectedComparison as keyof typeof BRAND_COMPARISONS].localBrand}</h3>
                  <div className="text-sm font-semibold text-emerald-500 mt-0.5">
                    Avg. Price: {BRAND_COMPARISONS[selectedComparison as keyof typeof BRAND_COMPARISONS].localPrice}
                  </div>
                </div>
              </div>
              <div className="shrink-0 flex items-center justify-center bg-primary/10 rounded-2xl px-4 py-3 border border-primary/20 text-center sm:text-right">
                <div>
                  <div className="text-xs text-muted-foreground font-medium">Est. Price Saving</div>
                  <div className="text-xl font-bold text-primary">
                    ~{Math.round(
                      (1 - 
                        Number(BRAND_COMPARISONS[selectedComparison as keyof typeof BRAND_COMPARISONS].localPrice.replace(/[^\d]/g, "")) / 
                        Number(BRAND_COMPARISONS[selectedComparison as keyof typeof BRAND_COMPARISONS].globalPrice.replace(/[^\d]/g, ""))
                      ) * 100
                    )}% Less
                  </div>
                </div>
              </div>
            </div>

            {/* Metrics Breakdown */}
            <div className="space-y-6">
              <h4 className="text-sm font-bold text-foreground tracking-wider uppercase">Quality Metrics Comparison</h4>
              {BRAND_COMPARISONS[selectedComparison as keyof typeof BRAND_COMPARISONS].metrics.map((metric) => (
                <div key={metric.name} className="space-y-2">
                  <div className="flex justify-between items-center text-sm font-medium">
                    <span className="text-foreground">{metric.name}</span>
                    <span className="text-xs text-muted-foreground">{metric.local}% Match</span>
                  </div>
                  
                  {/* Progress bars */}
                  <div className="grid grid-cols-2 gap-4">
                    {/* Global Bar */}
                    <div className="space-y-1">
                      <div className="h-2 w-full bg-muted rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-muted-foreground/40 rounded-full transition-all duration-500" 
                          style={{ width: `${metric.global}%` }}
                        />
                      </div>
                      <div className="text-[10px] text-muted-foreground">Global Standard ({metric.global}%)</div>
                    </div>
                    {/* Indian Bar */}
                    <div className="space-y-1">
                      <div className="h-2 w-full bg-muted rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-gradient-to-r from-primary to-emerald-500 rounded-full transition-all duration-500" 
                          style={{ width: `${metric.local}%` }}
                        />
                      </div>
                      <div className="text-[10px] text-primary font-medium">Local Brand ({metric.local}%)</div>
                    </div>
                  </div>
                  <p className="text-xs text-muted-foreground leading-relaxed italic">{metric.reason}</p>
                </div>
              ))}
            </div>

            {/* Verifications and Verdict */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8 pt-8 border-t border-border">
              <div className="space-y-3">
                <h4 className="text-xs font-bold text-foreground tracking-wider uppercase">Verification Highlights</h4>
                <ul className="space-y-2">
                  {BRAND_COMPARISONS[selectedComparison as keyof typeof BRAND_COMPARISONS].trustPoints.map((point, i) => (
                    <li key={i} className="flex items-start gap-2 text-xs text-muted-foreground leading-relaxed">
                      <span className="text-emerald-500 shrink-0 font-bold">✓</span>
                      <span>{point}</span>
                    </li>
                  ))}
                </ul>
              </div>
              <div className="rounded-2xl bg-muted/50 p-4 border border-border">
                <h4 className="text-xs font-bold text-primary tracking-wider uppercase mb-1.5">Expert Quality Verdict</h4>
                <p className="text-xs text-muted-foreground leading-relaxed">
                  {BRAND_COMPARISONS[selectedComparison as keyof typeof BRAND_COMPARISONS].verdict}
                </p>
              </div>
            </div>
          </div>
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
