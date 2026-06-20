import os
import json
import time
import threading
from typing import List, Dict, Any, Optional
from backend.ai.embeddings import get_openai_embeddings
from backend.ai.vector_store import ProductVectorStore

# Ingestion state tracking
ingestion_state = {
    "status": "idle", # idle, ingesting, complete, error
    "processed": 0,
    "total": 0,
    "error_message": None
}

class IngestionManager:
    def __init__(self, vector_store: ProductVectorStore):
        self.vector_store = vector_store
        
    def get_status(self) -> Dict[str, Any]:
        global ingestion_state
        # Also return vector store count
        db_count = self.vector_store.get_count()
        return {
            "status": ingestion_state["status"],
            "processed": ingestion_state["processed"],
            "total": ingestion_state["total"],
            "db_count": db_count,
            "error_message": ingestion_state["error_message"]
        }
        
    def start_ingestion_background(self, api_key: str, products_file_path: str, force: bool = False):
        global ingestion_state
        if ingestion_state["status"] == "ingesting":
            return
            
        ingestion_state["status"] = "ingesting"
        ingestion_state["processed"] = 0
        ingestion_state["error_message"] = None
        
        thread = threading.Thread(
            target=self._run_ingestion,
            args=(api_key, products_file_path, force)
        )
        thread.daemon = True
        thread.start()
        
    def _run_ingestion(self, api_key: str, products_file_path: str, force: bool):
        global ingestion_state
        try:
            if not os.path.exists(products_file_path):
                raise FileNotFoundError(f"Products JSON file not found at {products_file_path}")
                
            with open(products_file_path, "r", encoding="utf-8") as f:
                products = json.load(f)
                
            if not isinstance(products, list):
                raise ValueError("Products JSON must be a list")
                
            ingestion_state["total"] = len(products)
            
            # If database already has products and we are not forcing a rebuild
            db_count = self.vector_store.get_count()
            if db_count >= len(products) and not force:
                ingestion_state["status"] = "complete"
                ingestion_state["processed"] = len(products)
                return
                
            if force:
                self.vector_store.clear_all()
                
            # Batch size for embedding API (OpenAI supports up to 2048, but let's use 100 for safety and rate-limit margins)
            batch_size = 100
            
            for i in range(0, len(products), batch_size):
                batch = products[i : i + batch_size]
                
                # Filter out already stored IDs if not forcing rebuild
                if not force:
                    # Quick check (chromadb query is cheap)
                    # For simplicity, in bulk ingest we overwrite/add
                    pass
                    
                # Create text documents to embed
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
                    
                # Compute embeddings using OpenAI API (fallback to zero vectors on error)
                try:
                    embeddings = get_openai_embeddings(batch_texts, api_key)
                except Exception as e:
                    print(f"Failed to generate OpenAI embeddings: {e}. Falling back to zero vectors.")
                    embeddings = [[0.0] * 1536 for _ in batch]
                
                # Insert to ChromaDB
                self.vector_store.add_products(batch, embeddings)
                
                ingestion_state["processed"] += len(batch)
                
                # Small pause to avoid hitting rate limits
                time.sleep(0.5)
                
            ingestion_state["status"] = "complete"
            
        except Exception as e:
            print(f"Error in background ingestion: {e}")
            ingestion_state["status"] = "error"
            ingestion_state["error_message"] = str(e)


if __name__ == "__main__":
    import argparse
    from dotenv import load_dotenv
    
    # Load env variables from .env file
    load_dotenv()
    
    parser = argparse.ArgumentParser(description="Ingest products from products.json to ChromaDB")
    parser.add_argument("--key", help="OpenAI API Key (or fallback to OPENAI_API_KEY environment variable)")
    parser.add_argument("--force", action="store_true", help="Force rebuild ChromaDB (clear existing data first)")
    
    args = parser.parse_args()
    
    # Resolve API key
    api_key = args.key or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: OpenAI API Key is required. Set the OPENAI_API_KEY environment variable in your .env file or pass --key.")
        exit(1)
        
    # Paths
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    project_root = os.path.dirname(backend_dir)
    products_file = os.path.join(project_root, "data", "products.json")
    
    print(f"Loading products from: {products_file}")
    if not os.path.exists(products_file):
        print(f"Error: Products file not found at {products_file}")
        exit(1)
        
    # Initialize store and manager
    store = ProductVectorStore()
    manager = IngestionManager(store)
    
    print(f"Current database item count: {store.get_count()} items.")
    print("Starting synchronous ingestion. Please wait...")
    
    # Run ingestion synchronously
    manager._run_ingestion(api_key, products_file, force=args.force)
    
    status = manager.get_status()
    print(f"Ingestion finished with status: {status['status']}")
    print(f"Processed: {status['processed']}/{status['total']} items.")
    print(f"Final database item count: {status['db_count']} items.")
    if status["error_message"]:
        print(f"Error details: {status['error_message']}")

