import os
import pandas as pd
from modules.probate_scraper import ProbateScraper
from modules.pdf_parser import extract_info_from_pdf
from modules.auditor_scraper import AuditorScraper
from config import settings

os.makedirs(settings.PDF_DOWNLOAD_PATH, exist_ok=True)

# 1️⃣ Scrape probate cases
scraper = ProbateScraper()
scraper.accept_terms()
all_cases = []

for case_type in settings.CASE_TYPES:
    scraper.search_cases(case_type, settings.DATE_FROM, settings.DATE_TO)
    links = scraper.extract_case_links()
    for link in links:
        pdf_path = scraper.download_case_pdf(link)
        if pdf_path:
            info = extract_info_from_pdf(pdf_path)
            info["case_url"] = link
            all_cases.append(info)

scraper.close()

# 2️⃣ Save probate cases to CSV
cases_df = pd.DataFrame(all_cases)
cases_df.to_csv("output/cases.csv", index=False)

# 3️⃣ Search auditor site
auditor_scraper = AuditorScraper()
auditor_results = []

for address in cases_df["decedent"].dropna().tolist():
    results = auditor_scraper.search_by_address(address)
    for res in results:
        auditor_results.append({"decedent_address": address, "auditor_data": res})

# 4️⃣ Save auditor results
auditor_df = pd.DataFrame(auditor_results)
auditor_df.to_csv("output/auditors_results.csv", index=False)

print("Scraping workflow completed successfully!")

