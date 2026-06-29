"""
Run all configured basis scrapers and save one combined CSV.
"""
import csv
import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

sys.path.insert(0, os.path.dirname(__file__))

from config.scraper_config import (
    DATA_DIRECTORY,
    DELIVERY_END_CUTOFF,
    GROUP_ORDER,
    OUTPUT_COLUMNS,
    SCRAPER_ORDER,
    SCRAPERS,
)


def build_scraper(scraper_name: str, config: Dict[str, Any]):
    scraper_type = config.get("type", "html").lower()

    if scraper_type == "cgb":
        from scrapers.CGB_scrape import CGBScraper

        return CGBScraper(
            scraper_name,
            url=config.get("url"),
            data_dir=DATA_DIRECTORY,
            location_id=config.get("location_id"),
            location_filter=config.get("location_filter"),
            allowed_commodities=config.get("allowed_commodities"),
        )

    if scraper_type == "gradable":
        from scrapers.gradable_scraper import GradableScraper

        return GradableScraper(
            scraper_name,
            config["url"],
            config["location"],
            DATA_DIRECTORY,
            config.get("allowed_commodities"),
        )

    if scraper_type == "barchart_jsonp":
        from scrapers.barchart_jsonp_scraper import BarchartJSONPScraper

        return BarchartJSONPScraper(
            scraper_name,
            config["url"],
            config["location"],
            DATA_DIRECTORY,
            config.get("allowed_commodities"),
            config.get("product_filter"),
            config.get("product_filter_exclude"),
        )

    if scraper_type == "bushel_html":
        from scrapers.bushel_html_scraper import BushelHTMLScraper

        return BushelHTMLScraper(
            scraper_name,
            config["url"],
            config["location"],
            DATA_DIRECTORY,
            config.get("section_filter"),
            config.get("forced_commodity"),
        )

    if scraper_type == "alto_pekin":
        from scrapers.simple_table_scraper import AltoPekinScraper

        return AltoPekinScraper(
            scraper_name,
            config["url"],
            config["location"],
            DATA_DIRECTORY,
        )

    if scraper_type == "andersons_clymers":
        from scrapers.simple_table_scraper import AndersonsClymersScraper

        return AndersonsClymersScraper(
            scraper_name,
            config["url"],
            config["location"],
            DATA_DIRECTORY,
        )

    if scraper_type == "mid_mo_energy":
        from scrapers.simple_table_scraper import MidMissouriEnergyScraper

        return MidMissouriEnergyScraper(
            scraper_name,
            config["url"],
            config["location"],
            DATA_DIRECTORY,
        )

    if scraper_type == "quality_roasting":
        from scrapers.simple_table_scraper import QualityRoastingScraper

        return QualityRoastingScraper(
            scraper_name,
            config["url"],
            config["location"],
            DATA_DIRECTORY,
            config.get("forced_commodity", "Beans"),
        )

    if scraper_type == "mfa_rail":
        from scrapers.simple_table_scraper import MFARailScraper

        return MFARailScraper(
            scraper_name,
            config["url"],
            config["location"],
            DATA_DIRECTORY,
        )

    if scraper_type == "jbs_cash":
        from scrapers.simple_table_scraper import JBSCashScraper

        return JBSCashScraper(
            scraper_name,
            config["url"],
            config["location"],
            DATA_DIRECTORY,
        )

    if scraper_type == "bunge_location":
        from scrapers.simple_table_scraper import BungeLocationScraper

        return BungeLocationScraper(
            scraper_name,
            config["url"],
            config["location"],
            DATA_DIRECTORY,
            config.get("commodity_tab", "soybeans"),
            config.get("forced_commodity", "Beans"),
        )

    if scraper_type == "cihedging":
        from scrapers.cihedging_scraper import CIHedgingScraper

        return CIHedgingScraper(
            scraper_name,
            config["company_id"],
            config["location"],
            DATA_DIRECTORY,
            config.get("forced_commodity", "Corn"),
        )

    if scraper_type == "agricharts_embed":
        from scrapers.agricharts_embed_scraper import AgrichartsEmbedScraper

        return AgrichartsEmbedScraper(
            scraper_name,
            config["url"],
            config["location"],
            DATA_DIRECTORY,
            config.get("forced_commodity"),
            config.get("location_filter"),
            config.get("allowed_commodities"),
        )

    if scraper_type == "html":
        from scrapers.html_scraper_template import HTMLScraper

        return HTMLScraper(scraper_name, config["url"], DATA_DIRECTORY)

    if scraper_type == "javascript":
        from scrapers.javascript_scraper_template import JavaScriptScraper

        return JavaScriptScraper(scraper_name, config["url"], DATA_DIRECTORY)

    raise ValueError(f"Unknown scraper type: {scraper_type}")


def row_is_within_delivery_cutoff(row: Dict[str, Any]) -> bool:
    delivery_end = row.get("delivery_end") or row.get("delivery_start")
    if not delivery_end:
        return True

    for date_format in ("%m/%d/%Y", "%m/%d/%y", "%b %d, %Y"):
        try:
            parsed = datetime.strptime(delivery_end, date_format).date()
            return parsed <= DELIVERY_END_CUTOFF
        except ValueError:
            continue

    return True


def parse_sort_date(value: Any) -> datetime:
    if not value:
        return datetime.max

    for date_format in ("%m/%d/%Y", "%m/%d/%y", "%b %d, %Y"):
        try:
            return datetime.strptime(str(value), date_format)
        except ValueError:
            continue

    return datetime.max


def commodity_sort_key(value: Any) -> int:
    commodity_order = {
        "Corn": 0,
        "Beans": 1,
        "Bean/Other": 2,
        "SRW Wheat": 3,
    }
    return commodity_order.get(str(value or ""), 99)


def sort_combined_rows(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    group_order = {group: index for index, group in enumerate(GROUP_ORDER)}
    scraper_order = {name: index for index, name in enumerate(SCRAPER_ORDER)}

    def row_key(row: Dict[str, Any]):
        scraper_name = row.get("__scraper_name", "")
        group_name = row.get("__group", "")
        return (
            group_order.get(group_name, 99),
            scraper_order.get(scraper_name, 999),
            commodity_sort_key(row.get("commodity")),
            parse_sort_date(row.get("delivery_start")),
            parse_sort_date(row.get("delivery_end")),
            str(row.get("symbol", "")),
            str(row.get("basis", "")),
        )

    return sorted(rows, key=row_key)


def save_combined_csv(data: List[Dict[str, Any]], filename: Optional[str] = None) -> Optional[str]:
    if not data:
        print("No data to save.")
        return None

    data = sort_combined_rows(data)

    os.makedirs(DATA_DIRECTORY, exist_ok=True)

    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"basis_values_{timestamp}"

    filepath = os.path.join(DATA_DIRECTORY, f"{filename}.csv")

    with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=OUTPUT_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        for row in data:
            writer.writerow({column: row.get(column, "") for column in OUTPUT_COLUMNS})

    return filepath


def run_all_scrapers() -> Optional[str]:
    print("\n" + "=" * 60)
    print("BASIS VALUE SCRAPER")
    print("=" * 60)

    if not SCRAPERS:
        print("\nNo scrapers configured. Add scrapers to config/scraper_config.py")
        return None

    all_rows = []
    results = {}

    for scraper_name, config in SCRAPERS.items():
        if not config.get("enabled", False):
            print(f"\nSkipping {scraper_name} (disabled)")
            continue

        try:
            print(f"\nRunning scraper: {scraper_name}")
            scraper = build_scraper(scraper_name, config)
            rows = scraper.scrape()
            rows = [row for row in rows if row_is_within_delivery_cutoff(row)]
            for row in rows:
                row["__scraper_name"] = scraper_name
                row["__group"] = config.get("group", "")
            all_rows.extend(rows)
            results[scraper_name] = len(rows)
        except Exception as exc:
            print(f"Error running {scraper_name}: {exc}")
            results[scraper_name] = None

    output_path = save_combined_csv(all_rows)

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for scraper_name, row_count in results.items():
        status = "FAILED" if row_count is None else f"{row_count} rows"
        print(f"{scraper_name}: {status}")

    print(f"\nCombined output: {output_path or 'No file created'}")
    print("=" * 60 + "\n")
    return output_path


if __name__ == "__main__":
    run_all_scrapers()
