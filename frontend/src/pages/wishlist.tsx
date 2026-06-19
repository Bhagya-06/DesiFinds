import { useState, useEffect } from "react";
import { useLocation } from "wouter";
import { motion } from "framer-motion";
import { Heart, Search, Lock, User } from "lucide-react";
import { useListProducts } from "@workspace/api-client-react";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import ProductCard from "@/components/ProductCard";
import { useAuth } from "@/context/AuthContext";
import { getWishlist } from "@/lib/utils";
import ProductSkeleton from "@/components/ProductCard"; // we can write a simple skeleton loader locally

export default function WishlistPage() {
  const [, navigate] = useLocation();
  const { currentUser, setAuthModalOpen } = useAuth();
  const [wishlistIds, setWishlistIds] = useState<string[]>([]);
  
  // Reload wishlist IDs whenever user session or local storage changes
  const reloadWishlist = () => {
    setWishlistIds(getWishlist(currentUser?.username));
  };

  useEffect(() => {
    reloadWishlist();
  }, [currentUser]);

  // Listen for storage events (e.g. if tabs modify it or a card adds/removes an item)
  useEffect(() => {
    window.addEventListener("storage", reloadWishlist);
    return () => window.removeEventListener("storage", reloadWishlist);
  }, [currentUser]);

  // Fetch products (limit=3500 is extremely fast since the backend caches them in memory)
  const { data, isLoading } = useListProducts(
    { limit: 3500 },
    { query: { enabled: !!currentUser } as any }
  );

  const wishlistProducts = data?.products.filter((p) => wishlistIds.includes(p.id)) || [];

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Navbar />

      <main className="flex-grow max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {!currentUser ? (
          /* Guest State */
          <div className="flex flex-col items-center justify-center py-20 text-center">
            <div className="w-16 h-16 rounded-2xl bg-primary/10 border border-primary/20 flex items-center justify-center mb-6">
              <Lock className="w-8 h-8 text-primary" />
            </div>
            <h1 className="text-2xl font-bold text-foreground mb-2">Member Wishlist</h1>
            <p className="text-muted-foreground text-sm max-w-md mb-8">
              Sign in to save and organize your premium Indian product alternatives.
            </p>
            <button
              onClick={() => setAuthModalOpen(true)}
              className="flex items-center gap-2 px-6 py-3 bg-primary text-primary-foreground font-semibold rounded-xl hover:opacity-90 transition-opacity shadow-md shadow-primary/15 text-sm"
            >
              <User className="w-4 h-4" />
              Sign In to View
            </button>
          </div>
        ) : (
          /* Logged In State */
          <>
            {/* Header */}
            <div className="mb-8">
              <h1 className="text-2xl font-bold text-foreground mb-1 flex items-center gap-2">
                <Heart className="w-6 h-6 text-red-500 fill-current animate-pulse" />
                My Wishlist
              </h1>
              <p className="text-muted-foreground text-sm">
                Saved Indian alternatives for {currentUser.username} ({wishlistProducts.length} items)
              </p>
            </div>

            {isLoading ? (
              /* Loading Skeletons */
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                {[...Array(4)].map((_, i) => (
                  <div key={i} className="bg-card border border-border rounded-2xl overflow-hidden animate-pulse h-[360px]" />
                ))}
              </div>
            ) : wishlistProducts.length > 0 ? (
              /* Product list */
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                {wishlistProducts.map((product, i) => (
                  <motion.div
                    key={product.id}
                    initial={{ opacity: 0, y: 15 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.05 }}
                  >
                    {/* We re-render the card, and handle wishlist action */}
                    <ProductCard product={product} index={i} />
                  </motion.div>
                ))}
              </div>
            ) : (
              /* Empty state */
              <div className="text-center py-20 bg-muted/20 border border-dashed border-border rounded-3xl">
                <div className="w-16 h-16 rounded-full bg-muted flex items-center justify-center mx-auto mb-4">
                  <Heart className="w-8 h-8 text-muted-foreground" />
                </div>
                <h3 className="font-semibold text-foreground mb-2">Your wishlist is empty</h3>
                <p className="text-sm text-muted-foreground mb-6">
                  Discover high-quality local alternatives and save them here.
                </p>
                <button
                  onClick={() => navigate("/explore")}
                  className="px-5 py-2.5 bg-primary text-primary-foreground font-semibold rounded-xl text-xs hover:opacity-95 transition-opacity"
                >
                  Explore Indian Products
                </button>
              </div>
            )}
          </>
        )}
      </main>

      <Footer />
    </div>
  );
}
