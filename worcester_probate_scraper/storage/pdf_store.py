import requests
from pathlib import Path

def download_pdf(url, case_id):
    path = Path("data/raw_pdfs") / f"{case_id}.pdf"
    r = requests.get(url, timeout=30)
    path.write_bytes(r.content)
    return path
