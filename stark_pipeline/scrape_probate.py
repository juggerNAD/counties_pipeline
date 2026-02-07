import requests
from bs4 import BeautifulSoup
import time
import csv
import re
from io import BytesIO
from PIL import Image
import pdfplumber

# Hugging Face TrOCR
from transformers import TrOCRProcessor, VisionEncoderDecoderModel

# -------------------------
# CONFIGURATION
# -------------------------
START_CASE = 254576
END_CASE = 254600  # Adjust as needed
PROBATE_URL = "http://www.probate.co.stark.oh.us/search/search.html"
AUDITOR_URL = "https://realestate.starkcountyohio.gov/Search/Disclaimer.aspx?FromUrl=../search/commonsearch.aspx?mode=realprop"

VALID_CASE_TYPES = ["will", "estate", "real property"]
CSV_FILE = "stark_county_estates_trocr.csv"

# Initialize TrOCR
print("Loading TrOCR model... This may take a minute the first time.")
trocr_processor = TrOCRProcessor.from_pretrained("microsoft/trocr-base-handwritten")
trocr_model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-base-handwritten")

# -------------------------
# UTILITY FUNCTIONS
# -------------------------

def is_valid_case(case_type: str) -> bool:
    """Check if the case type is relevant (estate/will/real property)."""
    case_type = case_type.lower()
    return any(keyword in case_type for keyword in VALID_CASE_TYPES)

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extract text from PDF using pdfplumber + TrOCR for scanned pages."""
    text = ""
    try:
        with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                # Try extracting text normally
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
                else:
                    # OCR with TrOCR if no text found
                    im = page.to_image(resolution=300).original
                    pixel_values = trocr_processor(images=im, return_tensors="pt").pixel_values
                    generated_ids = trocr_model.generate(pixel_values)
                    ocr_text = trocr_processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
                    text += ocr_text + "\n"
    except Exception as e:
        print("PDF extraction error:", e)
    return text

def search_auditor(name_or_address: str) -> list:
    """Search the auditor website by name or address."""
    session = requests.Session()
    session.get(AUDITOR_URL)  # disclaimer page
    search_page = "https://realestate.starkcountyohio.gov/search/commonsearch.aspx?mode=realprop"
    response = session.get(search_page)
    soup = BeautifulSoup(response.text, "html.parser")

    payload = {
        "ctl00$MainContent$txtOwner": name_or_address,
        "ctl00$MainContent$btnSearch": "Search"
    }

    result = session.post(search_page, data=payload)
    soup = BeautifulSoup(result.text, "html.parser")

    properties = []
    for row in soup.select("table#MainContent_gvResults tr")[1:]:
        cols = row.find_all("td")
        if len(cols) >= 3:
            properties.append({
                "PropertyAddress": cols[0].get_text(strip=True),
                "Owner": cols[1].get_text(strip=True),
                "ParcelNumber": cols[2].get_text(strip=True)
            })
    return properties

# -------------------------
# MAIN SCRAPER
# -------------------------

def scrape_probate_cases():
    results = []

    for case_number in range(START_CASE, END_CASE + 1):
        print(f"Processing case #{case_number}...")
        try:
            response = requests.get(PROBATE_URL)
            soup = BeautifulSoup(response.text, "html.parser")

            # Submit search for the case number (adjust form fields if needed)
            search_payload = {"caseNumber": str(case_number)}
            search_response = requests.post(PROBATE_URL, data=search_payload)
            search_soup = BeautifulSoup(search_response.text, "html.parser")

            case_type_elem = search_soup.find("span", {"id": "caseType"})
            if not case_type_elem:
                print("Case type not found, skipping...")
                continue

            case_type = case_type_elem.get_text(strip=True)
            if not is_valid_case(case_type):
                print(f"Skipping case #{case_number} (case type: {case_type})")
                continue

            # Extract parties
            parties = search_soup.find_all("tr", class_="partyRow")
            decedent_name = fiduciary_name = ""
            for party in parties:
                role_elem = party.find("td", class_="role")
                name_elem = party.find("td", class_="name")
                if not role_elem or not name_elem:
                    continue
                role = role_elem.get_text(strip=True).lower()
                name = name_elem.get_text(strip=True)
                if "in regard to" in role:
                    decedent_name = name
                elif "administrator" in role or "fiduciary" in role:
                    fiduciary_name = name

            # Auto-detect PDF links
            pdf_links = [a['href'] for a in search_soup.select("a[href$='.pdf']")]

            pdf_text = ""
            for pdf_url in pdf_links:
                print("Downloading PDF:", pdf_url)
                pdf_response = requests.get(pdf_url)
                pdf_text += extract_text_from_pdf(pdf_response.content) + "\n"
                time.sleep(1)  # gentle delay

            # Extract decedent address and fiduciary phone using regex
            address_match = re.search(r'\d{1,5}\s+\w+.*\n.*\n.*', pdf_text)
            phone_match = re.search(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', pdf_text)
            decedent_address = address_match.group(0) if address_match else ""
            fiduciary_phone = phone_match.group(0) if phone_match else ""

            # Search auditor site
            auditor_info = search_auditor(decedent_name or decedent_address)

            # Save results
            results.append({
                "CaseNumber": case_number,
                "CaseType": case_type,
                "Decedent": decedent_name,
                "Fiduciary": fiduciary_name,
                "FiduciaryPhone": fiduciary_phone,
                "DecedentAddress": decedent_address,
                "AuditorInfo": auditor_info
            })

            time.sleep(2)

        except Exception as e:
            print(f"Error processing case #{case_number}: {e}")
            continue

    # Save to CSV
    if results:
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            for row in results:
                writer.writerow(row)

    print(f"Scraping completed! Results saved to {CSV_FILE}")

# -------------------------
# RUN SCRIPT
# -------------------------

if __name__ == "__main__":
    scrape_probate_cases()
