import requests
from bs4 import BeautifulSoup
import logging
from datetime import datetime

# Logging setup
logging.basicConfig(filename='logs/scraper.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def get_soup(url, data=None, headers=None):
    try:
        if data:
            response = requests.post(url, data=data, headers=headers)
        else:
            response = requests.get(url, headers=headers)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'lxml')
    except Exception as e:
        logging.error(f"Failed to get soup for {url}: {e}")
        return None

def save_to_csv(data, filename="data/output.csv"):
    import pandas as pd
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
