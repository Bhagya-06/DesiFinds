import re
from typing import List, Dict, Any, Optional
import requests
from bs4 import BeautifulSoup
from backend.scrapers.brand_scrapers.base_scraper import BaseScraper

class ShopifyScraper(BaseScraper):
    """
    Generic scraper for Shopify-powered stores that reads the public /products.json catalog.
    """
    def __init__(self, brand_name: str, brand_url: str, category_mapping: Optional[Dict[str, str]] = None):
        super().__init__(brand_name, brand_url)
        self.category_mapping = category_mapping or {}

    def scrape(self, limit: int = 100) -> List[Dict[str, Any]]:
        products_url = f"{self.brand_url.rstrip('/')}/products.json?limit={limit}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        try:
            resp = requests.get(products_url, headers=headers, timeout=15)
            if resp.status_code != 200:
                print(f"[{self.brand_name}] Failed to fetch products.json, status: {resp.status_code}")
                return []
                
            data = resp.json()
            raw_products = data.get("products", [])
            
            scraped_items = []
            for rp in raw_products:
                name = rp.get("title", "").strip()
                handle = rp.get("handle", "")
                product_url = f"{self.brand_url.rstrip('/')}/products/{handle}"
                
                # Strip HTML tags from description
                body_html = rp.get("body_html", "")
                description = ""
                if body_html:
                    soup_desc = BeautifulSoup(body_html, "html.parser")
                    description = soup_desc.get_text(separator=" ").strip()
                    # Collapse multiple spaces
                    description = re.sub(r"\s+", " ", description)
                
                # Images
                images = rp.get("images", [])
                image_url = images[0].get("src", "") if images else ""
                
                # Variants (Price)
                variants = rp.get("variants", [])
                price = 0.0
                original_price = None
                
                if variants:
                    # Use the first variant as the main pricing info
                    v = variants[0]
                    try:
                        price = float(v.get("price", 0.0))
                    except ValueError:
                        price = 0.0
                        
                    compare_at = v.get("compare_at_price")
                    if compare_at:
                        try:
                            original_price = float(compare_at)
                            # Handle cases where compare_at is equal to or less than price
                            if original_price <= price:
                                original_price = None
                        except ValueError:
                            original_price = None
                
                tags = rp.get("tags", [])
                if isinstance(tags, str):
                    tags = [t.strip() for t in tags.split(",") if t.strip()]
                
                # Category normalization
                raw_type = rp.get("product_type", "")
                category = self._normalize_category(name, raw_type, tags)
                
                # Extract materials from text description
                materials = self._extract_materials(name, description)
                
                # Ratings and reviews (initially None, to be populated from product page JSON-LD/meta or Amazon/external later if possible)
                rating = None
                review_count = None
                
                scraped_items.append({
                    "brand": self.brand_name,
                    "name": name,
                    "description": description,
                    "category": category,
                    "tags": tags,
                    "materials": materials,
                    "price": price,
                    "originalPrice": original_price,
                    "rating": rating,
                    "reviewCount": review_count,
                    "productUrl": product_url,
                    "imageUrl": image_url,
                    "brandUrl": self.brand_url,
                    "reviewSummary": "",
                    "madeInIndia": True,
                    "badges": []
                })
                
            return scraped_items
            
        except Exception as e:
            print(f"[{self.brand_name}] Error scraping shopify store: {e}")
            return []

    def _normalize_category(self, name: str, product_type: str, tags: List[str]) -> str:
        text = f"{name} {product_type} {' '.join(tags)}".lower()
        
        # Mapping rules
        category_keywords = {
            "Apparel": ["shirt", "kurta", "tshirt", "jeans", "trousers", "jacket", "coat", "dress", "saree", "clothing", "top", "tee", "pant", "chinos", "short", "sweatshirt"],
            "Footwear": ["shoes", "sneakers", "sandals", "boots", "flats", "chappal", "runners", "slip-ons", "derby", "oxford"],
            "Electronics": ["laptop", "phone", "tablet", "keyboard", "mouse", "charger", "powerbank", "device", "speaker", "projector", "cable"],
            "Audio": ["headphones", "earphones", "earbuds", "speaker", "soundbar", "tws", "neckband", "pods"],
            "Watches": ["watch", "smartwatch", "timepiece", "chronograph"],
            "Skincare": ["moisturizer", "serum", "sunscreen", "cleanser", "lotion", "cream", "facewash", "toner", "face wash"],
            "Bags": ["backpack", "handbag", "tote", "messenger", "duffel", "luggage", "trolley", "briefcase", "sling", "purse"],
            "Jewelry": ["ring", "necklace", "earring", "bracelet", "gold", "silver", "jhumka", "bangle", "pendant"],
            "Furniture": ["sofa", "chair", "table", "bed", "mattress", "desk", "bookshelf", "decor"],
            "Home Decor": ["vase", "rug", "cushion", "pillow", "lamp", "painting", "decor", "curtain", "candle"],
            "Kitchen": ["pan", "pot", "blender", "cooker", "bottle", "kettle", "casserole", "tawa", "cookware", "griddle"],
            "Fitness": ["dumbbell", "mat", "kettlebell", "band", "wheel", "fitness", "workout", "protein"],
            "Perfumes": ["perfume", "fragrance", "scent", "cologne", "attar", "mist", "edp"],
            "Eyewear": ["glasses", "sunglasses", "frames", "spectacles", "lenses"]
        }
        
        # Check custom mapping
        if product_type in self.category_mapping:
            return self.category_mapping[product_type]
            
        # Match by keywords
        max_matches = 0
        matched_cat = "Apparel"  # Default
        for cat, keywords in category_keywords.items():
            matches = sum(1 for kw in keywords if kw in text)
            if matches > max_matches:
                max_matches = matches
                matched_cat = cat
                
        return matched_cat

    def _extract_materials(self, name: str, description: str) -> List[str]:
        materials_keywords = ["linen", "cotton", "polyester", "wool", "silk", "leather", "nylon", "bamboo", "acrylic", "denim", "suede", "mesh", "polycarbonate", "silicone", "brass", "ceramic", "glass", "canvas", "wood", "sheesham", "mango wood"]
        text = f"{name} {description}".lower()
        extracted = []
        for m in materials_keywords:
            if m in text:
                extracted.append(m.capitalize())
        return list(set(extracted))
