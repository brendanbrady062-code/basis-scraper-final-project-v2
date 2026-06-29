import unittest

from scrapers.agricharts_embed_scraper import AgrichartsEmbedScraper


class AgrichartsYellowCornFilterTest(unittest.TestCase):
    def test_only_yellow_corn_is_kept_for_allowed_commodities(self):
        html = """
        var bids = [{"name":"Atchison","cashbids":[
          {"ccommodity":"Yellow Corn","basis":"1.20","delivery_start":"08/01/2026","delivery_end":"08/31/2026","basismonth":"SEP","price":"4.50"},
          {"ccommodity":"White Corn","basis":"0.80","delivery_start":"08/01/2026","delivery_end":"08/31/2026","basismonth":"SEP","price":"4.20"}
        ]}];var config = {};
        """

        scraper = AgrichartsEmbedScraper(
            name="test",
            url="https://example.com",
            location="Bartlett Atchison",
            forced_commodity=None,
            location_filter="Atchison",
            allowed_commodities=["Yellow Corn"],
        )

        rows = scraper.parse_html(html)

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["commodity"], "Yellow Corn")


if __name__ == "__main__":
    unittest.main()
