---
title: DesiFinds API
emoji: 🛍️
colorFrom: indigo
colorTo: red
sdk: docker
app_port: 7860
pinned: false
---

# DesiFinds - Find Better. Find Indian. 🇮🇳

DesiFinds is a premium, startup-style AI-powered Indian product discovery platform. Users can input any international product name, brand, description, or URL, and the platform discovers and recommends high-quality, premium Indian alternatives matching in category, materials, features, craftsmanship, and aesthetic style - at a significantly better value.

Live Link - https://desifinds.vercel.app/
---

## 🌟 Key Features

1. **Enterprise RAG System**: Leverages a localized **ChromaDB** vector store and dynamic **OpenAI Embeddings** to perform semantic search queries over a curated database of **2,769+ real products** across 14 categories.
2. **Dynamic Contextual Badges**: Auto-extracts product quality and feature labels (e.g., *Eco-Friendly, Handcrafted, Premium Quality, Comfortable, Skin Friendly*) directly from live descriptions, tags, materials, and reviews.
3. **User Authentication & Scoped Wishlists**: Includes a client-side login/signup system that persists sessions locally and stores wishlists on a per-user basis. Wishlisting is gated; anonymous users are guided to log in.
4. **LangGraph Workflow Orchestration**: Implements a multi-agent orchestration state machine:
   - **Product Deconstructor**: Parses queries to extract category, features, materials, and styles.
   - **RAG Matcher**: Queries ChromaDB for top alternatives using vector similarity.
   - **Review Analyzer**: Evaluates alternatives' review logs to fetch Pros and Cons.
   - **Quality Curator**: Assigns match scores (50%–99%) and value propositions.
   - **Formatter**: Packs the final discovery state into standard JSON.
5. **AI Chatbot Shopping Assistant**: An interactive RAG chatbot allowing comparisons, recommendations, and buying advice with sustained context history.
6. **Data Scrapers**: Built-in BeautifulSoup and Shopify product scraper (`master_pipeline.py`) that extracts live, real product data directly from brand feeds.
7. **Cleaned & Validated Database**: Includes 100% working product links, Unsplash images related to product names, and distinct prices (`originalPrice > price`) showing valid discounts. Unnecessary files (like `scraped_images.json`) have been pruned.

---

## 🛠️ Technology Stack

- **Frontend**: React + Vite (TypeScript), Axios, wouter, TanStack React Query, Tailwind CSS, Lucide Icons, Framer Motion
- **Backend**: FastAPI (Python 3.12), Uvicorn, Pydantic
- **AI / RAG**: LangGraph, LangChain, OpenAI API, ChromaDB
- **Data Collection**: BeautifulSoup, Requests

---

## 📁 Folder Structure

```
├── backend/
│   ├── ai/
│   │   ├── graph.py           # LangGraph state machine builder
│   │   ├── nodes.py           # Product deconstruction, matching, review, curation nodes
│   │   ├── state.py           # TypedDict state structure
│   │   ├── embeddings.py      # OpenAI embeddings helper (uses dynamic key)
│   │   ├── vector_store.py    # Persistent ChromaDB store wrapper
│   │   └── langsmith.py       # LangSmith tracing configuration
│   ├── rag/
│   │   ├── ingest.py          # Ingests products from JSON to ChromaDB
│   │   └── retriever.py       # Retrieval logic (semantic search + keyword fallback)
│   ├── scrapers/
│   │   ├── products/          # BeautifulSoup Shopify product details scraper
│   │   ├── brands/            # Local brand info lookup repository
│   │   ├── master_pipeline.py # Scraping execution pipeline (with dynamic badges & enrichment)
│   │   └── enrich_existing.py # Dataset data enricher (rating, reviews, price, badges)
│   ├── Dockerfile             # Production container definition
│   ├── requirements.txt       # Python dependencies
│   └── main.py                # FastAPI server entrypoint
├── frontend/                  # React + Vite frontend source code
│   ├── src/
│   │   ├── context/
│   │   │   └── AuthContext.tsx # User login, registration, and session manager
│   │   ├── components/
│   │   │   ├── AuthModal.tsx   # Login/Signup dialog box
│   │   │   └── Navbar.tsx      # Header navbar showing user profile dropdown
│   │   ├── pages/
│   │   │   └── wishlist.tsx    # User-scoped wishlist products grid
│   │   │   └── explore.tsx     # Indian products directory
│   │   │   └── ...
│   │   └── ...
├── data/
│   ├── products.json          # 2,769+ item consolidated live scraped & Kaggle catalog
│   ├── external_kaggle_products.json # Raw external Kaggle products dataset
│   └── chromadb/              # (Git-ignored) ChromaDB persistent vectors
├── start.bat                  # Quick-start local run script (Windows)
├── .env.example               # Template for environment configuration
└── pnpm-workspace.yaml        # Workspace configuration
```

---

## 💻 Local Setup & Execution

### 1. Prerequisites
Ensure you have **Node.js (v18+)** and **Python (3.11 or 3.12)** installed.

### 2. Dependency Installation

```bash
# 1. Install Node workspace dependencies
pnpm install --ignore-scripts

# 2. Setup Python Virtual Environment
cd backend
python -m venv .venv

# 3. Activate Virtual Environment (Windows PowerShell)
.venv\Scripts\Activate.ps1

# 4. Install backend dependencies
pip install -r requirements.txt
cd ..
```

### 3. Run the App

- **Windows Quick Start**: Double-click [start.bat](file:///c:/Users/Bhagya%20B/Downloads/Desi-Finds/start.bat) to launch the FastAPI backend (port `8080`) and Vite React frontend (port `19993`).
- **Manual Launch**:
  ```bash
  # Start Backend (Terminal 1)
  cd backend
  .venv\Scripts\activate
  python -m uvicorn main:app --host 0.0.0.0 --port 8080

  # Start Frontend (Terminal 2)
  cd frontend
  $env:PORT="19993"
  $env:BASE_PATH="/"
  pnpm run dev
  ```

---

## 🚀 Scrapers & Data Seeding

### 1. Live Web Scraping
To refresh the database with new live products directly from brand catalogs, run the scraping pipeline:
```bash
cd backend
.venv\Scripts\activate
python -u -m backend.scrapers.master_pipeline --limit 200 --skip-validation
```

### 2. Seeding Mock Catalog
For testing purposes, you can generate 3,000 synthetic products using the seeder script:
```bash
pnpm --filter @workspace/scripts exec tsx ./src/seed-products.ts
```
*(After seeding mock data, run `python -m backend.scrapers.enrich_existing` to fill in rating and price fields).*

### 3. Kaggle Datasets Ingestion Pipeline
To programmatically download, clean, and consolidate products from the **Indian E-commerce Dataset (INR)** (`amaymishra11/indian-e-commerce-dataset-inr`) and the **Indian Products on Amazon (Reviews)** dataset (`nehaprabhavalkar/indian-products-on-amazon`) using `kagglehub` (which downloads public datasets anonymously without credential configuration), run:
```bash
cd backend
.venv\Scripts\activate
python -m backend.scrapers.ingest_external_data
```
This runs the full cleaning pipeline, validates URLs, resolves Pandas serialization float NaN trap issues, generates search fallbacks, and updates the RAG database.

