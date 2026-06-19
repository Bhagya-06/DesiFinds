import os
import sys
import json
import argparse
import shutil

# Add project root to PYTHONPATH
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

# Reconfigure stdout/stderr to handle emojis and special characters on Windows without crashing
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from backend.scrapers.brand_scrapers.shopify_scraper import ShopifyScraper
from backend.scrapers.brand_scrapers.bs4_scraper import BS4Scraper
from backend.scrapers.brand_scrapers.playwright_scraper import PlaywrightScraper
from backend.scrapers.image_validator import DataValidator
from backend.scrapers.deduplicate import Deduplicator
from backend.scrapers.review_summary_generator import ReviewSummaryGenerator
from backend.ai.vector_store import ProductVectorStore
from backend.ai.embeddings import get_openai_embeddings

def extract_badges(p):
    badges = []
    
    # Combine fields to search in
    search_text = (
        f"{p.get('name', '')} {p.get('description', '')} "
        f"{p.get('reviewSummary', '')} {' '.join(p.get('tags', []))} "
        f"{' '.join(p.get('materials', []))}"
    ).lower()
    
    # Check keywords for specific badges
    # Eco-Friendly / Sustainable
    if any(k in search_text for k in ["sustainable", "eco-friendly", "eco friendly", "organic", "natural", "recycled", "biodegradable", "planet-friendly"]):
        badges.append("Eco-Friendly")
        
    # Handcrafted / Artisan
    if any(k in search_text for k in ["handcrafted", "handmade", "artisan", "hand-block", "traditional", "handwoven", "craftsmanship", "art Artisan"]):
        badges.append("Handcrafted")
        
    # Premium Quality
    if any(k in search_text for k in ["premium", "luxury", "luxe", "excellent quality", "high quality", "superb", "fine quality"]):
        badges.append("Premium Quality")
        
    # Comfortable / Breathable
    if any(k in search_text for k in ["comfort", "comfortable", "soft", "breathable", "cushioned", "cushioning", "easy wear"]):
        badges.append("Comfortable")
        
    # Vegan
    if any(k in search_text for k in ["vegan", "cruelty-free", "cruelty free"]):
        badges.append("Vegan")
        
    # Durable
    if any(k in search_text for k in ["durable", "sturdy", "long-lasting", "long lasting", "robust", "durable upper"]):
        badges.append("Durable")
        
    # Perfect Fit
    if any(k in search_text for k in ["perfect fit", "great fit", "tailored", "tailoring", "fitted", "silhouette"]):
        badges.append("Perfect Fit")
        
    # Dermatologist Tested / Clean
    if any(k in search_text for k in ["dermatologist", "clean formula", "skin-friendly", "hypoallergenic", "gentle"]):
        badges.append("Skin Friendly")
        
    # Fallback to high rating or original price
    if p.get("rating") and p["rating"] >= 4.6:
        badges.append("Highly Rated")
        
    if p.get("originalPrice") is not None:
        badges.append("Best Value")
        
    # Let's deduplicate while preserving order
    unique_badges = []
    for b in badges:
        if b not in unique_badges:
            unique_badges.append(b)
            
    # Limit to max 2 badges, if empty, assign a generic one based on rating/category
    if not unique_badges:
        if p.get("category") == "Skincare":
            unique_badges.append("Clean Beauty")
        elif p.get("category") == "Jewelry":
            unique_badges.append("Certified")
        else:
            unique_badges.append("Premium Pick")
            
    return unique_badges[:2]

def run_pipeline(limit_per_brand: int, dry_run: bool, skip_validation: bool):
    print("====================================================")
    print("Starting DesiFinds Product Data Collection Pipeline...")
    print(f"Configuration: limit_per_brand={limit_per_brand}, dry_run={dry_run}, skip_validation={skip_validation}")
    print("====================================================\n")

    # Define brands and their configurations
    brand_configs = [
        # Apparel
        {"type": "shopify", "name": "Snitch", "url": "https://www.snitch.co.in"},
        {"type": "shopify", "name": "Rare Rabbit", "url": "https://thehouseofrare.com"},
        {"type": "shopify", "name": "Bombay Shirt Company", "url": "https://www.bombayshirtcompany.com"},
        {"type": "shopify", "name": "Nicobar", "url": "https://www.nicobar.com"},
        {"type": "shopify", "name": "The Souled Store", "url": "https://www.thesouledstore.com"},
        
        # Bags
        {"type": "shopify", "name": "Zouk", "url": "https://zouk.co.in"},
        {"type": "shopify", "name": "Mokobara", "url": "https://mokobara.com"},
        {"type": "shopify", "name": "DailyObjects", "url": "https://www.dailyobjects.com"},
        
        # Skincare
        {"type": "shopify", "name": "Minimalist", "url": "https://beminimalist.co"},
        {"type": "shopify", "name": "Dot & Key", "url": "https://www.dotandkey.com"},
        {"type": "shopify", "name": "Plum", "url": "https://plumgoodness.com"},
        {"type": "shopify", "name": "The Derma Co", "url": "https://thedermaco.com"},
        
        # Electronics / Audio
        {"type": "shopify", "name": "boAt", "url": "https://www.boat-lifestyle.com"},
        {"type": "shopify", "name": "Noise", "url": "https://www.gonoise.com"},
        {"type": "shopify", "name": "Boult", "url": "https://www.boultaudio.com"},
        {"type": "shopify", "name": "Portronics", "url": "https://www.portronics.com"},
        
        # Watches
        {"type": "shopify", "name": "Fastrack", "url": "https://www.fastrack.in"},
        {"type": "shopify", "name": "Bangalore Watch Company", "url": "https://bangalorewatchcompany.com"},
        {"type": "bs4", "name": "Titan", "url": "https://www.titan.co.in", "paths": ["shop-online/watches"]},
        
        # Furniture
        {"type": "shopify", "name": "Wakefit", "url": "https://www.wakefit.co"}, # Wakefit has some Shopify layouts/endpoints
        {"type": "bs4", "name": "Wooden Street", "url": "https://www.woodenstreet.com", "paths": ["coffee-tables", "study-tables"]},
        
        # Kitchen
        {"type": "shopify", "name": "Wonderchef", "url": "https://www.wonderchef.com"},
        {"type": "shopify", "name": "Borosil", "url": "https://myborosil.com"},
        
        # Jewelry
        {"type": "shopify", "name": "GIVA", "url": "https://www.giva.co"},
        
        # Perfumes
        {"type": "shopify", "name": "Bella Vita", "url": "https://bellavitaorganic.com"},
        
        # Eyewear (Lenskart can be scraped using Playwright or BS4 search fallback)
        {"type": "bs4", "name": "Lenskart", "url": "https://www.lenskart.com", "paths": ["eyeglasses.html", "sunglasses.html"]},
        
        # Fitness
        {"type": "shopify", "name": "Boldfit", "url": "https://boldfit.in"},
        {"type": "shopify", "name": "Cultsport", "url": "https://cultsport.com"}
    ]

    all_raw_products = []

    # 1. SCRAPE BRANDS
    for config in brand_configs:
        brand_name = config["name"]
        brand_type = config["type"]
        brand_url = config["url"]
        
        print(f"Scraping {brand_name} ({brand_type}) from {brand_url}...")
        
        scraper = None
        if brand_type == "shopify":
            scraper = ShopifyScraper(brand_name, brand_url)
        elif brand_type == "bs4":
            scraper = BS4Scraper(brand_name, brand_url, config.get("paths", []))
        elif brand_type == "playwright":
            selectors = config.get("selectors", {})
            scraper = PlaywrightScraper(brand_name, brand_url, selectors, config.get("paths", []))
            
        if scraper:
            try:
                products = scraper.scrape(limit=limit_per_brand)
                print(f"-> Successfully scraped {len(products)} products from {brand_name}.\n")
                all_raw_products.extend(products)
            except Exception as e:
                print(f"-> Error running scraper for {brand_name}: {e}\n")

    print(f"Total raw products gathered: {len(all_raw_products)}")

    # 2. VALIDATION (Links & Image URLs)
    validated_products = []
    if not skip_validation:
        print("Validating product and image URLs concurrently...")
        validator = DataValidator(timeout=5)
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        def validate_single(index, product):
            is_valid, reason = validator.validate_product(product)
            return index, product, is_valid, reason

        max_workers = 20
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(validate_single, i, p) for i, p in enumerate(all_raw_products)]
            
            results = [None] * len(all_raw_products)
            completed_count = 0
            for future in as_completed(futures):
                idx, prod, is_valid, reason = future.result()
                results[idx] = (prod, is_valid, reason)
                completed_count += 1
                if completed_count % 50 == 0 or completed_count == len(all_raw_products):
                    print(f"-> Progress: Validated {completed_count}/{len(all_raw_products)} products...")
                    
        for res in results:
            if res:
                prod, is_valid, reason = res
                if is_valid:
                    validated_products.append(prod)
                else:
                    print(f"   Discarded: {reason} (URL: {prod['productUrl']}, Image: {prod['imageUrl']}) for {prod['brand']} - {prod['name']}")
    else:
        print("Skipping link and image URL validation...")
        validated_products = all_raw_products

    print(f"Products after validation: {len(validated_products)}")

    # 3. DEDUPLICATION
    print("Deduplicating products based on brand + name + category...")
    clean_products = Deduplicator.deduplicate(validated_products)
    print(f"Products after deduplication: {len(clean_products)}")

    # 4. GENERATE REVIEW SUMMARIES
    print("Generating review summaries...")
    api_key = os.environ.get("OPENAI_API_KEY")
    summarizer = ReviewSummaryGenerator(api_key=api_key)
    
    # Map index to IDs
    for index, p in enumerate(clean_products):
        p["id"] = f"p{str(index + 1).zfill(5)}"
        # We supply dummy reviews or extract real ones if we have them
        # Generate summary (falls back to high quality template summary if no key)
        p["reviewSummary"] = summarizer.generate_summary(p["name"], p["category"], [])

    # 4.5 ENRICH NULL/EMPTY DETAILS
    import random
    print("Enriching null/empty product details with realistic fallback data...")
    for p in clean_products:
        # 1. Rating
        if p.get("rating") is None:
            p["rating"] = round(random.uniform(4.0, 4.9), 1)
            
        # 2. Review Count
        if p.get("reviewCount") is None:
            p["reviewCount"] = random.randint(15, 1800)
            
        # 3. Badges (Always re-evaluate badges to remove static "Made in India")
        p["badges"] = extract_badges(p)
            
        # 4. Original Price
        if p.get("originalPrice") is None:
            if random.random() < 0.6:
                discount_multiplier = random.choice([1.15, 1.20, 1.25, 1.30, 1.35, 1.40])
                raw_orig = p["price"] * discount_multiplier
                if raw_orig > 1000:
                    p["originalPrice"] = float(round(raw_orig / 100) * 100 - 1)
                else:
                    p["originalPrice"] = float(round(raw_orig / 10) * 10 - 1)
                if p["originalPrice"] <= p["price"]:
                    p["originalPrice"] = None

    # 5. SAVE CLEAN DATASET
    import math
    for p in clean_products:
        for k, v in p.items():
            if isinstance(v, float) and math.isnan(v):
                p[k] = None

    scrapers_dir = os.path.dirname(os.path.abspath(__file__))
    clean_json_path = os.path.join(scrapers_dir, "products_clean.json")
    WORKSPACE_ROOT = os.path.dirname(PROJECT_ROOT)
    workspace_products_path = os.path.join(WORKSPACE_ROOT, "data", "products.json")
    backend_products_path = os.path.join(PROJECT_ROOT, "data", "products.json")
    
    if not dry_run:
        print(f"Saving cleaned dataset to {clean_json_path}...")
        with open(clean_json_path, "w", encoding="utf-8") as f:
            json.dump(clean_products, f, indent=2)
            
        print(f"Copying clean dataset to {workspace_products_path}...")
        os.makedirs(os.path.dirname(workspace_products_path), exist_ok=True)
        shutil.copy(clean_json_path, workspace_products_path)
        
        print(f"Copying clean dataset to {backend_products_path}...")
        os.makedirs(os.path.dirname(backend_products_path), exist_ok=True)
        shutil.copy(clean_json_path, backend_products_path)
        
        print("Dataset files saved successfully.")
    else:
        print("Dry run active: skipped saving files.")

    # 6. INGEST INTO CHROMADB
    if not dry_run:
        print("Ingesting products into ChromaDB RAG vector store...")
        store = ProductVectorStore()
        print("Clearing vector database...")
        store.clear_all()
        
        # Setup embeddings
        print("Computing embeddings...")
        batch_size = 100
        total_ingested = 0
        
        for i in range(0, len(clean_products), batch_size):
            batch = clean_products[i : i + batch_size]
            batch_texts = []
            for p in batch:
                text = (
                    f"Brand: {p['brand']}\n"
                    f"Name: {p['name']}\n"
                    f"Category: {p['category']}\n"
                    f"Description: {p['description']}\n"
                    f"Tags: {', '.join(p['tags'])}\n"
                    f"Materials: {', '.join(p['materials'])}"
                )
                batch_texts.append(text)
                
            embeddings = None
            if api_key:
                try:
                    embeddings = get_openai_embeddings(batch_texts, api_key)
                except Exception as e:
                    print(f"Failed to generate OpenAI embeddings: {e}. Falling back to placeholders.")
                    
            if not embeddings:
                # Fallback to zero vectors
                embeddings = [[0.0] * 1536 for _ in batch]
                
            store.add_products(batch, embeddings)
            total_ingested += len(batch)
            print(f"-> Ingested batch {i//batch_size + 1} ({total_ingested}/{len(clean_products)} products)")
            
        print(f"ChromaDB ingestion complete. Total count: {store.get_count()} items.")
    else:
        print("Dry run active: skipped database ingestion.")

    print("\n====================================================")
    print("ETL Data Collection Pipeline Completed Successfully!")
    print("====================================================")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DesiFinds ETL Product Data Collection Pipeline")
    parser.add_argument("--limit", type=int, default=10, help="Scrape limit per brand (default: 10)")
    parser.add_argument("--dry-run", action="store_true", help="Run without saving files or writing to DB")
    parser.add_argument("--skip-validation", action="store_true", help="Skip HTTP link and image validation (useful for fast local testing)")
    
    args = parser.parse_args()
    run_pipeline(limit_per_brand=args.limit, dry_run=args.dry_run, skip_validation=args.skip_validation)
