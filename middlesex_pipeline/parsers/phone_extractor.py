import re

PHONE_REGEX = re.compile(
    r'(\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4})'
)

def find_phone(text):
    matches = PHONE_REGEX.findall(text)
    return matches[0] if matches else None
