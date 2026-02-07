import time
from selenium.webdriver.common.by import By

VALID_TYPES = ["EST", "WD"]

def collect_cases(driver):
    cases = []

    rows = driver.find_elements(By.CSS_SELECTOR, "tr.k-master-row")
    for row in rows:
        case_type = row.text.split()[1]
        if case_type in VALID_TYPES:
            cases.append(row)
    return cases


def open_case(row):
    row.click()
    time.sleep(4)
