# Signature: Mourad.Soltani
"""
Health tests for FounderPricingDigest.
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import extract_prices, content_hash, check_url


class TestHealth(unittest.TestCase):
    def test_extract_prices_basic(self):
        html = "<html><body>Pro plan $29/mo. Enterprise $99. Free $0.</body></html>"
        prices = extract_prices(html)
        self.assertTrue(any("$29" in p for p in prices))
        self.assertTrue(any("$99" in p for p in prices))

    def test_content_hash_stable(self):
        html1 = "<html><body>Price is $10</body></html>"
        html2 = "<html><body>  Price is $10  </body></html>"
        h1 = content_hash(html1)
        h2 = content_hash(html2)
        self.assertEqual(h1, h2)

    def test_content_hash_changes(self):
        html1 = "<html><body>Price is $10</body></html>"
        html2 = "<html><body>Price is $20</body></html>"
        self.assertNotEqual(content_hash(html1), content_hash(html2))

    @patch("main.fetch_page")
    @patch("main.save_snapshot")
    @patch("main.load_snapshot")
    def test_check_url_changed(self, mock_load, mock_save, mock_fetch):
        mock_fetch.return_value = "<html><body>$50 plan</body></html>"
        mock_load.return_value = {"hash": "oldhash", "prices": ["$40"]}
        result = check_url("https://example.com/pricing")
        self.assertEqual(result["status"], "changed")
        self.assertIn("$50", "".join(result["prices"]))
        mock_save.assert_called()


if __name__ == "__main__":
    unittest.main()
