from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import os
import pandas as pd
from modules.utils import wait_for_element, delay, setup_logger
from config import settings

logger = setup_logger(settings.LOG_FILE)

class ProbateScraper:
    def __init__(self, driver_path="drivers/chromedriver.exe"):
        options = Options()
        if settings.HEADLESS:
            options.add_argument("--headless")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--start-maximized")
        self.driver = webdriver.Chrome(service=Service(driver_path), options=options)

    def accept_terms(self):
        self.driver.get(settings.PROBATE_URL)
        delay(2)
        try:
            accept_btn = self.driver.find_element(By.XPATH, "//input[@value='I Accept']")
            accept_btn.click()
            logger.info("Accepted terms")
            delay(2)
        except Exception as e:
            logger.warning(f"No accept button found: {e}")

    def search_cases(self, case_type, date_from, date_to):
        # Select case type
        select = self.driver.find_element(By.XPATH, f"//select[@name='caseType']/option[text()='{case_type}']")
        select.click()
        delay(1)
        # Enter date range
        self.driver.find_element(By.NAME, "dateFrom").send_keys(date_from)
        self.driver.find_element(By.NAME, "dateTo").send_keys(date_to)
        # Click search
        self.driver.find_element(By.NAME, "searchButton").click()
        delay(3)

    def extract_case_links(self):
        # AJAX table: collect unique case links
        links = set()
        rows = self.driver.find_elements(By.XPATH, "//table[@id='results']//tr")
        for row in rows:
            try:
                link = row.find_element(By.TAG_NAME, "a").get_attribute("href")
                links.add(link)
            except:
                continue
        logger.info(f"Found {len(links)} unique cases")
        return list(links)

    def download_case_pdf(self, case_url):
        self.driver.get(case_url)
        delay(2)
        try:
            docket_tab = self.driver.find_element(By.XPATH, "//a[text()='Dockets']")
            docket_tab.click()
            delay(2)
            # Earliest uploaded PDF (first row)
            pdf_link = self.driver.find_element(By.XPATH, "//table[@id='dockets']//tr[1]//a").get_attribute("href")
            filename = pdf_link.split("/")[-1]
            output_path = os.path.join(settings.PDF_DOWNLOAD_PATH, filename)
            os.system(f"curl -o \"{output_path}\" \"{pdf_link}\"")
            logger.info(f"Downloaded PDF: {filename}")
            return output_path
        except Exception as e:
            logger.error(f"Failed to download PDF from {case_url}: {e}")
            return None

    def close(self):
        self.driver.quit()

