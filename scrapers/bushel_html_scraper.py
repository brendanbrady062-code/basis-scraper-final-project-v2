"""
Scraper for Bushel-style cash bid HTML pages.
"""
import calendar
import re
from datetime import date
from typing import Any, Dict, List, Optional, Tuple

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
    "june": 6,
    "jul": 7,
    "july": 7,
    "aug": 8,
    "sept": 9,
    "sep": 9,
    "oct": 10,
    "nov": 11,
    "dec": 12,
}

SEASON_RANGES = {
    "fall": ((9, 1), (10, 31)),
}


class BushelHTMLScraper(BaseScraper):
    """Scraper for cash bid pages with Bushel-style location sections."""

    def __init__(
        self,
        name: str,
        url: str,
        location: str,
        data_dir: str = "data",
        section_filter: Optional[str] = None,
        forced_commodity: Optional[str] = None,
    ):
        super().__init__(name, data_dir)
        self.url = url
        self.location = location
        self.section_filter = (section_filter or location).lower()
        self.forced_commodity = forced_commodity
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36"
            )
        }

    def scrape(self) -> List[Dict[str, Any]]:
        print(f"Fetching Bushel HTML bids from: {self.url}")
        response = requests.get(
            self.url,
            headers=self.headers,
            timeout=20,
            verify=False,
        )
        response.raise_for_status()
        rows = self.parse_html(response.text)
        print(f"Extracted {len(rows)} records")
        return rows

    def parse_html(self, html: str) -> List[Dict[str, Any]]:
        soup = BeautifulSoup(html, "html.parser")
        page_year = self._find_page_year(soup) or date.today().year
        rows = []

        for section in soup.select("div.cashBidLocation"):
            heading = section.find("h2")
            section_name = heading.get_text(" ", strip=True) if heading else ""
            if self.section_filter not in section_name.lower():
                continue

            current_commodity = self.forced_commodity or ""
            for child in section.find_all(["h3", "ul"]):
                if child.name == "h3":
                    current_commodity = self.forced_commodity or self._clean_commodity(
                        child.get_text(" ", strip=True)
                    )
                    continue

                cells = [li.get_text(" ", strip=True) for li in child.find_all("li")]
                if len(cells) < 6 or cells[0].lower() == "delivery":
                    continue

                delivery_start, delivery_end = self._delivery_range(cells[0], page_year)
                rows.append(
                    {
                        "location": self.location,
                        "basis": self._format_basis(cells[2]),
                        "delivery_start": delivery_start,
                        "delivery_end": delivery_end,
                        "symbol": cells[5],
                        "cash_price": self._format_currency(cells[1]),
                        "commodity": current_commodity,
                    }
                )

        return rows

    def _find_page_year(self, soup: BeautifulSoup) -> Optional[int]:
        match = re.search(r"Cash bids for .*?, .*?(\d{4})", soup.get_text(" ", strip=True))
        if match:
            return int(match.group(1))
        return None

    def _delivery_range(self, delivery: str, page_year: int) -> Tuple[str, str]:
        parts = delivery.lower().replace(".", "").split()
        if not parts:
            return delivery, delivery

        season = SEASON_RANGES.get(parts[0])
        if season:
            year = page_year
            for part in parts[1:]:
                if part.isdigit():
                    year = 2000 + int(part) if len(part) == 2 else int(part)
                    break
            (start_month, start_day), (end_month, end_day) = season
            return (
                f"{start_month:02d}/{start_day:02d}/{year}",
                f"{end_month:02d}/{end_day:02d}/{year}",
            )

        month = MONTHS.get(parts[0][:4]) or MONTHS.get(parts[0][:3])
        year = page_year

        for part in parts[1:]:
            if part.isdigit():
                year = 2000 + int(part) if len(part) == 2 else int(part)
                break

        if not month:
            return delivery, delivery

        last_day = calendar.monthrange(year, month)[1]
        return f"{month:02d}/01/{year}", f"{month:02d}/{last_day:02d}/{year}"

    def _clean_commodity(self, value: str) -> str:
        lowered = value.lower()
        if "corn" in lowered or lowered in {"yc", "yellow corn"}:
            return "Corn"
        if "soy" in lowered or "bean" in lowered:
            return "Beans"
        return value

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
