import requests
import pdfplumber
import pytesseract
from io import BytesIO
from pdfplumber.utils import PDFSyntaxError
from PIL import Image
import logging

def download_pdf(url):
    try:
        r = requests.get(url)
        r.raise_for_status()
        return BytesIO(r.content)
    except Exception as e:
        logging.error(f"PDF download failed: {e}")
        return None

def extract_text_from_pdf(pdf_file):
    text = ""
    try:
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
                else:  # OCR fallback
                    image = page.to_image()
                    text += pytesseract.image_to_string(image.original) + "\n"
    except PDFSyntaxError:
        logging.error("PDFSyntaxError: Could not parse PDF")
    return text

def extract_phone(text):
    import re
    pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    matches = re.findall(pattern, text)
    return matches[0] if matches else None
