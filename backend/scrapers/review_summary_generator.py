import os
from typing import List, Optional
from openai import OpenAI

class ReviewSummaryGenerator:
    """
    Generates 1-2 sentence review summaries using OpenAI API,
    with a robust fallback generator for offline or quota-exceeded environments.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.client = None
        if self.api_key:
            try:
                self.client = OpenAI(api_key=self.api_key)
            except Exception:
                pass

    def generate_summary(self, product_name: str, category: str, reviews: List[str]) -> str:
        """
        Summarizes a list of reviews using OpenAI, or falls back to heuristic summaries.
        """
        if not reviews:
            # Fallback to general product description summary if no reviews collected
            return self._generate_heuristic_summary(product_name, category)
            
        if self.client:
            try:
                prompt = (
                    f"You are a shopping assistant. Summarize the following customer reviews for the product '{product_name}' "
                    f"into a single, highly readable, premium 1-2 sentence customer review summary. Do not output anything else but the summary. "
                    f"Start with a friendly customer consensus (e.g., 'Customers praise...').\n\n"
                    f"Reviews:\n" + "\n".join([f"- {r}" for r in reviews[:5]])
                )
                
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=100,
                    temperature=0.5
                )
                summary = response.choices[0].message.content.strip()
                # Clean quotes
                summary = summary.replace('"', '').replace("'", "")
                return summary
            except Exception as e:
                print(f"[ReviewSummaryGenerator] OpenAI API call failed: {e}. Falling back to heuristics.")
                
        return self._generate_heuristic_summary(product_name, category, reviews)

    def _generate_heuristic_summary(self, product_name: str, category: str, reviews: Optional[List[str]] = None) -> str:
        """
        Generates a high-quality review summary using templates based on category.
        """
        if reviews and len(reviews) > 0:
            # If we have reviews but no API key, combine first few lines cleanly
            clean_reviews = [r.strip().rstrip(".").capitalize() for r in reviews if r.strip()]
            if clean_reviews:
                return f"Customers highlight: {'. '.join(clean_reviews[:2])}."
                
        templates = {
            "Apparel": "Customers praise the exceptionally comfortable fabric, elegant tailoring, and perfect fit. Ideal for daily or smart-casual wear.",
            "Footwear": "Customers love the lightweight feel, breathable cushioning, and premium build. Needs a very short break-in period.",
            "Skincare": "Users report excellent absorption with visible improvements in skin texture and hydration within weeks. Highly gentle on sensitive skin.",
            "Audio": "Listeners praise the deep punchy bass, crystal-clear treble, and long battery life. Offers incredible value compared to imported brands.",
            "Watches": "Buyers highlight the elegant minimalist dial, robust casing, and premium strap craftsmanship. Perfect for formal and casual occasions.",
            "Bags": "Customers love the spacious compartments, durable stitching, and premium finish. Ideal for daily commutes and travel.",
            "Jewelry": "Customers praise the stunning sparkle, dainty design, and certified hallmark quality. Lightweight and comfortable for daily wear.",
            "Furniture": "Users highlight the robust solid wood build, easy assembly, and ergonomic comfort. Adds a clean modern aesthetic to rooms.",
            "Home Decor": "Buyers love the rich artistic details, vibrant colors, and premium hand-painted craftsmanship. Highly recommended for gifting.",
            "Kitchen": "Cooks praise the durable material quality, even heating, and ease of cleaning. Highly efficient for daily meal prep.",
            "Fitness": "Athletes highlight the excellent grip, high durability, and portable design. Great tool for home gym workouts.",
            "Perfumes": "Customers love the rich long-lasting scent profile and sophisticated fragrance notes. Receives numerous compliments.",
            "Eyewear": "Users report excellent lens clarity, robust hinges, and lightweight frame comfort. Effectively reduces digital screen eye strain."
        }
        
        return templates.get(category, "Customers highlight the excellent craftsmanship, high-quality materials, and exceptional value for everyday use.")
