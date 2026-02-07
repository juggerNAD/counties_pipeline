# utils/normalizers.py
import re

def normalize_whitespace(text: str) -> str:
    return re.sub(r'\s+', ' ', text).strip()


def normalize_phone(phone: str) -> str | None:
    digits = re.sub(r'\D', '', phone)
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    return None


def normalize_name(name: str) -> str:
    return normalize_whitespace(name).title()


def safe_filename(value: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', '_', value)
