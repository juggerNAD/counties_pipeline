# scraper/case_parser.py
from urllib.parse import urljoin

BASE_CASE_URL = "https://www.courts.mo.gov/casenet/"

def parse_case_row(row):
    """
    Parses a single case row from the search results table
    """
    cells = row.find_all("td")
    if len(cells) < 6:
        return None

    case_number = cells[0].get_text(strip=True)
    case_type = cells[2].get_text(strip=True)
    filing_date = cells[3].get_text(strip=True)

    link_tag = cells[0].find("a")
    if not link_tag:
        return None

    case_url = urljoin(BASE_CASE_URL, link_tag["href"])

    return {
        "case_number": case_number,
        "case_type": case_type,
        "filing_date": filing_date,
        "case_url": case_url
    }
