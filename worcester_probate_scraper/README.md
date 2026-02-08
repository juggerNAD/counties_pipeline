# Worcester Probate Scraper

This repository contains a Python scraper for Worcester County probate cases. It extracts decedent, petitioner/fiduciary, docket entries, and PDFs, and attempts to locate petitioner phone numbers in the uploaded documents.

## Project Structure

```
worcester_probate_scraper/
├── config/
├── core/
├── parsers/
├── normalizers/
├── storage/
├── data/
└── logs/
```

## Setup

1. Clone the repository or download the folder.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Make sure you have a compatible WebDriver installed for Selenium (e.g., ChromeDriver for Chrome).

## Usage

```bash
python main.py
```

- The scraper reads selectors and settings from `config/`.
- PDF files are stored in `data/raw_pdfs/`.
- Extracted data is saved in `data/extracted_cases.jsonl`.
- Checkpoints are managed via `storage/checkpoint.py` to allow resuming scraping.

## Notes

- Only probate cases are scraped; small estate or guardian/conservator cases are ignored.
- Phone numbers are usually located in documents starting with "App" or "Affd".
- If the phone number is not in the earliest document, subsequent documents are checked.

## Contribution

If you want to contribute:

1. Fork the repository.
2. Make changes or add features.
3. Submit a pull request.
