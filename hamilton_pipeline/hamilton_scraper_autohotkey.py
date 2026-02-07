import json
import time
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright

# -----------------------------
# CONFIGURATION
# -----------------------------
START_CASE = 2026000050
END_CASE = 2026000500
BASE_URL = "https://www.probatect.org/court-records/court-record-search"
DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)
PROCESSED_FILE = Path("processed_cases.json")
TARGET_DOCS = [
    "APPLICATION TO PROBATE WILL",
    "APPLICATION FOR AUTHORITY TO ADMINISTER ESTATE"
]
AHK_PATH = r"C:\Program Files\AutoHotkey\AutoHotkey.exe"
AHK_SCRIPT = r"C:\Users\juggernad\Desktop\PythonScrapingProject\hamilton_pipeline\print_pdf.ahk"

# Load processed cases if exists
if PROCESSED_FILE.exists():
    with open(PROCESSED_FILE, "r") as f:
        processed_cases = set(json.load(f))
else:
    processed_cases = set()


# -----------------------------
# FUNCTION TO RUN AUTOHOTKEY
# -----------------------------
def run_ahk(case_number: int):
    pdf_file = DOWNLOAD_DIR / f"{case_number}.pdf"

    # Delete existing PDF if exists
    if pdf_file.exists():
        print(f"⚠️ PDF {pdf_file} already exists. Replacing...")
        pdf_file.unlink()

    # Run AutoHotkey
    subprocess.Popen([AHK_PATH, AHK_SCRIPT, str(case_number)])

    # Wait until PDF appears
    print(f"⏳ Waiting for PDF {pdf_file} to be saved...")
    timeout = 60  # seconds
    start_time = time.time()
    while not pdf_file.exists():
        time.sleep(1)
        if time.time() - start_time > timeout:
            raise RuntimeError(f"❌ Timeout waiting for {pdf_file} to be created")
    time.sleep(2)  # ensure write completed
    print(f"✅ PDF {pdf_file} saved successfully!")


# -----------------------------
# MAIN SCRAPER LOOP
# -----------------------------
try:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()

        for case_number in range(START_CASE, END_CASE + 1):
            if str(case_number) in processed_cases:
                print(f"⏭️ Skipping already processed case {case_number}")
                continue

            print(f"\n🔎 Searching case {case_number}...")
            page = context.new_page()  # new tab per case
            page.goto(BASE_URL, wait_until="networkidle")

            # Fill case number & submit
            page.fill("#caseSearchForm > div:nth-child(6) > input", str(case_number))
            page.click("#caseSearchForm > div:nth-child(7) > input")

            # Wait for results frame
            try:
                page.wait_for_selector("#results-frame", timeout=10000)
            except:
                print(f"⚠️ No results frame found for case {case_number}. Skipping...")
                processed_cases.add(str(case_number))
                page.close()
                continue

            frame = page.frame_locator("#results-frame")
            rows = frame.locator("table.table-striped-alt tr")

            # Search for target documents
            found_doc = False
            for i in range(rows.count()):
                row = rows.nth(i)
                txt = row.inner_text().upper()
                if any(d in txt for d in TARGET_DOCS):
                    found_doc = True
                    # Open PDF viewer
                    with context.expect_page() as doc_page_info:
                        row.locator("a").first.click()
                    doc_page = doc_page_info.value
                    doc_page.wait_for_load_state("domcontentloaded")
                    time.sleep(2)

                    # Force load all pages by scrolling
                    print("📄 Viewer opened, scrolling to load all pages...")
                    last_height = 0
                    for _ in range(30):
                        doc_page.mouse.wheel(0, 5000)
                        time.sleep(0.7)
                        height = doc_page.evaluate("document.body.scrollHeight")
                        if height == last_height:
                            break
                        last_height = height

                    # Trigger AutoHotkey to print PDF
                    print(f"🖨️ Triggering AutoHotkey to print case {case_number} → PDF")
                    run_ahk(case_number)

                    # Close PDF tab to free resources
                    doc_page.close()
                    time.sleep(1)
                    break

            if not found_doc:
                print(f"ℹ️ No target documents found for case {case_number}, skipping PDF.")

            # Close search tab
            page.close()
            time.sleep(1)  # give Chrome a little breathing room

            # Mark case as processed
            processed_cases.add(str(case_number))

            # Save progress after each case
            with open(PROCESSED_FILE, "w") as f:
                json.dump(list(processed_cases), f)

except KeyboardInterrupt:
    print("\n⏹️ Process interrupted by user. Progress saved.")

finally:
    browser.close()
    print("\n✅ Scraper finished. All progress saved.")
