# main.py
from datetime import datetime, timedelta
from scraper.session import create_session
from scraper.probate_search import fetch_probate_cases

session = create_session()
start = datetime.today() - timedelta(days=30)

while start < datetime.today():
    cases = fetch_probate_cases(session, "SLC", start)
    # process cases...
    start += timedelta(days=7)
