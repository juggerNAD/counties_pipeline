from datetime import date, timedelta

def build_search_payload(config):
    end = date.today()
    start = end - timedelta(days=config["days_window"])

    return {
        "countyCode": config["county_code"],
        "courtCode": config["court_code"],
        "caseType": config["case_type"],
        "startDate": start.strftime("%m/%d/%Y"),
        "endDate": end.strftime("%m/%d/%Y"),
        "newSearch": "Y"
    }

