"""
Improved news scraper with better headers, delays, and error handling
"""

import requests
import time
import random
from bs4 import BeautifulSoup
from typing import List, Dict
from scrapers.base_scraper import BaseScraper
from utils.logger import setup_logger
from utils.helpers import clean_text

logger = setup_logger()

class NewsScraper(BaseScraper):
    """Scraper for news websites with anti-blocking measures"""
    
    def __init__(self, source_name: str, source_url: str):
        super().__init__(source_name, source_url)
        
        # Realistic browser headers to avoid detection
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        }
    
    def scrape(self) -> List[Dict]:
        """Scrape articles with delays and proper headers"""
        try:
            logger.info(f"Scraping {self.source_name}...")
            
            # Add random delay to appear more human-like
            time.sleep(random.uniform(2, 5))
            
            # Make request with headers
            response = requests.get(
                self.source_url, 
                headers=self.headers,
                timeout=30,
                allow_redirects=True
            )
            
            # Check response status
            if response.status_code == 429:
                logger.warning(f"{self.source_name}: Rate limited (429). Waiting...")
                time.sleep(60)  # Wait 1 minute
                return []
            
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = self.parse_articles(soup)
            
            logger.info(f"Found {len(articles)} articles from {self.source_name}")
            return articles
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error scraping {self.source_name}: {e}")
            return []
        except Exception as e:
            logger.error(f"Error scraping {self.source_name}: {e}")
            return []
    
    def parse_article(self, element) -> Dict:
        """Parse single article element"""
        try:
            # Try multiple possible selectors for title
            title = (element.find('h2') or 
                    element.find('h3') or 
                    element.find('a', class_=['title', 'post-title', 'entry-title']))
            
            # Try to find link
            link = element.find('a', href=True)
            
            # Try to find summary/description
            summary = (element.find('p') or 
                      element.find('div', class_=['excerpt', 'summary', 'description']))
            
            if not title or not link:
                return {}
            
            article_url = link.get('href', '')
            
            # Handle relative URLs
            if article_url and not article_url.startswith('http'):
                from urllib.parse import urljoin
                article_url = urljoin(self.source_url, article_url)
            
            return {
                'title': clean_text(title.get_text()) if title else "",
                'url': article_url,
                'summary': clean_text(summary.get_text()[:300]) if summary else "",
                'source': self.source_name,
                'date': None
            }
        except Exception as e:
            logger.error(f"Error parsing article: {e}")
            return {}
    
    def parse_articles(self, soup) -> List[Dict]:
        """Parse all articles from page with multiple selector strategies"""
        articles = []
        
        # Multiple strategies to find articles
        selectors = [
            'article',
            'div.post',
            'div.article',
            'div.entry',
            'div[class*="post"]',
            'div[class*="article"]',
            'li.post',
            'div.wp-block-post'
        ]
        
        article_elements = []
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                article_elements = elements
                logger.info(f"Found articles using selector: {selector}")
                break
        
        if not article_elements:
            logger.warning(f"No articles found for {self.source_name}")
            return []
        
        # Parse each article
        for element in article_elements[:10]:
            article = self.parse_article(element)
            if article and article.get('title') and article.get('url'):
                articles.append(article)
        
        return articles
