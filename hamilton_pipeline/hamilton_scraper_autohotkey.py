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

# Downloads folder next to script/exe
BASE_DIR = Path(__file__).parent.resolve()
DOWNLOAD_DIR = BASE_DIR / "downloads"
DOWNLOAD_DIR.mkdir(exist_ok=True)

PROCESSED_FILE = BASE_DIR / "processed_cases.json"

TARGET_DOCS = [
    "APPLICATION TO PROBATE WILL",
    "APPLICATION FOR AUTHORITY TO ADMINISTER ESTATE"
]

AHK_PATH = r"C:\Program Files\AutoHotkey\AutoHotkey.exe"
AHK_SCRIPT = BASE_DIR / "print_pdf.ahk"  # AHK script in same folder

# Load processed cases
if PROCESSED_FILE.exists():
    with open(PROCESSED_FILE, "r") as f:
        processed_cases = set(json.load(f))
else:
    processed_cases = set()


# -----------------------------
# RUN AUTOHOTKEY TO SAVE PDF
# -----------------------------
def run_ahk(case_number: int):
    pdf_file = DOWNLOAD_DIR / f"{case_number}.pdf"

    # Delete existing PDF
    if pdf_file.exists():
        print(f"⚠️ PDF {pdf_file} already exists. Replacing...")
        pdf_file.unlink()

    # Run AutoHotkey
    subprocess.run([AHK_PATH, str(AHK_SCRIPT), str(case_number)], check=True)

    # Wait until PDF exists and is stable
    print(f"⏳ Waiting for PDF {pdf_file} to be fully saved...")
    timeout = 60  # max 1 minute per PDF
    start_time = time.time()
    last_size = -1
    stable_counter = 0

    while True:
        if pdf_file.exists():
            current_size = pdf_file.stat().st_size
            if current_size == last_size:
                stable_counter += 1
            else:
                stable_counter = 0
            last_size = current_size

            if stable_counter >= 2:  # stable for ~1 second
                break

        if time.time() - start_time > timeout:
            print(f"⚠️ Timeout waiting for {pdf_file}. Skipping this case.")
            return False

        time.sleep(0.5)

    print(f"✅ PDF {pdf_file} saved successfully!")
    return True

# -----------------------------
# MAIN SCRAPER LOOP
# -----------------------------
def main():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()

            for case_number in range(START_CASE, END_CASE + 1):
                if str(case_number) in processed_cases:
                    print(f"⏭️ Skipping already processed case {case_number}")
                    continue

                print(f"\n🔎 Searching case {case_number}...")
                page = context.new_page()
                page.goto(BASE_URL, wait_until="networkidle")

                # Fill case number & submit
                page.fill("#caseSearchForm > div:nth-child(6) > input", str(case_number))
                page.click("#caseSearchForm > div:nth-child(7) > input")

                # Wait for results frame
                try:
                    page.wait_for_selector("#results-frame", timeout=10000)
                except:
                    print(f"⚠️ No results frame for case {case_number}. Skipping...")
                    processed_cases.add(str(case_number))
                    page.close()
                    continue

                frame = page.frame_locator("#results-frame")
                rows = frame.locator("table.table-striped-alt tr")

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

                        # Scroll to load all pages
                        print("📄 Viewer opened, scrolling to load all pages...")
                        last_height = 0
                        for _ in range(30):
                            doc_page.mouse.wheel(0, 5000)
                            time.sleep(0.7)
                            height = doc_page.evaluate("document.body.scrollHeight")
                            if height == last_height:
                                break
                            last_height = height

                        # Trigger AutoHotkey
                        print(f"🖨️ Triggering AutoHotkey to print case {case_number} → PDF")
                        success = run_ahk(case_number)
                        if not success:
                            print(f"⚠️ Skipping PDF for case {case_number} due to timeout.")

                        doc_page.close()
                        time.sleep(1)
                        break

                if not found_doc:
                    print(f"ℹ️ No target documents found for case {case_number}, skipping PDF.")

                page.close()
                time.sleep(1)

                # Save processed case
                processed_cases.add(str(case_number))
                with open(PROCESSED_FILE, "w") as f:
                    json.dump(list(processed_cases), f)

    except KeyboardInterrupt:
        print("\n⏹️ Process interrupted by user. Progress saved.")

    finally:
        try:
            browser.close()
        except:
            pass
        print("\n✅ Scraper finished. All progress saved!")


# -----------------------------
# ENTRY POINT
# -----------------------------
if __name__ == "__main__":
    main()
