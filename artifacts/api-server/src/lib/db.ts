import { readFileSync } from "fs";
import { join, dirname } from "path";
import { fileURLToPath } from "url";

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

let _products: Product[] | null = null;

function loadProducts(): Product[] {
  if (_products) return _products;

  // Walk up to find workspace root
  const dir = dirname(fileURLToPath(import.meta.url));
  const candidates = [
    join(dir, "../../../../data/products.json"),
    join(dir, "../../../data/products.json"),
    join(dir, "../../data/products.json"),
    join(process.cwd(), "data/products.json"),
  ];

  for (const candidate of candidates) {
    try {
      const raw = readFileSync(candidate, "utf-8");
      _products = JSON.parse(raw) as Product[];
      return _products;
    } catch {
      // try next
    }
  }

  // Fallback empty
  _products = [];
  return _products;
}

const productIndex = new Map<string, Product>();

export const db = {
  getAllProducts(): Product[] {
    const products = loadProducts();
    return products;
  },

  getProductById(id: string): Product | undefined {
    const products = loadProducts();
    if (productIndex.size === 0) {
      for (const p of products) {
        productIndex.set(p.id, p);
      }
    }
    return productIndex.get(id);
  },
};
