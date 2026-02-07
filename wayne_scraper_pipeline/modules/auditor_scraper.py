import requests
from bs4 import BeautifulSoup
import pandas as pd
import logging
from modules.utils import setup_logger
from config import settings

logger = setup_logger("logs/auditor_scraper.log")

class AuditorScraper:
    def __init__(self):
        self.base_url = settings.AUDITOR_URL

    def search_by_address(self, address):
        params = {
            "SearchFocus": "All Records",
            "SearchCategory": "Address",
            "SearchText": address
        }
        try:
            r = requests.get(self.base_url, params=params)
            soup = BeautifulSoup(r.text, "lxml")
            results = []
            table = soup.find("table")
            if table:
                for row in table.find_all("tr")[1:]:
                    cols = [c.text.strip() for c in row.find_all("td")]
                    results.append(cols)
            logger.info(f"Found {len(results)} auditor entries for {address}")
            return results
        except Exception as e:
            logger.error(f"Auditor search failed for {address}: {e}")
            return []

