from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseScraper(ABC):
    """
    Abstract Base Class for all brand web scrapers.
    """
    def __init__(self, brand_name: str, brand_url: str):
        self.brand_name = brand_name
        self.brand_url = brand_url

    @abstractmethod
    def scrape(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Scrape products from the brand website.
        Should return a list of dicts matching the product schema guidelines:
        - brand: str
        - name: str
        - description: str
        - price: float
        - originalPrice: Optional[float]
        - rating: Optional[float]
        - reviewCount: Optional[int]
        - productUrl: str
        - imageUrl: str
        - brandUrl: str
        - tags: List[str]
        - materials: List[str]
        - category: str
        """
        pass
