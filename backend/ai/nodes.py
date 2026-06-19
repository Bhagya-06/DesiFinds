import json
import os
import re
from typing import Dict, Any, List
from openai import OpenAI
from backend.ai.state import DiscoveryState
from backend.rag.retriever import ProductRetriever
from backend.ai.vector_store import ProductVectorStore
from langsmith import traceable

# Fallback keyword definitions for rule-based matching
CATEGORY_KEYWORDS = {
    "Apparel": ["shirt", "kurta", "tshirt", "t-shirt", "jeans", "trouser", "linen", "cotton", "denim", "jacket", "hoodie", "saree", "kurti", "ethnic", "formal", "dress", "blouse", "sherwani", "pant", "chino"],
    "Footwear": ["shoe", "sneaker", "chappal", "sandal", "boot", "runner", "trainer", "loafer", "derby", "oxford", "kolhapuri"],
    "Electronics": ["laptop", "phone", "tablet", "keyboard", "mouse", "speaker", "hub", "charger", "powerbank", "gadget", "smartwatch"],
    "Audio": ["headphone", "earphone", "earbud", "airpod", "tws", "neckband", "soundbar", "earpiece", "music"],
    "Watches": ["watch", "timepiece", "smartwatch", "fitbit", "analog", "digital"],
    "Skincare": ["moisturizer", "serum", "cleanser", "sunscreen", "face wash", "lotion", "cream", "toner", "mask", "spf", "niacinamide", "vitamin c"],
    "Bags": ["bag", "backpack", "handbag", "tote", "luggage", "suitcase", "trolley", "wallet", "purse", "sling"],
    "Jewelry": ["necklace", "ring", "earring", "bracelet", "jhumka", "kundan", "diamond", "gold", "silver", "pendant"],
    "Furniture": ["sofa", "chair", "table", "desk", "shelf", "wardrobe", "bed", "mattress", "couch", "cabinet"],
    "Home Decor": ["vase", "lamp", "rug", "curtain", "pillow", "cushion", "art", "plant", "planter", "painting", "candle"],
    "Kitchen": ["cooker", "pan", "pot", "kadai", "tawa", "blender", "mixer", "bottle", "container", "utensil"],
    "Fitness": ["mat", "dumbbell", "weight", "band", "yoga", "gym", "protein", "supplement", "kettlebell", "barbell"],
    "Perfumes": ["perfume", "fragrance", "cologne", "attar", "oud", "mist", "scent", "deodorant"],
    "Eyewear": ["sunglasses", "spectacles", "glasses", "frames", "lens", "optical"]
}

@traceable
def deconstructor_node(state: DiscoveryState) -> Dict[str, Any]:
    """
    Extract category, features, materials, style, price range and original brand.
    """
    query = state["query"]
    api_key = state.get("api_key")
    
    # 1. AI execution path
    if api_key:
        try:
            client = OpenAI(api_key=api_key)
            prompt = (
                "You are an expert product analyst. Deconstruct the following user query for an international product:\n"
                f"Query: {query}\n\n"
                "Respond strictly with a JSON object. Do not include markdown code block formatting or backticks. Format:\n"
                "{\n"
                '  "category": "One of Apparel, Footwear, Electronics, Audio, Watches, Skincare, Bags, Jewelry, Furniture, Home Decor, Kitchen, Fitness, Perfumes, Eyewear",\n'
                '  "features": ["list", "of", "features"],\n'
                '  "materials": ["list", "of", "materials"],\n'
                '  "price_range": "estimated price range in INR (e.g. ₹2000 - ₹5000)",\n'
                '  "aesthetic_style": "description of aesthetic style",\n'
                '  "original_brand": "detected brand name"\n'
                "}"
            )
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0
            )
            content = response.choices[0].message.content.strip()
            # Strip potential json fences
            content = re.sub(r"^```json\s*", "", content)
            content = re.sub(r"\s*```$", "", content)
            
            data = json.loads(content)
            
            return {
                "category": data.get("category", "Apparel"),
                "features": data.get("features", []),
                "materials": data.get("materials", []),
                "price_range": data.get("price_range", "₹1,000 – ₹5,000"),
                "aesthetic_style": data.get("aesthetic_style", "Classic casual"),
                "original_brand": data.get("original_brand", "International Brand"),
                "workflow_steps": [{
                    "name": "Product Deconstructor",
                    "status": "complete",
                    "output": f"AI identified: {data.get('category')} / Brand: {data.get('original_brand')}\nFeatures: {', '.join(data.get('features', []))}\nStyle: {data.get('aesthetic_style')}"
                }]
            }
        except Exception as e:
            print(f"Deconstructor node API error: {e}. Falling back to heuristics.")
            
    # 2. Heuristic fallback path
    lower = query.lower()
    detected_cat = "Apparel"
    max_m = 0
    for cat, keywords in CATEGORY_KEYWORDS.items():
        m = sum(1 for kw in keywords if kw in lower)
        if m > max_m:
            max_m = m
            detected_cat = cat
            
    # Extract features/materials
    feat_kw = ["linen", "cotton", "leather", "wool", "slim", "oversized", "wireless", "noise cancelling", "anc", "waterproof", "organic", "sustainable"]
    features = [f.capitalize() for f in feat_kw if f in lower]
    
    mat_kw = ["linen", "cotton", "leather", "wool", "silk", "polyester", "nylon", "bamboo", "polycarbonate", "denim"]
    materials = [m.capitalize() for m in mat_kw if m in lower]
    
    # Simple brand detection
    brands = ["zara", "h&m", "uniqlo", "nike", "adidas", "apple", "airpods", "sony", "bose", "logitech", "cerave", "dyson", "ikea", "ray-ban"]
    original_brand = "International Brand"
    for b in brands:
        if b in lower:
            original_brand = b.capitalize()
            break
            
    return {
        "category": detected_cat,
        "features": features,
        "materials": materials,
        "price_range": "₹1,000 – ₹4,000",
        "aesthetic_style": "Contemporary casual with minimalist details",
        "original_brand": original_brand,
        "workflow_steps": [{
            "name": "Product Deconstructor",
            "status": "complete",
            "output": f"Heuristics identified: {detected_cat} / Brand: {original_brand}\nFeatures: {', '.join(features) or 'general'}\nStyle: Contemporary"
        }]
    }

@traceable
def retriever_node(state: DiscoveryState) -> Dict[str, Any]:
    """
    Search product databases to fetch top matching alternatives.
    """
    vs = ProductVectorStore()
    retriever = ProductRetriever(vs)
    
    matches = retriever.retrieve_alternatives(
        query=state["query"],
        category=state["category"],
        features=state["features"],
        materials=state["materials"],
        api_key=state.get("api_key"),
        n_results=5
    )
    
    step_output = f"Retrieved {len(matches)} Indian alternatives from database."
    if matches:
        top_match = matches[0]
        step_output += f"\nTop Alternative match: {top_match['name']} by {top_match['brand']} ({int(top_match.get('similarity_score', 0.8)*100)}% match)"
        
    return {
        "matches": matches,
        "workflow_steps": state["workflow_steps"] + [{
            "name": "RAG Matcher",
            "status": "complete",
            "output": step_output
        }]
    }

@traceable
def reviewer_node(state: DiscoveryState) -> Dict[str, Any]:
    """
    Analyze customer reviews or summaries to compile structured pros and cons.
    """
    matches = state["matches"]
    api_key = state.get("api_key")
    reviews_analysis = {}
    
    for p in matches:
        p_id = p["id"]
        summary = p.get("reviewSummary", "Great quality product, highly recommended by users.")
        
        # 1. AI execution path
        if api_key:
            try:
                client = OpenAI(api_key=api_key)
                prompt = (
                    "You are a consumer research analyst. Analyze customer reviews/descriptions for this Indian alternative product:\n"
                    f"Name: {p['name']}\n"
                    f"Brand: {p['brand']}\n"
                    f"Description: {p['description']}\n"
                    f"Review Summary: {summary}\n\n"
                    "Respond strictly with a JSON object. Do not include markdown code block formatting. Format:\n"
                    "{\n"
                    '  "pros": ["list of 2-3 specific pros"],\n'
                    '  "cons": ["list of 1-2 specific cons"],\n'
                    '  "summary": "one sentence feedback summary"\n'
                    "}"
                )
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.0
                )
                content = response.choices[0].message.content.strip()
                content = re.sub(r"^```json\s*", "", content)
                content = re.sub(r"\s*```$", "", content)
                
                data = json.loads(content)
                reviews_analysis[p_id] = {
                    "pros": data.get("pros", ["Good quality", "Premium finish"]),
                    "cons": data.get("cons", ["Limited sizes"]),
                    "summary": data.get("summary", summary)
                }
                continue
            except Exception as e:
                print(f"Reviewer node API error for {p_id}: {e}. Falling back.")
                
        # 2. Heuristic fallback path
        pros = ["Excellent value for money", "Premium build quality"]
        if p["category"] == "Skincare":
            pros = ["Clean formulation", "Suits sensitive Indian skin"]
        elif p["category"] == "Apparel":
            pros = ["Breathable premium cotton", "Tailored fit"]
            
        reviews_analysis[p_id] = {
            "pros": pros,
            "cons": ["Only available online"],
            "summary": summary
        }
        
    return {
        "reviews_analysis": reviews_analysis,
        "workflow_steps": state["workflow_steps"] + [{
            "name": "Review Analyzer",
            "status": "complete",
            "output": f"Analyzed reviews for {len(matches)} alternatives.\nCompiled pros, cons, and feedback summaries."
        }]
    }

@traceable
def curator_node(state: DiscoveryState) -> Dict[str, Any]:
    """
    Formulate match scores, craftsmanship explanations, and price savings comparisons.
    """
    matches = state["matches"]
    query = state["query"]
    api_key = state.get("api_key")
    curation = {}
    
    for p in matches:
        p_id = p["id"]
        
        # 1. AI execution path
        if api_key:
            try:
                client = OpenAI(api_key=api_key)
                prompt = (
                    "You are a luxury curator and retail expert. Compare the international search query with this Indian alternative product:\n"
                    f"International Query: {query}\n"
                    f"Indian Product: {p['name']} by {p['brand']}\n"
                    f"Price: ₹{p['price']}\n"
                    f"Rating: {p['rating']}\n\n"
                    "Respond strictly with a JSON object. Do not include markdown code block formatting. Format:\n"
                    "{\n"
                    '  "match_score": integer between 50 and 99,\n'
                    '  "match_reason": "why this matches the international query",\n'
                    '  "craftsmanship": "explanation of craftsmanship or quality details",\n'
                    '  "value_prop": "better value explanation compared to the original"\n'
                    "}"
                )
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.0
                )
                content = response.choices[0].message.content.strip()
                content = re.sub(r"^```json\s*", "", content)
                content = re.sub(r"\s*```$", "", content)
                
                data = json.loads(content)
                curation[p_id] = {
                    "match_score": data.get("match_score", 85),
                    "match_reason": data.get("match_reason", f"High-quality local option matching {p['category']}"),
                    "craftsmanship": data.get("craftsmanship", "Handmade detailing and premium sourcing."),
                    "value_prop": data.get("value_prop", "Similar premium feel at a better local price.")
                }
                continue
            except Exception as e:
                print(f"Curator node API error for {p_id}: {e}. Falling back.")
                
        # 2. Heuristic fallback path
        # Derive match score from similarity score
        sim = p.get("similarity_score", 0.8)
        match_score = int(sim * 100)
        
        reasons = []
        if "Made in India" in p["badges"]:
            reasons.append("proudly made in India")
        if "Handcrafted" in p["badges"]:
            reasons.append("handcrafted by local artisans")
        if p["rating"] >= 4.5:
            reasons.append("highly rated by customers")
            
        reason_str = f"Matches query in category. Recommended as it is " + (", ".join(reasons) if reasons else "a top alternative")
        
        curation[p_id] = {
            "match_score": match_score,
            "match_reason": reason_str,
            "craftsmanship": "Produced using local sourcing and sustainable assembly methods.",
            "value_prop": "Saves markup and shipping taxes, offering identical performance."
        }
        
    return {
        "curation": curation,
        "workflow_steps": state["workflow_steps"] + [{
            "name": "Quality Curator",
            "status": "complete",
            "output": f"Generated match scores and value propositions for matches."
        }]
    }

@traceable
def formatter_node(state: DiscoveryState) -> Dict[str, Any]:
    """
    Format output into frontend-ready JSON.
    """
    matches = state["matches"]
    reviews_analysis = state["reviews_analysis"]
    curation = state["curation"]
    
    formatted_matches = []
    for p in matches:
        p_id = p["id"]
        cur = curation.get(p_id, {})
        rev = reviews_analysis.get(p_id, {})
        
        # Inject pros, cons, and summaries into the product details
        product_copy = p.copy()
        product_copy["reviewSummary"] = rev.get("summary", p.get("reviewSummary", ""))
        product_copy["pros"] = rev.get("pros", [])
        product_copy["cons"] = rev.get("cons", [])
        product_copy["craftsmanship"] = cur.get("craftsmanship", "")
        
        formatted_matches.append({
            "product": product_copy,
            "matchScore": cur.get("match_score", 80),
            "matchReason": cur.get("match_reason", ""),
            "valueProp": cur.get("value_prop", ""),
            "priceSavings": None # calculated dynamically if needed
        })
        
    analysis = {
        "category": state["category"],
        "features": state["features"],
        "materials": state["materials"],
        "priceRange": state["price_range"],
        "aestheticStyle": state["aesthetic_style"],
        "originalBrand": state["original_brand"]
    }
    
    # Update workflow list to include Formatter step
    workflow = state["workflow_steps"] + [{
        "name": "Formatter",
        "status": "complete",
        "output": f"Assembled final response JSON payload with {len(formatted_matches)} products."
    }]
    
    return {
        "formatted_output": {
            "query": state["query"],
            "analysis": analysis,
            "matches": formatted_matches,
            "workflow": workflow,
            "aiPowered": bool(state.get("api_key"))
        }
    }
