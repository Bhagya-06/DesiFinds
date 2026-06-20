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

UNSPLASH_POOL = {
    "apparel": [
        "photo-1523381210434-271e8be1f52b", "photo-1583743814966-8936f5b7be1a",
        "photo-1596755094514-f87e34085b2c", "photo-1618354691373-d851c5c3a990",
        "photo-1620799140408-edc6dcb6d633", "photo-1602810318383-e386cc2a3ccf",
        "photo-1603252109303-2751441dd157", "photo-1576566588028-4147f3842f27",
        "photo-1489987707025-afc232f7ea0f", "photo-1507679799987-c73779587ccf"
    ],
    "footwear": [
        "photo-1542291026-7eec264c27ff", "photo-1606107557195-0e29a4b5b4aa",
        "photo-1608231387042-66d1773070a5", "photo-1549298916-b41d501d3772",
        "photo-1595950653106-6c9ebd614d3a", "photo-1539185441755-769473a23570",
        "photo-1600185365483-26d7a4cc7519", "photo-1460353581641-37baddab0fa2",
        "photo-1491553895911-0055eca6402d", "photo-1560769629-975ec94e6a86"
    ],
    "electronics": [
        "photo-1498049794561-7780e7231661", "photo-1588872657578-7efd1f1555ed",
        "photo-1563770660941-20978e870e26", "photo-1546868871-7041f2a55e12",
        "photo-1585776245991-cf89dd7fc73a", "photo-1527689368864-3a821dbccc34",
        "photo-1616440347437-b1c73416efc2", "photo-1518770660439-4636190af475",
        "photo-1531297484001-80022131f5a1", "photo-1611186871348-b1ce696e52c9"
    ],
    "audio": [
        "photo-1505740420928-5e560c06d30e", "photo-1546435770-a3e426bf472b",
        "photo-1590658268037-6bf12165a8df", "photo-1608156639585-b3a032ef9689",
        "photo-1606220588913-b3aacb4d2f46", "photo-1524678606370-a47ad25cb82a",
        "photo-1583394838336-acd977736f90", "photo-1545454675-3531b543be5d",
        "photo-1484755560695-a4c748918c6b", "photo-1613040809024-b4ef7ba99bc3"
    ],
    "watches": [
        "photo-1523275335684-37898b6baf30", "photo-1524592094714-0f0654e20314",
        "photo-1522312346375-d1a52e2b99b3", "photo-1542496658-e33a6d0d50f6",
        "photo-1509048191080-d2984bad6ae5", "photo-1617038260897-41a1f14a8ca0",
        "photo-1619134778706-7015533a6150", "photo-1539874754764-5a96559165b0",
        "photo-1622434641406-a158123450f9", "photo-1434056886845-dac89ffee9b5"
    ],
    "skincare": [
        "photo-1556228720-195a672e8a03", "photo-1608248597279-f99d160bfcbc",
        "photo-1612817288484-6f916006741a", "photo-1620916566398-39f1143ab7be",
        "photo-1570172619644-dfd03ed5d881", "photo-1601049541289-9b1b7bbbfe19",
        "photo-1598440947619-2c35fc9aa908", "photo-1535585209827-a15fcdbc4c2d",
        "photo-1617897903246-719242758050", "photo-1626806787461-102c1bfaaea1"
    ],
    "bags": [
        "photo-1584917865442-de89df76afd3", "photo-1553062407-98eeb64c6a62",
        "photo-1622560480605-d83c853bc5c3", "photo-1590874103328-eac38a683ce7",
        "photo-1605733513597-a8f8341083ea", "photo-1544816155-12df9643f363",
        "photo-1598532163257-ae3c6b2524d6", "photo-1622560480654-d96214fdc887",
        "photo-1572196284554-4e321b0e7e0b", "photo-1532103054090-334e6e60ab29"
    ],
    "eyewear": [
        "photo-1511499767150-a48a237f0083", "photo-1572635196237-14b3f281503f",
        "photo-1508296695146-257a814070b4", "photo-1591076482161-42ce6da69f67",
        "photo-1509695507497-903c140c43b0", "photo-1511556532299-8f662fc26c06",
        "photo-1473496169904-658ba7c44d8a", "photo-1502680390469-be75c86b636f",
        "photo-1577803645773-f96470509666", "photo-1512410751373-cfb4a9ef13f1"
    ],
    "kitchen": [
        "photo-1584269600464-37b1b58a9fe7", "photo-1599940824399-b87987ceb72a",
        "photo-1506368249639-73a05d6f6488", "photo-1574656562475-323be059f77f",
        "photo-1588854337236-6889d631faa8", "photo-1610557892470-7661873ee99d",
        "photo-1600585154340-be6161a56a0c", "photo-1556910103-1c02745aae4d",
        "photo-1610701596007-11502861dcfa", "photo-1608354586889-be75c86b636f"
    ],
    "home decor": [
        "photo-1513519245088-0e12902e5a38", "photo-1540518614846-7eded433c457",
        "photo-1583847268964-b28dc8f51f92", "photo-1531835551805-16d864c8d311",
        "photo-1600121848594-d8644e57abab", "photo-1606744824163-985d376605aa",
        "photo-1602872030219-cbf948a2609c", "photo-1617103996702-96ff29b1c467",
        "photo-1519710164239-da123dc03ef4", "photo-1594026112284-02bb6f3352fe"
    ],
    "furniture": [
        "photo-1586023492125-27b2c045efd7", "photo-1493663284031-b7e3aefcae8e",
        "photo-1505691938895-1758d7feb511", "photo-1532372320978-9b4d6a3a854c",
        "photo-1592078615290-033ee584e267", "photo-1618221195710-dd6b41faaea6",
        "photo-1581428982868-e410dd047a90", "photo-1544030288-e6e6108867f6",
        "photo-1538688525198-9b88f6f53126", "photo-1555041469-a586c61ea9bc"
    ],
    "fitness": [
        "photo-1517838277536-f5f99be501cd", "photo-1601925260368-ae2f83cf8b7f",
        "photo-1599058917212-d750089bc07e", "photo-1518310383802-640c2de311b2",
        "photo-1571019613454-1cb2f99b2d8b", "photo-1541534741688-6078c6bfb5c5",
        "photo-1584735935682-2f2b69dff9d2", "photo-1534438327276-14e5300c3a48",
        "photo-1605296867304-46d5465a25f1", "photo-1571019613454-1cb2f99b2d8b"
    ],
    "perfumes": [
        "photo-1541643600914-78b084683601", "photo-1594035910387-fea47794261f",
        "photo-1523293182086-7651a899d37f", "photo-1592945403244-b3fbafd7f539",
        "photo-1615397349754-cfa2066a298e", "photo-1616949755610-8c9bbc08f138",
        "photo-1547887537-6158d64c35b3", "photo-1605651260664-52643a6d1a93",
        "photo-1588405748373-122b2321bc31", "photo-1630573133526-8d090e0269af"
    ],
    "jewelry": [
        "photo-1599643478518-a784e5dc4c8f", "photo-1605100804763-247f67b3557e",
        "photo-1535632066927-ab7c9ab60908", "photo-1617038260897-41a1f14a8ca0",
        "photo-1602751584552-8ba73aad10e1", "photo-1598560917505-59a3ad559071"
    ]
}

def get_diverse_unsplash_image(p_id: str, name: str, category: str) -> str:
    import hashlib
    h = int(hashlib.md5(f"{p_id}_{name}".encode("utf-8")).hexdigest(), 16)
    cat_key = str(category).lower()
    if cat_key == "accessories":
        cat_key = "apparel"
    elif cat_key not in UNSPLASH_POOL:
        cat_key = "apparel"
    pool = UNSPLASH_POOL[cat_key]
    photo_id = pool[h % len(pool)]
    return f"https://images.unsplash.com/{photo_id}?w=600&q=80"

def validate_url_concurrent(url, headers, timeout=4):
    if not url or not url.startswith("http"):
        return False
    url_lower = url.lower()
    # Skip validation for Google Searches or homepages
    if "google.com" in url_lower or "google.in" in url_lower:
        return True
    
    for hp in BRAND_HOME_PAGES.values():
        if url.strip("/").lower() == hp.strip("/").lower():
            return True
            
    try:
        r = requests.head(url, headers=headers, timeout=timeout, allow_redirects=True)
        # Lenient check: Only mark invalid if it strictly returns 404.
        # Rate limits (403, 429, etc.) mean the page exists but blocked the head check.
        if r.status_code == 404:
            r_get = requests.get(url, headers=headers, timeout=timeout, stream=True, allow_redirects=True)
            return r_get.status_code != 404
        return True
    except Exception as e:
        # If it's a DNS resolution error, it's invalid.
        # Timeout or other network glitches shouldn't break the URL.
        err_str = str(e).lower()
        if "failed to resolve" in err_str or "nameresolutionerror" in err_str or "getaddrinfo failed" in err_str:
            return False
        return True

def clean_and_sanitize_urls(products: list) -> list:
    print("Checking and fixing broken URLs concurrently...")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    
    # Pre-resolve homepages
    def get_homepage(brand_name):
        bn = brand_name.strip().lower()
        for k, url in BRAND_HOME_PAGES.items():
            if k in bn or bn in k:
                return url
        return "https://www.snitch.co.in" # absolute fallback

    # Check unique urls concurrently to save network overhead
    urls_to_check = list(set([p["productUrl"] for p in products]))
    
    results = {}
    with ThreadPoolExecutor(max_workers=30) as executor:
        futures = {executor.submit(validate_url_concurrent, url, headers): url for url in urls_to_check}
        for fut in as_completed(futures):
            url = futures[fut]
            try:
                results[url] = fut.result()
            except Exception:
                results[url] = True # Default to True on thread error to avoid false positive homepage fallbacks

    fixed_count = 0
    for p in products:
        p_url = p["productUrl"]
        # Normalize snitch.com to snitch.co.in if it redirects or fails
        if "snitch.com" in p_url:
            p_url_new = p_url.replace("snitch.com", "snitch.co.in")
            p["productUrl"] = p_url_new
            p_url = p_url_new
            
        is_valid = results.get(p_url, True)
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
            "imageUrl": get_diverse_unsplash_image(f"pa{str(idx).zfill(5)}", clean_name, mapped_cat),
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
            
        name = str(row.get("product_name", "Product"))
        image_url = get_diverse_unsplash_image(f"pi{str(idx).zfill(5)}", name, mapped_cat)
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

    # Clean flixcart image URLs which are hotlink protected
    image_url = p.get("imageUrl", "")
    if "flixcart.com" in image_url or "rukminim" in image_url:
        cat_lower = str(p.get("category", "")).lower()
        images_map = {
            "apparel": "https://images.unsplash.com/photo-1523381210434-271e8be1f52b?w=600&q=80",
            "footwear": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600&q=80",
            "skincare": "https://images.unsplash.com/photo-1556228720-195a672e8a03?w=600&q=80",
            "audio": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&q=80",
            "watches": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&q=80",
            "bags": "https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=600&q=80",
            "eyewear": "https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=600&q=80",
            "kitchen": "https://images.unsplash.com/photo-1584269600464-37b1b58a9fe7?w=600&q=80",
            "home decor": "https://images.unsplash.com/photo-1513519245088-0e12902e5a38?w=600&q=80",
            "furniture": "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=600&q=80",
            "electronics": "https://images.unsplash.com/photo-1498049794561-7780e7231661?w=600&q=80",
        }
        p["imageUrl"] = images_map.get(cat_lower, images_map["apparel"])

    # Clean madeInIndia
    p["madeInIndia"] = bool(p.get("madeInIndia", True))

    if not p.get("imageUrl") or p["imageUrl"].strip() == "":
        p["imageUrl"] = get_diverse_unsplash_image(p["id"], p["name"], p["category"])

    return p

def main():
    print("==========================================")
    print("DesiFinds Database Expansion & Ingestion (with Live Repair)")
    print("==========================================")
    
    # 1. Load products_real_india_brands.json (verified products)
    base_file = "C:/Users/Bhagya B/Downloads/products_real_india_brands.json"
    with open(base_file, "r", encoding="utf-8") as f:
        base_products = json.load(f)
    print(f"Loaded {len(base_products)} base products from products_real_india_brands.json")
    
    # 2. Scrape live Shopify stores to repair broken base product images & links
    from backend.scrapers.brand_scrapers.shopify_scraper import ShopifyScraper
    from concurrent.futures import ThreadPoolExecutor, as_completed
    
    live_shopify_brands = {
        "snitch": "https://www.snitch.co.in",
        "rare rabbit": "https://thehouseofrare.com",
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
        "borosil": "https://myborosil.com",
        "giva": "https://www.giva.co",
        "bella vita": "https://bellavitaorganic.com",
        "wonderchef": "https://www.wonderchef.com"
    }
    
    def scrape_brand_live(brand_name, brand_url):
        try:
            print(f"Scraping live products from {brand_name} ({brand_url})...")
            scraper = ShopifyScraper(brand_name, brand_url)
            # Scrape up to 50 items per brand to find good replacements
            return brand_name.lower(), scraper.scrape(limit=50)
        except Exception as e:
            print(f"Failed live scrape for {brand_name}: {e}")
            return brand_name.lower(), []

    print("\nStarting concurrent scraping of Shopify brands to repair database...")
    scraped_live = {}
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(scrape_brand_live, name, url): name for name, url in live_shopify_brands.items()}
        for fut in as_completed(futures):
            brand_key, prods = fut.result()
            scraped_live[brand_key] = prods
            print(f"   Fetched {len(prods)} live products for {brand_key}")

    print("\nRepairing base products...")
    repaired_base_products = []
    used_live_products = set() # Track to avoid duplicate assignments
    
    # We will build a helper lookup for fuzzy matching
    def normalize_name(n):
        return re.sub(r"[^\w\s]", "", n.lower()).strip()
        
    for p in base_products:
        brand = p["brand"]
        brand_key = brand.lower()
        
        # If it's a live brand, let's try to match it or replace it with a live product
        if brand_key in live_shopify_brands and scraped_live.get(brand_key):
            live_pool = scraped_live[brand_key]
            norm_name = normalize_name(p["name"])
            
            # A. Try to find direct match
            matched_p = None
            for lp in live_pool:
                lp_key = f"{brand_key}_{lp['name']}"
                if lp_key in used_live_products:
                    continue
                lp_norm = normalize_name(lp["name"])
                if lp_norm == norm_name or lp_norm in norm_name or norm_name in lp_norm:
                    matched_p = lp
                    used_live_products.add(lp_key)
                    break
            
            # B. If no direct match, pick the first unused live product from this brand to replace it!
            if not matched_p:
                for lp in live_pool:
                    lp_key = f"{brand_key}_{lp['name']}"
                    if lp_key not in used_live_products:
                        matched_p = lp
                        used_live_products.add(lp_key)
                        break
            
            if matched_p:
                # Copy live product metadata but preserve rating/reviewCount if live ones are empty
                p["name"] = matched_p["name"]
                p["productUrl"] = matched_p["productUrl"]
                p["imageUrl"] = matched_p["imageUrl"] or get_diverse_unsplash_image(p["id"], matched_p["name"], p["category"])
                p["price"] = matched_p["price"]
                p["originalPrice"] = matched_p["originalPrice"] or matched_p["price"]
                if matched_p.get("description"):
                    p["description"] = matched_p["description"]
                if matched_p.get("materials"):
                    p["materials"] = matched_p["materials"]
                if matched_p.get("tags"):
                    p["tags"] = matched_p["tags"]
                # Regenerate review summary and badges
                p["badges"] = extract_badges(p)
                p["reviewSummary"] = generate_unique_review_summary(p)
                repaired_base_products.append(p)
                continue

        # If it is not a live brand OR no live products were retrieved/available:
        # We keep the base product but repair its imageUrl/productUrl if broken
        image_url = p.get("imageUrl", "")
        # If image returns 404 on Shopify, replace with diverse Unsplash image
        if "cdn.shopify.com" in image_url or not image_url:
            p["imageUrl"] = get_diverse_unsplash_image(p["id"], p["name"], p["category"])
            
        # Fix snitch.com to snitch.co.in or rarerabbit.in to thehouseofrare.com in URLs
        p_url = p.get("productUrl", "")
        if "snitch.com" in p_url:
            p["productUrl"] = p_url.replace("snitch.com", "snitch.co.in")
        elif "rarerabbit.in" in p_url:
            p["productUrl"] = p_url.replace("rarerabbit.in", "thehouseofrare.com")
            
        p["badges"] = extract_badges(p)
        repaired_base_products.append(p)

    print(f"Successfully repaired {len(repaired_base_products)} base products.")
    
    # 3. Parse external datasets
    amazon_products = parse_amazon_dataset()
    inr_products = parse_local_inr_dataset()
    
    # 4. Consolidate and clean
    combined = repaired_base_products + amazon_products + inr_products
    print(f"Consolidated total products before deduplication: {len(combined)}")
    
    # 5. Deduplicate
    deduped = Deduplicator.deduplicate(combined)
    print(f"Deduplicated to {len(deduped)} products.")
    
    # 6. URL validation & link fixing (lenient validator)
    sanitized = clean_and_sanitize_urls(deduped)
    
    # 7. Re-generate IDs to ensure unique sequential order and clean types
    for idx, p in enumerate(sanitized):
        p = sanitize_product_types(p)
        p["id"] = f"p{str(idx + 1).zfill(5)}"
        sanitized[idx] = p
        
    # 8. Enrich brand_info.py with any newly added brands
    enrich_brand_info_py()
    
    # 9. Save back to all three paths
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
