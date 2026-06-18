import { Router, type IRouter } from "express";
import { db } from "../lib/db";

const router: IRouter = Router();

router.get("/products", (req, res) => {
  const { category, brand, minPrice, maxPrice, minRating, q, limit = "50", offset = "0" } = req.query as Record<string, string>;
  const lim = Math.min(parseInt(limit, 10) || 50, 200);
  const off = parseInt(offset, 10) || 0;

  let filtered = db.getAllProducts();

  if (category) {
    filtered = filtered.filter((p) => p.category.toLowerCase() === category.toLowerCase());
  }
  if (brand) {
    filtered = filtered.filter((p) => p.brand.toLowerCase().includes(brand.toLowerCase()));
  }
  if (minPrice) {
    filtered = filtered.filter((p) => p.price >= parseFloat(minPrice));
  }
  if (maxPrice) {
    filtered = filtered.filter((p) => p.price <= parseFloat(maxPrice));
  }
  if (minRating) {
    filtered = filtered.filter((p) => p.rating >= parseFloat(minRating));
  }
  if (q) {
    const lower = q.toLowerCase();
    filtered = filtered.filter(
      (p) =>
        p.name.toLowerCase().includes(lower) ||
        p.brand.toLowerCase().includes(lower) ||
        p.category.toLowerCase().includes(lower) ||
        p.tags.some((t) => t.toLowerCase().includes(lower)) ||
        p.description.toLowerCase().includes(lower)
    );
  }

  const total = filtered.length;
  const products = filtered.slice(off, off + lim);

  res.json({ products, total, offset: off, limit: lim });
});

router.get("/products/:id", (req, res) => {
  const product = db.getProductById(req.params.id);
  if (!product) {
    res.status(404).json({ error: "Product not found" });
    return;
  }
  res.json(product);
});

export default router;
