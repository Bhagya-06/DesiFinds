import os
import json
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Body, Query, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.ai.vector_store import ProductVectorStore
from backend.ai.graph import run_product_discovery
from backend.ai.langsmith import configure_langsmith
from backend.rag.retriever import ProductRetriever
from backend.rag.ingest import IngestionManager, ingestion_state
from backend.scrapers.brands.brand_info import get_brand_details, get_all_brands
from backend.scrapers.products.scraper import scrape_product_details

app = FastAPI(title="DesiFinds API", version="0.1.0")

# CORS middleware config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Resolve paths
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)
PRODUCTS_JSON_PATH = os.path.join(PROJECT_ROOT, "data", "products.json")

# In-memory product cache
products_cache: List[Dict[str, Any]] = []

def load_products():
    global products_cache
    if os.path.exists(PRODUCTS_JSON_PATH):
        try:
            with open(PRODUCTS_JSON_PATH, "r", encoding="utf-8") as f:
                products_cache = json.load(f)
            print(f"Loaded {len(products_cache)} products into memory cache.")
        except Exception as e:
            print(f"Error caching products: {e}")
            products_cache = []

@app.on_event("startup")
def startup_event():
    load_products()

# Global instances
vector_store = ProductVectorStore()
retriever = ProductRetriever(vector_store)
ingest_manager = IngestionManager(vector_store)

# Global chat history cache
chat_history_store: List[Dict[str, Any]] = []

# Pydantic Schemas
class SearchInput(BaseModel):
    query: str
    apiKey: Optional[str] = None

class IngestInput(BaseModel):
    apiKey: str
    force: Optional[bool] = False

class ChatMessage(BaseModel):
    role: str # user, assistant
    content: str

class ChatInput(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = []
    apiKey: Optional[str] = None

# Routes

@app.get("/healthz")
@app.get("/api/healthz")
def health_check():
    return {"status": "ok"}

@app.get("/api/status")
@app.get("/status")
def get_system_status():
    return ingest_manager.get_status()

@app.post("/api/search")
@app.post("/search")
def search_products(payload: SearchInput):
    query = payload.query.strip()
    api_key = payload.apiKey
    
    if not query:
        raise HTTPException(status_code=400, detail="query is required")
        
    try:
        # Trace using LangSmith if configuration headers are present
        configure_langsmith() 
        
        # Execute LangGraph discovery
        result = run_product_discovery(query, api_key)
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Search execution failed: {str(e)}")

@app.post("/api/ingest")
@app.post("/ingest")
def trigger_ingestion(payload: IngestInput):
    api_key = payload.apiKey
    force = payload.force
    
    if not api_key:
        raise HTTPException(status_code=400, detail="apiKey is required")
        
    ingest_manager.start_ingestion_background(api_key, PRODUCTS_JSON_PATH, force)
    return {"status": "ingesting", "message": "Bulk product ingestion started in background"}

@app.post("/api/chat")
@app.post("/chat")
def chat_assistant(payload: ChatInput):
    global chat_history_store
    message = payload.message.strip()
    history = payload.history
    api_key = payload.apiKey
    
    if not message:
        raise HTTPException(status_code=400, detail="message is required")
        
    # Append user message to global store
    chat_history_store.append({"role": "user", "content": message})
    
    retrieved_products = []
    
    # Check if any brand is mentioned in the query
    from backend.scrapers.brands.brand_info import BRAND_METADATA
    mentioned_brands = []
    message_lower = message.lower()
    for key, meta in BRAND_METADATA.items():
        if key in message_lower or meta["name"].lower() in message_lower:
            mentioned_brands.append(meta)
            
    # Check if asking about founders/story/info of a brand
    is_brand_info_query = any(keyword in message_lower for keyword in ["founder", "who started", "founded", "history", "story", "about", "ceo"])

    # 1. AI RAG workflow
    if api_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            
            # Step A: Semantic retrieval from vector store if populated
            if not is_brand_info_query:
                # Compute embeddings for user query to find relevant products
                from backend.ai.embeddings import get_openai_embeddings
                q_emb_list = get_openai_embeddings([message], api_key)
                if q_emb_list and vector_store.get_count() > 0:
                    retrieved_products = vector_store.query_products(q_emb_list[0], n_results=3)
                else:
                    # Fallback to retriever keyword matching if vector store empty
                    retrieved_products = retriever.retrieve_alternatives(
                        query=message,
                        category="Apparel",
                        features=[],
                        materials=[],
                        api_key=api_key,
                        n_results=3
                    )
                
            # Construct context from products
            context_blocks = []
            for p in retrieved_products:
                context_blocks.append(
                    f"Product: {p['name']} by {p['brand']}\n"
                    f"Category: {p['category']}\n"
                    f"Price: ₹{p['price']}\n"
                    f"Rating: {p['rating']} stars ({p['reviewCount']} reviews)\n"
                    f"Description: {p['description']}\n"
                    f"Materials: {', '.join(p['materials'])}\n"
                    f"Badges: {', '.join(p['badges'])}\n"
                    f"Review Summary: {p.get('reviewSummary', '')}\n"
                    f"Link: {p['productUrl']}"
                )
            context = "\n---\n".join(context_blocks)
            
            # Construct brand metadata context block
            brands_context = ""
            if mentioned_brands:
                brands_blocks = []
                for b in mentioned_brands:
                    brands_blocks.append(
                        f"Brand: {b['name']}\n"
                        f"Founded: {b['founded']}\n"
                        f"Founder(s): {b.get('founders', 'Unknown')}\n"
                        f"Website: {b['websiteUrl']}\n"
                        f"Story & Origins: {b.get('story', b['description'])}"
                    )
                brands_context = "\n---\n".join(brands_blocks)
            
            # Step B: Call OpenAI
            system_prompt = (
                "You are DesiFinds AI, a friendly and expert shopping assistant dedicated to finding premium Indian alternatives to global products.\n"
                "Answer the user's questions about products, buying advice, comparison, and recommendations.\n"
                "You are also an expert on Indian startup founders, origins, and histories. If asked about the founder, history, or background of a brand, "
                "always answer factually using the Brand Details Context provided below.\n\n"
                "Indian Products Context:\n"
                f"{context}\n\n"
            )
            
            if brands_context:
                system_prompt += (
                    "Brand Details Context (Specific to user's query):\n"
                    f"{brands_context}\n\n"
                )
                
            system_prompt += (
                "Always point the user to specific local brands and explain why they match the quality, material, or aesthetic of global brands.\n"
                "Be premium, startup-like, helpful, and concise. Never make up URLs or prices. If you don't know, suggest checking explore."
            )
            
            messages = [{"role": "system", "content": system_prompt}]
            # Add request history (limit to last 5)
            for h_msg in history[-5:]:
                messages.append({"role": h_msg.role, "content": h_msg.content})
                
            messages.append({"role": "user", "content": message})
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.7
            )
            reply = response.choices[0].message.content
            chat_history_store.append({"role": "assistant", "content": reply})
            
            return {
                "response": reply,
                "history": chat_history_store,
                "retrievedProducts": retrieved_products
            }
        except Exception as e:
            print(f"OpenAI chatbot error: {e}")
            
    # 2. Heuristic fallback path if no API key or exception occurs
    # Check if asking about founders/story in fallback
    if mentioned_brands and any(keyword in message_lower for keyword in ["founder", "who started", "founded", "history", "story", "about"]):
        replies = []
        for b in mentioned_brands:
            replies.append(
                f"🇮🇳 **{b['name']}** was founded in **{b['founded']}** by **{b.get('founders', 'Unknown')}**.\n"
                f"**Story**: {b.get('story', b['description'])}\n"
                f"Website: [Visit {b['name']}]({b['websiteUrl']})"
            )
        reply = "\n\n".join(replies) + "\n\n*Tip: Input your OpenAI API key in the sidebar to engage in a continuous conversation about brand stories and comparison metrics!*"
        chat_history_store.append({"role": "assistant", "content": reply})
        return {
            "response": reply,
            "history": chat_history_store,
            "retrievedProducts": retrieved_products
        }

    # Standard product matching in fallback
    matched_items = []
    for p in products_cache:
        if p["category"].lower() in message_lower or p["name"].lower() in message_lower or p["brand"].lower() in message_lower:
            matched_items.append(p)
            if len(matched_items) >= 3:
                break
                
    retrieved_products = matched_items
    
    if retrieved_products:
        reply_items = [f"- **{p['name']}** by {p['brand']} (₹{p['price']}): {p['description']}" for p in retrieved_products]
        reply = (
            f"Here are some premium Indian alternatives matching your query:\n" + 
            "\n".join(reply_items) + 
            "\n\nAdd your OpenAI API key in the Search or Chat sidebar to get full AI-powered reasoning, buying guides, and pros/cons analysis!"
        )
    else:
        reply = (
            "Welcome to DesiFinds AI! Ask me about premium Indian alternatives in Apparel, Electronics, Skincare, Audio, and more. "
            "For example: 'What is a good Indian alternative for CeraVe?' or 'Who founded boAt?'\n\n"
            "Tip: Add your OpenAI API key in the toolbar or sidebar to enable deep semantic RAG chatbot discovery!"
        )
        
    chat_history_store.append({"role": "assistant", "content": reply})
    return {
        "response": reply,
        "history": chat_history_store,
        "retrievedProducts": retrieved_products
    }

@app.get("/api/chat-history")
@app.get("/chat-history")
def get_chat_history():
    return chat_history_store

@app.get("/api/products")
@app.get("/products")
def list_products(
    category: Optional[str] = None,
    brand: Optional[str] = None,
    minPrice: Optional[float] = None,
    maxPrice: Optional[float] = None,
    minRating: Optional[float] = None,
    q: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    filtered = products_cache
    
    if category:
        filtered = [p for p in filtered if p["category"].lower() == category.lower()]
    if brand:
        filtered = [p for p in filtered if brand.lower() in p["brand"].lower()]
    if minPrice is not None:
        filtered = [p for p in filtered if p["price"] >= minPrice]
    if maxPrice is not None:
        filtered = [p for p in filtered if p["price"] <= maxPrice]
    if minRating is not None:
        filtered = [p for p in filtered if p["rating"] is not None and p["rating"] >= minRating]
    if q:
        q_lower = q.lower()
        filtered = [
            p for p in filtered if (
                q_lower in p["name"].lower() or 
                q_lower in p["brand"].lower() or
                q_lower in p["description"].lower() or
                any(q_lower in tag.lower() for tag in p["tags"])
            )
        ]
        
    total = len(filtered)
    sliced = filtered[offset : offset + limit]
    return {
        "products": sliced,
        "total": total,
        "offset": offset,
        "limit": limit
    }

@app.get("/api/products/{id}")
@app.get("/products/{id}")
def get_product(id: str):
    for p in products_cache:
        if p["id"] == id:
            return p
    raise HTTPException(status_code=404, detail="Product not found")

@app.get("/api/categories")
@app.get("/categories")
def list_categories():
    counts = {}
    for p in products_cache:
        cat = p["category"]
        counts[cat] = counts.get(cat, 0) + 1
        
    icons = {
        "Apparel": "👔", "Footwear": "👟", "Electronics": "💻", "Audio": "🎧",
        "Watches": "⌚", "Skincare": "✨", "Bags": "👜", "Jewelry": "💍",
        "Furniture": "🛋️", "Home Decor": "🏮", "Kitchen": "🍳", "Fitness": "🏋️",
        "Perfumes": "🌸", "Eyewear": "👓",
    }
    
    result = []
    for cat, count in counts.items():
        result.append({
            "name": cat,
            "count": count,
            "icon": icons.get(cat, "🛍️")
        })
        
    # Sort by count descending
    result.sort(key=lambda x: x["count"], reverse=True)
    return result

@app.get("/api/brands")
@app.get("/brands")
def list_brands():
    return get_all_brands()

@app.get("/api/trending")
@app.get("/trending")
def get_trending():
    # Top rated products
    top = sorted(products_cache, key=lambda x: (x.get("rating") or 0.0) * ((x.get("reviewCount") or 0) + 1), reverse=True)[:12]
    # New arrivals (px identifiers)
    new = [p for p in products_cache if p["id"].startswith("px")][:8]
    if not new:
        new = products_cache[:8]
        
    popular = [
        "Zara Linen Shirt", "AirPods Pro", "Nike Running Shoes", "CeraVe Moisturizer",
        "Logitech MX Master", "Dyson Air Purifier", "Ray-Ban Sunglasses", "IKEA Sofa",
        "Apple Watch", "Levi's 501 Jeans"
    ]
    
    return {
        "popularSearches": popular,
        "topProducts": top,
        "newArrivals": new
    }

@app.get("/api/workflow")
@app.get("/workflow")
def get_workflow():
    # Provide node definitions or status mapping
    return [
        {"name": "Product Deconstructor", "description": "Analyzes international product queries to map materials and features."},
        {"name": "RAG Matcher", "description": "Retrieves matching local alternatives from ChromaDB using semantic vectors."},
        {"name": "Review Analyzer", "description": "Analyzes review summaries and extracts pros/cons feedback."},
        {"name": "Quality Curator", "description": "Calculates likeness scores, craftsmanship details, and value props."},
        {"name": "Formatter", "description": "Formulates response payload structure."}
    ]
