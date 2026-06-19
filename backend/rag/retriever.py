import os
import json
import re
from typing import List, Dict, Any, Optional
from backend.ai.embeddings import get_openai_embeddings
from backend.ai.vector_store import ProductVectorStore

# Resolve paths
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)
PRODUCTS_JSON_PATH = os.path.join(PROJECT_ROOT, "data", "products.json")

# ============================================================================
# Standalone Enterprise RAG Helper Functions (Module Scope)
# ============================================================================

def parse_filters(query: str) -> Dict[str, Any]:
    """
    Parse price range filters from the query.
    e.g., 'under 2000', 'below 1.5k', 'above 3000'
    """
    filters = {}
    lower_query = query.lower()
    
    # 1. Look for max price limit
    max_price_match = re.search(r"(?:under|below|less than|max|up to|budget of)\s*(?:rs\.?|inr|₹)?\s*(\d+(?:\.\d+)?)\s*(k)?", lower_query)
    if max_price_match:
        val = float(max_price_match.group(1))
        if max_price_match.group(2): # 'k' multiplier
            val *= 1000
        filters["max_price"] = val
        
    # 2. Look for min price limit
    min_price_match = re.search(r"(?:above|over|more than|min|at least|starting from)\s*(?:rs\.?|inr|₹)?\s*(\d+(?:\.\d+)?)\s*(k)?", lower_query)
    if min_price_match:
        val = float(min_price_match.group(1))
        if min_price_match.group(2): # 'k' multiplier
            val *= 1000
        filters["min_price"] = val
        
    return filters

def expand_query(query: str) -> str:
    """
    Translate common international brand names into their descriptive categories/keywords.
    """
    brand_expansions = {
        "zara": "apparel linen shirt cotton dress clothing premium casual sleek",
        "h&m": "apparel clothing casual basic dress minimal affordable",
        "uniqlo": "apparel cotton basic minimal t-shirt comfortable casual",
        "levis": "apparel jeans denim pants jacket rugged sturdy classic",
        "levi's": "apparel jeans denim pants jacket rugged sturdy classic",
        "nike": "footwear sneakers athletic running shoes activewear premium",
        "adidas": "footwear sneakers athletic running shoes activewear sporty",
        "puma": "footwear sneakers athletic running shoes activewear comfort",
        "airpods": "audio wireless earbuds tws headphones music portable sound",
        "airpod": "audio wireless earbuds tws headphones music portable sound",
        "bose": "audio headphones noise cancelling premium travel sound quality",
        "sony": "audio headphones noise cancelling premium audio tech bass",
        "jbl": "audio headphones speaker heavy bass waterproof portable",
        "cerave": "skincare moisturizer face cream active hydrating spf gentle dermatologist",
        "cetaphil": "skincare moisturizer face wash cleanser gentle sensitive dermatologist",
        "ordinary": "skincare active serum salicylic hyaluronic acid minimalist skin concern",
        "neutrogena": "skincare sunscreen active sunscreen hydrogel spf non-comedogenic",
        "mokobara": "bags luggage backpack suitcase travel trolley premium aesthetic",
        "samsonite": "bags luggage backpack suitcase travel trolley durable business",
        "ikea": "furniture minimalist home decor desk chair table workspace aesthetic",
        "dyson": "electronics fan air purifier vacuum hair premium design technology"
    }
    
    lower_query = query.lower()
    expanded_terms = []
    
    for brand, expansion in brand_expansions.items():
        if brand in lower_query:
            expanded_terms.append(expansion)
            
    if expanded_terms:
        # Prepend original query to expanded terms
        return f"{query} {' '.join(expanded_terms)}"
    return query

def reciprocal_rank_fusion(
    dense_results: List[Dict[str, Any]], 
    sparse_results: List[Dict[str, Any]], 
    n_results: int = 5,
    filters: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Combine dense and sparse search results using Reciprocal Rank Fusion.
    Applies optional price filters during fusion.
    """
    rrf_scores = {}
    product_map = {}
    
    # 1. Score dense results
    for rank, p in enumerate(dense_results):
        pid = p["id"]
        # Apply filters
        price = p.get("price", 0.0)
        if filters:
            if "max_price" in filters and price > filters["max_price"]:
                continue
            if "min_price" in filters and price < filters["min_price"]:
                continue
                
        rrf_scores[pid] = rrf_scores.get(pid, 0.0) + (1.0 / (60.0 + rank))
        product_map[pid] = p
        
    # 2. Score sparse results
    for rank, p in enumerate(sparse_results):
        pid = p["id"]
        # Apply filters
        price = p.get("price", 0.0)
        if filters:
            if "max_price" in filters and price > filters["max_price"]:
                continue
            if "min_price" in filters and price < filters["min_price"]:
                continue
                
        rrf_scores[pid] = rrf_scores.get(pid, 0.0) + (1.0 / (60.0 + rank))
        # Keep product details from whichever source had it (prefer dense since it might have similarity score already)
        if pid not in product_map:
            product_map[pid] = p
            
    # 3. Sort by RRF score descending
    sorted_pids = sorted(rrf_scores.keys(), key=lambda pid: rrf_scores[pid], reverse=True)
    
    final_products = []
    for pid in sorted_pids[:n_results]:
        p_copy = product_map[pid].copy()
        # Set normalized similarity_score based on normalized RRF score
        # Max theoretical RRF score with 2 sources at rank 0 is (1/60 + 1/60) = 0.0333
        # Normalize to a 0.5 - 0.99 range for UI consistency
        raw_score = rrf_scores[pid]
        max_possible = 2.0 / 60.0
        normalized_sim = 0.5 + 0.49 * (raw_score / max_possible)
        p_copy["similarity_score"] = float(min(0.99, max(0.5, normalized_sim)))
        final_products.append(p_copy)
        
    return final_products


# ============================================================================
# Product Retriever Class (Class Scope)
# ============================================================================

class ProductRetriever:
    def __init__(self, vector_store: ProductVectorStore):
        self.vector_store = vector_store
        self.products = []
        self._load_products()
        
    def _load_products(self):
        if os.path.exists(PRODUCTS_JSON_PATH):
            try:
                with open(PRODUCTS_JSON_PATH, "r", encoding="utf-8") as f:
                    self.products = json.load(f)
            except Exception as e:
                print(f"Error loading products from {PRODUCTS_JSON_PATH}: {e}")

    def retrieve_alternatives(
        self, 
        query: str, 
        category: str,
        features: List[str],
        materials: List[str],
        api_key: Optional[str] = None, 
        n_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve alternatives using Enterprise Hybrid Search (Dense + Sparse) with RRF
        and dynamic metadata filtering.
        """
        # 1. Parse price/metadata filters from query
        filters = parse_filters(query)
        
        # 2. Expand search query terms for international brands
        expanded_query_str = expand_query(query)
        
        dense_matches = []
        
        # 3. Dense / Semantic Search
        if api_key and self.vector_store.get_count() > 0:
            try:
                # Combine search tokens to create a query-rich semantic context
                search_text = (
                    f"Query: {expanded_query_str} "
                    f"Category: {category} "
                    f"Features: {', '.join(features)} "
                    f"Materials: {', '.join(materials)}"
                )
                embeddings = get_openai_embeddings([search_text], api_key)
                if embeddings:
                    query_emb = embeddings[0]
                    # Query ChromaDB, filtered by category, request larger candidate pool for RRF
                    dense_matches = self.vector_store.query_products(
                        query_embedding=query_emb,
                        n_results=n_results * 3,
                        category_filter=category
                    )
            except Exception as e:
                print(f"Semantic retrieval failed: {e}. Falling back to keyword search.")
                
        # 4. Sparse / Keyword Search
        sparse_matches = self._keyword_search(
            query=expanded_query_str,
            category=category,
            features=features,
            materials=materials,
            n_results=n_results * 3
        )
        
        # 5. Hybrid Fusion or Fallback Filtering
        if dense_matches:
            # Perform RRF blending with filters
            return reciprocal_rank_fusion(dense_matches, sparse_matches, n_results, filters)
        else:
            # Fallback to keyword matches, filtering by price limits
            filtered_matches = []
            for p in sparse_matches:
                price = p.get("price", 0.0)
                if filters:
                    if "max_price" in filters and price > filters["max_price"]:
                        continue
                    if "min_price" in filters and price < filters["min_price"]:
                        continue
                filtered_matches.append(p)
            return filtered_matches[:n_results]
        
    def _keyword_search(
        self, 
        query: str, 
        category: str,
        features: List[str],
        materials: List[str],
        n_results: int = 5
    ) -> List[Dict[str, Any]]:
        scored_products = []
        lower_query = query.lower()
        query_words = [w for w in re.split(r'\s+', lower_query) if len(w) > 2]
        
        for p in self.products:
            score = 0
            
            # Category match (heavily weighted)
            if p["category"].lower() == category.lower():
                score += 40
            elif p["category"].lower() in lower_query or lower_query in p["category"].lower():
                score += 10
                
            # Keyword overlaps in name, tags, description, materials
            for word in query_words:
                if word in p["name"].lower():
                    score += 8
                if any(word in tag.lower() for tag in p["tags"]):
                    score += 5
                if word in p["description"].lower():
                    score += 3
                if any(word in mat.lower() for mat in p["materials"]):
                    score += 4
                    
            # Feature matches
            for f in features:
                if f.lower() in p["name"].lower() or f.lower() in p["description"].lower():
                    score += 5
                if any(f.lower() in tag.lower() for tag in p["tags"]):
                    score += 3
                    
            # Material matches
            for m in materials:
                if any(m.lower() in mat.lower() for mat in p["materials"]):
                    score += 8
                    
            # Quality signals (rating + review count)
            score += min(15, (p.get("rating") or 0.0) * 2.5)
            import math
            score += min(10, math.log10((p.get("reviewCount") or 0) + 1) * 3)
            
            # Badges
            if "Made in India" in p["badges"]:
                score += 3
            if "Handcrafted" in p["badges"]:
                score += 2
                
            if score > 0:
                similarity = min(99, max(50, score)) / 100.0
                p_copy = p.copy()
                p_copy["similarity_score"] = similarity
                scored_products.append((p_copy, score))
                
        scored_products.sort(key=lambda x: x[1], reverse=True)
        return [sp[0] for sp in scored_products[:n_results]]
