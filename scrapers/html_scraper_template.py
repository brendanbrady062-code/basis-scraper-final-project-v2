"""
Template for scraping websites with simple HTML parsing (no JavaScript required)
"""
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from .base_scraper import BaseScraper


class HTMLScraper(BaseScraper):
    """
    Template for scraping websites using requests and BeautifulSoup
    
    For websites that serve content directly in HTML without JavaScript rendering.
    """
    
    def __init__(self, name: str, url: str, data_dir: str = "data"):
        """
        Initialize HTML scraper
        
        Args:
            name: Name of the scraper
            url: URL to scrape
            data_dir: Directory to save CSV files
        """
        super().__init__(name, data_dir)
        self.url = url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def fetch_html(self) -> str:
        """
        Fetch HTML content from the URL
        
        Returns:
            HTML content as string
        """
        try:
            response = requests.get(
                self.url,
                headers=self.headers,
                timeout=10,
                verify=False,
            )
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching {self.url}: {e}")
            return None
    
    def parse_html(self, html: str) -> List[Dict[str, Any]]:
        """
        Parse HTML and extract basis values
        
        This method should be overridden in subclasses
        
        Args:
            html: HTML content
        
        Returns:
            List of dictionaries with extracted data
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        # TODO: Customize this parsing logic for your specific website
        # Example structure - modify based on actual HTML structure:
        data = []
        
        # Find the relevant elements using soup.find() or soup.select()
        # Extract basis values and other relevant information
        
        return data
    
    def scrape(self) -> List[Dict[str, Any]]:
        """
        Main scraping method
        
        Returns:
            List of dictionaries containing basis values
        """
        print(f"Fetching content from: {self.url}")
        
        html = self.fetch_html()
        if not html:
            return []
        
        data = self.parse_html(html)
        print(f"Extracted {len(data)} records")
        
        return data
