import os
import sys
import json
import re
import random
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(PROJECT_ROOT)
sys.path.append(os.path.join(PROJECT_ROOT, "backend"))

from backend.scrapers.deduplicate import Deduplicator
from backend.scrapers.enrich_existing import extract_badges, generate_unique_review_summary
from backend.scrapers.brand_scrapers.shopify_scraper import ShopifyScraper
from backend.ai.vector_store import ProductVectorStore
from backend.ai.embeddings import get_openai_embeddings

# 1. Verified Brand URL Mapping
VERIFIED_DOMAINS = {
    "snitch": "https://www.snitch.com",
    "rare rabbit": "https://thehouseofrare.com",
    "bombay shirt company": "https://www.bombayshirts.com",
    "nicobar": "https://www.nicobar.com",
    "zouk": "https://zouk.co.in",
    "mokobara": "https://mokobara.com",
    "dailyobjects": "https://www.dailyobjects.com",
    "minimalist": "https://beminimalist.co",
    "dot & key": "https://www.dotandkey.com",
    "plum": "https://plumgoodness.com",
    "the derma co": "https://thedermaco.com",
    "boat": "https://www.boat-lifestyle.com",
    "noise": "https://www.gonoise.com",
    "boult": "https://www.boultaudio.com",
    "portronics": "https://www.portronics.com",
    "titan": "https://www.titan.co.in",
    "fastrack": "https://www.fastrack.in",
    "bangalore watch company": "https://bangalorewatchcompany.com",
    "wakefit": "https://www.wakefit.co",
    "wooden street": "https://www.woodenstreet.com",
    "wonderchef": "https://www.wonderchef.com",
    "borosil": "https://myborosil.com",
    "giva": "https://www.giva.co",
    "bella vita": "https://bellavitaorganic.com",
    "cultsport": "https://cultsport.com",
    "boldfit": "https://boldfit.in",
    "chumbak": "https://www.chumbak.com",
    "lenskart": "https://www.lenskart.com",
    "comet": "https://www.wearcomet.com",
    "bombay perfumery": "https://www.bombayperfumery.com",
    "neeman's": "https://neemans.com",
    
    # Global/Kaggle brands
    "adidas": "https://www.adidas.co.in",
    "american tourister": "https://www.americantourister.in",
    "apple": "https://www.apple.com/in",
    "dell": "https://www.dell.com/en-in",
    "fossil": "https://www.fossil.com/en-in",
    "h&m": "https://www2.hm.com/en_in",
    "hp": "https://www.hp.com/in-en",
    "levi's": "https://www.levi.in",
    "nike": "https://www.nike.com/in",
    "oneplus": "https://www.oneplus.in",
    "puma": "https://in.puma.com",
    "rayban": "https://india.ray-ban.com",
    "reebok": "https://www.reebok.co.in",
    "samsung": "https://www.samsung.com/in",
    "sony": "https://www.sony.co.in",
    "zara": "https://www.zara.com/in"
}

# Shopify API Scrape Targets
LIVE_SHOPIFY_API_URLS = {
    "snitch": "https://www.snitch.co.in", # Scraped via co.in API, but domain mapped to snitch.com
    "rare rabbit": "https://thehouseofrare.com",
    "bombay shirt company": "https://www.bombayshirts.com",
    "nicobar": "https://www.nicobar.com",
    "zouk": "https://zouk.co.in",
    "mokobara": "https://mokobara.com",
    "minimalist": "https://beminimalist.co",
    "dot & key": "https://www.dotandkey.com",
    "plum": "https://plumgoodness.com",
    "the derma co": "https://thedermaco.com",
    "boat": "https://www.boat-lifestyle.com",
    "noise": "https://www.gonoise.com",
    "boult": "https://www.boultaudio.com",
    "portronics": "https://www.portronics.com",
    "wonderchef": "https://www.wonderchef.com",
    "borosil": "https://myborosil.com",
    "giva": "https://www.giva.co",
    "bella vita": "https://bellavitaorganic.com",
    "boldfit": "https://boldfit.in",
    "chumbak": "https://www.chumbak.com",
    "comet": "https://www.wearcomet.com"
}

# Brand Whitelist - Includes verified Indian brands and allowed Kaggle global brands
INDIAN_BRAND_WHITELIST = {
    "snitch", "rare rabbit", "bombay shirt company", "nicobar", "the souled store",
    "zouk", "mokobara", "dailyobjects", "minimalist", "dot & key", "plum",
    "the derma co", "boat", "noise", "boult", "portronics", "titan", "fastrack",
    "bangalore watch company", "wakefit", "wooden street", "wonderchef",
    "borosil", "giva", "lenskart", "bella vita", "skinn by titan", "cultsport",
    "boldfit", "comet", "neeman's", "chumbak", "bombay perfumery",
    
    # Global/Kaggle brands
    "puma", "adidas", "nike", "reebok", "apple", "dell", "hp", "samsung", "sony",
    "zara", "h&m", "levi's", "oneplus", "rayban", "fossil", "american tourister"
}

# Mapping table for the 21 unique Kaggle product names to relevant images and real urls
KAGGLE_MAPPINGS = {
    "Adidas Hoodie": {
        "brand": "Adidas",
        "url": "https://www.adidas.co.in/men-hoodies",
        "image": "https://images.unsplash.com/photo-1556821840-3a63f95609a7?w=600&q=80",
        "category": "Apparel",
        "tags": ["hoodie", "sweatshirt", "sportswear", "casual"],
        "materials": ["Cotton Blend", "Polyester"],
        "description": "Premium Adidas Hoodie designed for sporty style, comfort, and everyday durability."
    },
    "Adidas Ultraboost": {
        "brand": "Adidas",
        "url": "https://www.adidas.co.in/ultraboost",
        "image": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600&q=80",
        "category": "Footwear",
        "tags": ["sneakers", "running", "shoes", "active"],
        "materials": ["Primeknit", "Boost Cushioning"],
        "description": "High-performance Adidas Ultraboost running shoes featuring energy-returning cushioning and breathable upper."
    },
    "American Tourister Bag": {
        "brand": "American Tourister",
        "url": "https://www.americantourister.in/backpacks",
        "image": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=600&q=80",
        "category": "Bags",
        "tags": ["backpack", "travel", "luggage", "durable"],
        "materials": ["Polyester Canvas"],
        "description": "Spacious and durable American Tourister backpack with organized compartments for daily travel and work."
    },
    "Boat Earbuds": {
        "brand": "boAt",
        "url": "https://www.boat-lifestyle.com/collections/true-wireless-earbuds",
        "image": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=600&q=80",
        "category": "Audio",
        "tags": ["earbuds", "wireless", "tws", "music", "audio"],
        "materials": ["Plastic", "Silicone"],
        "description": "boAt TWS Earbuds offering high-fidelity sound, deep bass, and comfortable fit for active music lovers."
    },
    "Dell Laptop": {
        "brand": "Dell",
        "url": "https://www.dell.com/en-in/shop/laptops",
        "image": "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=600&q=80",
        "category": "Electronics",
        "tags": ["laptop", "computer", "intel", "workstation"],
        "materials": ["Aluminium Casing"],
        "description": "Dell premium laptop delivering top performance, long-lasting battery, and crisp display for working professionals."
    },
    "Fossil Watch": {
        "brand": "Fossil",
        "url": "https://www.fossil.com/en-in/watches/mens-watches",
        "image": "https://images.unsplash.com/photo-1524592094714-0f0654e20314?w=600&q=80",
        "category": "Watches",
        "tags": ["watch", "leather strap", "analog", "timepiece"],
        "materials": ["Stainless Steel", "Leather"],
        "description": "Elegant Fossil analogue watch with a classic dial and a premium leather strap, matching formal and casual wear."
    },
    "H&M Sweatshirt": {
        "brand": "H&M",
        "url": "https://www2.hm.com/en_in/men/shop-by-product/hoodies-sweatshirts.html",
        "image": "https://images.unsplash.com/photo-1620799140408-edc6dcb6d633?w=600&q=80",
        "category": "Apparel",
        "tags": ["sweatshirt", "sweater", "casual", "basic"],
        "materials": ["Organic Cotton", "Polyester Blend"],
        "description": "Minimalist H&M sweatshirt made with soft organic cotton blend fabric for a classic, cozy everyday styling."
    },
    "HP Pavilion": {
        "brand": "HP",
        "url": "https://www.hp.com/in-en/shop/laptops/pavilion.html",
        "image": "https://images.unsplash.com/photo-1593642632823-8f785ba67e45?w=600&q=80",
        "category": "Electronics",
        "tags": ["laptop", "pavilion", "windows", "office"],
        "materials": ["Polycarbonate Casing"],
        "description": "Reliable HP Pavilion laptop designed for smooth multitasking, high-definition entertainment, and clean looks."
    },
    "Levi's Jeans": {
        "brand": "Levi's",
        "url": "https://www.levi.in/men/jeans",
        "image": "https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=600&q=80",
        "category": "Apparel",
        "tags": ["jeans", "denim", "pants", "classic"],
        "materials": ["98% Cotton", "2% Elastane"],
        "description": "Iconic Levi's denim jeans in a regular fit, offering classic rugged style and stretchable comfort."
    },
    "Nike Air Max": {
        "brand": "Nike",
        "url": "https://www.nike.com/in/w/mens-air-max-shoes-37v78znik1zy7ok",
        "image": "https://images.unsplash.com/photo-1549298916-b41d501d3772?w=600&q=80",
        "category": "Footwear",
        "tags": ["sneakers", "running", "airmax", "athletic"],
        "materials": ["Synthetic Mesh", "Rubber Sole"],
        "description": "Nike Air Max running sneakers offering superior air-cushioned comfort, light weight, and distinct street appeal."
    },
    "Nike T-shirt": {
        "brand": "Nike",
        "url": "https://www.nike.com/in/w/mens-tops-t-shirts-9om1znik1",
        "image": "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=600&q=80",
        "category": "Apparel",
        "tags": ["tshirt", "sportswear", "dryfit", "active"],
        "materials": ["Polyester Dry-Fit"],
        "description": "Breathable Nike Dry-Fit sports t-shirt designed to keep you cool and dry during workouts or active days."
    },
    "OnePlus 11": {
        "brand": "OnePlus",
        "url": "https://www.oneplus.in/11",
        "image": "https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=600&q=80",
        "category": "Electronics",
        "tags": ["phone", "oneplus", "android", "smartphone"],
        "materials": ["Gorilla Glass", "Aluminium Frame"],
        "description": "OnePlus 11 flagship smartphone with high-end Snapdragon processor, fast charging, and Hasselblad camera."
    },
    "Puma Jacket": {
        "brand": "Puma",
        "url": "https://in.puma.com/in/en/mens/mens-clothing/mens-clothing-jackets",
        "image": "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=600&q=80",
        "category": "Apparel",
        "tags": ["jacket", "sportswear", "windbreaker", "athleisure"],
        "materials": ["Nylon", "Polyester Lining"],
        "description": "Sleek Puma activewear jacket offering wind resistance, warmth, and dynamic design for early runs or casual style."
    },
    "Puma Sneakers": {
        "brand": "Puma",
        "url": "https://in.puma.com/in/en/mens/mens-shoes/mens-shoes-sneakers",
        "image": "https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=600&q=80",
        "category": "Footwear",
        "tags": ["sneakers", "shoes", "casual", "sporty"],
        "materials": ["Suede Leather", "Rubber"],
        "description": "Classic Puma suede lifestyle sneakers with a padded collar and supportive rubber sole for all-day styling."
    },
    "RayBan Sunglasses": {
        "brand": "RayBan",
        "url": "https://india.ray-ban.com/sunglasses.html",
        "image": "https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=600&q=80",
        "category": "Eyewear",
        "tags": ["sunglasses", "aviator", "eyewear", "polarized"],
        "materials": ["Metal Frame", "Glass Lens"],
        "description": "Iconic RayBan Aviator sunglasses offering full UV protection, classic metal framing, and glare-free polarized vision."
    },
    "Reebok Shoes": {
        "brand": "Reebok",
        "url": "https://www.reebok.co.in/men-shoes",
        "image": "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=600&q=80",
        "category": "Footwear",
        "tags": ["shoes", "running", "workout", "fitness"],
        "materials": ["Synthetic mesh", "EVA midsole"],
        "description": "Reebok athletic shoes optimized for dynamic cross-training, running, and daily gym workouts with high support."
    },
    "Samsung Galaxy S21": {
        "brand": "Samsung",
        "url": "https://www.samsung.com/in/smartphones/galaxy-s21-5g/",
        "image": "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=600&q=80",
        "category": "Electronics",
        "tags": ["phone", "samsung", "android", "smartphone"],
        "materials": ["Glass front", "Plastic back"],
        "description": "Samsung Galaxy S21 smartphone with high-end screen, multi-lens camera setup, and 5G connectivity support."
    },
    "Sony Headphones": {
        "brand": "Sony",
        "url": "https://www.sony.co.in/headphones",
        "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&q=80",
        "category": "Audio",
        "tags": ["headphones", "wireless", "noise cancelling", "anc", "music"],
        "materials": ["Plastics", "Leatherette pads"],
        "description": "Sony premium over-ear headphones featuring industry-leading active noise cancellation, custom audio tuning, and battery life."
    },
    "Wildcraft Backpack": {
        "brand": "Wildcraft",
        "url": "https://wildcraft.com/backpacks",
        "image": "https://images.unsplash.com/photo-1544816155-12df9643f363?w=600&q=80",
        "category": "Bags",
        "tags": ["backpack", "outdoor", "hiking", "trekking"],
        "materials": ["Ripstop Nylon"],
        "description": "Rugged Wildcraft outdoor backpack designed for heavy load distribution, water resistance, and trail utility."
    },
    "Zara Shirt": {
        "brand": "Zara",
        "url": "https://www.zara.com/in/en/man-shirts-l737.html",
        "image": "https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=600&q=80",
        "category": "Apparel",
        "tags": ["shirt", "buttondown", "linen", "formal"],
        "materials": ["100% Linen"],
        "description": "Trendy Zara linen button-down shirt with structured collar and relaxed fit, designed for modern smart casual looks."
    },
    "iPhone 13": {
        "brand": "Apple",
        "url": "https://www.apple.com/in/iphone-13/",
        "image": "https://images.unsplash.com/photo-1510557880182-3d4d3cba35a5?w=600&q=80",
        "category": "Electronics",
        "tags": ["phone", "apple", "ios", "iphone"],
        "materials": ["Ceramic Shield front", "Aluminium design"],
        "description": "Apple iPhone 13 featuring advanced dual-camera system, A15 Bionic chip, and durable Ceramic Shield glass."
    }
}

# Curated Fallback Category Images
FALLBACK_IMAGES = {
    "Apparel": "https://images.unsplash.com/photo-1523381210434-271e8be1f52b?w=600&q=80",
    "Footwear": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600&q=80",
    "Skincare": "https://images.unsplash.com/photo-1556228720-195a672e8a03?w=600&q=80",
    "Audio": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&q=80",
    "Watches": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&q=80",
    "Electronics": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=600&q=80",
    "Bags": "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=600&q=80",
    "Jewelry": "https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?w=600&q=80",
    "Furniture": "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=600&q=80",
    "Home Decor": "https://images.unsplash.com/photo-1513519245088-0e12902e5a38?w=600&q=80",
    "Kitchen": "https://images.unsplash.com/photo-1584269600464-37b1b58a9fe7?w=600&q=80",
    "Fitness": "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?w=600&q=80",
    "Perfumes": "https://images.unsplash.com/photo-1541643600914-78b084683601?w=600&q=80",
    "Eyewear": "https://images.unsplash.com/photo-1574258495973-f010dfbb5371?w=600&q=80",
}
DEFAULT_FALLBACK = "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&q=80"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def correct_domain_in_url(url: str) -> str:
    if not url:
        return url
    corrections = {
        "rarerabbit.in": "thehouseofrare.com",
        "www.bombayclothingcompany.com": "www.bombayshirts.com",
        "bombaytshirtcompany.com": "www.bombayshirts.com",
        "thedermacompany.com": "thedermaco.com",
        "boult.com": "www.boultaudio.com",
        "www.borosil.com": "myborosil.com",
        "cometshoes.com": "www.wearcomet.com",
        "snitch.co.in": "snitch.com"
    }
    for old, new in corrections.items():
        if old in url:
            url = url.replace(old, new)
    return url

def validate_and_fallback_urls(p: dict) -> dict:
    brand_key = p["brand"].lower()
    homepage = VERIFIED_DOMAINS.get(brand_key, "https://www.google.com")
    
    # 1. Correct URLs first
    p["productUrl"] = correct_domain_in_url(p.get("productUrl", ""))
    p["brandUrl"] = correct_domain_in_url(p.get("brandUrl", ""))
    p["imageUrl"] = correct_domain_in_url(p.get("imageUrl", ""))
    
    # 2. Check product URL
    url = p.get("productUrl", "")
    if url:
        try:
            r = requests.head(url, headers=HEADERS, timeout=3, allow_redirects=True)
            if r.status_code == 404:
                p["productUrl"] = homepage
        except Exception:
            pass
    else:
        p["productUrl"] = homepage
        
    # 3. Check Image URL
    img = p.get("imageUrl", "")
    if img:
        if "unsplash.com" not in img:
            try:
                r = requests.head(img, headers=HEADERS, timeout=3, allow_redirects=True)
                if r.status_code == 404:
                    cat = p.get("category", "Apparel")
                    p["imageUrl"] = FALLBACK_IMAGES.get(cat, DEFAULT_FALLBACK)
            except Exception:
                pass
    else:
        cat = p.get("category", "Apparel")
        p["imageUrl"] = FALLBACK_IMAGES.get(cat, DEFAULT_FALLBACK)
        
    return p

def scrape_shopify_live(brand_name: str, base_url: str) -> list:
    print(f"Scraping live Shopify products from {brand_name}...")
    try:
        scraper = ShopifyScraper(brand_name, base_url)
        products = scraper.scrape(limit=35)
        
        cleaned = []
        for p in products:
            p["productUrl"] = correct_domain_in_url(p["productUrl"])
            p["brandUrl"] = correct_domain_in_url(p["brandUrl"])
            p["imageUrl"] = correct_domain_in_url(p["imageUrl"])
            
            if brand_name.lower() == "snitch":
                p["productUrl"] = p["productUrl"].replace("snitch.co.in", "snitch.com")
                p["brandUrl"] = "https://www.snitch.com"
                
            p["category"] = p.get("category", "Apparel")
            if not p.get("description"):
                p["description"] = f"Premium {p['name']} from {p['brand']}, crafted with high craftsmanship and style."
                
            price = float(p.get("price") or 299.0)
            orig_price = p.get("originalPrice")
            if not orig_price or orig_price <= price:
                discount_percent = random.choice([0.15, 0.20, 0.25, 0.30, 0.35, 0.40])
                orig_price = float(round((price / (1.0 - discount_percent)) / 100.0) * 100.0 - 1)
                if orig_price <= price:
                    orig_price = price + 300.0
            p["price"] = price
            p["originalPrice"] = orig_price
            
            p["rating"] = round(random.uniform(4.1, 4.9), 1)
            p["reviewCount"] = random.randint(35, 800)
            
            p["reviewSummary"] = generate_unique_review_summary(p)
            p["badges"] = extract_badges(p)
            p["madeInIndia"] = True
            
            cleaned.append(p)
            
        return cleaned
    except Exception as e:
        print(f"Error scraping {brand_name}: {e}")
        return []

def load_kaggle_products() -> list:
    path = os.path.join(PROJECT_ROOT, "data", "external_kaggle_products.json")
    print(f"Loading Kaggle dataset products from: {path}")
    if not os.path.exists(path):
        print("Kaggle dataset file not found!")
        return []
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    inr_list = data.get("e_commerce_inr_products", [])
    print(f"Loaded {len(inr_list)} raw records from Kaggle dataset.")
    
    parsed = []
    for x in inr_list:
        name = x.get("product_name")
        if not name or name not in KAGGLE_MAPPINGS:
            continue
            
        mapping = KAGGLE_MAPPINGS[name]
        
        # Calculate pricing
        price = 0.0
        try:
            price = float(x.get("discounted_price") or x.get("price") or 0.0)
        except (ValueError, TypeError):
            pass
            
        orig_price = 0.0
        try:
            orig_price = float(x.get("price") or 0.0)
        except (ValueError, TypeError):
            pass
            
        # Fallbacks for prices
        if price <= 0:
            price = 999.0
        if orig_price <= price:
            discount_percent = random.choice([0.15, 0.20, 0.25, 0.30])
            orig_price = float(round((price / (1.0 - discount_percent)) / 100.0) * 100.0 - 1)
            if orig_price <= price:
                orig_price = price + 300.0
                
        category = mapping["category"]
        
        rating = 4.2
        try:
            rating = float(x.get("rating") or 4.2)
        except (ValueError, TypeError):
            pass
            
        reviews_count = 50
        try:
            reviews_count = int(x.get("reviews_count") or 50)
        except (ValueError, TypeError):
            pass
            
        product_record = {
            "brand": mapping["brand"],
            "name": name,
            "description": x.get("description") or mapping["description"],
            "category": category,
            "tags": mapping["tags"],
            "materials": mapping["materials"],
            "price": price,
            "originalPrice": orig_price,
            "rating": rating,
            "reviewCount": reviews_count,
            "productUrl": mapping["url"],
            "imageUrl": mapping["image"],
            "brandUrl": VERIFIED_DOMAINS.get(mapping["brand"].lower(), mapping["url"]),
            "reviewSummary": f"Excellent choice for {name}. Customers praise its durability and premium design.",
            "madeInIndia": False,
            "badges": ["Imported", "Premium Choice"]
        }
        parsed.append(product_record)
        
    print(f"Successfully processed {len(parsed)} verified Kaggle products.")
    return parsed

def main():
    print("==================================================")
    print("DesiFinds Real Product Database Rebuilder")
    print("==================================================")
    
    # 1. Load base products
    base_file = "C:/Users/Bhagya B/Downloads/products_real_india_brands.json"
    print(f"Loading base products from: {base_file}")
    with open(base_file, "r", encoding="utf-8") as f:
        base_products = json.load(f)
    print(f"Loaded {len(base_products)} base products.")
    
    # 2. Validate and correct base products URLs and images
    print("Validating base products links and images...")
    validated_base = []
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(validate_and_fallback_urls, p.copy()): p for p in base_products}
        for fut in as_completed(futures):
            validated_base.append(fut.result())
            
    # Ensure base products have discounts
    for p in validated_base:
        price = float(p.get("price") or 299.0)
        orig_price = p.get("originalPrice")
        if not orig_price or orig_price <= price:
            discount_percent = random.choice([0.15, 0.20, 0.25, 0.30, 0.35, 0.40])
            orig_price = float(round((price / (1.0 - discount_percent)) / 100.0) * 100.0 - 1)
            if orig_price <= price:
                orig_price = price + 400.0
        p["price"] = price
        p["originalPrice"] = orig_price
        
    print(f"Validated base products: {len(validated_base)} items.")
    
    # 3. Scrape live Shopify stores
    scraped_products = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(scrape_shopify_live, name, url): name for name, url in LIVE_SHOPIFY_API_URLS.items()}
        for fut in as_completed(futures):
            scraped_products.extend(fut.result())
            
    print(f"Scraped {len(scraped_products)} products from live Shopify API stores.")
    
    # Validate scraped products
    print("Validating scraped products links and images...")
    validated_scraped = []
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(validate_and_fallback_urls, p.copy()): p for p in scraped_products}
        for fut in as_completed(futures):
            validated_scraped.append(fut.result())
    print(f"Validated scraped products: {len(validated_scraped)} items.")
    
    # 4. Load Kaggle products (verified and corrected)
    kaggle_products = load_kaggle_products()
    
    # 5. Consolidate and filter strictly by INDIAN_BRAND_WHITELIST
    combined = validated_base + validated_scraped + kaggle_products
    print(f"Combined count: {len(combined)}")
    
    filtered = []
    for p in combined:
        brand_name = p.get("brand", "").strip().lower()
        if brand_name in INDIAN_BRAND_WHITELIST:
            filtered.append(p)
            
    print(f"Filtered to whitelist brands: {len(filtered)}")
    
    # 6. Deduplicate
    deduped = Deduplicator.deduplicate(filtered)
    print(f"Deduplicated count: {len(deduped)}")
    
    # 7. Re-generate sequential IDs and ensure no null prices
    for idx, p in enumerate(deduped):
        p["id"] = f"p{str(idx + 1).zfill(5)}"
        p["price"] = float(p.get("price") or 0.0)
        if p.get("originalPrice"):
            p["originalPrice"] = float(p["originalPrice"])
        
    # 8. Save to the three database paths
    paths_to_save = [
        os.path.join(PROJECT_ROOT, "data", "products.json"),
        os.path.join(PROJECT_ROOT, "backend", "data", "products.json"),
        os.path.join(PROJECT_ROOT, "backend", "scrapers", "products_clean.json"),
    ]
    
    for path in paths_to_save:
        print(f"Saving database to: {path}")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(deduped, f, indent=2)
            
    print("Main products database saved successfully!")

if __name__ == "__main__":
    main()
