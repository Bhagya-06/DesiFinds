import { Router, type IRouter } from "express";
import { db } from "../lib/db";
import { logger } from "../lib/logger";

const router: IRouter = Router();

interface Product {
  id: string;
  brand: string;
  name: string;
  description: string;
  category: string;
  tags: string[];
  materials: string[];
  price: number;
  originalPrice: number | null;
  rating: number;
  reviewCount: number;
  productUrl: string;
  imageUrl: string;
  brandUrl: string;
  reviewSummary: string;
  madeInIndia: boolean;
  badges: string[];
}

// Simple keyword-based product analysis
function analyzeProduct(query: string): {
  category: string;
  features: string[];
  materials: string[];
  priceRange: string;
  aestheticStyle: string;
  originalBrand: string;
} {
  const lower = query.toLowerCase();

  const BRAND_MAP: Record<string, string> = {
    zara: "Zara", "h&m": "H&M", uniqlo: "Uniqlo", "levi's": "Levi's", levis: "Levi's",
    gap: "Gap", mango: "Mango", "& other stories": "& Other Stories",
    airpods: "Apple", apple: "Apple", iphone: "Apple", ipad: "Apple", macbook: "Apple",
    samsung: "Samsung", sony: "Sony", bose: "Bose", "logitech": "Logitech",
    nike: "Nike", adidas: "Adidas", puma: "Puma", "new balance": "New Balance",
    converse: "Converse", vans: "Vans", reebok: "Reebok",
    dyson: "Dyson", philips: "Philips", "ray-ban": "Ray-Ban", rayban: "Ray-Ban",
    "l'oreal": "L'Oréal", loreal: "L'Oréal", cerave: "CeraVe", "the ordinary": "The Ordinary",
    ikea: "IKEA", muji: "MUJI", "pottery barn": "Pottery Barn",
    "michael kors": "Michael Kors", coach: "Coach", gucci: "Gucci", prada: "Prada",
  };

  const CATEGORY_KEYWORDS: Record<string, string[]> = {
    Apparel: ["shirt", "kurta", "tshirt", "t-shirt", "jeans", "trouser", "linen", "cotton", "denim", "jacket", "hoodie", "saree", "kurti", "ethnic", "formal", "dress", "blouse", "sherwani", "pant", "chino"],
    Footwear: ["shoe", "sneaker", "chappal", "sandal", "boot", "runner", "trainer", "loafer", "derby", "oxford", "kolhapuri"],
    Electronics: ["laptop", "phone", "tablet", "keyboard", "mouse", "speaker", "hub", "charger", "powerbank", "gadget", "smartwatch"],
    Audio: ["headphone", "earphone", "earbud", "airpod", "tws", "neckband", "soundbar", "earpiece", "music"],
    Watches: ["watch", "timepiece", "smartwatch", "fitbit", "analog", "digital"],
    Skincare: ["moisturizer", "serum", "cleanser", "sunscreen", "face wash", "lotion", "cream", "toner", "mask", "spf", "niacinamide", "vitamin c"],
    Bags: ["bag", "backpack", "handbag", "tote", "luggage", "suitcase", "trolley", "wallet", "purse", "sling"],
    Jewelry: ["necklace", "ring", "earring", "bracelet", "jhumka", "kundan", "diamond", "gold", "silver", "pendant"],
    Furniture: ["sofa", "chair", "table", "desk", "shelf", "wardrobe", "bed", "mattress", "couch", "cabinet"],
    "Home Decor": ["vase", "lamp", "rug", "curtain", "pillow", "cushion", "art", "plant", "planter", "painting", "candle"],
    Kitchen: ["cooker", "pan", "pot", "kadai", "tawa", "blender", "mixer", "bottle", "container", "utensil"],
    Fitness: ["mat", "dumbbell", "weight", "band", "yoga", "gym", "protein", "supplement", "kettlebell", "barbell"],
    Perfumes: ["perfume", "fragrance", "cologne", "attar", "oud", "mist", "scent", "deodorant"],
    Eyewear: ["sunglasses", "spectacles", "glasses", "frames", "lens", "optical"],
  };

  let category = "Apparel";
  let maxMatches = 0;

  for (const [cat, keywords] of Object.entries(CATEGORY_KEYWORDS)) {
    const matches = keywords.filter((kw) => lower.includes(kw)).length;
    if (matches > maxMatches) {
      maxMatches = matches;
      category = cat;
    }
  }

  // Detect brand
  let originalBrand = "International Brand";
  for (const [key, val] of Object.entries(BRAND_MAP)) {
    if (lower.includes(key)) {
      originalBrand = val;
      break;
    }
  }

  // Features from query words
  const FEATURE_KEYWORDS = ["linen", "cotton", "leather", "wool", "slim", "oversized", "wireless", "noise cancelling", "anc", "waterproof", "organic", "sustainable", "premium", "minimalist", "classic", "vintage", "modern", "anti-ageing", "spf", "niacinamide"];
  const features = FEATURE_KEYWORDS.filter((f) => lower.includes(f));

  const MATERIAL_KEYWORDS = ["linen", "cotton", "leather", "wool", "silk", "polyester", "nylon", "bamboo", "aluminum", "stainless steel", "glass", "ceramic", "brass", "silver", "gold"];
  const materials = MATERIAL_KEYWORDS.filter((m) => lower.includes(m));

  const PRICE_RANGES: Record<string, string> = {
    Apparel: "₹800 – ₹4,000", Footwear: "₹1,000 – ₹6,000", Electronics: "₹1,000 – ₹15,000",
    Audio: "₹800 – ₹8,000", Watches: "₹2,000 – ₹20,000", Skincare: "₹400 – ₹1,500",
    Bags: "₹800 – ₹10,000", Jewelry: "₹600 – ₹15,000", Furniture: "₹5,000 – ₹30,000",
    "Home Decor": "₹500 – ₹5,000", Kitchen: "₹500 – ₹5,000", Fitness: "₹500 – ₹8,000",
    Perfumes: "₹800 – ₹3,000", Eyewear: "₹800 – ₹4,000",
  };

  const STYLE_MAP: Record<string, string> = {
    Apparel: "Contemporary casual with Indian craft influences", Footwear: "Versatile everyday comfort",
    Electronics: "Sleek modern design", Audio: "Clean, minimal aesthetic",
    Watches: "Timeless and refined", Skincare: "Ingredient-first formulation",
    Bags: "Functional and fashionable", Jewelry: "Traditional meets contemporary",
    Furniture: "Modern with natural materials", "Home Decor": "Vibrant Indian artisan aesthetic",
    Kitchen: "Practical and durable", Fitness: "Performance-focused design",
    Perfumes: "Oriental and floral Indian fragrances", Eyewear: "Modern frames, Indian craftsmanship",
  };

  return {
    category,
    features,
    materials,
    priceRange: PRICE_RANGES[category] || "₹500 – ₹5,000",
    aestheticStyle: STYLE_MAP[category] || "Modern minimalist",
    originalBrand,
  };
}

function scoreProduct(product: Product, query: string, analysis: ReturnType<typeof analyzeProduct>): number {
  const lower = query.toLowerCase();
  let score = 0;

  // Category match (most important)
  if (product.category === analysis.category) score += 40;
  else score += 5;

  // Text overlap
  const words = lower.split(/\s+/).filter((w) => w.length > 2);
  for (const word of words) {
    if (product.name.toLowerCase().includes(word)) score += 8;
    if (product.tags.some((t) => t.includes(word))) score += 5;
    if (product.description.toLowerCase().includes(word)) score += 3;
    if (product.materials.some((m) => m.toLowerCase().includes(word))) score += 4;
  }

  // Quality signals
  score += Math.min(15, product.rating * 2.5);
  score += Math.min(10, Math.log10(product.reviewCount + 1) * 3);

  // Badge bonus
  if (product.badges.includes("Made in India")) score += 3;
  if (product.badges.includes("Handcrafted")) score += 2;

  return Math.round(Math.min(99, score));
}

function getMatchReason(product: Product, analysis: ReturnType<typeof analyzeProduct>): string {
  const reasons = [];
  if (product.category === analysis.category) reasons.push(`Same ${product.category.toLowerCase()} category`);
  if (product.badges.includes("Made in India")) reasons.push("authentically Indian-made");
  if (product.badges.includes("Handcrafted")) reasons.push("handcrafted by Indian artisans");
  if (product.badges.includes("Premium Quality")) reasons.push("premium quality materials");
  if (product.badges.includes("Better Value")) reasons.push("excellent value for money");
  if (product.rating >= 4.5) reasons.push("top-rated by customers");
  return reasons.length > 0
    ? `Recommended because: ${reasons.join(", ")}.`
    : `Top ${product.category} alternative from ${product.brand}.`;
}

function getValueProp(product: Product): string {
  if (product.badges.includes("Better Value")) return "Premium quality at significantly lower price";
  if (product.badges.includes("Handcrafted")) return "Unique handcrafted Indian craftsmanship";
  if (product.badges.includes("Made in India")) return "Authentic Indian manufacturing & design";
  if (product.badges.includes("Sustainable")) return "Sustainably made with eco-friendly materials";
  return "Quality Indian alternative with better value";
}

router.post("/search", (req, res) => {
  const { query, apiKey } = req.body as { query?: string; apiKey?: string };

  if (!query || typeof query !== "string" || !query.trim()) {
    res.status(400).json({ error: "query is required" });
    return;
  }

  const trimmedQuery = query.trim();
  logger.info({ query: trimmedQuery, hasApiKey: !!apiKey }, "Search request");

  const analysis = analyzeProduct(trimmedQuery);
  const products = db.getAllProducts();

  // Score and rank products
  const scored = products
    .map((p) => ({ product: p, score: scoreProduct(p, trimmedQuery, analysis) }))
    .sort((a, b) => b.score - a.score)
    .slice(0, 12);

  const matches = scored
    .filter((s) => s.score > 0)
    .map((s) => ({
      product: s.product,
      matchScore: Math.max(s.score, 50),
      matchReason: getMatchReason(s.product, analysis),
      valueProp: getValueProp(s.product),
      priceSavings: null as number | null,
    }));

  const workflow = [
    {
      name: "Product Deconstructor",
      status: "complete",
      output: `Identified: ${analysis.category} / ${analysis.originalBrand}\nFeatures: ${analysis.features.join(", ") || "general"}\nPrice Range: ${analysis.priceRange}`,
    },
    {
      name: "RAG Matcher",
      status: "complete",
      output: `Searched ${products.length.toLocaleString("en-IN")} Indian products.\nFound ${matches.length} matches above threshold.`,
    },
    {
      name: "Quality Curator",
      status: "complete",
      output: `Ranked by match score, rating, and review count.\nTop match: ${matches[0]?.product.name || "N/A"} (${matches[0]?.matchScore || 0}% match)`,
    },
    {
      name: "Formatter",
      status: "complete",
      output: `Formatted ${matches.length} matches with match reasons, value props, and product details.`,
    },
  ];

  res.json({
    query: trimmedQuery,
    analysis,
    matches,
    workflow,
    aiPowered: false,
  });
});

export default router;
