import os
import json
import unittest
import requests

BACKEND_URL = "http://127.0.0.1:8080"
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PRODUCTS_JSON_PATH = os.path.join(PROJECT_ROOT, "data", "products.json")

class DesiFindsTestSuite(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # Verify backend is running
        try:
            r = requests.get(f"{BACKEND_URL}/api/healthz", timeout=5)
            cls.backend_available = r.status_code == 200
        except Exception:
            cls.backend_available = False
            print(f"Warning: Backend is not responding at {BACKEND_URL}. Some API tests will be skipped.")

        # Load database for direct tests
        cls.products = []
        if os.path.exists(PRODUCTS_JSON_PATH):
            try:
                with open(PRODUCTS_JSON_PATH, "r", encoding="utf-8") as f:
                    cls.products = json.load(f)
            except Exception as e:
                print(f"Error loading database: {e}")

    # ==========================================
    # DATABASE & DATA INTEGRITY TESTS (8 Tests)
    # ==========================================

    def test_01_database_exists(self):
        """Test that the products.json database file exists in the expected path."""
        self.assertTrue(os.path.exists(PRODUCTS_JSON_PATH), "data/products.json does not exist")

    def test_02_database_size(self):
        """Test that database has at least 3,150 real products."""
        self.assertGreaterEqual(len(self.products), 3150, f"Expected >= 3150 products, got {len(self.products)}")

    def test_03_database_integrity_unique_ids(self):
        """Test that all products in the database have unique IDs."""
        ids = [p.get("id") for p in self.products if p.get("id")]
        self.assertEqual(len(ids), len(set(ids)), "Found duplicate product IDs in the database!")

    def test_04_database_integrity_critical_fields(self):
        """Test that critical fields (id, name, brand, category, productUrl, imageUrl) are present and valid."""
        for p in self.products:
            pid = p.get("id", "Unknown ID")
            self.assertTrue(p.get("id"), f"Product {pid} is missing 'id'")
            self.assertTrue(p.get("name"), f"Product {pid} is missing 'name'")
            self.assertTrue(p.get("brand"), f"Product {pid} is missing 'brand'")
            self.assertTrue(p.get("category"), f"Product {pid} is missing 'category'")
            self.assertTrue(p.get("productUrl"), f"Product {pid} is missing 'productUrl'")
            self.assertTrue(p.get("imageUrl"), f"Product {pid} is missing 'imageUrl'")

    def test_05_database_integrity_prices(self):
        """Test that price and originalPrice fields are positive numbers, and discount price <= originalPrice."""
        for p in self.products:
            pid = p.get("id")
            price = p.get("price")
            orig_price = p.get("originalPrice")
            
            self.assertIsNotNone(price, f"Product {pid} has null price")
            self.assertIsNotNone(orig_price, f"Product {pid} has null originalPrice")
            
            self.assertTrue(isinstance(price, (int, float)), f"Product {pid} price is not a number: {price}")
            self.assertTrue(isinstance(orig_price, (int, float)), f"Product {pid} originalPrice is not a number: {orig_price}")
            
            self.assertGreaterEqual(price, 0, f"Product {pid} price is negative: {price}")
            self.assertGreaterEqual(orig_price, 0, f"Product {pid} originalPrice is negative: {orig_price}")
            self.assertLessEqual(price, orig_price, f"Product {pid} price ({price}) is higher than originalPrice ({orig_price})")

    def test_06_database_integrity_ratings(self):
        """Test that ratings are within [1.0, 5.0] range or None/0, and review counts are non-negative integers."""
        for p in self.products:
            pid = p.get("id")
            rating = p.get("rating")
            rev_count = p.get("reviewCount")
            
            if rating is not None:
                self.assertTrue(isinstance(rating, (int, float)), f"Product {pid} rating is not a number: {rating}")
                self.assertTrue(0.0 <= rating <= 5.0, f"Product {pid} rating out of bounds [0, 5]: {rating}")
            
            if rev_count is not None:
                self.assertTrue(isinstance(rev_count, int), f"Product {pid} reviewCount is not an int: {rev_count}")
                self.assertGreaterEqual(rev_count, 0, f"Product {pid} reviewCount is negative: {rev_count}")

    def test_07_database_integrity_badges(self):
        """Test that badges exist and are parsed as a list of strings."""
        for p in self.products:
            pid = p.get("id")
            badges = p.get("badges")
            self.assertIsNotNone(badges, f"Product {pid} has null badges list")
            self.assertTrue(isinstance(badges, list), f"Product {pid} badges is not a list: {badges}")
            for b in badges:
                self.assertTrue(isinstance(b, str), f"Product {pid} contains a non-string badge: {b}")

    def test_08_database_categories_distribution(self):
        """Test that products span a rich variety of Indian categories (Apparel, Footwear, Skincare, Audio, etc.)."""
        categories = set(p.get("category") for p in self.products if p.get("category"))
        expected_cats = {"Apparel", "Footwear", "Skincare", "Audio", "Watches", "Electronics", "Bags"}
        # Check if we have at least 5 of the key categories represented
        intersection = categories.intersection(expected_cats)
        self.assertGreaterEqual(len(intersection), 5, f"Expected key categories representation, got: {categories}")

    # ==========================================
    # API ENDPOINT TESTS (15 Tests)
    # ==========================================

    def test_09_api_healthz(self):
        """Test /api/healthz endpoint returns 200 and status: ok."""
        if not self.backend_available:
            self.skipTest("Backend server not available")
        r = requests.get(f"{BACKEND_URL}/api/healthz")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), {"status": "ok"})

    def test_10_api_status(self):
        """Test /api/status endpoint returns ingestion status."""
        if not self.backend_available:
            self.skipTest("Backend server not available")
        r = requests.get(f"{BACKEND_URL}/api/status")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn("status", data)

    def test_11_api_workflow(self):
        """Test /api/workflow returns list of nodes."""
        if not self.backend_available:
            self.skipTest("Backend server not available")
        r = requests.get(f"{BACKEND_URL}/api/workflow")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertTrue(isinstance(data, list))
        self.assertGreater(len(data), 0)
        self.assertIn("name", data[0])

    def test_12_api_categories(self):
        """Test /api/categories returns a list sorted by count descending."""
        if not self.backend_available:
            self.skipTest("Backend server not available")
        r = requests.get(f"{BACKEND_URL}/api/categories")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertTrue(isinstance(data, list))
        self.assertGreater(len(data), 0)
        self.assertIn("name", data[0])
        self.assertIn("count", data[0])
        self.assertIn("icon", data[0])
        # Verify counts are descending
        counts = [c["count"] for c in data]
        self.assertEqual(counts, sorted(counts, reverse=True))

    def test_13_api_brands(self):
        """Test /api/brands returns a valid list of metadata brands."""
        if not self.backend_available:
            self.skipTest("Backend server not available")
        r = requests.get(f"{BACKEND_URL}/api/brands")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertTrue(isinstance(data, list))
        self.assertGreater(len(data), 0)
        self.assertIn("name", data[0])
        self.assertIn("founded", data[0])

    def test_14_api_trending(self):
        """Test /api/trending returns top products, searches, and new arrivals."""
        if not self.backend_available:
            self.skipTest("Backend server not available")
        r = requests.get(f"{BACKEND_URL}/api/trending")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn("popularSearches", data)
        self.assertIn("topProducts", data)
        self.assertIn("newArrivals", data)
        self.assertTrue(isinstance(data["topProducts"], list))
        self.assertGreater(len(data["topProducts"]), 0)

    def test_15_api_products_list_default(self):
        """Test /api/products returns correct response structure and paginated default list."""
        if not self.backend_available:
            self.skipTest("Backend server not available")
        r = requests.get(f"{BACKEND_URL}/api/products")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn("products", data)
        self.assertIn("total", data)
        self.assertIn("offset", data)
        self.assertIn("limit", data)
        self.assertEqual(len(data["products"]), data["limit"])

    def test_16_api_products_pagination(self):
        """Test pagination limit and offset parameters work correctly."""
        if not self.backend_available:
            self.skipTest("Backend server not available")
        r_limit = requests.get(f"{BACKEND_URL}/api/products?limit=10")
        self.assertEqual(r_limit.status_code, 200)
        data_limit = r_limit.json()
        self.assertEqual(len(data_limit["products"]), 10)
        
        r_offset = requests.get(f"{BACKEND_URL}/api/products?limit=10&offset=10")
        self.assertEqual(r_offset.status_code, 200)
        data_offset = r_offset.json()
        self.assertNotEqual(data_limit["products"][0]["id"], data_offset["products"][0]["id"])

    def test_17_api_products_category_filter(self):
        """Test category filter works on products list."""
        if not self.backend_available:
            self.skipTest("Backend server not available")
        r = requests.get(f"{BACKEND_URL}/api/products?category=Skincare&limit=10")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        for p in data["products"]:
            self.assertEqual(p["category"], "Skincare")

    def test_18_api_products_brand_filter(self):
        """Test brand filter works on products list."""
        if not self.backend_available:
            self.skipTest("Backend server not available")
        # Use Snitch as a test case since it is a popular brand
        r = requests.get(f"{BACKEND_URL}/api/products?brand=Snitch&limit=10")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        for p in data["products"]:
            self.assertIn("snitch", p["brand"].lower())

    def test_19_api_products_price_filter(self):
        """Test minPrice and maxPrice filtering."""
        if not self.backend_available:
            self.skipTest("Backend server not available")
        r = requests.get(f"{BACKEND_URL}/api/products?minPrice=500&maxPrice=1500&limit=20")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        for p in data["products"]:
            self.assertTrue(500 <= p["price"] <= 1500, f"Product price {p['price']} is out of range [500, 1500]")

    def test_20_api_products_rating_filter(self):
        """Test rating filtering."""
        if not self.backend_available:
            self.skipTest("Backend server not available")
        r = requests.get(f"{BACKEND_URL}/api/products?minRating=4.5&limit=10")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        for p in data["products"]:
            rating = p.get("rating")
            if rating is not None:
                self.assertGreaterEqual(rating, 4.5)

    def test_21_api_product_details(self):
        """Test details fetching for existing and non-existing products."""
        if not self.backend_available:
            self.skipTest("Backend server not available")
        if not self.products:
            self.skipTest("No products in database")
        
        # Test valid detail
        pid = self.products[0]["id"]
        r = requests.get(f"{BACKEND_URL}/api/products/{pid}")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["id"], pid)
        
        # Test 404
        r_404 = requests.get(f"{BACKEND_URL}/api/products/non-existent-id-xyz")
        self.assertEqual(r_404.status_code, 404)

    def test_22_api_chat_history(self):
        """Test fetching chat history."""
        if not self.backend_available:
            self.skipTest("Backend server not available")
        r = requests.get(f"{BACKEND_URL}/api/chat-history")
        self.assertEqual(r.status_code, 200)
        self.assertTrue(isinstance(r.json(), list))

    def test_23_api_chat_assistant_fallback(self):
        """Test chat fallback response for brand questions and standard recommendations."""
        if not self.backend_available:
            self.skipTest("Backend server not available")
        
        # Test brand inquiry fallback
        payload = {"message": "Who founded boAt?"}
        r = requests.post(f"{BACKEND_URL}/api/chat", json=payload)
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn("response", data)
        self.assertIn("Aman Gupta", data["response"])
        
        # Test keyword matching fallback
        payload_rec = {"message": "Show me some Snitch shirts"}
        r_rec = requests.post(f"{BACKEND_URL}/api/chat", json=payload_rec)
        self.assertEqual(r_rec.status_code, 200)
        data_rec = r_rec.json()
        self.assertIn("response", data_rec)
        self.assertIn("retrievedProducts", data_rec)

if __name__ == "__main__":
    unittest.main()
