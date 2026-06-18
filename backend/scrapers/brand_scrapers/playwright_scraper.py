from typing import List, Dict, Any
from playwright.sync_api import sync_playwright
from backend.scrapers.brand_scrapers.base_scraper import BaseScraper

class PlaywrightScraper(BaseScraper):
    """
    Playwright-based scraper for dynamic React/SPA websites.
    """
    def __init__(self, brand_name: str, brand_url: str, selectors: Dict[str, str], collection_paths: List[str]):
        super().__init__(brand_name, brand_url)
        self.selectors = selectors
        self.collection_paths = collection_paths

    def scrape(self, limit: int = 10) -> List[Dict[str, Any]]:
        scraped_items = []
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                # Navigate to collection paths to discover and extract products
                for path in self.collection_paths:
                    full_url = f"{self.brand_url.rstrip('/')}/{path.lstrip('/')}"
                    print(f"[{self.brand_name}] Navigating to {full_url}...")
                    
                    try:
                        page.goto(full_url, wait_until="networkidle", timeout=30000)
                        
                        # Wait for the product card selector to appear
                        card_sel = self.selectors.get("product_card")
                        if card_sel:
                            page.wait_for_selector(card_sel, timeout=10000)
                            
                        # Extract cards
                        cards = page.query_selector_all(card_sel)
                        print(f"[{self.brand_name}] Found {len(cards)} products on page.")
                        
                        for card in cards[:limit]:
                            name = ""
                            name_sel = self.selectors.get("name")
                            if name_sel:
                                name_el = card.query_selector(name_sel)
                                if name_el:
                                    name = name_el.inner_text().strip()
                                    
                            if not name:
                                continue
                                
                            price = 0.0
                            price_sel = self.selectors.get("price")
                            if price_sel:
                                price_el = card.query_selector(price_sel)
                                if price_el:
                                    price_text = price_el.inner_text().strip()
                                    # Extract numbers
                                    digits = "".join(c for c in price_text if c.isdigit() or c == ".")
                                    try:
                                        price = float(digits)
                                    except ValueError:
                                        pass
                                        
                            product_url = self.brand_url
                            link_sel = self.selectors.get("link")
                            if link_sel:
                                link_el = card.query_selector(link_sel)
                                if link_el:
                                    href = link_el.get_attribute("href")
                                    if href:
                                        if href.startswith("/"):
                                            product_url = f"{self.brand_url.rstrip('/')}{href}"
                                        else:
                                            product_url = href
                                            
                            image_url = ""
                            img_sel = self.selectors.get("image")
                            if img_sel:
                                img_el = card.query_selector(img_sel)
                                if img_el:
                                    image_url = img_el.get_attribute("src") or img_el.get_attribute("data-src") or ""
                                    if image_url.startswith("//"):
                                        image_url = "https:" + image_url
                                        
                            # Stub tags, materials, and categories
                            scraped_items.append({
                                "brand": self.brand_name,
                                "name": name,
                                "description": f"Premium {name} by {self.brand_name}.",
                                "category": "Apparel", # Will be normalized in master pipeline
                                "tags": [],
                                "materials": [],
                                "price": price,
                                "originalPrice": None,
                                "rating": 4.5, # Default value if dynamic review extraction omitted
                                "reviewCount": 100,
                                "productUrl": product_url,
                                "imageUrl": image_url,
                                "brandUrl": self.brand_url,
                                "reviewSummary": "",
                                "madeInIndia": True,
                                "badges": []
                            })
                            
                            if len(scraped_items) >= limit:
                                break
                    except Exception as e:
                        print(f"[{self.brand_name}] Error scraping collection {full_url}: {e}")
                        
                    if len(scraped_items) >= limit:
                        break
                        
                browser.close()
        except Exception as e:
            print(f"[{self.brand_name}] Playwright initialization error: {e}")
            
        return scraped_items
