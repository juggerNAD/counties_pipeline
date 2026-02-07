import time
import os
import re
import pdfplumber
from selenium.webdriver.common.by import By  # ✅ ADD THIS LINE

PHONE_REGEX = r"(\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4})"

def download_pdfs(driver):
    links = driver.find_elements(By.LINK_TEXT, "PDF")
    for link in links:
        for _ in range(3):
            try:
                link.click()
                time.sleep(7)  # Lucas County PDFs are slow
                break
            except:
                time.sleep(5)

def extract_phone(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            match = re.search(PHONE_REGEX, text)
            if match:
                return match.group(1)
    return None
