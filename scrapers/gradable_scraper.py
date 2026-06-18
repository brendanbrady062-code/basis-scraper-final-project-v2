"""
Scraper for Gradable cash bid API endpoints.
"""
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import requests

from .base_scraper import BaseScraper


COMMODITY_NAMES = {
    "cn": "Corn",
    "corn": "Corn",
    "soft red winter": "SRW Wheat",
    "srw": "SRW Wheat",
    "wheat": "SRW Wheat",
    "soybeans": "Beans",
    "beans": "Beans",
}


class GradableScraper(BaseScraper):
    """Scraper for ADM/POET Gradable market API responses."""

    def __init__(
        self,
        name: str,
        url: str,
        location: str,
        data_dir: str = "data",
        allowed_commodities: Optional[List[str]] = None,
    ):
        super().__init__(name, data_dir)
        self.url = url
        self.location = location
        self.allowed_commodities = {
            COMMODITY_NAMES.get(commodity.lower(), commodity)
            for commodity in (allowed_commodities or [])
        }
        self.headers = {
            "Accept": "application/json",
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36"
            ),
        }

    def scrape(self) -> List[Dict[str, Any]]:
        print(f"Fetching Gradable bids from: {self.url}")
        response = requests.get(
            self.url,
            headers=self.headers,
            timeout=20,
            verify=False,
        )
        response.raise_for_status()
        data = response.json()
        rows = self.parse_data(data)
        print(f"Extracted {len(rows)} records")
        return rows

    def parse_data(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        crop_names = {
            crop.get("crop_id"): self._normalize_commodity(crop.get("crm_display_name", ""))
            for crop in data.get("crops", [])
        }
        rows = []

        for instrument in data.get("instruments", []):
            commodity = crop_names.get(instrument.get("commodity_id"), "")
            if not commodity:
                continue
            if self.allowed_commodities and commodity not in self.allowed_commodities:
                continue

            rows.append(
                {
                    "location": self.location,
                    "basis": self._format_basis(instrument.get("basis_bid")),
                    "delivery_start": self._format_epoch_date(
                        instrument.get("delivery_period_start")
                    ),
                    "delivery_end": self._format_epoch_date(
                        instrument.get("delivery_period_end")
                    ),
                    "symbol": instrument.get("display_name")
                    or instrument.get("option_month", ""),
                    "cash_price": self._format_currency(instrument.get("cash_bid")),
                    "commodity": commodity,
                }
            )

        return rows

    def _normalize_commodity(self, value: str) -> str:
        value_lower = value.lower()
        if value_lower == "cn":
            return "Corn"
        if "soft red winter" in value_lower:
            return "SRW Wheat"
        if "white" in value_lower and "corn" in value_lower:
            return value.strip()
        if value_lower == "corn":
            return "Corn"
        for key, commodity in COMMODITY_NAMES.items():
            if key in value_lower:
                return commodity
        return value.strip()

    def _format_epoch_date(self, value: Any) -> str:
        if value in (None, ""):
            return ""
        return datetime.fromtimestamp(int(value), tz=timezone.utc).strftime("%m/%d/%Y")

    def _format_currency(self, value: Any) -> str:
        if value in (None, ""):
            return ""
        return f"${float(value):.4f}"

    def _format_basis(self, value: Any) -> str:
        if value in (None, ""):
            return ""
        number = float(value) * 100
        if number.is_integer():
            return str(int(number))
        return f"{number:.2f}".rstrip("0").rstrip(".")
