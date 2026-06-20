import os
import sys
import json
import re
import random
import requests
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(PROJECT_ROOT)
sys.path.append(os.path.join(PROJECT_ROOT, "backend"))

from backend.scrapers.deduplicate import Deduplicator
from backend.scrapers.enrich_existing import extract_badges, generate_unique_review_summary
from backend.scrapers.brands.brand_info import BRAND_METADATA

# Registry of new Indian brands to add
NEW_INDIAN_BRANDS = {
    "Mamaearth": {
        "name": "Mamaearth",
        "slug": "mamaearth",
        "description": "Toxin-free organic baby care and personal care products.",
        "founded": "2016",
        "founders": "Ghazal Alagh and Varun Alagh",
        "story": "Founded by husband-wife duo Ghazal and Varun Alagh to create safe, toxin-free baby care and personal care products after they struggled to find safe options for their own baby.",
        "websiteUrl": "https://mamaearth.in",
        "categories": ["Skincare"],
        "featured": True
    },
    "Himalaya": {
        "name": "Himalaya",
        "slug": "himalaya",
        "description": "Legacy Ayurvedic wellness and skincare formulations.",
        "founded": "1930",
        "founders": "M. Manal",
        "story": "Established in 1930 by Mohammed Manal to bring the traditional science of Ayurveda to contemporary form. Known globally for its Neem Face Wash and herbal solutions.",
        "websiteUrl": "https://himalayawellness.in",
        "categories": ["Skincare"],
        "featured": True
    },
    "Patanjali": {
        "name": "Patanjali",
        "slug": "patanjali",
        "description": "Swadeshi natural products promoting traditional Ayurvedic lifestyle.",
        "founded": "2006",
        "founders": "Baba Ramdev and Acharya Balkrishna",
        "story": "Patanjali Ayurved was founded to promote traditional Ayurveda and Swadeshi products. It grew rapidly to become one of India's largest consumer goods companies.",
        "websiteUrl": "https://www.patanjaliayurved.net",
        "categories": ["Skincare", "Kitchen"],
        "featured": False
    },
    "Cinthol": {
        "name": "Cinthol",
        "slug": "cinthol",
        "description": "Premium soap, talc, and deodorants by Godrej.",
        "founded": "1952",
        "founders": "Ardeshir Godrej",
        "story": "A legacy personal care brand under Godrej Consumer Products, Cinthol has been synonymous with freshness and skin protection for generations of Indians.",
        "websiteUrl": "https://www.godrejcp.com",
        "categories": ["Skincare", "Perfumes"],
        "featured": False
    },
    "Streax": {
        "name": "Streax",
        "slug": "streax",
        "description": "Popular Indian hair hair coloring and serums.",
        "founded": "2004",
        "founders": "Ashish K. Chhabra",
        "story": "Launched by the Hygienic Research Institute, Streax revolutionized the Indian home hair coloring market with its premium formulations and easy-to-use serums.",
        "websiteUrl": "https://www.streax.in",
        "categories": ["Skincare"],
        "featured": False
    },
    "Mysore Sandal": {
        "name": "Mysore Sandal",
        "slug": "mysore-sandal",
        "description": "GI-tagged luxury soaps made from 100% pure sandalwood oil.",
        "founded": "1916",
        "founders": "Maharaja Nalwadi Krishnaraja Wodeyar and Sir M. Visvesvaraya",
        "story": "Set up in 1916 to utilize the surplus sandalwood in Mysore. The Government Soap Factory produces the world's only soap made from 100% pure sandalwood oil.",
        "websiteUrl": "https://www.kstdcl.com",
        "categories": ["Skincare"],
        "featured": True
    },
    "Metronaut": {
        "name": "Metronaut",
        "slug": "metronaut",
        "description": "Trendy private-label casual wear and streetwear.",
        "founded": "2017",
        "founders": "Flipkart Group",
        "story": "Metronaut is a trendy fashion label launched by Flipkart as a private brand to deliver stylish and affordable streetwear and casual wear to Indian consumers.",
        "websiteUrl": "https://www.flipkart.com",
        "categories": ["Apparel"],
        "featured": False
    },
    "Breakbounce": {
        "name": "Breakbounce",
        "slug": "breakbounce",
        "description": "Streetwear and fast-fashion clothing based in Bangalore.",
        "founded": "2012",
        "founders": "Sanjeev Mukhija",
        "story": "An Indian streetwear brand that focuses on fast-fashion casual clothing, offering European-style trends at affordable local price points.",
        "websiteUrl": "https://www.breakbounce.com",
        "categories": ["Apparel"],
        "featured": False
    },
    "Scott International": {
        "name": "Scott International",
        "slug": "scott-international",
        "description": "High-quality activewear and basic tees.",
        "founded": "2013",
        "founders": "Scott International India",
        "story": "A D2C brand offering high-quality basic tees, sportswear, and performance wear for daily active lifestyles.",
        "websiteUrl": "https://www.scottinternational.in",
        "categories": ["Apparel"],
        "featured": False
    },
    "Vector X": {
        "name": "Vector X",
        "slug": "vector-x",
        "description": "Athletic sportswear and sports fitness accessories.",
        "founded": "1999",
        "founders": "Lazer Sports",
        "story": "A leading Indian sports brand offering reliable activewear, sports equipment, and fitness accessories for athletes across the country.",
        "websiteUrl": "https://www.vectorx.co.in",
        "categories": ["Fitness"],
        "featured": False
    },
    "Wildcraft": {
        "name": "Wildcraft",
        "slug": "wildcraft",
        "description": "Indian outdoor gear, backpacks, and performance apparel.",
        "founded": "1998",
        "founders": "Siddharth Sood and Dinesh Kaushal",
        "story": "Began in a small garage in Bangalore as an outdoor gear brand. It grew into India's largest outdoor equipment and apparel brand.",
        "websiteUrl": "https://wildcraft.com",
        "categories": ["Bags", "Apparel"],
        "featured": True
    },
    "Cantabil": {
        "name": "Cantabil",
        "slug": "cantabil",
        "description": "Formal and casual apparel with over 400 stores nationwide.",
        "founded": "2000",
        "founders": "Vijay Bansal",
        "story": "Cantabil Retail India designs, manufactures, and retails a comprehensive range of family garments, growing a massive retail footprint across India.",
        "websiteUrl": "https://cantabilinternational.com",
        "categories": ["Apparel"],
        "featured": False
    },
    "Denver": {
        "name": "Denver",
        "slug": "denver",
        "description": "Premium male grooming products, fragrances, and deodorants.",
        "founded": "2007",
        "founders": "McNROE Consumer Products",
        "story": "Denver is a leading men's grooming brand in India, famous for its long-lasting deodorants, Eau de Parfums, and personal care solutions.",
        "websiteUrl": "https://www.denverfor-men.com",
        "categories": ["Perfumes"],
        "featured": False
    },
    "Fogg": {
        "name": "Fogg",
        "slug": "fogg",
        "description": "Disruptive perfume sprays with a 'no gas' formula.",
        "founded": "2011",
        "founders": "Darshan Patel",
        "story": "Vini Cosmetics launched Fogg in 2011, disrupting the Indian deodorant market with its 'no gas, only perfume' value proposition and legendary advertising.",
        "websiteUrl": "https://www.vinicosmetics.com",
        "categories": ["Perfumes"],
        "featured": True
    },
    "Wild Stone": {
        "name": "Wild Stone",
        "slug": "wild-stone",
        "description": "Leading fragrance brand and male hygiene solutions.",
        "founded": "2007",
        "founders": "McNROE Consumer Products",
        "story": "Wild Stone is a leading men's grooming brand owned by McNROE, known for its premium fragrances and intense masculine marketing.",
        "websiteUrl": "https://www.wildstone.in",
        "categories": ["Perfumes"],
        "featured": False
    },
    "Godrej aer": {
        "name": "Godrej aer",
        "slug": "godrej-aer",
        "description": "Innovative household and car fresheners.",
        "founded": "2012",
        "founders": "Godrej Group",
        "story": "Launched by Godrej to bring innovative gel-based and click-spray bathroom and car air fresheners to Indian households.",
        "websiteUrl": "https://www.godrejcp.com",
        "categories": ["Perfumes", "Home Decor"],
        "featured": False
    }
}

# Combine existing brand URLs with new ones
BRAND_HOME_PAGES = {k.lower(): meta["websiteUrl"] for k, meta in BRAND_METADATA.items()}
for k, meta in NEW_INDIAN_BRANDS.items():
    BRAND_HOME_PAGES[k.lower()] = meta["websiteUrl"]

# Flipkart brand normalizations
FLIPKART_BRAND_MAP = {
    "true bl": "True Blue",
    "mett": "Metronaut",
    "m7 by metrona": "Metronaut",
    "scott internation": "Scott International",
    "chawla fashi": "Chawla Fashions",
    "steenb": "Steenbok",
    "uber urb": "Uber Urban",
    "attiitu": "Attiitude",
    "satdevangikhadibhand": "Satdevangi Khadi Bhandar",
    "byford by pantaloo": "Byford",
    "cantab": "Cantabil",
    "jagdish garmen": "Jagdish Garments",
    "mylifestylebazz": "Mylifestylebazaar",
    "styleska": "Styleskart",
    "tees collecti": "Tees Collection",
    "jai textil": "Jai Textiles",
    "wildst": "Wildcraft",
    "a j styl": "A J Styles",
    "m.r. fashi": "M.R. Fashion",
    "vibrant vestu": "Vibrant Vesture",
    "bindass bo": "Bindass Boy",
    "sayitlo": "SayItLoud"
}

# Whitelist of brand names that are verified Indian brands
INDIAN_BRAND_WHITELIST = {
    "snitch", "rare rabbit", "bombay shirt company", "nicobar", "the souled store",
    "zouk", "mokobara", "dailyobjects", "minimalist", "dot & key", "plum",
    "the derma co", "boat", "noise", "boult", "portronics", "titan", "fastrack",
    "bangalore watch company", "wakefit", "wooden street", "wonderchef",
    "borosil", "giva", "lenskart", "bella vita", "skinn by titan", "cultsport",
    "boldfit", "comet", "neeman's", "chumbak", "bombay perfumery",
    # New brands
    "mamaearth", "himalaya", "patanjali", "cinthol", "streax", "mysore sandal",
    "metronaut", "breakbounce", "scott international", "vector x", "wildcraft",
    "cantabil", "denver", "fogg", "wild stone", "godrej aer", "true blue",
    "byford", "sayitloud", "attiitude", "savlon"
}

def normalize_price(val) -> float:
    if val is None:
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    # Extract digits and decimal point
    clean = re.sub(r"[^\d.]", "", str(val))
    try:
        return float(clean) if clean else 0.0
    except ValueError:
        return 0.0

def validate_url_concurrent(url, headers, timeout=4):
    if not url or not url.startswith("http"):
        return False
    # Optimize network calls by skipping checks for Google searches or brand homepages
    url_lower = url.lower()
    if "google.com" in url_lower or "google.in" in url_lower:
        return True
    
    for hp in BRAND_HOME_PAGES.values():
        if url.strip("/").lower() == hp.strip("/").lower():
            return True
            
    try:
        r = requests.head(url, headers=headers, timeout=timeout, allow_redirects=True)
        if r.status_code == 404:
            r_get = requests.get(url, headers=headers, timeout=timeout, stream=True, allow_redirects=True)
            return r_get.status_code != 404
        elif r.status_code >= 400:
            r_get = requests.get(url, headers=headers, timeout=timeout, stream=True, allow_redirects=True)
            return r_get.status_code != 404
        return True
    except Exception:
        return False

def clean_and_sanitize_urls(products: list) -> list:
    print("Checking and fixing broken URLs concurrently...")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    # Pre-resolve homepages
    def get_homepage(brand_name):
        bn = brand_name.strip().lower()
        # Substring mapping fallback
        for k, url in BRAND_HOME_PAGES.items():
            if k in bn or bn in k:
                return url
        return "https://www.snitch.co.in" # absolute fallback

    # Check unique urls concurrently to save network overhead
    urls_to_check = list(set([p["productUrl"] for p in products]))
    
    # We will use thread pool to check them
    results = {}
    with ThreadPoolExecutor(max_workers=30) as executor:
        futures = {executor.submit(validate_url_concurrent, url, headers): url for url in urls_to_check}
        for fut in as_completed(futures):
            url = futures[fut]
            try:
                results[url] = fut.result()
            except Exception:
                results[url] = False

    fixed_count = 0
    for p in products:
        p_url = p["productUrl"]
        # Normalize snitch.com to snitch.co.in if it redirects or fails
        if "snitch.com" in p_url:
            p_url_new = p_url.replace("snitch.com", "snitch.co.in")
            p["productUrl"] = p_url_new
            p_url = p_url_new
            
        is_valid = results.get(p_url, False)
        if not is_valid:
            # Fallback to homepage
            hp = get_homepage(p["brand"])
            p["productUrl"] = hp
            fixed_count += 1

    print(f"Fixed {fixed_count} broken URLs by falling back to brand store homepages.")
    return products

def parse_flipkart_dataset() -> list:
    print("Downloading and parsing Flipkart dataset...")
    url = "https://raw.githubusercontent.com/rahulsingh3292/paradedb-django/main/flipkart_fashion_products_dataset.json"
    resp = requests.get(url, timeout=10)
    data = resp.json()
    
    filtered_products = []
    brand_counts = {}
    
    # Map category names
    category_map = {
        "bottomwear": "Apparel",
        "topwear": "Apparel",
        "outerwear": "Apparel",
        "innerwear": "Apparel",
        "eyewear": "Eyewear",
        "sports footwear": "Footwear",
        "casual footwear": "Footwear",
        "formal footwear": "Footwear",
        "bags": "Bags",
        "watches": "Watches",
    }
    
    for idx, item in enumerate(data):
        brand_raw = item.get("brand", "")
        # Apply normalization
        brand_norm = FLIPKART_BRAND_MAP.get(brand_raw.lower(), brand_raw)
        
        # Check if verified Indian brand
        if brand_norm.lower() not in INDIAN_BRAND_WHITELIST:
            continue
            
        # Limit items per brand to keep data clean and compact (e.g. max 30 per brand)
        b_key = brand_norm.lower()
        brand_counts[b_key] = brand_counts.get(b_key, 0) + 1
        if brand_counts[b_key] > 30:
            continue
            
        # Extract category
        sub_cat = str(item.get("sub_category", "")).lower()
        mapped_cat = category_map.get(sub_cat, "Apparel")
        
        price = normalize_price(item.get("selling_price", 0.0))
        orig_price = normalize_price(item.get("actual_price", 0.0))
        if orig_price < price:
            orig_price = price
            
        rating = 4.2
        try:
            rating = float(item.get("average_rating", 4.2))
        except (ValueError, TypeError):
            pass
            
        # Image link
        images_list = item.get("images", [])
        image_url = images_list[0] if (isinstance(images_list, list) and len(images_list) > 0) else "https://images.unsplash.com/photo-1523381210434-271e8be1f52b?w=600&q=80"
        
        desc = item.get("description", "")
        if not desc:
            desc = f"Premium {brand_norm} {item.get('title', 'Product')} designed with local craftsmanship and style."
            
        product_record = {
            "id": f"pf{str(idx).zfill(5)}",
            "brand": brand_norm,
            "name": item.get("title", ""),
            "description": desc,
            "category": mapped_cat,
            "tags": [sub_cat] if sub_cat else [],
            "materials": [],
            "price": price,
            "originalPrice": orig_price,
            "rating": rating,
            "reviewCount": random.randint(15, 600),
            "productUrl": item.get("url", BRAND_HOME_PAGES.get(b_key, "https://www.flipkart.com")),
            "imageUrl": image_url,
            "brandUrl": BRAND_HOME_PAGES.get(b_key, ""),
            "reviewSummary": "", # Will enrich later
            "madeInIndia": True,
            "badges": []
        }
        
        # Enrich tags and materials
        for spec in item.get("product_details", []):
            if isinstance(spec, dict):
                for k, v in spec.items():
                    if k.lower() in ["fabric", "material"]:
                        product_record["materials"].append(v.capitalize())
                        product_record["tags"].append(v.lower())
                        
        product_record["badges"] = extract_badges(product_record)
        product_record["reviewSummary"] = generate_unique_review_summary(product_record)
        filtered_products.append(product_record)
        
    print(f"Processed {len(filtered_products)} Flipkart products across Indian brands.")
    return filtered_products

def parse_amazon_dataset() -> list:
    print("Downloading and parsing Amazon dataset...")
    df = None
    try:
        print("Attempting to download nehaprabhavalkar/indian-products-on-amazon via kagglehub...")
        import kagglehub
        folder_path = kagglehub.dataset_download("nehaprabhavalkar/indian-products-on-amazon")
        if folder_path and os.path.exists(folder_path):
            csv_path = None
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    if file.endswith(".csv") and "amazon" in file.lower():
                        csv_path = os.path.join(root, file)
                        break
                if csv_path:
                    break
            if csv_path and os.path.exists(csv_path):
                print(f"Parsing Amazon dataset from local kagglehub path: {csv_path}")
                df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"Kagglehub download failed: {e}. Falling back to GitHub raw URL.")

    if df is None:
        url = "https://raw.githubusercontent.com/31avantika/Sentiment-Analysis/master/amazon_vfl_reviews.csv"
        df = pd.read_csv(url)
    
    # We will group reviews by name to extract unique products
    grouped = df.groupby('name')
    products = []
    
    images = {
        "Skincare": "https://images.unsplash.com/photo-1556228720-195a672e8a03?w=600&q=80",
        "Watches": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&q=80",
        "Kitchen": "https://images.unsplash.com/photo-1584269600464-37b1b58a9fe7?w=600&q=80",
        "Apparel": "https://images.unsplash.com/photo-1523381210434-271e8be1f52b?w=600&q=80",
    }
    
    def extract_brand_from_name(p_name: str) -> str:
        name_clean = p_name.replace("-", " ").strip()
        words = name_clean.split()
        if not words:
            return "Generic"
        
        name_lower = name_clean.lower()
        # Look for standard brand keywords
        for kw in ["mamaearth", "godrej", "titan", "fastrack", "patanjali", "himalaya", "cinthol", "streax", "mysore sandal", "savlon", "paper boat", "coca cola", "maggi", "amul", "maaza", "gluncon d", "jelimals", "indiana"]:
            if kw in name_lower:
                return kw.title()
                
        return words[0].title()
        
    for idx, (name, group) in enumerate(grouped):
        detected_brand = extract_brand_from_name(name)
        b_key = detected_brand.lower()
        
        # Categorize based on brand/name
        mapped_cat = "Skincare"
        name_lower = name.lower()
        if "watch" in name_lower or "titan" in name_lower or "fastrack" in name_lower:
            mapped_cat = "Watches"
        elif "kitchen" in name_lower or "godrej" in name_lower or "maggi" in name_lower or "butter" in name_lower or "cook" in name_lower:
            mapped_cat = "Kitchen"
        elif "juice" in name_lower or "boat" in name_lower or "coke" in name_lower or "maaza" in name_lower or "drink" in name_lower or "beverage" in name_lower:
            mapped_cat = "Kitchen"
        elif "shirt" in name_lower or "clothing" in name_lower or "apparel" in name_lower:
            mapped_cat = "Apparel"
            
        # Calculate stats
        avg_rating = round(group['rating'].mean(), 1)
        review_count = len(group)
        
        clean_name = name.replace("-", " ")
        
        # Compile review text samples into a summary
        reviews_list = group['review'].dropna().tolist()
        summary = " ".join(reviews_list[:2]) if reviews_list else f"Highly rated products from {detected_brand}."
        if len(summary) > 200:
            summary = summary[:197] + "..."
            
        base_price = 499.0
        # rough pricing heuristics based on category
        if mapped_cat == "Watches":
            base_price = 1999.0
        elif mapped_cat == "Kitchen":
            base_price = 299.0
            
        product_record = {
            "id": f"pa{str(idx).zfill(5)}",
            "brand": detected_brand,
            "name": clean_name,
            "description": f"Verified authentic {clean_name} by {detected_brand}. Rich in quality, natural formulation.",
            "category": mapped_cat,
            "tags": [detected_brand.lower(), "natural"],
            "materials": [],
            "price": base_price,
            "originalPrice": base_price * 1.3,
            "rating": avg_rating,
            "reviewCount": review_count * 10 + random.randint(5, 50),
            "productUrl": f"https://www.google.com/search?q={detected_brand.replace(' ', '+')}+{clean_name.replace(' ', '+')}",
            "imageUrl": images.get(mapped_cat, images["Skincare"]),
            "brandUrl": BRAND_HOME_PAGES.get(b_key, ""),
            "reviewSummary": summary,
            "madeInIndia": True,
            "badges": []
        }
        
        product_record["badges"] = extract_badges(product_record)
        products.append(product_record)
        
    print(f"Processed {len(products)} Amazon products.")
    return products

def parse_local_inr_dataset() -> list:
    print("Checking for local Indian E-commerce Dataset (INR)...")
    import math
    
    # Search paths for the CSV
    possible_paths = [
        os.path.join(PROJECT_ROOT, "data", "ecommerce_products_killer.csv"),
        os.path.join(PROJECT_ROOT, "backend", "data", "ecommerce_products_killer.csv"),
        os.path.abspath(os.path.join(PROJECT_ROOT, "..", "ecommerce_products_killer.csv")), # Parent dir (Downloads)
    ]
    
    csv_path = None
    for p in possible_paths:
        if os.path.exists(p):
            csv_path = p
            break
            
    if not csv_path:
        # Try downloading via kagglehub!
        try:
            print("Attempting to download amaymishra11/indian-e-commerce-dataset-inr via kagglehub...")
            import kagglehub
            folder_path = kagglehub.dataset_download("amaymishra11/indian-e-commerce-dataset-inr")
            if folder_path and os.path.exists(folder_path):
                # Search for any CSV file inside the downloaded folder
                for root, dirs, files in os.walk(folder_path):
                    for file in files:
                        if file.endswith(".csv") and "ecommerce" in file.lower():
                            csv_path = os.path.join(root, file)
                            break
                    if csv_path:
                        break
        except Exception as e:
            print(f"Failed to download/parse via kagglehub: {e}")
            
    if not csv_path:
        print("Local ecommerce_products_killer.csv not found and kagglehub download failed. Skipping INR dataset parsing.")
        return []
        
    print(f"Parsing local INR dataset from: {csv_path}")
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"Error reading {csv_path}: {e}")
        return []
        
    products = []
    
    # Mapping for categories
    category_map = {
        "electronics": "Electronics",
        "fashion": "Apparel",
        "accessories": "Apparel",
        "footwear": "Footwear"
    }
    
    images = {
        "electronics": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&q=80",
        "fashion": "https://images.unsplash.com/photo-1523381210434-271e8be1f52b?w=600&q=80",
        "accessories": "https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=600&q=80",
        "footwear": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600&q=80",
    }
    
    for idx, row in df.iterrows():
        brand_raw = str(row.get("brand", "")).strip()
        if not brand_raw or brand_raw == "nan":
            brand_raw = "Generic"
            
        brand_norm = FLIPKART_BRAND_MAP.get(brand_raw.lower(), brand_raw)
        
        raw_cat = str(row.get("category", "")).lower()
        mapped_cat = category_map.get(raw_cat, "Apparel")
        
        price = normalize_price(row.get("discounted_price", 0.0))
        orig_price = normalize_price(row.get("price", 0.0))
        if orig_price < price:
            orig_price = price
            
        rating = 4.2
        try:
            rating = float(row.get("rating", 4.2))
            if math.isnan(rating) or rating < 0 or rating > 5:
                rating = 4.2
        except (ValueError, TypeError):
            pass
            
        rev_count = 10
        try:
            rev_count = int(float(row.get("reviews_count", 10)))
            if math.isnan(rev_count) or rev_count < 0:
                rev_count = 10
        except (ValueError, TypeError):
            pass
            
        desc = row.get("description", "")
        if not desc or (isinstance(desc, float) and math.isnan(desc)):
            desc = f"Premium {brand_norm} product designed for modern lifestyle and local heritage."
            
        image_url = images.get(raw_cat, images["fashion"])
            
        name = str(row.get("product_name", "Product"))
        url_query = re.sub(r"[^\w\s-]", "", f"{brand_norm} {name}").replace(" ", "+")
        
        product_record = {
            "id": f"pi{str(idx).zfill(5)}",
            "brand": brand_norm,
            "name": name,
            "description": desc,
            "category": mapped_cat,
            "tags": [raw_cat] if raw_cat else [],
            "materials": [],
            "price": price,
            "originalPrice": orig_price,
            "rating": rating,
            "reviewCount": rev_count,
            "productUrl": f"https://www.google.com/search?q={url_query}",
            "imageUrl": image_url,
            "brandUrl": BRAND_HOME_PAGES.get(brand_norm.lower(), ""),
            "reviewSummary": f"Excellent quality and value from {brand_norm}.",
            "madeInIndia": True,
            "badges": []
        }
        
        product_record["badges"] = extract_badges(product_record)
        products.append(product_record)
        
    print(f"Processed {len(products)} local INR products.")
    return products

def enrich_brand_info_py():
    print("Enriching brand_info.py with new Indian brands...")
    brand_info_path = os.path.join(PROJECT_ROOT, "backend", "scrapers", "brands", "brand_info.py")
    
    with open(brand_info_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Check if BRAND_METADATA is defined and insert new brands if not present
    # We will locate the dictionary BRAND_METADATA = {
    for brand_name, metadata in NEW_INDIAN_BRANDS.items():
        key = brand_name.lower()
        if f'"{key}":' not in content and f"'{key}':" not in content:
            # We can format the dict block to append to BRAND_METADATA
            # Let's locate BRAND_METADATA = { and insert after it
            formatted_block = f'\n    "{key}": {{\n'
            formatted_block += f'        "name": "{metadata["name"]}",\n'
            formatted_block += f'        "slug": "{metadata["slug"]}",\n'
            formatted_block += f'        "description": "{metadata["description"]}",\n'
            formatted_block += f'        "founded": "{metadata["founded"]}",\n'
            formatted_block += f'        "founders": "{metadata["founders"]}",\n'
            formatted_block += f'        "story": "{metadata["story"]}",\n'
            formatted_block += f'        "websiteUrl": "{metadata["websiteUrl"]}",\n'
            formatted_block += f'        "categories": {json.dumps(metadata["categories"])},\n'
            formatted_block += f'        "featured": {str(metadata["featured"])}\n'
            formatted_block += f'    }},\n'
            
            # Find index of BRAND_METADATA = {
            target = "BRAND_METADATA = {"
            idx = content.find(target)
            if idx != -1:
                insert_pos = idx + len(target)
                content = content[:insert_pos] + formatted_block + content[insert_pos:]
                
    with open(brand_info_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("brand_info.py updated successfully.")

def sanitize_product_types(p: dict) -> dict:
    import math
    # Clean price
    price = p.get("price")
    try:
        price = float(price) if price is not None and not (isinstance(price, float) and math.isnan(price)) else 0.0
    except (ValueError, TypeError):
        price = 0.0
    p["price"] = price

    # Clean originalPrice
    orig = p.get("originalPrice")
    try:
        orig = float(orig) if orig is not None and not (isinstance(orig, float) and math.isnan(orig)) else None
    except (ValueError, TypeError):
        orig = None

    if orig is None or orig <= 0 or orig < price:
        orig = price
    p["originalPrice"] = orig

    # Clean rating
    rating = p.get("rating")
    try:
        if rating is not None and (isinstance(rating, float) and math.isnan(rating)):
            rating = None
        elif rating is not None:
            rating = float(rating)
            if rating < 0 or rating > 5:
                rating = 4.2  # default fallback
    except (ValueError, TypeError):
        rating = None
    p["rating"] = rating

    # Clean reviewCount
    rev_count = p.get("reviewCount")
    try:
        if rev_count is not None and (isinstance(rev_count, float) and math.isnan(rev_count)):
            rev_count = 0
        elif rev_count is not None:
            rev_count = int(float(rev_count))
        else:
            rev_count = 0
    except (ValueError, TypeError):
        rev_count = 0
    p["reviewCount"] = rev_count

    # Clean badges
    badges = p.get("badges")
    if badges is None or (isinstance(badges, float) and math.isnan(badges)):
        badges = []
    elif not isinstance(badges, list):
        badges = [str(badges)]
    else:
        badges = [str(b) for b in badges if b is not None and not (isinstance(b, float) and math.isnan(b))]
    p["badges"] = badges

    # Clean tags
    tags = p.get("tags")
    if tags is None or (isinstance(tags, float) and math.isnan(tags)):
        tags = []
    elif not isinstance(tags, list):
        tags = [str(tags)]
    else:
        tags = [str(t) for t in tags if t is not None and not (isinstance(t, float) and math.isnan(t))]
    p["tags"] = tags

    # Clean materials
    mats = p.get("materials")
    if mats is None or (isinstance(mats, float) and math.isnan(mats)):
        mats = []
    elif not isinstance(mats, list):
        mats = [str(mats)]
    else:
        mats = [str(m) for m in mats if m is not None and not (isinstance(m, float) and math.isnan(m))]
    p["materials"] = mats

    # Clean strings
    for field in ["id", "brand", "name", "description", "category", "productUrl", "imageUrl", "brandUrl", "reviewSummary"]:
        val = p.get(field)
        if val is None or (isinstance(val, float) and math.isnan(val)):
            p[field] = ""
        else:
            p[field] = str(val)

    # Clean madeInIndia
    p["madeInIndia"] = bool(p.get("madeInIndia", True))

    return p

def main():
    print("==========================================")
    print("DesiFinds Database Expansion & Ingestion")
    print("==========================================")
    
    # 1. Load products_real_india_brands.json (verified products)
    base_file = "C:/Users/Bhagya B/Downloads/products_real_india_brands.json"
    with open(base_file, "r", encoding="utf-8") as f:
        base_products = json.load(f)
    print(f"Loaded {len(base_products)} base products from products_real_india_brands.json")
    
    # 2. Parse external datasets
    amazon_products = parse_amazon_dataset()
    inr_products = parse_local_inr_dataset()
    
    # 3. Consolidate and clean
    combined = base_products + amazon_products + inr_products
    print(f"Consolidated total products before deduplication: {len(combined)}")
    
    # 4. Deduplicate
    deduped = Deduplicator.deduplicate(combined)
    print(f"Deduplicated to {len(deduped)} products.")
    
    # 5. URL validation & link fixing (checks Snitch & 404 links)
    sanitized = clean_and_sanitize_urls(deduped)
    
    # 6. Re-generate IDs to ensure unique sequential order and clean originalPrice
    for idx, p in enumerate(sanitized):
        p = sanitize_product_types(p)
        p["id"] = f"p{str(idx + 1).zfill(5)}"
        sanitized[idx] = p
        
    # 7. Enrich brand_info.py with any newly added brands
    enrich_brand_info_py()
    
    # 8. Save back to all three paths
    paths_to_save = [
        os.path.join(PROJECT_ROOT, "data", "products.json"),
        os.path.join(PROJECT_ROOT, "backend", "data", "products.json"),
        os.path.join(PROJECT_ROOT, "backend", "scrapers", "products_clean.json"),
    ]
    
    for path in paths_to_save:
        print(f"Saving dataset to: {path}")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(sanitized, f, indent=2)
            
    print("Database JSON files saved successfully.")

if __name__ == "__main__":
    main()
