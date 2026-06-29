"""
Scraper for Barchart/Cargill JSONP cash bid endpoints.
"""
import json
import re
from typing import Any, Dict, List, Optional

import requests

from .base_scraper import BaseScraper


COMMODITY_NAMES = {
    "corn": "Corn",
    "soybean": "Beans",
    "soybeans": "Beans",
    "beans": "Beans",
}


class BarchartJSONPScraper(BaseScraper):
    """Scraper for Cargill/Barchart JSONP cash bid feeds."""

    def __init__(
        self,
        name: str,
        url: str,
        location: str,
        data_dir: str = "data",
        allowed_commodities: Optional[List[str]] = None,
        product_filter: Optional[str] = None,
        product_filter_exclude: Optional[str] = None,
    ):
        super().__init__(name, data_dir)
        self.url = url
        self.location = location
        self.allowed_commodities = {
            COMMODITY_NAMES.get(commodity.lower(), commodity)
            for commodity in (allowed_commodities or [])
        }
        self.product_filter = product_filter.lower() if product_filter else None
        self.product_filter_exclude = product_filter_exclude.lower() if product_filter_exclude else None
        self.headers = {
            "Accept": "application/json,text/javascript,*/*",
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36"
            ),
        }

    def scrape(self) -> List[Dict[str, Any]]:
        print(f"Fetching Barchart JSONP bids from: {self.url}")
        response = requests.get(
            self.url,
            headers=self.headers,
            timeout=20,
            verify=False,
        )
        response.raise_for_status()
        data = self._parse_jsonp(response.text)
        rows = self.parse_data(data)
        print(f"Extracted {len(rows)} records")
        return rows

    def parse_data(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        rows = []
        for group in data.get("bigGroups", []):
            commodity = self._normalize_commodity(group.get("name", ""))
            if not commodity:
                continue
            if self.allowed_commodities and commodity not in self.allowed_commodities:
                continue
            group_name = group.get("name", "").lower()
            if self.product_filter:
                if self.product_filter not in group_name:
                    continue
            if self.product_filter_exclude:
                if self.product_filter_exclude in group_name:
                    continue

            for bid in group.get("cashbids", []):
                rows.append(
                    {
                        "location": self.location,
                        "basis": self._format_basis(bid.get("basis")),
                        "delivery_start": bid.get("delivery_start", ""),
                        "delivery_end": bid.get("delivery_end", ""),
                        "symbol": bid.get("futuresymbol") or group.get("symbol", ""),
                        "cash_price": self._format_currency(
                            bid.get("flatprice") or bid.get("pricebushel")
                        ),
                        "commodity": commodity,
                    }
                )
        return rows

    def _parse_jsonp(self, text: str) -> Dict[str, Any]:
        match = re.match(r"^[^(]+\((.*)\)\s*;?\s*$", text, re.S)
        if not match:
            raise ValueError("Expected JSONP response")
        return json.loads(match.group(1))

    def _normalize_commodity(self, value: str) -> str:
        value_lower = value.lower()
        for key, commodity in COMMODITY_NAMES.items():
            if key in value_lower:
                return commodity
        return value.strip()

    def _format_basis(self, value: Any) -> str:
        if value in (None, ""):
            return ""
        number = float(value) * 100
        if number.is_integer():
            return str(int(number))
        return f"{number:.2f}".rstrip("0").rstrip(".")

    def _format_currency(self, value: Any) -> str:
        if value in (None, ""):
            return ""
        return f"${float(value):.4f}"
