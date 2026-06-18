import { useLocation } from "wouter";
import { Sparkles, Github, Heart } from "lucide-react";

const CATEGORIES = ["Apparel", "Footwear", "Electronics", "Audio", "Watches", "Skincare", "Bags", "Jewelry", "Kitchen", "Fitness", "Perfumes", "Eyewear"];
const BRANDS = ["Minimalist", "boAt", "Mokobara", "Snitch", "Titan", "GIVA", "Neeman's", "Lenskart", "Wakefit", "Wonderchef"];

export default function Footer() {
  const [, navigate] = useLocation();

  return (
    <footer className="border-t border-border bg-card mt-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Lotus divider */}
        <div className="lotus-divider mb-10" />

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-10">
          {/* Brand */}
          <div className="lg:col-span-1">
            <button onClick={() => navigate("/")} className="flex items-center gap-2 mb-3">
              <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
                <Sparkles className="w-4 h-4 text-white" />
              </div>
              <span className="text-lg font-bold">
                <span className="text-primary">Desi</span>
                <span className="text-foreground">Finds</span>
              </span>
            </button>
            <p className="text-sm text-muted-foreground leading-relaxed mb-4">
              Discover premium Indian alternatives to global brands. Find Better. Find Indian.
            </p>
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <span>Made with</span>
              <Heart className="w-3 h-3 fill-red-500 text-red-500" />
              <span>in India</span>
            </div>
          </div>

          {/* Mission */}
          <div>
            <h4 className="font-semibold text-foreground text-sm mb-4">About DesiFinds</h4>
            <div className="space-y-2">
              {["Our Mission", "How It Works", "AI Matching", "Privacy Policy", "Contact Us"].map((item) => (
                <div key={item} className="text-sm text-muted-foreground hover:text-foreground cursor-pointer transition-colors">{item}</div>
              ))}
            </div>
          </div>

          {/* Categories */}
          <div>
            <h4 className="font-semibold text-foreground text-sm mb-4">Categories</h4>
            <div className="grid grid-cols-2 gap-y-2">
              {CATEGORIES.slice(0, 8).map((cat) => (
                <button
                  key={cat}
                  onClick={() => navigate(`/explore?category=${cat}`)}
                  className="text-sm text-muted-foreground hover:text-foreground transition-colors text-left"
                >
                  {cat}
                </button>
              ))}
            </div>
          </div>

          {/* Indian Brands */}
          <div>
            <h4 className="font-semibold text-foreground text-sm mb-4">Featured Indian Brands</h4>
            <div className="space-y-2">
              {BRANDS.map((brand) => (
                <button
                  key={brand}
                  onClick={() => navigate(`/explore?brand=${brand}`)}
                  className="block text-sm text-muted-foreground hover:text-foreground transition-colors"
                >
                  {brand}
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="lotus-divider mb-6" />

        <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-xs text-muted-foreground">
            © 2025 DesiFinds. All rights reserved. Celebrating India's finest brands.
          </p>
          <div className="flex items-center gap-4">
            <a
              href="https://github.com"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground transition-colors"
            >
              <Github className="w-4 h-4" />
              <span>GitHub</span>
            </a>
            <span className="flex items-center gap-1.5 text-xs text-muted-foreground">
              🇮🇳 Proud to be Indian
            </span>
          </div>
        </div>
      </div>
    </footer>
  );
}
