# scraper/phone_extractor.py
import re

PHONE_REGEX = re.compile(
    r'(\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4})'
)

KEYWORDS = ("app", "affd", "application", "affidavit")

def extract_phone(text, filename):
    if not any(k in filename.lower() for k in KEYWORDS):
        return None

    matches = PHONE_REGEX.findall(text)
    return matches[0] if matches else None
