"""
Scraper for CIHedging cash bid widgets.
"""
import calendar
from typing import Any, Dict, List, Tuple

import requests
from bs4 import BeautifulSoup

from .base_scraper import BaseScraper


MONTHS = {
    "jan": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "may": 5,
    "jun": 6,
    "jul": 7,
    "aug": 8,
    "sep": 9,
    "oct": 10,
    "nov": 11,
    "dec": 12,
}


class CIHedgingScraper(BaseScraper):
    """Scraper for CIHedging widget HTML returned by company id."""

    URL_TEMPLATE = "https://www.cihedging.com/cih/api/index.cfm/origination/cashbids/{company_id}"

    def __init__(
        self,
        name: str,
        company_id: str,
        location: str,
        data_dir: str = "data",
        forced_commodity: str = "Corn",
    ):
        super().__init__(name, data_dir)
        self.company_id = company_id
        self.location = location
        self.forced_commodity = forced_commodity
        self.headers = {
            "Accept": "application/json,text/html,*/*",
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36"
            ),
        }

    def scrape(self) -> List[Dict[str, Any]]:
        print(f"Fetching CIHedging bids for company id: {self.company_id}")
        response = requests.post(
            self.URL_TEMPLATE.format(company_id=self.company_id),
            headers=self.headers,
            timeout=20,
            verify=False,
        )
        response.raise_for_status()
        html = response.json() if response.text.startswith('"') else response.text
        rows = self.parse_html(html)
        print(f"Extracted {len(rows)} records")
        return rows

    def parse_html(self, html: str) -> List[Dict[str, Any]]:
        soup = BeautifulSoup(html, "html.parser")
        rows = []

        for table in soup.find_all("table"):
            header_cells = [
                cell.get_text(" ", strip=True).lower()
                for cell in table.find_all("tr")[0].find_all(["th", "td"])
            ] if table.find("tr") else []
            if not {"delivery", "basis", "bid"}.issubset(set(header_cells)):
                continue

            for tr in table.find_all("tr")[1:]:
                cells = [cell.get_text(" ", strip=True) for cell in tr.find_all(["th", "td"])]
                if len(cells) < 5:
                    continue

                delivery_start, delivery_end = self._delivery_range(cells[0])
                rows.append(
                    {
                        "location": self.location,
                        "basis": self._format_basis(cells[-2]),
                        "delivery_start": delivery_start,
                        "delivery_end": delivery_end,
                        "symbol": cells[1],
                        "cash_price": self._format_currency(cells[-1]),
                        "commodity": self.forced_commodity,
                    }
                )

        return rows

    def _delivery_range(self, delivery: str) -> Tuple[str, str]:
        parts = delivery.lower().replace("'", "").split()
        if len(parts) < 2:
            return delivery, delivery

        month = MONTHS.get(parts[0][:3])
        year = int(parts[1])
        if year < 100:
            year += 2000
        if not month:
            return delivery, delivery

        last_day = calendar.monthrange(year, month)[1]
        return f"{month:02d}/01/{year}", f"{month:02d}/{last_day:02d}/{year}"

    def _format_basis(self, value: str) -> str:
        value = value.replace("$", "").strip()
        if not value:
            return ""
        number = float(value) * 100
        if number.is_integer():
            return str(int(number))
        return f"{number:.2f}".rstrip("0").rstrip(".")

    def _format_currency(self, value: str) -> str:
        value = value.replace("$", "").strip()
        if not value:
            return ""
        return f"${float(value):.4f}"
