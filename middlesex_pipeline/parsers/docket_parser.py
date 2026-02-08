def extract_pdf_links(docket_rows):
    pdfs = []
    for row in docket_rows:
        try:
            link = row.find_element("tag name", "a")
            if ".pdf" in link.get_attribute("href"):
                pdfs.append(link.get_attribute("href"))
        except:
            continue
    return pdfs
