from driver import get_driver
from login import login

driver = get_driver("downloads/pdfs")
login(driver)

input("If you see the Probate site, login worked. Press ENTER to close.")
driver.quit()
