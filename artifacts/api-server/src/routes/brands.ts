import { Router, type IRouter } from "express";
import { db } from "../lib/db";

const router: IRouter = Router();

function slugify(s: string): string {
  return s.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "");
}

router.get("/brands", (_req, res) => {
  const products = db.getAllProducts();
  const brandMap = new Map<string, { categories: Set<string>; urls: Set<string>; count: number }>();

  for (const p of products) {
    if (!brandMap.has(p.brand)) {
      brandMap.set(p.brand, { categories: new Set(), urls: new Set(), count: 0 });
    }
    const entry = brandMap.get(p.brand)!;
    entry.categories.add(p.category);
    entry.urls.add(p.brandUrl);
    entry.count += 1;
  }

  const brands = [...brandMap.entries()]
    .sort((a, b) => b[1].count - a[1].count)
    .map(([name, data]) => ({
      name,
      slug: slugify(name),
      description: `Premium Indian brand offering ${[...data.categories].slice(0, 2).join(" & ")}.`,
      logoUrl: "",
      websiteUrl: [...data.urls][0] || "",
      categories: [...data.categories],
      founded: "2015",
      featured: data.count > 20,
    }));

  res.json(brands);
});

export default router;
