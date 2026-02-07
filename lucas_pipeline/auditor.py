import time
from selenium.webdriver.common.by import By

def search_auditor(driver, name):
    driver.get(
        "https://icare.co.lucas.oh.us/lucascare/search/commonsearch.aspx?mode=owner"
    )

    time.sleep(2)
    driver.find_element(By.ID, "ownerName").send_keys(name)
    driver.find_element(By.ID, "search").click()

    time.sleep(4)

    results = driver.find_elements(By.CSS_SELECTOR, "tr")
    if results:
        return results[0].text
    return None
