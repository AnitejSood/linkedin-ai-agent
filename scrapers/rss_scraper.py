"""
RSS Feed scraper - More reliable than HTML scraping
"""

import feedparser
import time
import random
from typing import List, Dict
from scrapers.base_scraper import BaseScraper
from utils.logger import setup_logger

logger = setup_logger()

class RSSFeedScraper(BaseScraper):
    """Scraper for RSS feeds - more reliable for news sites"""
    
    def scrape(self) -> List[Dict]:
        """Scrape articles from RSS feed"""
        try:
            logger.info(f"Scraping RSS feed: {self.source_name}...")
            
            # Add delay
            time.sleep(random.uniform(1, 3))
            
            # Parse RSS feed
            feed = feedparser.parse(self.source_url)
            
            if not feed.entries:
                logger.warning(f"No entries found in RSS feed: {self.source_name}")
                return []
            
            articles = []
            for entry in feed.entries[:10]:
                article = self.parse_article(entry)
                if article:
                    articles.append(article)
            
            logger.info(f"Found {len(articles)} articles from {self.source_name}")
            return articles
            
        except Exception as e:
            logger.error(f"Error scraping RSS feed {self.source_name}: {e}")
            return []
    
    def parse_article(self, entry) -> Dict:
        """Parse single RSS entry"""
        try:
            return {
                'title': entry.get('title', '').strip(),
                'url': entry.get('link', ''),
                'summary': entry.get('summary', '')[:300],
                'source': self.source_name,
                'date': entry.get('published', None)
            }
        except Exception as e:
            logger.error(f"Error parsing RSS entry: {e}")
            return {}
