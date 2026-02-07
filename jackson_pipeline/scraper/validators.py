# scraper/validators.py
INVALID_TYPES = {
    "Small Est Affidavit",
    "Guardian",
    "Conservatorship"
}

def is_valid_case(case_type: str) -> bool:
    return not any(bad.lower() in case_type.lower() for bad in INVALID_TYPES)
