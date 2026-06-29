"""
Standalone scraper for CGB Hennepin location cash bids.
"""
from CGB_scrape import CGBScraper

if __name__ == "__main__":
    scraper = CGBScraper("CGB_hennepin", location_id="20592")
    scraper.run()
