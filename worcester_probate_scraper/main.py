from core.browser import get_driver
from storage.pdf_store import download_pdf
from parsers.pdf_parser import extract_text
from parsers.phone_extractor import find_phone
from normalizers.phone_normalizer import normalize

driver = get_driver()

# Pseudocode loop:
# 1. Search results
# 2. For each case:
#    - parse case
#    - download earliest PDF
#    - extract phone
#    - fallback to next PDF
#    - persist

