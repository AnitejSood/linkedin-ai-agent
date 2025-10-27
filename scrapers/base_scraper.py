"""
Base scraper class - Abstract base for all scrapers
"""

from abc import ABC, abstractmethod
from typing import List, Dict

class BaseScraper(ABC):
    """Abstract base class for all scrapers"""
    
    def __init__(self, source_name: str, source_url: str):
        self.source_name = source_name
        self.source_url = source_url
    
    @abstractmethod
    def scrape(self) -> List[Dict]:
        """
        Scrape articles from the source
        
        Returns:
            List of article dictionaries with keys:
            - title: Article title
            - summary: Article summary/description
            - url: Article URL
            - date: Publication date
            - source: Source name
        """
        pass
    
    @abstractmethod
    def parse_article(self, html) -> Dict:
        """Parse individual article from HTML"""
        pass
