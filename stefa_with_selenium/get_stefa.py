import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import time
import datetime
import os.path
import sys

STEFA_URL = r"https://www.stefanoricci.com/"

# Setup a selenium driver
def set_selenium_driver_chrome():
    # Setup
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(STEFA_URL)
    
    return driver
    
def set_selenium_driver_firefox():
    # Setup
    driver = webdriver.Firefox()
    driver.get(STEFA_URL)
    
    return driver
    
def run():
    #driver = set_selenium_driver_firefox()
    #driver = set_selenium_driver_chrome()
    serv=Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=serv)
    driver.get(STEFA_URL)
    
    headers = driver.find_elements(By.XPATH, '//ul[@class="nav navbar-nav skywalker_menu_catalogo"]/li')

    items_pages = []
    for header in headers:
        print(header.find_element(By.XPATH, 'a').get_attribute('innerHTML'))
        #print(header.get_attribute('innerHTML'))
        header_list = header.find_elements(By.XPATH, 'ul[@class="dropdown-menu"]/li/ul[@class="blocco-sx"]/li')
            
        if len(header_list) > 0:
            for header_child in header_list:
                try:
                    print("NAME: ",header_child.find_element(By.XPATH, 'a/span').get_attribute('textContent'))
                    if header_child.find_element(By.XPATH, 'a/span').get_attribute('textContent') == "View All":
                        header_link = header_child.find_element(By.XPATH, 'a').get_attribute("href")
                        items_pages.append(header_link)
                        break
                except:
                    continue
            else:
                for header_child in header_list:
                    header_link = header_child.find_element(By.XPATH, 'a').get_attribute("href")
                    items_pages.append(header_link)
        else:
            header_link = header.find_element(By.XPATH, 'a').get_attribute("href")
            items_pages.append(header_link)

    view_more_wait_time = WebDriverWait(driver, 5)
    stefa_items = {}
    for items_page in items_pages:
        driver.get(items_page)
        
        try:
            view_more_btn = view_more_wait_time. until(EC.presence_of_element_located((By.XPATH, '//button[@class="btn btn-primary btn-carrello-custom"]'))) 
        except NoSuchElementException:
            view_more_btn = None
        while view_more_btn != None:
            #view_more_btn.click()
            driver.implicitly_wait(10)
            ActionChains(driver).move_to_element(view_more_btn).click(view_more_btn).perform()
            try:
                view_more_btn = view_more_wait_time. until(EC.presence_of_element_located((By.XPATH, '//button[@class="btn btn-primary btn-carrello-custom"]')))
            except:
                view_more_btn = None
                
        items_list = []
        items_list = driver.find_elements(By.XPATH, '//div[@id="mainContainer"]/div[@class="col-lg-4"]')
        
        for item in items_list:
            item_id = item.find_element(By.XPATH, 'div/@id').extract()
            item_link = item.find_element(By.XPATH, 'div/div/a[@id="LnkImmagine"]').get_attribute("href")
            item_img = item.find_element(By.XPATH, 'div/div/a[@id="LnkImmagine"]/img').get_attribute("src")
            item_name = item.find_element(By.XPATH, 'div/div/div/a[@id="LnkProdotto"]/span').get_attribute("src")
            item_price = item.find_element(By.XPATH, 'div/div/div[@class="text-center"]/span').get_attribute('textContent')
            
            stefa_items[item_id] = {
                "item_link":item_link,
                "item_img":item_img,
                "item_name":item_name,
                "item_price":item_price
            }
            
    with open("stefa_export.csv", "w", encoding="utf-8", newline="") as outfile:
        csv_writer = csv.writer(outfile)
        for k, v in stefa_items.items():
            csv.writer.writerow([k, v["item_link"], v["item_img"], v["item_name"], v["item_price"]])
            
    driver.close()
    
if __name__ == "__main__":
    run()
