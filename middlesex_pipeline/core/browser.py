from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def get_driver():
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(options=opts)
