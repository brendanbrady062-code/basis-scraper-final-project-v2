"""
Scrapers for simple custom HTML cash bid tables.
"""
import calendar
import ast
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
    "august": 8,
    "sep": 9,
    "sept": 9,
    "september": 9,
    "oct": 10,
    "nov": 11,
    "dec": 12,
}


class AltoPekinScraper(BaseScraper):
    """Scraper for Alto Ingredients Pekin corn pricing table."""

    def __init__(self, name: str, url: str, location: str, data_dir: str = "data"):
        super().__init__(name, data_dir)
        self.url = url
        self.location = location
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/125.0.0.0 Safari/537.36"
            ),
            "Accept": (
                "text/html,application/xhtml+xml,application/xml;"
                "q=0.9,image/avif,image/webp,*/*;q=0.8"
            ),
            "Accept-Language": "en-US,en;q=0.9",
        }

    def scrape(self) -> List[Dict[str, Any]]:
        print(f"Fetching Alto/Pekin bids from: {self.url}")
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

        for table in soup.find_all("table"):
            in_bid_rows = False
            for tr in table.find_all("tr"):
                cells = [cell.get_text(" ", strip=True) for cell in tr.find_all(["td", "th"])]
                if len(cells) < 3:
                    continue

                if cells[0].upper() == "ALTO/ICP":
                    in_bid_rows = True
                    continue

                if in_bid_rows and not self._looks_like_delivery(cells[0]):
                    break

                if not in_bid_rows:
                    continue

                delivery_start, delivery_end = self._delivery_range(cells[0], page_year)
                rows.append(
                    {
                        "location": self.location,
                        "basis": self._format_basis(cells[2]),
                        "delivery_start": delivery_start,
                        "delivery_end": delivery_end,
                        "symbol": cells[3] if len(cells) > 3 else "",
                        "cash_price": self._format_currency(cells[1]),
                        "commodity": "Corn",
                    }
                )

        return rows

    def _find_page_year(self, soup: BeautifulSoup) -> Optional[int]:
        match = re.search(r"\b(\d{1,2})/\d{1,2}/(\d{4})\b", soup.get_text(" ", strip=True))
        if match:
            return int(match.group(2))
        match = re.search(r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+(\d{4})\b", soup.get_text(" ", strip=True))
        if match:
            return int(match.group(1))
        return None

    def _looks_like_delivery(self, value: str) -> bool:
        key = value.lower().split()[0][:3]
        return key in MONTHS

    def _delivery_range(self, delivery: str, page_year: int) -> Tuple[str, str]:
        key = delivery.lower().split()[0]
        month = MONTHS.get(key) or MONTHS.get(key[:3])
        if not month:
            return delivery, delivery
        last_day = calendar.monthrange(page_year, month)[1]
        return f"{month:02d}/01/{page_year}", f"{month:02d}/{last_day:02d}/{page_year}"

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


class AndersonsClymersScraper(BaseScraper):
    """Scraper for Andersons Clymers cash bid table."""

    def __init__(self, name: str, url: str, location: str, data_dir: str = "data"):
        super().__init__(name, data_dir)
        self.url = url
        self.location = location
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36"
            )
        }

    def scrape(self) -> List[Dict[str, Any]]:
        print(f"Fetching Andersons Clymers bids from: {self.url}")
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
        rows = []

        for table in soup.find_all("table"):
            for tr in table.find_all("tr"):
                cells = [cell.get_text(" ", strip=True) for cell in tr.find_all(["td", "th"])]
                if len(cells) < 6 or cells[0].lower() == "delivery":
                    continue

                delivery_start, delivery_end = self._delivery_range(cells[0])
                rows.append(
                    {
                        "location": self.location,
                        "basis": self._format_basis(cells[2]),
                        "delivery_start": delivery_start,
                        "delivery_end": delivery_end,
                        "symbol": cells[5],
                        "cash_price": self._format_currency(cells[1]),
                        "commodity": "Corn",
                    }
                )

        return rows

    def _delivery_range(self, delivery: str) -> Tuple[str, str]:
        parts = delivery.lower().split()
        if len(parts) < 2:
            return delivery, delivery

        year = 2000 + int(parts[1])
        if parts[0] == "on":
            return f"10/01/{year}", f"11/30/{year}"

        month = MONTHS.get(parts[0]) or MONTHS.get(parts[0][:3])
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


class MidMissouriEnergyScraper(BaseScraper):
    """Scraper for Mid-Missouri Energy cash bid script rows."""

    QUOTE_URL = (
        "https://www.agricharts.com/marketdata/jsquote.php?"
        "varname=quotes&symbols={symbols}&fields=name,month,last&user=&pass="
        "&settle=0&display_ice=&ice_exchanges=&exchsyms=&currencyconv="
        "&displayType=bids"
    )

    def __init__(self, name: str, url: str, location: str, data_dir: str = "data"):
        super().__init__(name, data_dir)
        self.url = url
        self.location = location
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36"
            )
        }

    def scrape(self) -> List[Dict[str, Any]]:
        print(f"Fetching Mid-Missouri Energy bids from: {self.url}")
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
        calls = self._extract_write_bid_calls(html)
        symbols = sorted(set(re.findall(r"quotes\['([^']+)'\]", html)))
        quote_prices = self._fetch_quote_prices(symbols)
        rows = []

        for call in calls:
            if not call.lstrip().startswith(("'", '"')):
                continue
            args = self._parse_write_bid_args(call)
            if len(args) < 15:
                continue

            commodity = args[0]
            basis = float(args[1])
            delivery_start = args[6]
            delivery_end = args[7]
            symbol = args[10]
            quote_symbol = args[14]
            futures_price = quote_prices.get(quote_symbol)
            cash_price = ""
            if futures_price is not None:
                cash_price = f"${(futures_price + basis / 100):.4f}"

            rows.append(
                {
                    "location": self.location,
                    "basis": self._format_basis(basis),
                    "delivery_start": delivery_start,
                    "delivery_end": delivery_end,
                    "symbol": symbol,
                    "cash_price": cash_price,
                    "commodity": "Corn" if "corn" in commodity.lower() else commodity,
                }
            )

        return rows

    def _extract_write_bid_calls(self, html: str) -> List[str]:
        calls = []
        marker = "writeBidRow("
        pos = 0

        while True:
            start = html.find(marker, pos)
            if start == -1:
                break

            i = start + len(marker)
            depth = 1
            in_quote = False
            quote_char = ""

            while i < len(html):
                char = html[i]
                prev = html[i - 1] if i > 0 else ""

                if in_quote:
                    if char == quote_char and prev != "\\":
                        in_quote = False
                else:
                    if char in ("'", '"'):
                        in_quote = True
                        quote_char = char
                    elif char == "(":
                        depth += 1
                    elif char == ")":
                        depth -= 1
                        if depth == 0:
                            calls.append(html[start + len(marker):i])
                            pos = i + 1
                            break

                i += 1
            else:
                break

        return calls

    def _parse_write_bid_args(self, call: str) -> List[Any]:
        call = re.sub(r"quotes\['([^']+)'\]", r"'\1'", call)
        call = re.sub(r"\bfalse\b", "False", call)
        call = re.sub(r"\btrue\b", "True", call)
        call = re.sub(r"\bnull\b", "None", call)
        call = call.replace("0-0", "0")
        return list(ast.literal_eval(f"({call})"))

    def _fetch_quote_prices(self, symbols: List[str]) -> Dict[str, float]:
        if not symbols:
            return {}

        url = self.QUOTE_URL.format(symbols=",".join(symbols))
        response = requests.get(
            url,
            headers=self.headers,
            timeout=20,
            verify=False,
        )
        response.raise_for_status()
        text = response.text
        prices = {}

        for symbol in symbols:
            match = re.search(
                rf"'{re.escape(symbol)}':\s*\{{.*?last:\s*'([^']+)'",
                text,
                re.S,
            )
            if match:
                prices[symbol] = float(match.group(1)) / 100

        return prices

    def _format_basis(self, value: Any) -> str:
        number = float(value)
        if number.is_integer():
            return str(int(number))
        return f"{number:.2f}".rstrip("0").rstrip(".")


class QualityRoastingScraper(BaseScraper):
    """Scraper for Quality Roasting QT Market Center cash bid embeds."""

    def __init__(
        self,
        name: str,
        url: str,
        location: str,
        data_dir: str = "data",
        forced_commodity: str = "Beans",
    ):
        super().__init__(name, data_dir)
        self.url = url
        self.location = location
        self.forced_commodity = forced_commodity
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36"
            )
        }

    def scrape(self) -> List[Dict[str, Any]]:
        print(f"Fetching Quality Roasting bids from: {self.url}")
        response = requests.get(
            self.url,
            headers=self.headers,
            timeout=20,
            verify=False,
        )
        response.raise_for_status()
        rows = self.parse_javascript(response.text)
        print(f"Extracted {len(rows)} records")
        return rows

    def parse_javascript(self, javascript: str) -> List[Dict[str, Any]]:
        soup = BeautifulSoup(self._extract_document_write_html(javascript), "html.parser")
        last_updated_year = self._find_last_updated_year(soup) or date.today().year
        rows = []

        current_commodity = self.forced_commodity
        for tr in soup.find_all("tr"):
            cells = [cell.get_text(" ", strip=True) for cell in tr.find_all(["td", "th"])]
            if len(cells) < 5 or cells[0].lower() == "commodity":
                continue

            if cells[0]:
                current_commodity = self.forced_commodity or self._clean_commodity(cells[0])

            delivery_start, delivery_end = self._delivery_range(cells[1], last_updated_year)
            rows.append(
                {
                    "location": self.location,
                    "basis": self._format_basis(cells[3]),
                    "delivery_start": delivery_start,
                    "delivery_end": delivery_end,
                    "symbol": cells[4],
                    "cash_price": self._format_currency(cells[2]),
                    "commodity": current_commodity,
                }
            )

        return rows

    def _extract_document_write_html(self, javascript: str) -> str:
        chunks = []
        marker = "document.write('"
        position = 0

        while True:
            start = javascript.find(marker, position)
            if start == -1:
                break

            i = start + len(marker)
            chunk = []
            while i < len(javascript):
                if javascript[i] == "'" and javascript[i - 1] != "\\":
                    if javascript[i:i + 3] == "');":
                        break
                chunk.append(javascript[i])
                i += 1

            chunks.append("".join(chunk).replace("\\'", "'"))
            position = i + 3

        return "".join(chunks)

    def _find_last_updated_year(self, soup: BeautifulSoup) -> Optional[int]:
        match = re.search(r"Last Updated:\s*(\d{1,2})/(\d{1,2})/(\d{4})", soup.get_text(" ", strip=True))
        if match:
            return int(match.group(3))
        return None

    def _delivery_range(self, delivery: str, year: int) -> Tuple[str, str]:
        delivery_lower = delivery.lower()
        if "new crop" in delivery_lower:
            match = re.search(r"(\d{2,4})", delivery_lower)
            crop_year = year
            if match:
                crop_year = int(match.group(1))
                if crop_year < 100:
                    crop_year += 2000
            return f"09/01/{crop_year}", f"11/30/{crop_year}"

        month = MONTHS.get(delivery_lower) or MONTHS.get(delivery_lower[:3])
        if not month:
            return delivery, delivery

        last_day = calendar.monthrange(year, month)[1]
        return f"{month:02d}/01/{year}", f"{month:02d}/{last_day:02d}/{year}"

    def _clean_commodity(self, value: str) -> str:
        if "soy" in value.lower() or "bean" in value.lower():
            return "Beans"
        if "corn" in value.lower():
            return "Corn"
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


class MFARailScraper(BaseScraper):
    """Scraper for MFA Rail Facility cash bid tables."""

    SEASON_RANGES = {
        "sep/oct/nov": ("09/01/{year}", "11/30/{year}"),
    }

    def __init__(self, name: str, url: str, location: str, data_dir: str = "data"):
        super().__init__(name, data_dir)
        self.url = url
        self.location = location
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36"
            )
        }

    def scrape(self) -> List[Dict[str, Any]]:
        print(f"Fetching MFA Rail bids from: {self.url}")
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
        display_offset = self._extract_display_offset(html)
        rows = []

        for heading_table in soup.find_all("table", attrs={"name": "commodity-ldp"}):
            heading = heading_table.get_text(" ", strip=True).upper()
            if "YELLOW CORN" not in heading:
                continue

            bid_table = heading_table.find_next("table", attrs={"name": "cashbids-data-table"})
            if not bid_table:
                continue

            for tr in bid_table.find_all("tr"):
                cells = tr.find_all("td")
                if len(cells) < 6:
                    continue

                delivery = cells[0].get_text(" ", strip=True)
                cash_value = self._extract_display_number(cells[1].decode_contents(), display_offset)
                basis_value = self._extract_display_number(cells[5].decode_contents(), display_offset)
                if cash_value is None or basis_value is None:
                    continue

                delivery_start, delivery_end = self._delivery_range(delivery)
                rows.append(
                    {
                        "location": self.location,
                        "basis": self._format_basis(basis_value),
                        "delivery_start": delivery_start,
                        "delivery_end": delivery_end,
                        "symbol": cells[2].get_text(" ", strip=True),
                        "cash_price": f"${cash_value:.4f}",
                        "commodity": "Corn",
                    }
                )

        return rows

    def _extract_display_offset(self, html: str) -> float:
        match = re.search(
            r"function displayNumber\(x, decimal_places\)(.*?)document\.write",
            html,
            re.S,
        )
        if not match:
            return 0.0

        offset = 0.0
        body = match.group(1)
        should_apply = True

        for raw_line in body.splitlines():
            line = raw_line.strip().replace("\r", "")
            if not line:
                continue

            if line.startswith("if(") and line.endswith(")"):
                condition = line[3:-1].strip()
                should_apply = bool(eval(condition, {"__builtins__": {}}, {}))
                continue

            if line.startswith("x ="):
                if should_apply:
                    expression = line.split("=", 1)[1].strip().rstrip(";")
                    offset = float(eval(expression, {"__builtins__": {}}, {"x": offset}))
                should_apply = True

        return offset

    def _extract_display_number(self, html: str, offset: float) -> Optional[float]:
        match = re.search(r"displayNumber\(([-0-9.]+),\s*\d+\)", html)
        if not match:
            return None
        return float(match.group(1)) + offset

    def _delivery_range(self, delivery: str) -> Tuple[str, str]:
        normalized = delivery.strip().lower()
        for key, (start_fmt, end_fmt) in self.SEASON_RANGES.items():
            if normalized.startswith(key):
                year_match = re.search(r"(\d{4})", normalized)
                year = int(year_match.group(1)) if year_match else date.today().year
                return start_fmt.format(year=year), end_fmt.format(year=year)

        parts = normalized.split()
        if len(parts) < 2:
            return delivery, delivery

        month = MONTHS.get(parts[0]) or MONTHS.get(parts[0][:3])
        year = int(parts[-1]) if parts[-1].isdigit() else date.today().year
        if not month:
            return delivery, delivery

        last_day = calendar.monthrange(year, month)[1]
        return f"{month:02d}/01/{year}", f"{month:02d}/{last_day:02d}/{year}"

    def _format_basis(self, value: float) -> str:
        number = value * 100
        if number.is_integer():
            return str(int(number))
        return f"{number:.2f}".rstrip("0").rstrip(".")


class JBSCashScraper(BaseScraper):
    """Scraper for JBS cash bid pages with writeBidRow records."""

    QUOTE_URL = (
        "https://www.agricharts.com/marketdata/jsquote.php?"
        "varname=quotes&symbols={symbols}&fields=name,month,last&user=&pass="
        "&settle=0&display_ice=&ice_exchanges=&exchsyms=&currencyconv="
        "&displayType=bids"
    )

    def __init__(self, name: str, url: str, location: str, data_dir: str = "data"):
        super().__init__(name, data_dir)
        self.url = url
        self.location = location
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36"
            )
        }

    def scrape(self) -> List[Dict[str, Any]]:
        print(f"Fetching JBS cash bids from: {self.url}")
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
        calls = self._extract_write_bid_calls(html)
        symbols = []
        parsed_calls = []

        for call in calls:
            if not call.lstrip().startswith(("'", '"')):
                continue
            args = self._parse_write_bid_args(call)
            if len(args) < 20:
                continue
            parsed_calls.append(args)
            symbols.append(args[14])

        quote_data = self._fetch_quote_data(sorted(set(symbols)))
        rows = []

        for args in parsed_calls:
            commodity = args[0]
            basis = float(args[1])
            delivery_start = args[6]
            delivery_end = args[7]
            quote_symbol = args[14]
            quote = quote_data.get(quote_symbol, {})
            futures_price = quote.get("last")
            cash_price = ""
            if futures_price is not None:
                cash_price = f"${(futures_price + basis / 100):.4f}"

            rows.append(
                {
                    "location": self.location,
                    "basis": self._format_basis(basis),
                    "delivery_start": delivery_start,
                    "delivery_end": delivery_end,
                    "symbol": quote.get("shortmonth", quote_symbol),
                    "cash_price": cash_price,
                    "commodity": "Corn" if "corn" in commodity.lower() else commodity,
                }
            )

        return rows

    def _extract_write_bid_calls(self, html: str) -> List[str]:
        calls = []
        marker = "writeBidRow("
        pos = 0

        while True:
            start = html.find(marker, pos)
            if start == -1:
                break

            i = start + len(marker)
            depth = 1
            in_quote = False
            quote_char = ""

            while i < len(html):
                char = html[i]
                prev = html[i - 1] if i > 0 else ""

                if in_quote:
                    if char == quote_char and prev != "\\":
                        in_quote = False
                else:
                    if char in ("'", '"'):
                        in_quote = True
                        quote_char = char
                    elif char == "(":
                        depth += 1
                    elif char == ")":
                        depth -= 1
                        if depth == 0:
                            calls.append(html[start + len(marker):i])
                            pos = i + 1
                            break

                i += 1
            else:
                break

        return calls

    def _parse_write_bid_args(self, call: str) -> List[Any]:
        call = re.sub(r"quotes\['([^']+)'\]", r"'\1'", call)
        call = re.sub(r"\bfalse\b", "False", call)
        call = re.sub(r"\btrue\b", "True", call)
        call = re.sub(r"\bnull\b", "None", call)
        call = call.replace("0-0", "0")
        return list(ast.literal_eval(f"({call})"))

    def _fetch_quote_data(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        if not symbols:
            return {}

        url = self.QUOTE_URL.format(symbols=",".join(symbols))
        response = requests.get(
            url,
            headers=self.headers,
            timeout=20,
            verify=False,
        )
        response.raise_for_status()
        text = response.text
        data: Dict[str, Dict[str, Any]] = {}

        for symbol in symbols:
            match = re.search(
                rf"'{re.escape(symbol)}':\s*\{{.*?last:\s*'([^']+)'.*?shortmonth:\s*'([^']+)'",
                text,
                re.S,
            )
            if match:
                data[symbol] = {
                    "last": float(match.group(1)) / 100,
                    "shortmonth": match.group(2),
                }

        return data

    def _format_basis(self, value: float) -> str:
        if value.is_integer():
            return str(int(value))
        return f"{value:.2f}".rstrip("0").rstrip(".")


class BungeLocationScraper(BaseScraper):
    """Scraper for Bunge location cash bid tables rendered in tab panes."""

    def __init__(
        self,
        name: str,
        url: str,
        location: str,
        data_dir: str = "data",
        commodity_tab: str = "soybeans",
        forced_commodity: str = "Beans",
    ):
        super().__init__(name, data_dir)
        self.url = url
        self.location = location
        self.commodity_tab = commodity_tab
        self.forced_commodity = forced_commodity
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36"
            )
        }

    def scrape(self) -> List[Dict[str, Any]]:
        print(f"Fetching Bunge location bids from: {self.url}")
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
        pane = soup.select_one(f"div.tab-pane#{self.commodity_tab}")
        if not pane:
            return []

        table = pane.find("table")
        if not table:
            return []

        page_year = self._extract_page_year(pane.get_text(" ", strip=True))
        rows = []
        for tr in table.find_all("tr"):
            cells = list(tr.stripped_strings)
            if len(cells) < 5 or cells[0] == "Delivery Period":
                continue

            delivery_start, delivery_end = self._delivery_range(cells[0], page_year)
            rows.append(
                {
                    "location": self.location,
                    "basis": self._format_basis(cells[3]),
                    "delivery_start": delivery_start,
                    "delivery_end": delivery_end,
                    "symbol": cells[1],
                    "cash_price": self._format_currency(cells[4]),
                    "commodity": self.forced_commodity,
                }
            )

        return rows

    def _extract_page_year(self, text: str) -> int:
        match = re.search(r"as of \d{2}-\d{2}-(\d{4})", text, re.I)
        if match:
            return int(match.group(1))
        return date.today().year

    def _delivery_range(self, label: str, page_year: int) -> Tuple[str, str]:
        normalized = " ".join(label.replace("\xa0", " ").split()).strip()
        lower = normalized.lower()

        match = re.search(r"([a-z]+)\s+'?(\d{2})$", lower)
        if match and not lower.startswith("fh "):
            month_key = match.group(1)
            year = 2000 + int(match.group(2))
            month = MONTHS.get(month_key) or MONTHS.get(month_key[:3])
            if month:
                last_day = calendar.monthrange(year, month)[1]
                return f"{month:02d}/01/{year}", f"{month:02d}/{last_day:02d}/{year}"

        fh_match = re.search(r"fh\s+([a-z]+)\s+'?(\d{2})$", lower)
        if fh_match:
            month = MONTHS.get(fh_match.group(1)) or MONTHS.get(fh_match.group(1)[:3])
            year = 2000 + int(fh_match.group(2))
            if month:
                return f"{month:02d}/01/{year}", f"{month:02d}/15/{year}"

        fall_match = re.search(r"fall\s+'?(\d{2})$", lower)
        if fall_match:
            year = 2000 + int(fall_match.group(1))
            return f"09/16/{year}", f"10/31/{year}"

        by_match = re.search(r"by\s+([a-z]+)\s+(\d{1,2})(?:st|nd|rd|th)?", lower)
        if by_match:
            month = MONTHS.get(by_match.group(1)) or MONTHS.get(by_match.group(1)[:3])
            day = int(by_match.group(2))
            if month:
                return f"{month:02d}/01/{page_year}", f"{month:02d}/{day:02d}/{page_year}"

        bal_fh_match = re.search(
            r"bal\s+([a-z]+)\s*/\s*fh\s+([a-z]+)",
            lower,
        )
        if bal_fh_match:
            start_month = MONTHS.get(bal_fh_match.group(1)) or MONTHS.get(bal_fh_match.group(1)[:3])
            end_month = MONTHS.get(bal_fh_match.group(2)) or MONTHS.get(bal_fh_match.group(2)[:3])
            if start_month and end_month:
                last_day = calendar.monthrange(page_year, start_month)[1]
                return f"{start_month:02d}/20/{page_year}", f"{end_month:02d}/15/{page_year}"

        lh_match = re.search(r"lh\s+([a-z]+)", lower)
        if lh_match:
            month = MONTHS.get(lh_match.group(1)) or MONTHS.get(lh_match.group(1)[:3])
            if month:
                last_day = calendar.monthrange(page_year, month)[1]
                return f"{month:02d}/16/{page_year}", f"{month:02d}/{last_day:02d}/{page_year}"

        slash_match = re.search(r"([a-z]+)\s*/\s*([a-z]+)$", lower)
        if slash_match:
            start_month = MONTHS.get(slash_match.group(1)) or MONTHS.get(slash_match.group(1)[:3])
            end_month = MONTHS.get(slash_match.group(2)) or MONTHS.get(slash_match.group(2)[:3])
            if start_month and end_month:
                end_last_day = calendar.monthrange(page_year, end_month)[1]
                return f"{start_month:02d}/01/{page_year}", f"{end_month:02d}/{end_last_day:02d}/{page_year}"

        single_month = MONTHS.get(lower) or MONTHS.get(lower[:3])
        if single_month:
            last_day = calendar.monthrange(page_year, single_month)[1]
            return f"{single_month:02d}/01/{page_year}", f"{single_month:02d}/{last_day:02d}/{page_year}"

        return normalized, normalized

    def _format_basis(self, value: str) -> str:
        number = float(value.replace("$", "").strip()) * 100
        if number.is_integer():
            return str(int(number))
        return f"{number:.2f}".rstrip("0").rstrip(".")

    def _format_currency(self, value: str) -> str:
        number = float(value.replace("$", "").strip())
        return f"${number:.4f}"
