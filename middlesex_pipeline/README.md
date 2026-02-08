# Middlesex Probate Scraper (Missouri Case.net)

## Overview
This project scrapes probate case data from the Missouri Case.net court system,
extracts docket PDFs, and attempts to locate petitioner phone numbers from
probate filings.

The scraper is designed to be:
- County-configurable
- Throttle-safe
- Retry-hardened
- PDF-first (not HTML-dependent)

## Supported Courts
- Missouri Probate Courts (all counties via Case.net)

## Data Extracted
- Case number
- Decedent name
- Petitioner / Fiduciary name
- Filing date
- PDF document links
- Phone number (if present)

## Case Filters
Excluded case types:
- Small Estate Affidavit
- Guardian
- Conservatorship

Included case types:
- All other estate-related probate cases

## How It Works
1. Queries Case.net using a 7-day filing window
2. Iterates through probate cases
3. Parses parties and docket entries
4. Downloads PDFs (earliest first)
5. Searches PDFs for phone numbers
6. Saves structured output to JSONL

## Project Structure
See directory layout in the root folder.

## Installation
```bash
pip install -r requirements.txt
