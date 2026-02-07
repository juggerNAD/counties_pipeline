from utils import get_soup
import logging

BASE_URL = "https://assessor.stlouiscountymo.gov/realestate/searchinput.aspx"

def search_property_by_owner(owner_name):
    """
    Search for properties using the owner/petitioner name.
    Returns a list of property info dictionaries.
    """
    properties = []
    
    # Prepare payload if required (some ASPX pages use form data)
    data = {
        "ctl00$ContentPlaceHolder1$txtSearch": owner_name,
        "ctl00$ContentPlaceHolder1$btnSearch": "Search"
    }

    soup = get_soup(BASE_URL, data=data)
    if not soup:
        return []

    # Extract property rows
    rows = soup.select("table#ctl00_ContentPlaceHolder1_gvResults tr")[1:]  # Skip header
    for row in rows:
        cols = row.find_all("td")
        if len(cols) >= 5:
            property_info = {
                "Owner": owner_name,
                "Parcel Number": cols[0].text.strip(),
                "Property Address": cols[1].text.strip(),
                "Property Type": cols[2].text.strip(),
                "Assessed Value": cols[3].text.strip(),
                "Tax Status": cols[4].text.strip()
            }
            properties.append(property_info)
    return properties
