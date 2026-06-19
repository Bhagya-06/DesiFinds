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
        Retrieve alternatives. Uses ChromaDB semantic search if an API key is provided and
        the database has items, otherwise falls back to structural keyword matching.
        """
        if api_key and self.vector_store.get_count() > 0:
            try:
                # Combine search tokens to create a query-rich semantic context
                search_text = (
                    f"Query: {query} "
                    f"Category: {category} "
                    f"Features: {', '.join(features)} "
                    f"Materials: {', '.join(materials)}"
                )
                embeddings = get_openai_embeddings([search_text], api_key)
                if embeddings:
                    query_emb = embeddings[0]
                    # Query ChromaDB, filtered by category
                    matches = self.vector_store.query_products(
                        query_embedding=query_emb,
                        n_results=n_results,
                        category_filter=category
                    )
                    if matches:
                        return matches
            except Exception as e:
                print(f"Semantic retrieval failed: {e}. Falling back to keyword search.")
                
        return self._keyword_search(query, category, features, materials, n_results)
        
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
