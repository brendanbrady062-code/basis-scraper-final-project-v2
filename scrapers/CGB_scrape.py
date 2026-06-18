"""
CGB cash bids scraper.
"""
from typing import Any, Dict, List, Optional

import requests
from bs4 import BeautifulSoup

try:
    from .base_scraper import BaseScraper
except ImportError:
    from base_scraper import BaseScraper


CGB_CASH_BIDS_URL_TEMPLATE = (
    "https://cgb.agricharts.com/inc/cashbids/cashbids-js.php?"
    "filter=all&location=cgblocation&commodity=&groupby=location&width=90%25"
    "&showtimestamp=1&showchart=1&format=table"
    "&fields=name%2Cdelivery_start%2Cdelivery_end%2Cbasismonth%2Cfutures%2C"
    "futureschange%2Cbasis%2Cprice"
    "&groupheading=table&bidsort=commodity&dateformat=%25m%2F%25d%2F%25Y"
    "&months=11&&acCnt=1&format=table&groupby=location&setLocation="
    "&commodity=&location={location_id}"
)


class CGBScraper(BaseScraper):
    """Scraper for CGB cash bids data."""

    def __init__(
        self,
        name: str,
        url: Optional[str] = None,
        data_dir: str = "data",
        location_id: Optional[str] = None,
        location_filter: Optional[str] = None,
        allowed_commodities: Optional[List[str]] = None,
    ):
        super().__init__(name, data_dir)

        if not url and location_id:
            url = CGB_CASH_BIDS_URL_TEMPLATE.format(location_id=location_id)
        if not url:
            raise ValueError("CGBScraper requires either url or location_id")

        self.url = url
        self.location_filter = location_filter.lower() if location_filter else None
        self.allowed_commodities = (
            {commodity.lower() for commodity in allowed_commodities}
            if allowed_commodities
            else None
        )
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36"
            )
        }

    def fetch_page(self) -> Optional[str]:
        try:
            response = requests.get(
                self.url,
                headers=self.headers,
                timeout=10,
                verify=False,
            )
            response.raise_for_status()
            return response.text
        except requests.RequestException as exc:
            print(f"Error fetching {self.url}: {exc}")
            return None

    def parse_data(self, html: str) -> List[Dict[str, Any]]:
        soup = BeautifulSoup(html, "html.parser")
        rows = []

        tables = soup.find_all("table")
        if not tables:
            tables = [soup]

        for table in tables:
            location = self._find_location_for_table(table)

            for row in table.find_all("tr"):
                cells = row.find_all("td")
                if len(cells) < 8:
                    continue

                commodity = cells[0].get_text(strip=True)
                delivery_start = cells[1].get_text(strip=True)
                delivery_end = cells[2].get_text(strip=True)
                symbol = cells[3].get_text(strip=True)
                basis = cells[6].get_text(strip=True)
                cash_price = cells[7].get_text(strip=True)

                if not commodity or commodity.lower() == "name" or not delivery_start:
                    continue
                if self.location_filter and self.location_filter not in location.lower():
                    continue
                if (
                    self.allowed_commodities is not None
                    and commodity.lower() not in self.allowed_commodities
                ):
                    continue

                rows.append(
                    {
                        "location": location or "",
                        "basis": basis,
                        "delivery_start": delivery_start,
                        "delivery_end": delivery_end,
                        "symbol": symbol,
                        "cash_price": cash_price,
                        "commodity": commodity,
                    }
                )

        return rows

    def _find_location_for_table(self, table) -> str:
        heading = table.find_previous(
            lambda tag: tag.name in ["h1", "h2", "h3", "h4", "h5", "strong", "b", "p", "div"]
            and tag.get_text(strip=True)
        )
        if heading:
            location = heading.get_text(separator="", strip=True)
            for header_text in ["NameDelivery", "Name Delivery"]:
                if header_text in location:
                    location = location.split(header_text)[0].strip()
            return location

        first_row = table.find("tr")
        if first_row:
            first_cells = first_row.find_all(["th", "td"])
            if len(first_cells) == 1:
                return first_cells[0].get_text(strip=True)

        return ""

    def scrape(self) -> List[Dict[str, Any]]:
        print(f"Fetching CGB cash bids from: {self.url}")

        html = self.fetch_page()
        if not html:
            print("Failed to fetch page")
            return []

        data = self.parse_data(html)
        print(f"Extracted {len(data)} records")
        return data


if __name__ == "__main__":
    scraper = CGBScraper("CGB_hennepin", location_id="20592")
    scraper.run()
