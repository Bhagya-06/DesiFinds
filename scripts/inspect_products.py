import json
import collections

with open("data/products.json", "r", encoding="utf-8") as f:
    products = json.load(f)

print(f"Total products: {len(products)}")

# Count by brand
brand_counts = collections.Counter(p["brand"] for p in products)
print("\nProduct count by brand:")
for brand, count in brand_counts.most_common(20):
    print(f"  {brand}: {count}")

# Check URL types/status for some samples
print("\nSamples of product urls/image urls by source:")
sources = {}
for p in products:
    brand = p["brand"]
    if brand not in sources:
        sources[brand] = p

for brand, p in list(sources.items())[:10]:
    print(f"\nBrand: {brand}")
    print(f"  Name: {p['name']}")
    print(f"  Product URL: {p['productUrl']}")
    print(f"  Image URL: {p['imageUrl']}")
