# DesiFinds - Find Better. Find Indian. 🇮🇳

DesiFinds is a premium, startup-style AI-powered Indian product discovery platform. Users can input any international product name, brand, description, or URL, and the platform discovers and recommends high-quality, premium Indian alternatives matching in category, materials, features, craftsmanship, and aesthetic style — at a significantly better value.

---

## 🌟 Key Features

1. **Enterprise RAG System**: Leverages a localized **ChromaDB** vector store and dynamic **OpenAI Embeddings** to perform semantic search queries over a curated database of 5,000+ real products across 14 categories.
2. **LangGraph Workflow Orchestration**: Implements a multi-agent orchestration state machine matching the following pipeline:
   - **Product Deconstructor**: Parses international search queries to extract category, features, materials, and styles.
   - **RAG Matcher**: Queries ChromaDB for top alternatives using vector similarity.
   - **Review Analyzer**: Evaluates alternatives' review logs to fetch Pros and Cons.
   - **Quality Curator**: Assigns match scores (50%–99%) and value propositions.
   - **Formatter**: Packs the final discovery state into standard JSON.
3. **AI Chatbot Shopping Assistant**: An interactive RAG chatbot allowing comparisons, recommendations, and buying advice with sustained context history.
4. **Data Scrapers**: Built-in BeautifulSoup scraper targeting landing pages, microdata (Shopify JSON-LD schemas), and OpenGraph tags to dynamically ingest new products.
5. **Local Wishlist**: Local storage integration saving user favorites without database dependencies.
6. **Robust Fallbacks**: A rule-based heuristic system allows the application to remain functional even when no OpenAI API key is supplied.

---

## 🛠️ Technology Stack

- **Frontend**: React + Vite (TypeScript), Axios, wouter, TanStack React Query, Tailwind CSS v4, Lucide Icons, Framer Motion
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
│   │   └── brands/            # Local brand info lookup repository
│   ├── Dockerfile             # Production container definition
│   ├── requirements.txt       # Python dependencies
│   └── main.py                # FastAPI server entrypoint
├── frontend/                  # React + Vite frontend source code
│   ├── src/
│   │   ├── pages/
│   │   │   └── ai-assistant.tsx # AI Chatbot page
│   │   │   └── workflow.tsx     # Discovery workflow visualization page
│   │   └── ...
│   └── vercel.json            # Vercel deployment configuration
├── data/
│   ├── products.json          # 5,000+ item catalog
│   └── chromadb/              # (Git-ignored) ChromaDB persistent vectors
├── render.yaml                # Render Blueprint file for one-click backend deployment
├── vercel.json                # Root Vercel deployment configuration
├── start.bat                  # Quick-start local run script (Windows)
├── .env.example               # Template for environment configuration
└── pnpm-workspace.yaml        # Workspace configuration
```

---

## 💻 Local Setup & Execution

### 1. Prerequisites
Ensure you have **Node.js (v18+)** and **Python (3.11 or 3.12)** installed on your machine.

### 2. Dependency Installation

Open your terminal and run the following commands:

```bash
# 1. Install monorepo Node dependencies
pnpm install --ignore-scripts

# 2. Setup Python Virtual Environment
cd backend
python -m venv .venv

# 3. Activate Virtual Environment
# On Windows (PowerShell):
.venv\Scripts\Activate.ps1
# On macOS / Linux:
source .venv/bin/activate

# 4. Install backend dependencies
pip install -r requirements.txt
cd ..
```

### 3. Run the App

- **Windows**: Double-click the [start.bat](file:///c:/Users/Bhagya%20B/Downloads/Desi-Finds/start.bat) script in the root directory. It will spawn:
  - The FastAPI Backend on `http://localhost:8080`
  - The React Frontend on `http://localhost:19993`
  
- **macOS / Linux / Manual execution**:
  ```bash
  # In terminal 1 (Backend):
  cd backend
  source .venv/bin/activate
  python -m uvicorn main:app --host 0.0.0.0 --port 8080 --reload

  # In terminal 2 (Frontend):
  cd frontend
  export PORT=19993
  export BASE_PATH=/
  pnpm run dev
  ```

---

## 🚀 Cloud Deployment Guide

To deploy the application to production, you will publish the code in a single **GitHub repository**, deploying the **Backend to Render/Railway** and hosting the **Frontend on Vercel**.

> [!NOTE]
> All application components are built under a monorepo. You should push the **entire directory structure** to your GitHub repository. Both Vercel and Render will pull from this repository and target their respective directories.

### 1. Deploying the Backend (via GitHub to Render)

The backend is fully containerized and configured with a [Dockerfile](file:///c:/Users/Bhagya%20B/Downloads/Desi-Finds/backend/Dockerfile) and a [render.yaml](file:///c:/Users/Bhagya%20B/Downloads/Desi-Finds/render.yaml) blueprint.

#### Method A: Using Render Blueprints (Recommended)
1. Push the project to GitHub.
2. In the **Render Dashboard**, click **New** -> **Blueprint**.
3. Connect your GitHub repository.
4. Render will automatically detect the [render.yaml](file:///c:/Users/Bhagya%20B/Downloads/Desi-Finds/render.yaml) file, create the `desifinds-backend` service, and configure its resources.
5. In the Render UI, supply your `OPENAI_API_KEY` when prompted.

#### Method B: Manual Web Service Setup
1. Create a new **Web Service** on Render or Railway and link your GitHub repository.
2. Configure settings:
   - **Runtime**: `Docker`
   - **Docker Context**: `backend`
   - **Dockerfile Path**: `backend/Dockerfile`
3. Expose port `8080`.
4. Add the following **Environment Variables**:
   - `PORT`: `8080`
   - `OPENAI_API_KEY`: (Your OpenAI secret key)

---

### 2. Deploying the Frontend (to Vercel)

Since the frontend resides in a `pnpm` workspace monorepo, Vercel must compile the assets while resolving local workspace dependencies like `lib/api-client-react`.

1. Create a new project in **Vercel** and connect your GitHub repository.
2. In the Vercel project configuration, set:
   - **Framework Preset**: `Vite`
   - **Root Directory**: `.` (Keep as workspace root to allow dependency resolution)
   - **Build Command**: `pnpm --filter @workspace/desifinds build`
   - **Output Directory**: `frontend/dist`
   - **Environment Variables**:
     - `PORT`: `19993`
     - `BASE_PATH`: `/`
3. Under the project settings, make sure **Include files outside of the Root Directory in the Build Step** is enabled (enabled by default for monorepos).

#### CORS Bypass (API Proxying)
We have pre-configured [vercel.json](file:///c:/Users/Bhagya%20B/Downloads/Desi-Finds/vercel.json) in both the workspace root and the `frontend/` folder.

> [!IMPORTANT]
> Once your backend is running on Render/Railway, open [vercel.json](file:///c:/Users/Bhagya%20B/Downloads/Desi-Finds/vercel.json) and replace the default URL:
> `"destination": "https://your-desi-finds-backend.onrender.com/api/:path*"`
> with your **live deployed backend URL**.
> This routes all frontend requests matching `/api/*` directly to your production API, bypassing CORS issues without setting broad origin headers.
