# scraper/pdf_parser.py
import pdfplumber
import fitz

def extract_text(pdf_path):
    text = ""

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""

    if len(text.strip()) < 50:
        doc = fitz.open(pdf_path)
        for page in doc:
            text += page.get_text()

    return text
