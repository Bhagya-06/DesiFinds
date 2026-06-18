import { useState } from "react";
import { useParams, useLocation } from "wouter";
import { motion } from "framer-motion";
import { ArrowLeft, Star, Heart, ExternalLink, Package, Tag, Layers, ChevronRight } from "lucide-react";
import { useGetProduct, getGetProductQueryKey } from "@workspace/api-client-react";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { Skeleton } from "@/components/ui/skeleton";
import { formatPrice, toggleWishlist, isWishlisted } from "@/lib/utils";
import { cn } from "@/lib/utils";

const BADGE_STYLES: Record<string, string> = {
  "Premium Quality": "bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-900/20 dark:text-amber-400",
  "Better Value": "bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-900/20 dark:text-emerald-400",
  "Highly Rated": "bg-blue-50 text-blue-700 border-blue-200 dark:bg-blue-900/20 dark:text-blue-400",
  "Handcrafted": "bg-rose-50 text-rose-700 border-rose-200 dark:bg-rose-900/20 dark:text-rose-400",
  "Artisan Made": "bg-purple-50 text-purple-700 border-purple-200 dark:bg-purple-900/20 dark:text-purple-400",
  "Sustainable": "bg-green-50 text-green-700 border-green-200 dark:bg-green-900/20 dark:text-green-400",
};

export default function ProductPage() {
  const { id } = useParams<{ id: string }>();
  const [, navigate] = useLocation();
  const [wishlisted, setWishlisted] = useState(() => isWishlisted(id || ""));
  const [imgError, setImgError] = useState(false);

  const { data: product, isLoading, error } = useGetProduct(id || "", {
    query: { enabled: !!id, queryKey: getGetProductQueryKey(id || "") },
  });

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        <Navbar />
        <div className="max-w-5xl mx-auto px-4 py-10">
          <Skeleton className="h-8 w-32 mb-8" />
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <Skeleton className="aspect-square rounded-2xl" />
            <div className="space-y-4">
              <Skeleton className="h-6 w-24" />
              <Skeleton className="h-8 w-3/4" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-5/6" />
              <Skeleton className="h-12 w-full" />
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !product) {
    return (
      <div className="min-h-screen bg-background">
        <Navbar />
        <div className="max-w-5xl mx-auto px-4 py-20 text-center">
          <p className="text-3xl mb-3">😕</p>
          <h2 className="text-xl font-semibold text-foreground mb-2">Product not found</h2>
          <p className="text-muted-foreground mb-6">This product may have been removed or the link is invalid.</p>
          <button onClick={() => navigate("/")} className="px-5 py-2.5 bg-primary text-primary-foreground rounded-xl font-medium text-sm hover:opacity-90 transition-opacity">
            Back to Home
          </button>
        </div>
      </div>
    );
  }

  const discount = product.originalPrice ? Math.round((1 - product.price / product.originalPrice) * 100) : null;

  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Breadcrumb */}
        <nav className="flex items-center gap-2 text-sm text-muted-foreground mb-8">
          <button onClick={() => navigate("/")} className="hover:text-foreground transition-colors">Home</button>
          <ChevronRight className="w-3.5 h-3.5" />
          <button onClick={() => navigate(`/explore?category=${product.category}`)} className="hover:text-foreground transition-colors">{product.category}</button>
          <ChevronRight className="w-3.5 h-3.5" />
          <span className="text-foreground line-clamp-1">{product.name}</span>
        </nav>

        {/* Back button */}
        <button
          onClick={() => window.history.back()}
          className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground mb-6 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Back
        </button>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Image */}
          <div className="space-y-3">
            <div className="relative rounded-2xl overflow-hidden bg-muted aspect-square">
              {!imgError ? (
                <img src={product.imageUrl} alt={product.name} className="w-full h-full object-cover" onError={() => setImgError(true)} />
              ) : (
                <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-primary/10 to-secondary/10">
                  <span className="text-8xl font-bold text-primary/20">{product.brand[0]}</span>
                </div>
              )}

              {/* Badges overlay */}
              <div className="absolute top-4 left-4 flex flex-col gap-2">
                {product.madeInIndia && (
                  <span className="flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold bg-white/90 text-emerald-700 shadow backdrop-blur-sm">
                    🇮🇳 Made in India
                  </span>
                )}
                {discount && (
                  <span className="px-3 py-1 rounded-full text-xs font-bold text-white bg-red-500 shadow">
                    {discount}% OFF
                  </span>
                )}
              </div>

              <button
                onClick={() => setWishlisted(toggleWishlist(product.id))}
                className={cn(
                  "absolute top-4 right-4 w-10 h-10 rounded-full flex items-center justify-center shadow transition-all",
                  wishlisted ? "bg-red-500 text-white" : "bg-white/90 text-muted-foreground hover:text-red-500 backdrop-blur-sm"
                )}
              >
                <Heart className={cn("w-5 h-5", wishlisted && "fill-current")} />
              </button>
            </div>
          </div>

          {/* Details */}
          <div>
            {/* Brand */}
            <span className="text-sm font-semibold text-primary uppercase tracking-wide">{product.brand}</span>
            <h1 className="text-2xl font-bold text-foreground mt-1 mb-3 leading-tight">{product.name}</h1>

            {/* Rating */}
            <div className="flex items-center gap-2 mb-4">
              <div className="flex items-center gap-0.5">
                {[...Array(5)].map((_, i) => (
                  <Star key={i} className={cn("w-4 h-4", i < Math.floor(product.rating) ? "fill-amber-400 text-amber-400" : "text-muted-foreground/30")} />
                ))}
              </div>
              <span className="font-semibold text-foreground">{product.rating}</span>
              <span className="text-muted-foreground text-sm">({product.reviewCount.toLocaleString("en-IN")} reviews)</span>
            </div>

            {/* Price */}
            <div className="flex items-baseline gap-3 mb-5">
              <span className="text-3xl font-bold text-foreground">{formatPrice(product.price)}</span>
              {product.originalPrice && (
                <>
                  <span className="text-lg text-muted-foreground line-through">{formatPrice(product.originalPrice)}</span>
                  <span className="text-sm font-semibold text-emerald-600">Save {formatPrice(product.originalPrice - product.price)}</span>
                </>
              )}
            </div>

            {/* Badges */}
            {product.badges.length > 0 && (
              <div className="flex flex-wrap gap-2 mb-5">
                {product.badges.map((badge) => (
                  <span key={badge} className={cn("px-3 py-1 rounded-lg text-xs font-semibold border", BADGE_STYLES[badge] || "bg-muted text-muted-foreground border-border")}>
                    {badge}
                  </span>
                ))}
              </div>
            )}

            {/* Description */}
            <p className="text-sm text-muted-foreground leading-relaxed mb-6">{product.description}</p>

            {/* Materials */}
            {product.materials.length > 0 && (
              <div className="mb-5">
                <div className="flex items-center gap-2 mb-2">
                  <Layers className="w-4 h-4 text-muted-foreground" />
                  <span className="text-sm font-semibold text-foreground">Materials</span>
                </div>
                <div className="flex flex-wrap gap-2">
                  {product.materials.map((m) => (
                    <span key={m} className="px-3 py-1 rounded-lg bg-muted text-xs text-foreground border border-border">{m}</span>
                  ))}
                </div>
              </div>
            )}

            {/* Tags */}
            {product.tags.length > 0 && (
              <div className="mb-6">
                <div className="flex items-center gap-2 mb-2">
                  <Tag className="w-4 h-4 text-muted-foreground" />
                  <span className="text-sm font-semibold text-foreground">Tags</span>
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {product.tags.slice(0, 8).map((tag) => (
                    <span key={tag} className="px-2.5 py-1 rounded-full text-xs bg-primary/10 text-primary">{tag}</span>
                  ))}
                </div>
              </div>
            )}

            {/* Review summary */}
            <div className="bg-muted/50 border border-border rounded-xl p-4 mb-6">
              <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-1.5">Customer Review Summary</p>
              <p className="text-sm text-foreground italic">"{product.reviewSummary}"</p>
            </div>

            {/* CTAs */}
            <div className="flex flex-col sm:flex-row gap-3">
              <a
                href={product.productUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="flex-1 flex items-center justify-center gap-2 px-5 py-3.5 bg-primary text-primary-foreground font-semibold rounded-xl hover:opacity-90 transition-opacity"
              >
                <Package className="w-4 h-4" />
                View on {product.brand}
                <ExternalLink className="w-4 h-4" />
              </a>
              <a
                href={product.brandUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center justify-center gap-2 px-5 py-3.5 border border-border text-foreground font-medium rounded-xl hover:bg-muted transition-colors text-sm"
              >
                Visit Brand Website
                <ExternalLink className="w-3.5 h-3.5" />
              </a>
            </div>
          </div>
        </motion.div>
      </div>

      <Footer />
    </div>
  );
}
