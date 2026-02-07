# scraper/probate_search.py
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

BASE_URL = "https://www.courts.mo.gov/casenet/searchResult.do"

def fetch_probate_cases(session, county_code, start_date):
    end_date = start_date + timedelta(days=7)

    params = {
        "countyCode": county_code,
        "newSearch": "Y",
        "caseType": "Probate",
        "caseStatus": "A",
        "startDate": start_date.strftime("%m/%d/%Y"),
        "endDate": end_date.strftime("%m/%d/%Y")
    }

    r = session.get(BASE_URL, params=params, timeout=30)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "lxml")
    return soup.select("table tr")[1:]
