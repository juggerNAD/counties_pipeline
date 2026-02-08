import pdfplumber
import re

def extract_text(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages[:3]:
            text += page.extract_text() or ""
    return text
