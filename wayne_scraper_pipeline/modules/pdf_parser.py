import pdfplumber
import re
import logging
from modules.utils import setup_logger
logger = setup_logger("logs/pdf_parser.log")

PHONE_REGEX = r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"

def extract_info_from_pdf(pdf_path):
    data = {"decedent": None, "fiduciary": None, "phone_numbers": []}
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if not text:
                    continue
                # Decedent
                if "Decedent" in text:
                    data["decedent"] = text.split("Decedent")[1].split("\n")[0].strip()
                # Fiduciary / Petitioner
                if "Petitioner" in text or "Fiduciary" in text:
                    data["fiduciary"] = text.split("Petitioner")[-1].split("\n")[0].strip()
                # Phone numbers
                phones = re.findall(PHONE_REGEX, text)
                for phone in phones:
                    if phone not in data["phone_numbers"]:
                        data["phone_numbers"].append(phone)
    except Exception as e:
        logger.error(f"Error parsing PDF {pdf_path}: {e}")
    return data

