import time
import csv
import requests 
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from pathlib import Path

# We can also initialise browser in headless mode to speed up the process and save on memory
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument('--disable-dev-shm-usage') 
chrome_options.add_argument('--no-sandbox')
# driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()))

# Custom function we will use to imitate slow typing and fool anti-bot software
def slow_typing(element, text):
    for character in text:
        element.send_keys(character)
        time.sleep(0.3)

driver.get("https://mcscertified.com/find-an-installer/")

# We will find the 'Name' text box and enter in the following keys
try:
    elem = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.ID, "msw-toggle-filters")) #This is a dummy element
    )
except:
    driver.quit()

elem.click()

time.sleep(5)

try:
    elem = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.ID, "msw-list-view")) #This is a dummy element
    )
except:
    driver.quit()

elem.click()

downloads_path = str(Path.home() / "Downloads")
f = open(downloads_path+"/mcs_installers_scrape.csv", 'w', newline='')
writer = csv.writer(f)
writer.writerow(['Company Name', 'Cert Number', 'Cert Body', 'Address', 'Contact Number', 'Regions', 'Measures'])

page = 1
while page <= 222:

    mytable = driver.find_element(By.ID, 'InstallerResultsTableBody')
    for row in mytable.find_elements(By.TAG_NAME, "tr"):
        btn = row.find_element(By.CLASS_NAME, "msw-list-view-arrow")
        btn.click()
        company_name = row.find_element(By.TAG_NAME, "h3").text
        cert_number = row.find_element(By.TAG_NAME, "h4").text.strip('Certification Number:')
        company_data = row.find_element(By.CLASS_NAME, "msw-list-view-item-more-info").find_element(By.CLASS_NAME, "msw-list-view-item-more-info-details")
        data_row = 1
        for company_data_row in company_data.find_elements(By.CLASS_NAME, "row"): 
            if(data_row == 1):
                # print(company_data_row.text.strip('Certification Body:').strip())
                cert_body = company_data_row.text.strip('Certification Body:').strip()
            elif(data_row == 4):
                # print(company_data_row.text.strip('Address:'))
                address = company_data_row.text.strip('Address:')
            elif(data_row == 5):
                # print(company_data_row.text.strip('Telephone:').strip())
                contact_number = company_data_row.text.strip('Telephone:').strip()
            elif(data_row == 7):
                # print(company_data_row.text.strip('Regions Covered:').strip())
                regions = company_data_row.text.strip('Regions Covered:').strip()
            data_row += 1 

        measures = ""
        company_measures = row.find_element(By.CLASS_NAME, "msw-list-view-item-more-info").find_element(By.CLASS_NAME, "msw-installer-technology-container")
        for company_measur_row in company_measures.find_elements(By.CLASS_NAME, "msw-installer-technology"):
            if company_measur_row.get_attribute("class").find('msw-tech-cannot-install') == -1:
                # print(company_measur_row.find_element(By.TAG_NAME, 'span').text)
                measures += company_measur_row.find_element(By.TAG_NAME, 'span').text + ", "
        
        writer.writerow([company_name, cert_number, cert_body, address, contact_number, regions, measures[:-2]])

    
    if page+1 > 5:
        btn_path = "//*[@data-dt-idx='4']"
    elif page+1 == 221:
        btn_path = "//*[@data-dt-idx='5']"
    elif page+1 == 222:
        btn_path = "//*[@data-dt-idx='6']"
    else:
        btn_path = "//*[@data-dt-idx='"+str(page+1)+"']"

    if page+1 < 223:
        next_btn = driver.find_element(By.XPATH, btn_path)
        next_btn.click()
    print(page)
    page += 1


driver.quit()