from selenium.webdriver.remote.webdriver import WebDriver
from typing import List

def extract_case_links(driver: WebDriver, selectors: dict) -> List[str]:
    """
    Extracts all case detail links from the search results page.
    """
    links = []
    rows = driver.find_elements("xpath", selectors["search"]["rows"])

    for row in rows:
        try:
            link_elem = row.find_element("xpath", selectors["search"]["link"])
            href = link_elem.get_attribute("href")
            if href:
                links.append(href)
        except:
            continue
    return links
