import os
import time
import sys
import pandas as pd

from driver import get_driver
from login import login
from advanced_search import advanced_search
from probate import collect_cases, open_case
from pdf_handler import extract_phone
from auditor import search_auditor


def main():
    print("🚀 Starting Lucas County Probate Scraper", flush=True)

    # -------------------------
    # Directory setup
    # -------------------------
    BASE_DIR = os.getcwd()
    PDF_DIR = os.path.join(BASE_DIR, "downloads", "pdfs")
    OUTPUT_DIR = os.path.join(BASE_DIR, "output")

    os.makedirs(PDF_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print(f"📁 PDFs directory: {PDF_DIR}")
    print(f"📁 Output directory: {OUTPUT_DIR}")

    # -------------------------
    # Launch browser
    # -------------------------
    try:
        driver = get_driver(PDF_DIR)
        print("🌐 Chrome launched successfully")
    except Exception as e:
        print("❌ Failed to launch browser:", e)
        sys.exit(1)

    # -------------------------
    # Manual Login
    # -------------------------
    try:
        login(driver)
        print("🔐 Login confirmed")
    except Exception as e:
        print("❌ Login failed:", e)
        driver.quit()
        sys.exit(1)

    # -------------------------
    # Apply Advanced Search filters
    # -------------------------
    try:
        print("\n🔎 Applying Advanced Search filters...")
        advanced_search(driver)
    except Exception as e:
        print("❌ Advanced Search failed:", e)
        driver.quit()
        sys.exit(1)

    # -------------------------
    # Collect probate cases
    # -------------------------
    print("\n🔍 Collecting probate cases...")
    try:
        cases = collect_cases(driver)
    except Exception as e:
        print("❌ Failed to collect cases:", e)
        driver.quit()
        sys.exit(1)

    print(f"📂 Total valid cases found: {len(cases)}")

    if not cases:
        print("⚠️ No EST / WD cases found. Exiting safely.")
        driver.quit()
        return

    records = []

    # -------------------------
    # Process each case
    # -------------------------
    for index, case in enumerate(cases, start=1):
        print(f"\n📄 Processing case {index} of {len(cases)}")

        try:
            open_case(case)
            time.sleep(3)
        except Exception as e:
            print("⚠️ Failed to open case:", e)
            continue

        phone = None

        # Scan downloaded PDFs
        try:
            for file_name in os.listdir(PDF_DIR):
                if not file_name.lower().endswith(".pdf"):
                    continue

                pdf_path = os.path.join(PDF_DIR, file_name)
                phone = extract_phone(pdf_path)

                if phone:
                    print(f"📞 Phone found: {phone}")
                    break
        except Exception as e:
            print("⚠️ PDF parsing error:", e)

        # Auditor lookup (placeholder name for now)
        auditor_data = None
        try:
            auditor_data = search_auditor(driver, "UNKNOWN")
        except Exception as e:
            print("⚠️ Auditor search failed:", e)

        records.append({
            "Case Index": index,
            "Phone": phone,
            "Auditor Data": auditor_data
        })

        # Go back to case list
        driver.back()
        time.sleep(3)

    # -------------------------
    # Save results
    # -------------------------
    df = pd.DataFrame(records)
    output_file = os.path.join(OUTPUT_DIR, "lucas_probate_results.csv")
    df.to_csv(output_file, index=False)

    print(f"\n✅ DONE. Results saved to:\n{output_file}")

    driver.quit()


# -------------------------
# Entry point
# -------------------------
if __name__ == "__main__":
    main()
