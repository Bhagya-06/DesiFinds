import re
import urllib.parse
from typing import Dict, Any, Optional
import requests
from bs4 import BeautifulSoup

def validate_url(url: str) -> bool:
    """
    Check if a URL is well-formed and has a valid HTTP/HTTPS scheme.
    """
    if not url:
        return False
    try:
        parsed = urllib.parse.urlparse(url)
        return bool(parsed.scheme and parsed.netloc and parsed.scheme in ["http", "https"])
    except Exception:
        return False

def validate_image_url(url: str) -> bool:
    """
    Validate that an image URL exists and returns an image content-type.
    """
    if not validate_url(url):
        return False
    try:
        # Send HEAD request first for efficiency
        resp = requests.head(url, timeout=5, headers={"User-Agent": "DesiFindsBot/1.0"})
        if resp.status_code == 200:
            content_type = resp.headers.get("Content-Type", "")
            if "image" in content_type:
                return True
                
        # Fallback to GET in case HEAD is blocked
        resp_get = requests.get(url, stream=True, timeout=5, headers={"User-Agent": "DesiFindsBot/1.0"})
        content_type = resp_get.headers.get("Content-Type", "")
        return bool(resp_get.status_code == 200 and "image" in content_type)
    except Exception:
        return False

def scrape_product_details(url: str) -> Dict[str, Any]:
    """
    Fetch and scrape a product URL to extract name, description, image, price, materials, brand, etc.
    """
    result = {
        "url": url,
        "name": "",
        "brand": "International Brand",
        "description": "",
        "imageUrl": "",
        "price": 0.0,
        "materials": [],
        "category": "Apparel",
        "tags": [],
        "success": False,
        "error": None
    }
    
    if not validate_url(url):
        result["error"] = "Invalid URL format"
        return result
        
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9"
        }
        resp = requests.get(url, timeout=10, headers=headers)
        if resp.status_code != 200:
            result["error"] = f"HTTP Error {resp.status_code}"
            return result
            
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # 1. Try to extract Shopify/Schema.org JSON-LD
        import json
        json_ld_scripts = soup.find_all("script", type="application/ld+json")
        for script in json_ld_scripts:
            try:
                data = json.loads(script.string or "")
                # Single product object or list of products
                products_data = []
                if isinstance(data, dict):
                    if data.get("@type") == "Product":
                        products_data.append(data)
                    elif "@graph" in data:
                        products_data.extend([item for item in data["@graph"] if item.get("@type") == "Product"])
                elif isinstance(data, list):
                    products_data.extend([item for item in data if item.get("@type") == "Product"])
                    
                for product_data in products_data:
                    if product_data.get("name"):
                        result["name"] = product_data["name"]
                    if product_data.get("description"):
                        result["description"] = product_data["description"]
                    if product_data.get("image"):
                        img = product_data["image"]
                        result["imageUrl"] = img[0] if isinstance(img, list) else img
                    if product_data.get("brand"):
                        brand_info = product_data["brand"]
                        result["brand"] = brand_info.get("name", "International Brand") if isinstance(brand_info, dict) else brand_info
                        
                    # Price extraction
                    offers = product_data.get("offers")
                    if offers:
                        if isinstance(offers, list) and len(offers) > 0:
                            offers = offers[0]
                        if isinstance(offers, dict):
                            result["price"] = float(offers.get("price", 0.0))
                            
                    result["success"] = True
                    break
            except Exception:
                continue
                
        # 2. OpenGraph metadata fallback if details not fully populated
        if not result["name"]:
            og_title = soup.find("meta", property="og:title")
            if og_title:
                result["name"] = og_title.get("content", "")
                
        if not result["imageUrl"]:
            og_image = soup.find("meta", property="og:image")
            if og_image:
                result["imageUrl"] = og_image.get("content", "")
                
        if not result["description"]:
            og_desc = soup.find("meta", property="og:description")
            if og_desc:
                result["description"] = og_desc.get("content", "")
                
        if result["price"] == 0.0:
            price_meta = soup.find("meta", property="product:price:amount") or soup.find("meta", name="twitter:label1")
            if price_meta:
                content = price_meta.get("content", "")
                # Extract digits
                price_match = re.search(r"\d+(\.\d+)?", content)
                if price_match:
                    result["price"] = float(price_match.group(0))
                    
        # 3. DOM selector fallbacks as final resort
        if not result["name"]:
            h1 = soup.find("h1")
            if h1:
                result["name"] = h1.text.strip()
                
        # Extract materials from text description if possible
        materials_keywords = ["linen", "cotton", "polyester", "wool", "silk", "leather", "nylon", "bamboo", "acrylic", "denim", "suede", "mesh", "polycarbonate", "silicone"]
        desc_lower = result["description"].lower()
        extracted_materials = []
        for m in materials_keywords:
            if m in desc_lower or m in result["name"].lower():
                extracted_materials.append(m.capitalize())
        result["materials"] = list(set(extracted_materials))
        
        # Categorization logic
        category_keywords = {
            "Apparel": ["shirt", "kurta", "tshirt", "jeans", "trousers", "jacket", "coat", "dress", "saree"],
            "Footwear": ["shoes", "sneakers", "sandals", "boots", "flats", "chappal"],
            "Electronics": ["laptop", "phone", "tablet", "keyboard", "mouse", "charger", "powerbank"],
            "Audio": ["headphones", "earphones", "earbuds", "speaker", "soundbar"],
            "Watches": ["watch", "smartwatch", "timepiece"],
            "Skincare": ["moisturizer", "serum", "sunscreen", "cleanser", "lotion", "cream"],
            "Bags": ["backpack", "handbag", "tote", "messenger", "duffel", "luggage"],
            "Jewelry": ["ring", "necklace", "earring", "bracelet", "gold", "silver"],
            "Furniture": ["sofa", "chair", "table", "bed", "mattress", "desk", "bookshelf"],
            "Home Decor": ["vase", "rug", "cushion", "pillow", "lamp", "painting"],
            "Kitchen": ["pan", "pot", "blender", "cooker", "bottle", "kettle"],
            "Fitness": ["dumbbell", "mat", "kettlebell", "band", "wheel"],
            "Perfumes": ["perfume", "fragrance", "scent", "cologne", "attar"],
            "Eyewear": ["glasses", "sunglasses", "frames", "spectacles"]
        }
        
        text_content = (result["name"] + " " + result["description"]).lower()
        matched_cat = "Apparel"
        max_matches = 0
        for cat, keywords in category_keywords.items():
            matches = sum(1 for kw in keywords if kw in text_content)
            if matches > max_matches:
                max_matches = matches
                matched_cat = cat
        result["category"] = matched_cat
        
        # Clean URLs
        if result["imageUrl"] and result["imageUrl"].startswith("//"):
            result["imageUrl"] = "https:" + result["imageUrl"]
            
        result["success"] = bool(result["name"])
        
    except Exception as e:
        result["error"] = str(e)
        
    return result
