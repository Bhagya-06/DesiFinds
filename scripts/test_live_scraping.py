import sys
import os
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)
sys.path.append(os.path.join(PROJECT_ROOT, "backend"))

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
        products = scraper.scrape(limit=50)
        return name, products
    except Exception as e:
        return name, []

print("Starting concurrent scrape of Shopify brands...")
results = {}
with ThreadPoolExecutor(max_workers=15) as executor:
    futures = {executor.submit(scrape_brand, name, url): name for name, url in brand_urls.items()}
    for fut in as_completed(futures):
        name = futures[fut]
        brand, products = fut.result()
        results[brand] = products
        print(f"Scraped {len(products)} products from {brand}")

total = sum(len(p) for p in results.values())
print(f"Total products scraped: {total}")
