# scraper_download_pdf.py
import os
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

CASE = "2026000055"
OUT = os.path.join(os.getcwd(), "downloads")
os.makedirs(OUT, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(accept_downloads=True)  # important
    page = context.new_page()
    
    # 1️⃣ Go to search page
    page.goto("https://www.probatect.org/court-records/court-record-search")
    
    # 2️⃣ Fill in case number and submit
    page.wait_for_selector("#caseSearchForm > div:nth-child(6) > input", timeout=20000)
    page.fill("#caseSearchForm > div:nth-child(6) > input", CASE)
    page.click("#caseSearchForm > div:nth-child(7) > input")
    
    # 3️⃣ Wait for results iframe
    page.wait_for_timeout(3000)
    detail_frame = None
    for f in page.frames:
        if "CaseSearch_Detail.asp" in (f.url or ""):
            detail_frame = f
            break
    if not detail_frame:
        raise Exception("Results iframe not found")
    
    # 4️⃣ Extract Decedent, Case Type, and Commissioner
    detail_frame.wait_for_selector("table.table-striped-alt", timeout=20000)
    html = detail_frame.content()
    soup = BeautifulSoup(html, "html.parser")
    
    table = soup.find("table", class_="table-striped-alt")
    rows = table.find_all("tr")[1]  # second row contains data
    
    decedent_td, parties_td = rows.find_all("td")
    
    # Decedent
    decedent_name_tag = decedent_td.find("strong", string="NAME:")
    decedent_name = decedent_name_tag.next_sibling.strip() if decedent_name_tag else "Not found"
    case_type_tag = decedent_td.find("strong", string="TYPE:")
    case_type = case_type_tag.next_sibling.strip() if case_type_tag else "Not found"
    
    # Commissioner (Fiduciary Non-Attorney)
    fid_tag = parties_td.find("strong", string=lambda x: x and "FIDUCIARY" in x)
    if fid_tag:
        fid_text = ""
        for sib in fid_tag.next_siblings:
            if getattr(sib, "name", None) == "br":
                continue
            if isinstance(sib, str):
                fid_text += sib.strip() + " "
        commissioner_name = fid_text.strip().split("\n")[0] if fid_text else "Not found"
        commissioner_address = fid_text.strip().split("\n")[1:] if fid_text else []
        commissioner_address = ", ".join([line.strip() for line in commissioner_address])
    else:
        commissioner_name = "Not found"
        commissioner_address = "Not found"
    
    print(f"Decedent: {decedent_name}")
    print(f"Case Type: {case_type}")
    print(f"Commissioner Name: {commissioner_name}")
    print(f"Commissioner Address: {commissioner_address}")
    
    # 5️⃣ Find the PDF link
    t2 = soup.find_all("table", class_="table-striped-alt")[1]
    pdf_url = None
    for row in t2.find_all("tr"):
        row_text = row.get_text(" ", strip=True).upper()
        if "APPLICATION TO PROBATE" in row_text or "APPLICATION FOR AUTHORITY TO ADMINISTER ESTATE" in row_text:
            a = row.find("a")
            if a:
                pdf_url = a["href"].replace("..", "")
                break
    if not pdf_url:
        raise Exception("PDF link not found")
    
    # 6️⃣ Open PDF in new tab
    pdf_page = context.new_page()
    final_pdf_url = f"https://www.probatect.org{pdf_url}"
    pdf_page.goto(final_pdf_url)
    
    # 7️⃣ Click the download arrow
    try:
        # Only click the PDF download arrow (safely)
        download = pdf_page.wait_for_event("download", timeout=30000)
        pdf_page.locator("div.icon.pdf").click()  # target correct icon
        pdf_path = download.value.path()
    except Exception as e:
        print("Failed to find or click PDF download arrow:", e)
        pdf_path = None
    
    if pdf_path:
        print("PDF saved to:", pdf_path)
    else:
        print("PDF download failed.")
    
    browser.close()
