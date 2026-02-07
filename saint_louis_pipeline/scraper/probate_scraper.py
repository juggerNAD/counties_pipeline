from utils import get_soup, save_to_csv
from pdf_parser import download_pdf, extract_text_from_pdf, extract_phone
from auditor_scraper import search_property_by_owner
from datetime import datetime, timedelta
import logging

BASE_URL = "https://www.courts.mo.gov/casenet/searchResult.do"

def scrape_county_probate(county_code="SLC", days_back=7):
    """
    Scrape Missouri probate cases, download PDFs, extract phone numbers (OCR fallback),
    and combine with Auditor property info. Normalize data so each property is one CSV row.
    """
    cases_data = []
    today = datetime.today()
    start_date = (today - timedelta(days=days_back)).strftime("%m/%d/%Y")
    end_date = today.strftime("%m/%d/%Y")
    
    data = {
        "countyCode": county_code,
        "newSearch": "Y",
        "courtCode": "CT21",
        "startDate": start_date,
        "caseStatus": "A",
        "caseType": "Probate",
        "locationCode": ""
    }
    
    soup = get_soup(BASE_URL, data=data)
    if not soup:
        logging.error("Failed to load search results.")
        return []

    case_links = [a['href'] for a in soup.select("a[href*='caseNo']")]

    for link in case_links:
        case_url = "https://www.courts.mo.gov" + link
        case_soup = get_soup(case_url)
        if not case_soup:
            continue

        decedent_tag = case_soup.find(text="Decedent:")
        petitioner_tag = case_soup.find(text="Petitioner/Fiduciary:")
        decedent = decedent_tag.find_next().text.strip() if decedent_tag else ""
        petitioner = petitioner_tag.find_next().text.strip() if petitioner_tag else ""

        # Download all PDFs for this case
        pdf_links = [a['href'] for a in case_soup.select("a[href$='.pdf']")]
        phone = None
        for pdf_url in pdf_links:
            pdf_file = download_pdf("https://www.courts.mo.gov" + pdf_url)
            if pdf_file:
                text = extract_text_from_pdf(pdf_file)
                phone = extract_phone(text)
                if phone:
                    break  # Stop at first found phone number

        # Search Auditor site for petitioner properties
        properties = search_property_by_owner(petitioner)

        if not properties:
            # No properties found: add a single row with blank property fields
            cases_data.append({
                "Decedent": decedent,
                "Petitioner": petitioner,
                "Phone": phone,
                "Case URL": case_url,
                "Parcel Number": "",
                "Property Address": "",
                "Property Type": "",
                "Assessed Value": "",
                "Tax Status": ""
            })
        else:
            # Normalize: one row per property
            for prop in properties:
                cases_data.append({
                    "Decedent": decedent,
                    "Petitioner": petitioner,
                    "Phone": phone,
                    "Case URL": case_url,
                    "Parcel Number": prop.get("Parcel Number", ""),
                    "Property Address": prop.get("Property Address", ""),
                    "Property Type": prop.get("Property Type", ""),
                    "Assessed Value": prop.get("Assessed Value", ""),
                    "Tax Status": prop.get("Tax Status", "")
                })

    # Save final CSV
    save_to_csv(cases_data)
    logging.info(f"Scraped {len(cases_data)} entries for county {county_code}")
    return cases_data
