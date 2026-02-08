import re
import pdfplumber

PHONE_REGEX = re.compile(
    r"(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})"
)

def extract_phone_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages[:2]:  # phone almost always page 1–2
            text = page.extract_text() or ""
            match = PHONE_REGEX.search(text)
            if match:
                return match.group(1)
    return None

