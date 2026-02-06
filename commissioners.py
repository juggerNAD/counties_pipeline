import os
import csv
import json
import re
import numpy as np
from pdf2image import convert_from_path
import cv2
import pytesseract
from playwright.sync_api import sync_playwright

# ================= CONFIG =================
DOWNLOAD_FOLDER = r"C:\Users\juggernad\Desktop\PythonScrapingProject\hamilton_pipeline\downloads"
ZONES_FILE = "zones/single_page.json"
OUTPUT_CSV = "output.csv"
DPI = 300

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ================= LOAD ZONE =================
with open(ZONES_FILE, "r") as f:
    ZONE = json.load(f)["decedent_domicile"]

# ================= HELPERS =================
def clean_text(text):
    text = text.upper()
    text = re.sub(r"[^A-Z0-9,\s]", "", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()

def extract_domicile(pdf_path):
    pages = convert_from_path(pdf_path, dpi=DPI)
    img = cv2.cvtColor(np.array(pages[0]), cv2.COLOR_RGB2BGR)
    x1, y1, x2, y2 = ZONE
    crop = img[y1:y2, x1:x2]
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray, config="--psm 6")
    return clean_text(text)

def get_commissioner(page, case_number, retries=3):
    for attempt in range(retries):
        try:
            # Go to search page
            page.goto("https://www.probatect.org/court-records/court-record-search")

            # Fill in case number and submit
            page.fill("#caseSearchForm > div:nth-child(6) > input", case_number)
            page.click("#caseSearchForm > div:nth-child(7) > input")

            # Wait a few seconds for results to render
            page.wait_for_timeout(3000)

            # Use CSS selector for the commissioner TD
            td = page.query_selector("body > table:nth-child(1) > tbody > tr:nth-child(2) > td:nth-child(2)")
            if not td:
                continue  # retry

            lines = [line.strip() for line in td.inner_text().splitlines() if line.strip()]
            for i, line in enumerate(lines):
                if "COMMISSIONER (NON ATTORNEY) (ACTIVE)" in line.upper() or \
                   "FIDUCIARY (NON ATTORNEY) (ACTIVE)" in line.upper():
                    if i + 1 < len(lines):
                        return lines[i + 1]  # name
        except Exception as e:
            print(f"⚠️ Attempt {attempt+1} failed for case {case_number}: {e}")

    print(f"⚠️ Commissioner not found for case {case_number}")
    return ""

# ================= MAIN =================
processed = set()
if os.path.exists(OUTPUT_CSV):
    with open(OUTPUT_CSV, newline="") as f:
        for r in csv.DictReader(f):
            processed.add(r["Case Number"])

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    with open(OUTPUT_CSV, "a", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["Case Number", "Decedent Domicile", "Commissioner Name"]
        )
        if not processed:
            writer.writeheader()

        for pdf in os.listdir(DOWNLOAD_FOLDER):
            if not pdf.lower().endswith(".pdf"):
                continue

            case_number = pdf.replace(".pdf", "")
            if case_number in processed:
                continue

            print(f"📄 Processing {case_number}")
            domicile = extract_domicile(os.path.join(DOWNLOAD_FOLDER, pdf))
            commissioner = get_commissioner(page, case_number)

            writer.writerow({
                "Case Number": case_number,
                "Decedent Domicile": domicile,
                "Commissioner Name": commissioner
            })
            f.flush()

            print("   ✔ Domicile:", domicile[:60])
            print("   ✔ Commissioner:", commissioner)

    browser.close()
print("✅ Extraction complete")
