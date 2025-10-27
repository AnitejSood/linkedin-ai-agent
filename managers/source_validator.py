"""
Source Validator - Validates and extracts credible sources
"""

from typing import List, Dict
from utils.helpers import extract_domain, load_json
from utils.logger import setup_logger

logger = setup_logger()

class SourceValidator:
    """Validates source credibility and extracts top sources"""
    
    def __init__(self):
        # Load credible domains from sources.json
        sources_data = load_json("data/sources.json")
        self.credible_domains = sources_data.get("credible_domains", [])
        logger.info(f"Loaded {len(self.credible_domains)} credible domains")
    
    def is_credible(self, url: str) -> bool:
        """Check if a URL is from a credible domain"""
        if not url:
            return False
        domain = extract_domain(url)
        return any(credible in domain for credible in self.credible_domains)
    
    def extract_sources(self, articles: List[Dict], num_sources: int = 4) -> List[Dict]:
        """
        Extract top credible sources from articles
        
        Returns:
            List of source dictionaries with 'title' and 'url'
        """
        credible_sources = []
        
        for article in articles:
            url = article.get('url', '')
            if self.is_credible(url):
                credible_sources.append({
                    'title': article.get('title', 'Untitled'),
                    'url': url
                })
        
        # Return top N sources
        result = credible_sources[:num_sources]
        logger.info(f"Extracted {len(result)} credible sources")
        return result
