from core.retry import retry
from core.throttling import throttle

@retry(attempts=3)
def parse_case(driver, case_url, selectors, throttle_cfg):
    driver.get(case_url)
    throttle(**throttle_cfg)

    parties = driver.find_element(*selectors["parties"]).text
    docket = driver.find_elements(*selectors["docket_rows"])

    return {
        "parties": parties,
        "docket_entries": docket
    }
