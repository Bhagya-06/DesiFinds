import { useState } from "react";
import { useLocation } from "wouter";
import { Heart, Star, ExternalLink, TrendingUp } from "lucide-react";
import { cn, formatPrice, toggleWishlist, isWishlisted } from "@/lib/utils";
import type { Product } from "@workspace/api-client-react";

interface ProductCardProps {
  product: Product;
  matchScore?: number;
  matchReason?: string;
  valueProp?: string;
  priceSavings?: number | null;
  index?: number;
}

const BADGE_STYLES: Record<string, string> = {
  "Premium Quality": "bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-900/20 dark:text-amber-400 dark:border-amber-800",
  "Better Value": "bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-900/20 dark:text-emerald-400 dark:border-emerald-800",
  "Highly Rated": "bg-blue-50 text-blue-700 border-blue-200 dark:bg-blue-900/20 dark:text-blue-400 dark:border-blue-800",
  "Handcrafted": "bg-rose-50 text-rose-700 border-rose-200 dark:bg-rose-900/20 dark:text-rose-400 dark:border-rose-800",
  "Artisan Made": "bg-purple-50 text-purple-700 border-purple-200 dark:bg-purple-900/20 dark:text-purple-400 dark:border-purple-800",
  "Sustainable": "bg-green-50 text-green-700 border-green-200 dark:bg-green-900/20 dark:text-green-400 dark:border-green-800",
  "Made in India": "bg-orange-50 text-orange-700 border-orange-200 dark:bg-orange-900/20 dark:text-orange-400 dark:border-orange-800",
};

export default function ProductCard({ product, matchScore, matchReason, valueProp, priceSavings, index = 0 }: ProductCardProps) {
  const [, navigate] = useLocation();
  const [wishlisted, setWishlisted] = useState(() => isWishlisted(product.id));
  const [imgError, setImgError] = useState(false);

  const handleWishlist = (e: React.MouseEvent) => {
    e.stopPropagation();
    const result = toggleWishlist(product.id);
    setWishlisted(result);
  };

  const matchColor = matchScore
    ? matchScore >= 90 ? "bg-emerald-500" : matchScore >= 75 ? "bg-amber-500" : "bg-blue-500"
    : null;

  return (
    <div
      className="product-card bg-card border border-card-border rounded-2xl overflow-hidden cursor-pointer group"
      onClick={() => navigate(`/product/${product.id}`)}
      style={{ animationDelay: `${index * 80}ms` }}
    >
      {/* Image */}
      <div className="relative aspect-[4/3] bg-muted overflow-hidden">
        {!imgError ? (
          <img
            src={product.imageUrl}
            alt={product.name}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
            onError={() => setImgError(true)}
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-primary/10 to-secondary/10">
            <span className="text-4xl font-bold text-primary/30">{product.brand[0]}</span>
          </div>
        )}

        {/* Overlay badges */}
        <div className="absolute top-3 left-3 flex flex-col gap-1.5">
          {matchScore && (
            <span className={cn("flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold text-white shadow-sm", matchColor)}>
              <TrendingUp className="w-3 h-3" />
              {matchScore}% Match
            </span>
          )}
          {product.madeInIndia && (
            <span className="flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-white/90 text-emerald-700 shadow-sm backdrop-blur-sm">
              🇮🇳 Made in India
            </span>
          )}
        </div>

        {/* Wishlist */}
        <button
          onClick={handleWishlist}
          className={cn(
            "absolute top-3 right-3 w-8 h-8 rounded-full flex items-center justify-center transition-all shadow-sm",
            wishlisted ? "bg-red-500 text-white" : "bg-white/90 text-muted-foreground hover:text-red-500 backdrop-blur-sm"
          )}
        >
          <Heart className={cn("w-4 h-4", wishlisted && "fill-current")} />
        </button>
      </div>

      {/* Content */}
      <div className="p-4">
        {/* Brand + category */}
        <div className="flex items-center justify-between mb-1">
          <span className="text-xs font-semibold text-primary uppercase tracking-wide">{product.brand}</span>
          <span className="text-xs text-muted-foreground bg-muted px-2 py-0.5 rounded-full">{product.category}</span>
        </div>

        {/* Name */}
        <h3 className="font-semibold text-foreground text-sm leading-snug mb-2 line-clamp-2 group-hover:text-primary transition-colors">
          {product.name}
        </h3>

        {/* Rating */}
        <div className="flex items-center gap-1.5 mb-3">
          <div className="flex items-center gap-0.5">
            {[...Array(5)].map((_, i) => (
              <Star
                key={i}
                className={cn("w-3 h-3", i < Math.floor(product.rating) ? "fill-amber-400 text-amber-400" : "text-muted-foreground/30")}
              />
            ))}
          </div>
          <span className="text-xs font-medium text-foreground">{product.rating}</span>
          <span className="text-xs text-muted-foreground">({product.reviewCount.toLocaleString("en-IN")})</span>
        </div>

        {/* Badges */}
        {product.badges.length > 0 && (
          <div className="flex flex-wrap gap-1 mb-3">
            {product.badges.slice(0, 2).map((badge) => (
              <span
                key={badge}
                className={cn("px-2 py-0.5 rounded-md text-xs font-medium border", BADGE_STYLES[badge] || "bg-muted text-muted-foreground border-border")}
              >
                {badge}
              </span>
            ))}
          </div>
        )}

        {/* Review summary */}
        <p className="text-xs text-muted-foreground line-clamp-2 mb-3 italic">
          "{product.reviewSummary}"
        </p>

        {/* Why this match */}
        {matchReason && (
          <div className="bg-primary/5 border border-primary/20 rounded-lg p-2.5 mb-3">
            <p className="text-xs text-foreground font-medium mb-0.5">Why this match?</p>
            <p className="text-xs text-muted-foreground line-clamp-2">{matchReason}</p>
          </div>
        )}

        {/* Price + CTA */}
        <div className="flex items-center justify-between mt-auto pt-2 border-t border-border/50">
          <div>
            <span className="text-lg font-bold text-foreground">{formatPrice(product.price)}</span>
            {product.originalPrice && (
              <span className="text-xs text-muted-foreground line-through ml-1.5">{formatPrice(product.originalPrice)}</span>
            )}
            {priceSavings && priceSavings > 0 && (
              <div className="text-xs text-emerald-600 font-medium">Save {formatPrice(priceSavings)}</div>
            )}
          </div>
          <a
            href={product.productUrl}
            target="_blank"
            rel="noopener noreferrer"
            onClick={(e) => e.stopPropagation()}
            className="flex items-center gap-1 px-3 py-1.5 bg-primary text-primary-foreground text-xs font-semibold rounded-lg hover:opacity-90 transition-opacity"
          >
            View <ExternalLink className="w-3 h-3" />
          </a>
        </div>
      </div>
    </div>
  );
}
