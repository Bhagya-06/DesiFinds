import { Router, type IRouter } from "express";
import { db } from "../lib/db";

const router: IRouter = Router();

const POPULAR_SEARCHES = [
  "Zara Linen Shirt",
  "AirPods Pro",
  "Nike Running Shoes",
  "CeraVe Moisturizer",
  "Logitech MX Master",
  "Dyson Air Purifier",
  "Ray-Ban Sunglasses",
  "IKEA Sofa",
  "Apple Watch",
  "Levi's 501 Jeans",
];

router.get("/trending", (_req, res) => {
  const products = db.getAllProducts();

  const topProducts = [...products]
    .sort((a, b) => b.rating * Math.log(b.reviewCount + 1) - a.rating * Math.log(a.reviewCount + 1))
    .slice(0, 12);

  const newArrivals = products
    .filter((p) => p.id.startsWith("px"))
    .slice(0, 8);

  res.json({
    popularSearches: POPULAR_SEARCHES,
    topProducts,
    newArrivals,
  });
});

export default router;
