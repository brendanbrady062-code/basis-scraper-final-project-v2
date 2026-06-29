"""
Scraper for Agricharts cash bid embed endpoints.
"""
import json
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests

from .base_scraper import BaseScraper


class AgrichartsEmbedScraper(BaseScraper):
    """Scraper for Agricharts embed pages and JSON bid endpoints."""

    def __init__(
        self,
        name: str,
        url: str,
        location: str,
        data_dir: str = "data",
        forced_commodity: Optional[str] = None,
        location_filter: Optional[str] = None,
        allowed_commodities: Optional[List[str]] = None,
    ):
        super().__init__(name, data_dir)
        self.url = url
        self.location = location
        self.forced_commodity = forced_commodity
        self.location_filter = location_filter.lower() if location_filter else None
        self.allowed_commodities = set(allowed_commodities or [])
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36"
            )
        }

    def scrape(self) -> List[Dict[str, Any]]:
        print(f"Fetching Agricharts bids from: {self.url}")
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
        data = self._extract_bids_data(html)
        rows = []

        for group in data:
            group_location = group.get("name", "")
            if self.location_filter and self.location_filter not in group_location.lower():
                continue

            group_commodity = self.forced_commodity or self._clean_commodity(
                group.get("display_name") or group.get("name", "")
            )

            for bid in group.get("cashbids", []):
                commodity_source = (
                    bid.get("ccommodity")
                    if not str(bid.get("ccommodity", "")).isdigit()
                    else ""
                )
                commodity = self.forced_commodity or self._clean_commodity(
                    commodity_source
                    or bid.get("sym_root")
                    or bid.get("symbol")
                    or group_commodity
                )
                if self.allowed_commodities and commodity not in self.allowed_commodities:
                    continue
                rows.append(
                    {
                        "location": self.location,
                        "basis": self._format_basis(bid.get("basis")),
                        "delivery_start": self._format_date(bid.get("delivery_start", "")),
                        "delivery_end": self._format_date(bid.get("delivery_end", "")),
                        "symbol": bid.get("basismonth") or bid.get("symbol", ""),
                        "cash_price": self._format_currency(
                            bid.get("price")
                            or bid.get("cashprice")
                            or bid.get("cashpricebushel")
                            or bid.get("cargill_flat_price")
                        ),
                        "commodity": commodity,
                    }
                )

        return rows

    def _extract_bids_data(self, html: str) -> List[Dict[str, Any]]:
        stripped = html.lstrip()
        if stripped.startswith("{"):
            payload = json.loads(stripped)
            if "bids" in payload:
                return payload["bids"]

        start = html.find("var bids = ")
        if start == -1:
            raise ValueError("Could not find Agricharts bids data")
        start += len("var bids = ")
        end = html.find(";var config", start)
        if end == -1:
            end = html.find(";</script>", start)
        if end == -1:
            raise ValueError("Could not find end of Agricharts bids data")
        return json.loads(html[start:end])

    def _clean_commodity(self, value: str) -> str:
        value_lower = value.lower()
        if "corn" in value_lower or value_lower in {"zc"}:
            return "Corn"
        if "soy" in value_lower or "bean" in value_lower or value_lower in {"zs"}:
            return "Beans"
        if "soft red winter" in value_lower or "wheat" in value_lower:
            return "SRW Wheat"
        return value.strip()

    def _format_basis(self, value: Any) -> str:
        if value in (None, ""):
            return ""
        number = float(value)
        if number.is_integer():
            return str(int(number))
        return f"{number:.2f}".rstrip("0").rstrip(".")

    def _format_currency(self, value: Any) -> str:
        if value in (None, ""):
            return ""
        text = str(value).replace("$", "").replace(",", "").strip()
        return f"${float(text):.4f}"

    def _format_date(self, value: str) -> str:
        for date_format in ("%m/%d/%Y", "%m/%d/%y", "%b %d, %Y"):
            try:
                return datetime.strptime(value, date_format).strftime("%m/%d/%Y")
            except ValueError:
                continue
        return value
