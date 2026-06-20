import json
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

with open("data/products.json", "r", encoding="utf-8") as f:
    products = json.load(f)

print(f"Total products to validate: {len(products)}")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def check_image(p):
    url = p.get("imageUrl", "")
    if not url:
        return p["id"], "empty", None
    try:
        r = requests.head(url, headers=headers, timeout=3, allow_redirects=True)
        if r.status_code == 200:
            return p["id"], "ok", url
        else:
            # try GET
            r_get = requests.get(url, headers=headers, timeout=3, stream=True)
            if r_get.status_code == 200:
                return p["id"], "ok", url
            else:
                return p["id"], f"fail_{r_get.status_code}", url
    except Exception as e:
        return p["id"], f"error_{type(e).__name__}", url

# Let's test a sample of 100 products (first 100) and some from different brands
samples = products[:50] + products[500:550] + products[1000:1050] + products[-50:]
print(f"Testing a sample of {len(samples)} products...")

results = []
with ThreadPoolExecutor(max_workers=20) as executor:
    futures = {executor.submit(check_image, p): p for p in samples}
    for fut in as_completed(futures):
        results.append(fut.result())

failures = [r for r in results if r[1] != "ok"]
ok = [r for r in results if r[1] == "ok"]

print(f"Sample results: OK: {len(ok)}, Failures: {len(failures)}")
print("\nFirst 10 Failures:")
for f in failures[:10]:
    print(f"  ID: {f[0]}, Status: {f[1]}, URL: {f[2]}")
