# Missouri Probate Case Scraper

This application scrapes **Missouri Case.net probate filings** and extracts
**petitioner phone numbers from docket PDFs**, following strict probate rules.

## ✅ Supported Sources
- Missouri Case.net (All Counties)
- Jackson County Auditor (optional enrichment)

## 🚫 Ignored Case Types
- Small Estate Affidavit
- Guardian
- Conservatorship

## 📅 Filing Date Rules
- Uses rolling **7-day windows**
- Automatically expands timeframe to offset missing phone numbers

## 📄 PDF Extraction Rules
- Start with earliest docket document
- Prefer documents containing:
  - App
  - Affd
  - Application
  - Affidavit
- OCR fallback for scanned PDFs

## 📁 Directory Structure
