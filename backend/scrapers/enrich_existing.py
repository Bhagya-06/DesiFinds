import os
import json
import random

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

def generate_unique_review_summary(p):
    brand = p.get("brand", "this brand")
    name = p.get("name", "product")
    cat = p.get("category", "")
    
    # 1. Select a random opening template
    openings = [
        f"Customers praise the premium build and elegant design of this {name} by {brand}.",
        f"Many reviewers highlight the high durability and excellent craftsmanship of this {name}.",
        f"Users love how lightweight, stylish, and premium this {name} feels for the price.",
        f"Highly rated for its premium materials and perfect build quality by {brand}.",
        f"Buyers are highly impressed by the performance and elegant design of this {name}.",
        f"Reviewers frequently mention the excellent material quality and soft feel of this {name}.",
        f"Customers report outstanding comfort and premium aesthetic detail for this {name}."
    ]
    opening = random.choice(openings)
    
    # 2. Select a category-specific closing template
    closings = {
        "Apparel": [
            "Ideal for daily or smart-casual wear.",
            "Perfect fit that holds its shape nicely after multiple washes.",
            "A clean silhouette that pairs easily with any outfit.",
            "Feels incredibly soft and light against the skin."
        ],
        "Footwear": [
            "Provides superb cushioning and slip resistance for active use.",
            "Highly breathable and great for long walking sessions.",
            "Extremely comfortable with a very short break-in period.",
            "Sturdy sole design offers excellent support and durability."
        ],
        "Skincare": [
            "Highly gentle on sensitive skin and yields a healthy, natural glow.",
            "Provides great hydration that doesn't feel heavy or greasy.",
            "Provides visible improvement in skin texture within days.",
            "Absorbs quickly and leaves a fresh, clean finish."
        ],
        "Audio": [
            "Offers deep, punchy bass and crystal clear acoustics.",
            "Outstanding battery backup and quick bluetooth connectivity.",
            "A comfortable fit that blocks out ambient noise effectively.",
            "High-fidelity sound tuning that rivals luxury imported brands."
        ],
        "Watches": [
            "The minimalist design dial adds a highly sophisticated look.",
            "Crafted with a durable casing and premium strap.",
            "Highly versatile for both formal and casual settings.",
            "An elegant timepiece that keeps highly precise time."
        ],
        "Bags": [
            "Spacious compartments with sturdy zippers for daily commute.",
            "The vegan leather finish is very durable and water resistant.",
            "Perfect size for travel, daily office, or weekend trips.",
            "Distributes weight evenly and feels comfortable to carry."
        ],
        "Jewelry": [
            "Certified hallmarked silver that doesn't tarnish easily.",
            "Dainty, elegant design suitable for everyday minimalist styling.",
            "Receives numerous compliments for its beautiful sparkle.",
            "Very lightweight and sits comfortably for all-day wear."
        ],
        "Furniture": [
            "Robust solid wood build that is easy to assemble.",
            "Very sturdy, adding a modern clean aesthetic to the home.",
            "The ergonomic design makes it comfortable for long working hours.",
            "Solid craftsmanship ensures it will last for years to come."
        ],
        "Home Decor": [
            "Adds a rich artistic vibe and warm lighting to any room.",
            "Handcrafted details that make it feel unique and premium.",
            "Great craftsmanship that makes it a perfect housewarming gift.",
            "Vibrant, eye-catching textures that elevate local spaces."
        ],
        "Kitchen": [
            "Heats evenly and is exceptionally easy to clean.",
            "Ergonomic handle and durable body designed for daily cooking.",
            "Extremely practical, food-safe, and aesthetic kitchen addition.",
            "Corrosion-resistant steel that retains its premium polish."
        ],
        "Fitness": [
            "Offers excellent grip and doesn't slide during workouts.",
            "Sturdy construction that withstands heavy daily usage.",
            "Highly portable, making home workouts extremely convenient.",
            "Excellent build quality that supports progressive training."
        ],
        "Perfumes": [
            "The scent is long-lasting and receives frequent compliments.",
            "Sophisticated fragrance profile that smells clean and premium.",
            "A subtle, refreshing scent that is perfect for summer days.",
            "Excellent projection that lingers pleasantly throughout the day."
        ],
        "Eyewear": [
            "Reduces digital eye strain and is comfortable to wear.",
            "Flexible frame and clear lenses that offer sharp vision.",
            "Very lightweight, making it comfortable for all-day wear.",
            "Stylish design that suits multiple face shapes perfectly."
        ]
    }
    
    cat_closings = closings.get(cat, [
        "Highly recommended for daily use and great value.",
        "An excellent local alternative that beats imported brands.",
        "Offers superb performance and premium material feel.",
        "Designed to last and highly rated by buyers."
    ])
    closing = random.choice(cat_closings)
    
    return f"{opening} {closing}"

def enrich_existing():
    # Resolve paths
    scrapers_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.dirname(scrapers_dir)
    project_root = os.path.dirname(backend_dir)
    
    products_file = os.path.join(project_root, "data", "products.json")
    backend_products_file = os.path.join(backend_dir, "data", "products.json")
    clean_json_file = os.path.join(scrapers_dir, "products_clean.json")
    
    print(f"Loading products from: {products_file}")
    if not os.path.exists(products_file):
        print(f"Error: Products file not found at {products_file}")
        return
        
    with open(products_file, "r", encoding="utf-8") as f:
        products = json.load(f)
        
    print(f"Enriching {len(products)} products...")
    
    # Category fallback images
    fallback_images = {
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
    default_fallback = "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&q=80"
    
    for p in products:
        # 1. Rating
        if p.get("rating") is None or p.get("rating") == 0:
            p["rating"] = round(random.uniform(4.0, 4.9), 1)
            
        # 2. Review Count
        if p.get("reviewCount") is None or p.get("reviewCount") < 0:
            p["reviewCount"] = random.randint(15, 1800)
            
        # 3. Badges (Always re-evaluate badges to remove static "Made in India")
        p["badges"] = extract_badges(p)
            
        # 4. Original Price
        if p.get("originalPrice") is None or p.get("originalPrice") <= 0:
            # Set original price with 70% probability as discounted, else same as price
            if random.random() < 0.7:
                discount_multiplier = random.choice([1.15, 1.20, 1.25, 1.30, 1.35, 1.40])
                raw_orig = p["price"] * discount_multiplier
                if raw_orig > 1000:
                    p["originalPrice"] = float(round(raw_orig / 100) * 100 - 1)
                else:
                    p["originalPrice"] = float(round(raw_orig / 10) * 10 - 1)
                # Safeguard
                if p["originalPrice"] <= p["price"]:
                    p["originalPrice"] = float(p["price"])
            else:
                p["originalPrice"] = float(p["price"])
        
        # 5. Image URL validation
        if not p.get("imageUrl") or p.get("imageUrl").strip() == "":
            cat = p.get("category", "")
            p["imageUrl"] = fallback_images.get(cat, default_fallback)

        # 6. Generate a unique, product-specific review summary to prevent duplicates
        # Replace if it's missing or matches one of the static fallback templates from ReviewSummaryGenerator
        current_summary = p.get("reviewSummary", "")
        is_default_template = current_summary in [
            "Customers praise the exceptionally comfortable fabric, elegant tailoring, and perfect fit. Ideal for daily or smart-casual wear.",
            "Customers love the lightweight feel, breathable cushioning, and premium build. Needs a very short break-in period.",
            "Users report excellent absorption with visible improvements in skin texture and hydration within weeks. Highly gentle on sensitive skin.",
            "Listeners praise the deep punchy bass, crystal-clear treble, and long battery life. Offers incredible value compared to imported brands.",
            "Buyers highlight the elegant minimalist dial, robust casing, and premium strap craftsmanship. Perfect for formal and casual occasions.",
            "Customers love the spacious compartments, durable stitching, and premium finish. Ideal for daily commutes and travel.",
            "Customers praise the stunning sparkle, dainty design, and certified hallmark quality. Lightweight and comfortable for daily wear.",
            "Users highlight the robust solid wood build, easy assembly, and ergonomic comfort. Adds a clean modern aesthetic to rooms.",
            "Buyers love the rich artistic details, vibrant colors, and premium hand-painted craftsmanship. Highly recommended for gifting.",
            "Cooks praise the durable material quality, even heating, and ease of cleaning. Highly efficient for daily meal prep.",
            "Athletes highlight the excellent grip, high durability, and portable design. Great tool for home gym workouts.",
            "Customers love the rich long-lasting scent profile and sophisticated fragrance notes. Receives numerous compliments.",
            "Users report excellent lens clarity, robust hinges, and lightweight frame comfort. Effectively reduces digital screen eye strain.",
            ""
        ]
        if is_default_template or not current_summary:
            p["reviewSummary"] = generate_unique_review_summary(p)

    # Save back to all three paths
    for path in [products_file, backend_products_file, clean_json_file]:
        print(f"Saving to {path}...")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(products, f, indent=2)
            
    print("Enrichment complete successfully!")

if __name__ == "__main__":
    enrich_existing()
