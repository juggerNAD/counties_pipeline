from bs4 import BeautifulSoup

def extract_docket_pdfs(html, keywords):
    soup = BeautifulSoup(html, "lxml")
    pdfs = []

    for row in soup.select("tr.docketRow"):
        text = row.get_text(" ", strip=True).lower()
        if any(k in text for k in keywords):
            link = row.find("a", href=True)
            if link:
                pdfs.append(link["href"])

    return pdfs

