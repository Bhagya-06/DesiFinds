# DesiFinds

AI-powered Indian product discovery platform where users search for international products and get Indian alternatives.

## Run & Operate

- `pnpm --filter @workspace/api-server run dev` — run the API server (port 8080, served at `/api`)
- `pnpm --filter @workspace/desifinds run dev` — run the React frontend (port 19993, served at `/`)
- `pnpm run typecheck` — full typecheck across all packages
- `pnpm run build` — typecheck + build all packages
- `pnpm --filter @workspace/api-spec run codegen` — regenerate API hooks and Zod schemas from the OpenAPI spec

## Stack

- pnpm workspaces, Node.js 24, TypeScript 5.9
- Frontend: React + Vite (artifact: `desifinds`)
- API: Express 5 (artifact: `api-server`, port 8080)
- Products: 5000-product JSON dataset at `data/products.json`
- Routing: wouter (React), path-based proxy for cross-artifact routing
- Theme: next-themes, Tailwind v4
- Design: saffron primary, peacock blue secondary, emerald accent, warm ivory background
- API codegen: Orval (from OpenAPI spec in `lib/api-spec/openapi.yaml`)

## Where things live

- `data/products.json` — 5,000 Indian products dataset (14 categories, 39+ brands)
- `lib/api-spec/openapi.yaml` — source of truth for API contract
- `lib/api-client-react/src/generated/` — generated React Query hooks
- `lib/api-zod/src/generated/` — generated Zod validation schemas
- `artifacts/api-server/src/routes/` — Express route handlers
- `artifacts/api-server/src/lib/db.ts` — products JSON loader (in-memory, no PostgreSQL)
- `artifacts/desifinds/src/pages/` — Home, Search, Explore, Workflow, Product pages
- `artifacts/desifinds/src/components/` — Navbar, ProductCard, SearchBar, Footer
- `artifacts/desifinds/src/index.css` — complete DesiFinds theme (Tailwind v4 CSS variables)

## Architecture decisions

- **No database** — products served from `data/products.json` loaded once into memory; no PostgreSQL/Drizzle used despite db package being present
- **wouter URL params** — `useLocation()` from wouter does NOT include query params; use `window.location.search` directly in pages
- **Search algorithm** — pure keyword + category scoring (no vector DB); OpenAI API key is optional and stored in localStorage
- **Product dataset** — generated in-memory via code_execution and written to `data/products.json`; `db.ts` resolves the file path by trying multiple candidate paths relative to `import.meta.url`

## Product

- **Home page** (`/`) — Hero search bar, category strip (with live counts from API), "Why DesiFinds" cards, trending brands grid, top products
- **Search page** (`/search?q=...`) — AI Product Analysis card, match-scored results grid with filters/sort, optional OpenAI API key input
- **Explore page** (`/explore`) — Full product browse with category pills, filters (price, rating), pagination
- **Workflow page** (`/workflow`) — LangGraph-style visualizer showing the 4-step AI pipeline
- **Product page** (`/product/:id`) — Full detail page with image, materials, badges, tags, review summary, CTAs

## User preferences

_Populate as you build — explicit user instructions worth remembering across sessions._

## Gotchas

- Do NOT use `pnpm dev` at workspace root — use per-artifact filters or `restart_workflow`
- `data/products.json` must exist before starting the API server — it's loaded at startup
- The api-server `db.ts` uses `import.meta.url` for path resolution; candidate paths cover dev and dist layouts
- After adding new routes in `routes/index.ts`, restart the API server workflow to rebuild
- `wouter` `useLocation()` returns path only, not query string — use `window.location.search` for query params

## Pointers

- See the `pnpm-workspace` skill for workspace structure, TypeScript setup, and package details
