import os
import time
import csv
import re
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from pdf2image import convert_from_path
from PIL import Image
import pytesseract
import concurrent.futures

# ---------- USER INPUT ----------
start_date = "01/01/2024"
end_date = "01/31/2024"
output_file = "summit_estate_cases.csv"
download_dir = "downloads"
max_threads = 5  # Number of parallel threads for docket OCR

os.makedirs(download_dir, exist_ok=True)

# ---------- TESSERACT CONFIG ----------
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # adjust path

# ---------- SETUP SELENIUM ----------
options = webdriver.ChromeOptions()
prefs = {"download.default_directory": os.path.abspath(download_dir)}
options.add_experimental_option("prefs", prefs)
options.add_argument("--headless")  # remove if you want to see browser
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)

# ---------- FUNCTION: Download + OCR ----------
def process_docket(file_url):
    """Download docket file and extract phone number using OCR."""
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

# ---------- STEP 1: Probate Website ----------
probate_url = "https://search.summitohioprobate.com/eservices/search.page.3.1?x=IMHge8hZipVr1ODOF8nmJA"
driver.get(probate_url)

# Select "Estate" case type
Select(wait.until(EC.presence_of_element_located((By.ID, "caseType")))).select_by_visible_text("Estate")
driver.find_element(By.ID, "beginFileDate").send_keys(start_date)
driver.find_element(By.ID, "endFileDate").send_keys(end_date)
driver.find_element(By.ID, "searchButton").click()
time.sleep(5)

# ---------- STEP 2: Scrape case list ----------
cases = []
case_rows = driver.find_elements(By.XPATH, "//table[@id='caseResults']//tr")[1:]
for row in case_rows:
    cols = row.find_elements(By.TAG_NAME, "td")
    case_code = cols[0].text
    file_date = cols[1].text
    case_link = cols[0].find_element(By.TAG_NAME, "a").get_attribute("href")
    cases.append({"case_code": case_code, "file_date": file_date, "link": case_link})

# ---------- STEP 3: Visit each case ----------
for case in cases:
    driver.get(case["link"])
    time.sleep(2)

    # Decedent & fiduciary info
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

    case.update({
        "decedent_name": decedent_name,
        "decedent_address": decedent_address,
        "fiduciary_name": fiduciary_name,
        "fiduciary_address": fiduciary_address
    })

    # ---------- STEP 4: Collect docket URLs ----------
    docket_links = driver.find_elements(By.XPATH, "//a[contains(text(),'Application')]")
    docket_urls = [link.get_attribute("href") for link in docket_links]

    # ---------- STEP 5: OCR in parallel ----------
    fiduciary_phone = ""
    if docket_urls:
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
            results = executor.map(process_docket, docket_urls)
            for phone in results:
                if phone:
                    fiduciary_phone = phone
                    break

    case["fiduciary_phone"] = fiduciary_phone

# ---------- STEP 6: Auditor Website ----------
auditor_url = "https://propertyaccess.summitoh.net/search/commonsearch.aspx?mode=realprop"
for case in cases:
    driver.get(auditor_url)
    time.sleep(3)

    try:
        driver.find_element(By.ID, "ctl00_PlaceHolderMain_txtSearchAddress").send_keys(case["decedent_address"])
        driver.find_element(By.ID, "ctl00_PlaceHolderMain_btnSearch").click()
        time.sleep(3)

        property_rows = driver.find_elements(By.XPATH, "//table[@id='ctl00_PlaceHolderMain_gvResults']//tr")[1:]
        properties = []
        for prop in property_rows:
            cells = prop.find_elements(By.TAG_NAME, "td")
            properties.append({
                "parcel_number": cells[0].text,
                "address": cells[1].text,
                "owner": cells[2].text,
                "value": cells[3].text
            })
        case["properties"] = properties
    except:
        case["properties"] = []

# ---------- STEP 7: Save CSV ----------
with open(output_file, mode="w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    header = ["case_code","file_date","decedent_name","decedent_address","fiduciary_name","fiduciary_address","fiduciary_phone","properties"]
    writer.writerow(header)
    for case in cases:
        writer.writerow([
            case["case_code"],
            case["file_date"],
            case["decedent_name"],
            case["decedent_address"],
            case["fiduciary_name"],
            case["fiduciary_address"],
            case["fiduciary_phone"],
            case["properties"]
        ])

print("Scraping complete! Data saved to", output_file)
driver.quit()
