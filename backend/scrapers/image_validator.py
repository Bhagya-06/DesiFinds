import requests
from typing import Tuple

class DataValidator:
    """
    Validates product links and image URLs using HTTP requests.
    """
    def __init__(self, timeout: int = 5):
        self.timeout = timeout
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    def validate_url(self, url: str) -> bool:
        """
        Check if a URL is valid and returns a successful response code.
        Supports both HEAD and GET fallback.
        """
        if not url or not url.startswith("http"):
            return False
            
        try:
            # Try HEAD first for performance
            resp = requests.head(url, headers=self.headers, timeout=self.timeout, allow_redirects=True)
            if resp.status_code in [200, 301, 302]:
                return True
                
            # Fallback to GET in case HEAD is blocked
            resp_get = requests.get(url, headers=self.headers, timeout=self.timeout, stream=True, allow_redirects=True)
            return resp_get.status_code in [200, 301, 302]
        except Exception:
            return False

    def validate_image_url(self, url: str) -> bool:
        """
        Check if an image URL returns 200 OK and contains an image Content-Type.
        """
        if not url or not url.startswith("http"):
            return False
            
        try:
            # Try HEAD first
            resp = requests.head(url, headers=self.headers, timeout=self.timeout, allow_redirects=True)
            if resp.status_code == 200:
                content_type = resp.headers.get("Content-Type", "")
                if "image" in content_type:
                    return True
                    
            # Fallback to GET (stream content to avoid downloading huge files)
            resp_get = requests.get(url, headers=self.headers, timeout=self.timeout, stream=True, allow_redirects=True)
            if resp_get.status_code == 200:
                content_type = resp_get.headers.get("Content-Type", "")
                # Some CDNs return generic binary streams or webp
                if "image" in content_type or "octet-stream" in content_type:
                    return True
            return False
        except Exception:
            return False
            
    def validate_product(self, product: dict) -> Tuple[bool, str]:
        """
        Validates both the product link and the image URL of a product dict.
        Returns a tuple: (is_valid, error_reason).
        """
        if not self.validate_url(product.get("productUrl", "")):
            return False, "Invalid productUrl"
            
        if not self.validate_image_url(product.get("imageUrl", "")):
            return False, "Invalid imageUrl"
            
        return True, ""
