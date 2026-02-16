import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

# -----------------------------
# CONFIGURATION
# -----------------------------
START_CASE = 2026000050
END_CASE = 2026000500
BASE_URL = "https://www.probatect.org/court-records/court-record-search"

BASE_DIR = Path(__file__).parent.resolve()
DOWNLOAD_DIR = BASE_DIR / "downloads"
DOWNLOAD_DIR.mkdir(exist_ok=True)

PROCESSED_FILE = BASE_DIR / "processed_cases.json"

TARGET_DOCS = [
    "APPLICATION TO PROBATE WILL",
    "APPLICATION FOR AUTHORITY TO ADMINISTER ESTATE"
]

# Load processed cases
if PROCESSED_FILE.exists():
    with open(PROCESSED_FILE, "r") as f:
        processed_cases = set(json.load(f))
else:
    processed_cases = set()


# -----------------------------
# MAIN SCRAPER LOOP
# -----------------------------
def main():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)  # MUST be headless for PDF
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

                        with context.expect_page() as doc_page_info:
                            row.locator("a").first.click()

                        doc_page = doc_page_info.value
                        doc_page.wait_for_load_state("networkidle")
                        time.sleep(2)

                        pdf_path = DOWNLOAD_DIR / f"{case_number}.pdf"

                        print(f"📄 Saving PDF for case {case_number}...")

                        doc_page.pdf(
                            path=str(pdf_path),
                            format="Letter"
                        )

                        print(f"✅ Saved {pdf_path}")
                        doc_page.close()
                        break

                if not found_doc:
                    print(f"ℹ️ No target documents found for case {case_number}")

                page.close()
                time.sleep(1)

                processed_cases.add(str(case_number))
                with open(PROCESSED_FILE, "w") as f:
                    json.dump(list(processed_cases), f)

    except KeyboardInterrupt:
        print("\n⏹️ Process interrupted by user.")

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
