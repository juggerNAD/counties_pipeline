# scraper/docket_scraper.py
from bs4 import BeautifulSoup

def extract_docket_pdfs(session, case_url):
    r = session.get(case_url)
    soup = BeautifulSoup(r.text, "lxml")

    pdf_links = []

    for row in soup.select("tr.docketRow"):
        if "+" in row.text:
            row.select_one("a").click()

        for a in row.select("a[href$='.pdf']"):
            pdf_links.append(a["href"])

    return pdf_links
