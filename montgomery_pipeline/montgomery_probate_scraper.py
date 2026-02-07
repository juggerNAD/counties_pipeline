import os
import time
import csv
import re
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pdf2image import convert_from_path
from PIL import Image
import pytesseract
import concurrent.futures

# ---------- USER INPUT ----------
start_case_number = 1          # 2026EST00001
end_case_number = 50           # last case to scrape
year = "2026"
output_file = "montgomery_estate_cases.csv"
download_dir = "downloads_mc"
max_threads = 5  # for parallel OCR

os.makedirs(download_dir, exist_ok=True)

# ---------- TESSERACT CONFIG ----------
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # adjust path

# ---------- SETUP SELENIUM ----------
options = webdriver.ChromeOptions()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)

# ---------- FUNCTION: OCR a docket PDF ----------
def process_docket(file_url):
    """Download docket PDF and extract phone number using OCR."""
    try:
        file_name = os.path.join(download_dir, file_url.split("/")[-1])
        r = requests.get(file_url)
        with open(file_name, "wb") as f:
            f.write(r.content)

        # OCR extraction
        if file_name.lower().endswith(".pdf"):
            images = convert_from_path(file_name)
            text = "".join([pytesseract.image_to_string(img) for img in images])
        else:
            img = Image.open(file_name)
            text = pytesseract.image_to_string(img)

        # Extract phone number
        phone_match = re.search(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
        if phone_match:
            return phone_match.group()
        return ""
    except Exception as e:
        print(f"Error processing file {file_url}: {e}")
        return ""

# ---------- STEP 1: Loop through cases ----------
cases = []
for i in range(start_case_number, end_case_number + 1):
    last5 = str(i).zfill(5)
    case_code = f"{year}EST{last5}"
    case_link = "https://go.mcohio.org/applications/probate/prodcfm/casesearchresultx.cfm?52514B565854050005020B02091657445F0105617873707263741D0101747D60707E7C7C"
    driver.get(case_link)
    time.sleep(2)

    # Enter year + last5 digits
    driver.find_element(By.ID, "caseNumberYear").clear()
    driver.find_element(By.ID, "caseNumberYear").send_keys(year)
    driver.find_element(By.ID, "caseNumberLast5").clear()
    driver.find_element(By.ID, "caseNumberLast5").send_keys(last5)
    driver.find_element(By.ID, "searchButton").click()  # adjust ID if needed
    time.sleep(3)

    # ---------- STEP 2: Scrape decedent/fiduciary info ----------
    try:
        decedent_name = driver.find_element(By.XPATH, "//span[contains(text(),'Decedent')]/following-sibling::span").text
        decedent_address = driver.find_element(By.XPATH, "//span[contains(text(),'Decedent Address')]/following-sibling::span").text
    except:
        decedent_name = ""
        decedent_address = ""

    try:
        fiduciary_name = driver.find_element(By.XPATH, "//span[contains(text(),'Fiduciary')]/following-sibling::span").text
        fiduciary_address = driver.find_element(By.XPATH, "//span[contains(text(),'Fiduciary Address')]/following-sibling::span").text
    except:
        fiduciary_name = ""
        fiduciary_address = ""

    # ---------- STEP 3: Collect docket PDF URLs ----------
    docket_links = driver.find_elements(By.XPATH, "//a[contains(text(),'Application') or contains(text(),'Notice of Deposit') or contains(text(),'SUMMARY RELEASE')]")
    docket_urls = [link.get_attribute("href") for link in docket_links]

    # ---------- STEP 4: Parallel OCR ----------
    fiduciary_phone = ""
    if docket_urls:
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
            results = executor.map(process_docket, docket_urls)
            for phone in results:
                if phone:
                    fiduciary_phone = phone
                    break

    # ---------- STEP 5: Add case data ----------
    cases.append({
        "case_code": case_code,
        "decedent_name": decedent_name,
        "decedent_address": decedent_address,
        "fiduciary_name": fiduciary_name,
        "fiduciary_address": fiduciary_address,
        "fiduciary_phone": fiduciary_phone
    })

# ---------- STEP 6: Auditor Website ----------
auditor_url = "https://www.mcrealestate.org/search/commonsearch.aspx?mode=owner"
for case in cases:
    driver.get(auditor_url)
    time.sleep(3)
    try:
        # Search by decedent name first
        driver.find_element(By.ID, "ctl00_PlaceHolderMain_txtSearchName").clear()
        driver.find_element(By.ID, "ctl00_PlaceHolderMain_txtSearchName").send_keys(case["decedent_name"])
        driver.find_element(By.ID, "ctl00_PlaceHolderMain_btnSearch").click()
        time.sleep(3)

        property_rows = driver.find_elements(By.XPATH, "//table[@id='ctl00_PlaceHolderMain_gvResults']//tr")[1:]
        properties = []
        for prop in property_rows:
            cells = prop.find_elements(By.TAG_NAME, "td")
            # Only include if owner matches decedent or fiduciary
            owner = cells[2].text
            if case["decedent_name"].lower() in owner.lower() or case["fiduciary_name"].lower() in owner.lower():
                properties.append({
                    "parcel_number": cells[0].text,
                    "address": cells[1].text,
                    "owner": owner,
                    "value": cells[3].text
                })
        case["properties"] = properties
    except:
        case["properties"] = []

# ---------- STEP 7: Save CSV ----------
with open(output_file, mode="w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    header = ["case_code","decedent_name","decedent_address","fiduciary_name","fiduciary_address","fiduciary_phone","properties"]
    writer.writerow(header)
    for case in cases:
        writer.writerow([
            case["case_code"],
            case["decedent_name"],
            case["decedent_address"],
            case["fiduciary_name"],
            case["fiduciary_address"],
            case["fiduciary_phone"],
            case["properties"]
        ])

print("Scraping complete! Data saved to", output_file)
driver.quit()
