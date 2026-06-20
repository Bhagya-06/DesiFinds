import json
import re

# Load base products
with open("C:/Users/Bhagya B/Downloads/products_real_india_brands.json", "r", encoding="utf-8") as f:
    base_products = json.load(f)

# Load scraped products (let's simulate the scraper)
# We can just scrape them or use the same code as test_live_scraping
# Let's see how many matches we can find if we normalize names

def normalize(name):
    name = name.lower()
    name = re.sub(r"[^\w\s]", "", name)
    name = " ".join(name.split())
    return name

# Let's run the actual scraping in a simple loop for this test
from concurrent.futures import ThreadPoolExecutor, as_completed
from backend.scrapers.brand_scrapers.shopify_scraper import ShopifyScraper

brand_urls = {
    "snitch": "https://www.snitch.co.in",
    "rare rabbit": "https://thehouseofrare.com",
    "bombay shirt company": "https://www.bombayshirtcompany.com",
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
    "fastrack": "https://www.fastrack.in",
    "bangalore watch company": "https://bangalorewatchcompany.com",
    "wakefit": "https://www.wakefit.co",
    "wonderchef": "https://www.wonderchef.com",
    "borosil": "https://myborosil.com",
    "giva": "https://www.giva.co",
    "bella vita": "https://bellavitaorganic.com",
    "cultsport": "https://cultsport.com"
}

def scrape_brand(name, url):
    try:
        scraper = ShopifyScraper(name, url)
        return name, scraper.scrape(limit=100) # get up to 100 to find more matches
    except Exception:
        return name, []

results = {}
with ThreadPoolExecutor(max_workers=15) as executor:
    futures = {executor.submit(scrape_brand, name, url): name for name, url in brand_urls.items()}
    for fut in as_completed(futures):
        brand, products = fut.result()
        results[brand.lower()] = products

# Create lookup
scraped_lookup = {} # (brand.lower(), normalized_name) -> product
for brand_name, products in results.items():
    for p in products:
        norm_name = normalize(p["name"])
        scraped_lookup[(brand_name, norm_name)] = p

# Let's match
matched = 0
not_matched = []

for bp in base_products:
    brand = bp["brand"].lower()
    norm_name = normalize(bp["name"])
    
    # Try exact match first
    match_prod = scraped_lookup.get((brand, norm_name))
    
    # Try fuzzy match if not found
    if not match_prod:
        # Check if any scraped product name is a substring or close
        for (b, n), p in scraped_lookup.items():
            if b == brand and (n in norm_name or norm_name in n):
                match_prod = p
                break
                
    if match_prod:
        matched += 1
    else:
        not_matched.append(bp)

print(f"Matched {matched} out of {len(base_products)}")
print(f"Not matched: {len(not_matched)}")
print("\nSample Not Matched:")
for p in not_matched[:15]:
    print(f"  Brand: {p['brand']}, Name: {p['name']}, Image: {p['imageUrl']}")
