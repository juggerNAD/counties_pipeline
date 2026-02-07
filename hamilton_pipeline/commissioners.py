import os
import csv
import json
import re
import numpy as np
import cv2
import torch
from pdf2image import convert_from_path
from PIL import Image
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from doctr.io import DocumentFile
from doctr.models import ocr_predictor
from playwright.sync_api import sync_playwright

# ================= CONFIG =================
DOWNLOAD_FOLDER = r"C:\Users\juggernad\Desktop\PythonScrapingProject\hamilton_pipeline\downloads"
ZONES_FILE = "zones/single_page.json"
OUTPUT_CSV = "output.csv"
DEBUG_DIR = "debug_crops"
DPI = 300

os.makedirs(DEBUG_DIR, exist_ok=True)

# ================= LOAD ZONE =================
with open(ZONES_FILE, "r") as f:
    ZONE = json.load(f)["decedent_domicile"]

# ================= OCR MODELS =================
device = "cuda" if torch.cuda.is_available() else "cpu"

trocr_processor = TrOCRProcessor.from_pretrained("microsoft/trocr-base-handwritten")
trocr_model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-base-handwritten")
trocr_model.to(device)

doctr_model = ocr_predictor(pretrained=True)

# ================= HELPERS =================
def clean_text(text):
    text = text.upper()
    text = re.sub(r"[^A-Z0-9,\s]", "", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()

def trocr_ocr(cv_img):
    pil_img = Image.fromarray(cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB))
    pixel_values = trocr_processor(pil_img, return_tensors="pt").pixel_values.to(device)
    with torch.no_grad():
        ids = trocr_model.generate(pixel_values)
    return trocr_processor.batch_decode(ids, skip_special_tokens=True)[0]

def doctr_ocr_fullpage(pil_img):
    doc = DocumentFile.from_images(pil_img)
    result = doctr_model(doc)
    return result.render()

# ================= DOMICILE EXTRACTION =================
def extract_domicile(pdf_path):
    pages = convert_from_path(pdf_path, dpi=300)
    page = pages[0]  # always page 1 per your confirmation

    doc = DocumentFile.from_images(page)
    result = doctr_model(doc)

    words = []
    for block in result.pages[0].blocks:
        for line in block.lines:
            for word in line.words:
                words.append({
                    "text": word.value.upper(),
                    "box": word.geometry  # ((x0,y0),(x1,y1)) normalized
                })

    # 1️⃣ Find anchor
    anchor = None
    for w in words:
        if "DECEDENT" in w["text"] and "DOMICILE" in w["text"]:
            anchor = w
            break

    if not anchor:
        return "", True

    ax0, ay0 = anchor["box"][0]
    ax1, ay1 = anchor["box"][1]

    # 2️⃣ Extract handwriting to the RIGHT of anchor
    candidates = []
    for w in words:
        wx0, wy0 = w["box"][0]
        wx1, wy1 = w["box"][1]

        same_line = abs(wy0 - ay0) < 0.03
        right_side = wx0 > ax1

        if same_line and right_side:
            candidates.append(w["text"])

    domicile = clean_text(" ".join(candidates))

    return domicile, False if domicile else True

# ================= COMMISSIONER SCRAPER =================
def get_commissioner(page, case_number, retries=3):
    for attempt in range(retries):
        try:
            page.goto("https://www.probatect.org/court-records/court-record-search")
            page.fill("#caseSearchForm > div:nth-child(6) > input", case_number)
            page.click("#caseSearchForm > div:nth-child(7) > input")
            page.wait_for_timeout(3000)

            td = page.query_selector(
                "body > table:nth-child(1) > tbody > tr:nth-child(2) > td:nth-child(2)"
            )
            if not td:
                continue

            lines = [l.strip() for l in td.inner_text().splitlines() if l.strip()]
            for i, line in enumerate(lines):
                if "COMMISSIONER" in line.upper() or "FIDUCIARY" in line.upper():
                    if i + 1 < len(lines):
                        return lines[i + 1]
        except Exception as e:
            print(f"⚠️ Attempt {attempt+1} failed for {case_number}: {e}")

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
            fieldnames=[
                "Case Number",
                "Decedent Domicile",
                "Commissioner Name",
                "Needs Review"
            ]
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

            domicile, needs_review = extract_domicile(
                os.path.join(DOWNLOAD_FOLDER, pdf),
                case_number
            )
            commissioner = get_commissioner(page, case_number)

            writer.writerow({
                "Case Number": case_number,
                "Decedent Domicile": domicile,
                "Commissioner Name": commissioner,
                "Needs Review": "YES" if needs_review else "NO"
            })
            f.flush()

            print("   ✔ Domicile:", domicile[:60])
            print("   ✔ Commissioner:", commissioner)
            print("   ⚠ Review:", needs_review)

    browser.close()

print("✅ Extraction complete")
