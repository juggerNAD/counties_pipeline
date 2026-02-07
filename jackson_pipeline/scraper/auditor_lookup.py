# scraper/auditor_lookup.py
def lookup_property(session, owner_name):
    url = "https://publicaccess.jacksongov.org/search/commonsearch.aspx"
    params = {
        "mode": "realprop",
        "searchstring": owner_name
    }

    r = session.get(url, params=params)
    return r.text
