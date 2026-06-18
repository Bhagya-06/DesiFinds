import os
import json
from typing import List, Dict, Any, Optional
import chromadb

# Resolve paths
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)
CHROMA_DB_PATH = os.path.join(PROJECT_ROOT, "data", "chromadb")

class ProductVectorStore:
    def __init__(self):
        os.makedirs(os.path.dirname(CHROMA_DB_PATH), exist_ok=True)
        self.client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        self.collection_name = "desi_finds_products"
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
    
    def add_products(self, products: List[Dict[str, Any]], embeddings: List[List[float]]):
        """
        Add a list of products with pre-computed embeddings to ChromaDB.
        """
        if not products or not embeddings:
            return
            
        ids = [p["id"] for p in products]
        documents = []
        metadatas = []
        
        for p in products:
            # Document text contains full textual descriptions for keyword/semantic indexing
            doc_text = (
                f"Brand: {p['brand']}\n"
                f"Name: {p['name']}\n"
                f"Category: {p['category']}\n"
                f"Description: {p['description']}\n"
                f"Tags: {', '.join(p['tags'])}\n"
                f"Materials: {', '.join(p['materials'])}\n"
                f"Review Summary: {p.get('reviewSummary', '')}"
            )
            documents.append(doc_text)
            
            # Serialize the product so we can retrieve it directly without hitting other databases
            metadatas.append({
                "id": p["id"],
                "brand": p["brand"],
                "category": p["category"],
                "price": float(p["price"]),
                "rating": float(p["rating"]),
                "product_json": json.dumps(p)
            })
            
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
        
    def query_products(self, query_embedding: List[float], n_results: int = 5, category_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieve the most semantically relevant products matching the query embedding.
        """
        where_clause = {}
        if category_filter:
            where_clause["category"] = category_filter
            
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where_clause if where_clause else None
        )
        
        products = []
        if not results or not results["metadatas"] or len(results["metadatas"][0]) == 0:
            return []
            
        for i, meta in enumerate(results["metadatas"][0]):
            product_json = meta["product_json"]
            product = json.loads(product_json)
            # Add match distance / similarity score from query results
            distance = results["distances"][0][i] if "distances" in results and results["distances"] else 0.0
            # Cosine similarity = 1 - Cosine distance (with clipping)
            similarity = max(0.0, min(1.0, 1.0 - distance))
            product["similarity_score"] = float(similarity)
            products.append(product)
            
        return products

    def get_count(self) -> int:
        return self.collection.count()

    def clear_all(self):
        try:
            self.client.delete_collection(self.collection_name)
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
        except Exception:
            pass
