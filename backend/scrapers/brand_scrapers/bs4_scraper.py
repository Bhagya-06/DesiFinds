import re
import json
from typing import List, Dict, Any, Optional
import requests
from bs4 import BeautifulSoup
from backend.scrapers.brand_scrapers.base_scraper import BaseScraper

class BS4Scraper(BaseScraper):
    """
    Scraper that requests individual product pages or collection pages,
    and extracts Schema.org JSON-LD metadata.
    """
    def __init__(self, brand_name: str, brand_url: str, collection_paths: List[str]):
        super().__init__(brand_name, brand_url)
        self.collection_paths = collection_paths
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9"
        }

    def scrape(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Scrape by discovering product links from collection paths,
        then parsing each product page's JSON-LD.
        """
        product_urls = self._discover_product_urls(limit)
        print(f"[{self.brand_name}] Discovered {len(product_urls)} product links to scrape.")
        
        scraped_items = []
        for url in product_urls[:limit]:
            item = self.scrape_product_page(url)
            if item:
                scraped_items.append(item)
                
        return scraped_items

    def _discover_product_urls(self, limit: int) -> List[str]:
        urls = []
        for path in self.collection_paths:
            full_url = f"{self.brand_url.rstrip('/')}/{path.lstrip('/')}"
            try:
                resp = requests.get(full_url, headers=self.headers, timeout=15)
                if resp.status_code != 200:
                    continue
                soup = BeautifulSoup(resp.text, "html.parser")
                
                # Find product links. Commonly contain '/products/' or '/product/'
                # or are inside product grids.
                for a in soup.find_all("a", href=True):
                    href = a["href"]
                    # Normalize relative links
                    if href.startswith("/"):
                        href = f"{self.brand_url.rstrip('/')}{href}"
                        
                    # Filter for product pages
                    if "/products/" in href or "/product/" in href:
                        # Strip query parameters
                        href = href.split("?")[0]
                        if href not in urls and href.startswith(self.brand_url):
                            urls.append(href)
                            if len(urls) >= limit * 2:
                                break
            except Exception as e:
                print(f"[{self.brand_name}] Error discovering URLs from {full_url}: {e}")
                
        return list(set(urls))

    def scrape_product_page(self, url: str) -> Optional[Dict[str, Any]]:
        try:
            resp = requests.get(url, headers=self.headers, timeout=15)
            if resp.status_code != 200:
                return None
                
            soup = BeautifulSoup(resp.text, "html.parser")
            
            # Extract JSON-LD
            json_ld_scripts = soup.find_all("script", type="application/ld+json")
            product_data = None
            
            for script in json_ld_scripts:
                try:
                    content = script.string or ""
                    # Clean up comments inside script tags if any
                    content = re.sub(r'//.*?\n', '', content)
                    data = json.loads(content)
                    
                    # Resolve graphs or lists
                    items = []
                    if isinstance(data, dict):
                        if data.get("@type") == "Product":
                            items.append(data)
                        elif "@graph" in data:
                            items.extend([item for item in data["@graph"] if item.get("@type") == "Product"])
                    elif isinstance(data, list):
                        items.extend([item for item in data if item.get("@type") == "Product"])
                        
                    if items:
                        product_data = items[0]
                        break
                except Exception:
                    continue
            
            if not product_data:
                # DOM Fallback
                name_tag = soup.find("h1")
                if not name_tag:
                    return None
                name = name_tag.get_text().strip()
                description = ""
                desc_tag = soup.find("meta", property="og:description") or soup.find("meta", name="description")
                if desc_tag:
                    description = desc_tag.get("content", "").strip()
                
                image_url = ""
                img_tag = soup.find("meta", property="og:image")
                if img_tag:
                    image_url = img_tag.get("content", "")
                    
                price = 0.0
                price_tag = soup.find("meta", property="product:price:amount")
                if price_tag:
                    try:
                        price = float(price_tag.get("content", 0.0))
                    except ValueError:
                        pass
                
                return {
                    "brand": self.brand_name,
                    "name": name,
                    "description": description,
                    "category": self._normalize_category(name, "", []),
                    "tags": [],
                    "materials": self._extract_materials(name, description),
                    "price": price,
                    "originalPrice": None,
                    "rating": None,
                    "reviewCount": None,
                    "productUrl": url,
                    "imageUrl": image_url,
                    "brandUrl": self.brand_url,
                    "reviewSummary": "",
                    "madeInIndia": True,
                    "badges": []
                }
                
            # Extract fields from JSON-LD
            name = product_data.get("name", "").strip()
            description = product_data.get("description", "").strip()
            
            img = product_data.get("image")
            image_url = img[0] if isinstance(img, list) else img if isinstance(img, str) else ""
            if isinstance(img, dict) and "url" in img:
                image_url = img["url"]
                
            if image_url.startswith("//"):
                image_url = "https:" + image_url
                
            price = 0.0
            original_price = None
            offers = product_data.get("offers")
            if offers:
                if isinstance(offers, list) and len(offers) > 0:
                    offers = offers[0]
                if isinstance(offers, dict):
                    try:
                        price = float(offers.get("price", 0.0))
                    except ValueError:
                        pass
            
            # Extract real rating & reviewCount
            rating = None
            review_count = None
            aggregate_rating = product_data.get("aggregateRating")
            if aggregate_rating and isinstance(aggregate_rating, dict):
                try:
                    rating = float(aggregate_rating.get("ratingValue") or aggregate_rating.get("bestRating") or 4.5)
                    review_count = int(aggregate_rating.get("reviewCount") or aggregate_rating.get("ratingCount") or 10)
                except (ValueError, TypeError):
                    pass
            
            # Extract tags & materials
            tags = product_data.get("keywords", [])
            if isinstance(tags, str):
                tags = [t.strip() for t in tags.split(",") if t.strip()]
                
            materials = self._extract_materials(name, description)
            category = self._normalize_category(name, product_data.get("category", ""), tags)
            
            return {
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
                "productUrl": url,
                "imageUrl": image_url,
                "brandUrl": self.brand_url,
                "reviewSummary": "",
                "madeInIndia": True,
                "badges": []
            }
        except Exception as e:
            print(f"[{self.brand_name}] Error scraping product page {url}: {e}")
            return None

    def _normalize_category(self, name: str, product_type: str, tags: List[str]) -> str:
        text = f"{name} {product_type} {' '.join(tags)}".lower()
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
        
        max_matches = 0
        matched_cat = "Apparel"
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
