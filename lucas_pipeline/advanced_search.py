import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def advanced_search(driver):
    """
    Fully automates Advanced Search in Lucas County Probate site:
    1. Dashboard → Advanced
    2. Search for: Cases
    3. Search by → Case Category → Select → check Probate & Mental Health → Done
    4. Click SEARCH
    """

    wait = WebDriverWait(driver, 60)

    # 1️⃣ Go to Dashboard
    driver.get("https://researchoh.tylerhost.net/CourtRecordsSearch/#!/dashboard")
    time.sleep(5)  # wait for page to render

    # 2️⃣ Click Advanced button (below Quick Search)
    advanced_btn = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(), 'Advanced')]")
        )
    )
    advanced_btn.click()
    time.sleep(3)  # allow Advanced Search page to load

    # 3️⃣ Ensure "Search for" dropdown is set to Cases
    search_for_select = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//select[@ng-model='advancedSearch.searchFor']")
        )
    )
    search_for_select.click()
    time.sleep(1)
    cases_option = search_for_select.find_element(By.XPATH, ".//option[text()='Cases']")
    cases_option.click()
    time.sleep(1)

    # 4️⃣ Click "Search By" dropdown → Case Category
    search_by_dropdown = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(@aria-label,'Search by')]")
        )
    )
    search_by_dropdown.click()
    time.sleep(2)

    # 5️⃣ Click SELECT button to open popup
    select_btn = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(),'SELECT')]")
        )
    )
    select_btn.click()
    time.sleep(2)

    # 6️⃣ In popup: check Probate and Mental Health
    probate_checkbox = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//label[contains(text(),'Probate')]/preceding-sibling::input[@type='checkbox']")
        )
    )
    mental_checkbox = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//label[contains(text(),'Mental Health')]/preceding-sibling::input[@type='checkbox']")
        )
    )

    if not probate_checkbox.is_selected():
        probate_checkbox.click()
        time.sleep(0.5)
    if not mental_checkbox.is_selected():
        mental_checkbox.click()
        time.sleep(0.5)

    # 7️⃣ Click DONE to close popup
    done_btn = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(),'Done')]")
        )
    )
    done_btn.click()
    time.sleep(2)

    # 8️⃣ Click SEARCH button to view all cases
    search_btn = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(),'SEARCH')]")
        )
    )
    search_btn.click()
    time.sleep(5)  # wait for results to load

    print("✅ Advanced Search applied: Cases → Probate / Mental Health")
