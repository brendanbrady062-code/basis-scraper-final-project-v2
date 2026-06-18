"""
Base scraper class for all website scrapers
"""
import csv
import os
from datetime import datetime
from abc import ABC, abstractmethod
from typing import List, Dict, Any

import urllib3


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class BaseScraper(ABC):
    """Abstract base class for all basis value scrapers"""
    
    def __init__(self, name: str, data_dir: str = "data"):
        """
        Initialize the scraper
        
        Args:
            name: Name of the scraper (used for output filename)
            data_dir: Directory to save CSV files
        """
        self.name = name
        self.data_dir = data_dir
        self.timestamp = datetime.now()
        
        # Create data directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
    
    @abstractmethod
    def scrape(self) -> List[Dict[str, Any]]:
        """
        Scrape the website and return data
        
        Returns:
            List of dictionaries containing scraped data
        """
        pass
    
    def save_to_csv(self, data: List[Dict[str, Any]], filename: str = None) -> str:
        """
        Save scraped data to CSV file
        
        Args:
            data: List of dictionaries to save
            filename: Optional custom filename (without extension)
        
        Returns:
            Path to saved CSV file
        """
        if not data:
            print(f"Warning: No data to save for {self.name}")
            return None
        
        # Generate filename if not provided
        if filename is None:
            filename = f"{self.name}_{self.timestamp.strftime('%Y%m%d_%H%M%S')}"
        
        filepath = os.path.join(self.data_dir, f"{filename}.csv")
        
        # Get fieldnames from first record
        fieldnames = list(data[0].keys())
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            
            print(f"✓ Data saved to: {filepath}")
            return filepath
        
        except Exception as e:
            print(f"✗ Error saving to CSV: {e}")
            return None
    
    def run(self, filename: str = None) -> str:
        """
        Execute the scraper and save results
        
        Args:
            filename: Optional custom filename for CSV
        
        Returns:
            Path to saved CSV file
        """
        print(f"\n{'='*60}")
        print(f"Running scraper: {self.name}")
        print(f"{'='*60}")
        
        try:
            data = self.scrape()
            return self.save_to_csv(data, filename)
        except Exception as e:
            print(f"✗ Error during scraping: {e}")
            return None
