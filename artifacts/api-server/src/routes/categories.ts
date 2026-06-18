import { Router, type IRouter } from "express";
import { db } from "../lib/db";

const router: IRouter = Router();

const CATEGORY_ICONS: Record<string, string> = {
  Apparel: "👔",
  Footwear: "👟",
  Electronics: "💻",
  Audio: "🎧",
  Watches: "⌚",
  Skincare: "✨",
  Bags: "👜",
  Jewelry: "💍",
  Furniture: "🛋️",
  "Home Decor": "🏮",
  Kitchen: "🍳",
  Fitness: "🏋️",
  Perfumes: "🌸",
  Eyewear: "👓",
};

router.get("/categories", (_req, res) => {
  const products = db.getAllProducts();
  const counts = new Map<string, number>();

  for (const p of products) {
    counts.set(p.category, (counts.get(p.category) || 0) + 1);
  }

  const categories = [...counts.entries()]
    .map(([name, count]) => ({
      name,
      count,
      icon: CATEGORY_ICONS[name] || "🛍️",
    }))
    .sort((a, b) => b.count - a.count);

  res.json(categories);
});

export default router;
