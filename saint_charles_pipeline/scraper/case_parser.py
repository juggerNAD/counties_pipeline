from bs4 import BeautifulSoup

INVALID_CASES = ("Small Est", "Guardian", "Conserv")

def parse_case_list(html):
    soup = BeautifulSoup(html, "lxml")
    cases = []

    for row in soup.select("table tr")[1:]:
        cols = row.find_all("td")
        if not cols:
            continue

        case_type = cols[2].get_text(strip=True)
        if any(x in case_type for x in INVALID_CASES):
            continue

        cases.append({
            "case_number": cols[0].get_text(strip=True),
            "case_url": cols[0].find("a")["href"],
            "case_type": case_type
        })

    return cases

