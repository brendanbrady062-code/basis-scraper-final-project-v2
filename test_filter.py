from scrapers.barchart_jsonp_scraper import BarchartJSONPScraper

scraper = BarchartJSONPScraper(
    "test",
    "https://cargillus.websol.barchart.com/?jsonpFunction=jQuery37007274726507964236_1782160231242&module=cashbids&location=62677&output=json&commOverviewByLocation=1&commRoots=%2CZS%2CZS&_=1782160231243",
    "Cargill Bloomington Yellow Beans",
    "data",
    ["Beans"],
    "yellow soybeans",
    "non gmo"
)

rows = scraper.scrape()
print(f"\nTotal rows extracted: {len(rows)}")
for row in rows:
    print(f"{row['delivery_start']} - {row['delivery_end']}: basis {row['basis']}")

