from scraper.probate_scraper import scrape_county_probate

if __name__ == "__main__":
    print("Starting Missouri Probate Scraper with property normalization...")
    # Scrape 2 weeks of cases for more volume
    data = scrape_county_probate(county_code="SLC", days_back=14)
    print(f"Scraped {len(data)} entries (probate cases + properties).")
    print("Data saved to data/output.csv")
