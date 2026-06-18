---
  name: DesiFinds wouter query params
  description: Why useLocation() from wouter doesn't include query strings and how to read them
  ---

  In DesiFinds, the wouter Router is initialized with a base from `import.meta.env.BASE_URL`. The `useLocation()` hook returns only the path component — query strings (e.g. `?q=Zara+Linen+Shirt`) are NOT included.

  **Rule:** In any DesiFinds page that reads URL query params (search.tsx, explore.tsx), use `window.location.search` directly:
  ```ts
  const initialQuery = new URLSearchParams(window.location.search).get("q") || "";
  ```

  **Why:** wouter strips query strings from the location it exposes to hooks; the router base further changes how paths are reported.

  **How to apply:** Any new page that needs to read URL query params should use `window.location.search`, not `useLocation()[0]`.
  