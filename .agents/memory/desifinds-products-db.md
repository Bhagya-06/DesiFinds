---
  name: DesiFinds products db
  description: How the 5000-product dataset is loaded in the API server
  ---

  Products are stored in `data/products.json` at the workspace root (14 categories, 39+ Indian brands, 5000 entries).

  The API server loads them once via `artifacts/api-server/src/lib/db.ts`, which tries multiple candidate paths relative to `import.meta.url` and also `process.cwd()` as a fallback.

  **Rule:** No PostgreSQL/Drizzle is used for products despite the `@workspace/db` package being present. Keep products in the JSON file.

  **Why:** The product catalog is static reference data; a JSON file avoids migration overhead and loads fast (one-time parse on server startup).

  **How to apply:** When adding new data fields, update the Product interface in db.ts AND the OpenAPI schema, then re-run codegen.
  