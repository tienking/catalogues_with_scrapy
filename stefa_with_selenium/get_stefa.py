import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException, ElementNotInteractableException, ElementClickInterceptedException
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
    serv=Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=serv, options=chrome_options)
    
    return driver

def check_popup_exists_by_xpath(check_driver, xpath, wait_time=0):
    if wait_time > 0:
        popup_wait_time = WebDriverWait(check_driver, wait_time)
        try:
            popup_element = popup_wait_time. until(EC.presence_of_element_located((By.XPATH, xpath))) 
        except NoSuchElementException:
            return False
        return True
    else:
        try:
            check_driver.find_element(By.XPATH, xpath)
        except NoSuchElementException:
            return False
        return True
    
def close_popup(driver):
    if check_popup_exists_by_xpath(driver, '//div[@class="iubenda-cs-rationale"]', wait_time=7):
        try:
            acc_coo_btn = driver.find_element(By.XPATH, '//button[@class="iubenda-cs-close-btn"]')
            acc_coo_btn.click()
        except (ElementNotInteractableException, StaleElementReferenceException):
            pass
    time.sleep(1)
    if check_popup_exists_by_xpath(driver, '//div[@id="myModal"]', wait_time=7):
        try:
            modal_btn = driver.find_element(By.XPATH, '//div[@class="modal-header"]/button[@class="close"]')
            modal_btn.click()
        except (ElementNotInteractableException, StaleElementReferenceException):
            pass

def wait_loading_screen(driver):
    time.sleep(1.5)
    while check_popup_exists_by_xpath(driver, '//div[@id="loadmoreajaxloader"])', wait_time=5):
        time.sleep(0.5)
        
def click_view_more(driver):
    view_more_wait_time = WebDriverWait(driver, 5)
    try:
        view_more_btn = view_more_wait_time. until(EC.presence_of_element_located((By.XPATH, '//div[@id="loadMoreButton"]/button')))
        view_more_btn.click()
    except:
        pass

def scroll_page(driver):
    SCROLL_PAUSE_TIME = 2

    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)
        
        wait_loading_screen(driver)
        click_view_more(driver)
        wait_loading_screen(driver)
        
        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)
        
        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
        
def run():
    driver = set_selenium_driver_chrome()
    driver.get(STEFA_URL)
    close_popup(driver)
    
    headers = driver.find_elements(By.XPATH, '//ul[@class="nav navbar-nav skywalker_menu_catalogo"]/li')

    items_pages = []
    for header in headers:
        header_list = header.find_elements(By.XPATH, 'ul[@class="dropdown-menu"]/li/ul[@class="blocco-sx"]/li')
            
        if len(header_list) > 0:
            for header_child in header_list:
                try:
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

    stefa_items = {}
    for items_page in items_pages:
        driver.get(items_page)
        
        try:
            check_popup_exists_by_xpath(driver, '//div[@id="mainContainer"]/div/div/div[@class="esposizion_quadro_box"]', wait_time=5)
        except TimeoutException:
            pass
        if len(driver.find_elements(By.XPATH, '//div[@id="mainContainer"]/div/div/div[@class="esposizion_quadro_box"]')) == 0:
            continue
        scroll_page(driver)
                
        items_list = []
        items_list = driver.find_elements(By.XPATH, '//div[@id="mainContainer"]/div/div/div[@class="esposizion_quadro_box"]')

        for item in items_list:
            item_id = item.get_attribute("id")
            item_link = item.find_element(By.XPATH, 'div/a[@id="LnkImmagine"]').get_attribute("href")
            item_img = item.find_element(By.XPATH, 'div/a[@id="LnkImmagine"]/img').get_attribute("src")
            item_name = item.find_element(By.XPATH, 'div/div/a[@id="LnkProdotto"]/span').get_attribute('textContent')
            item_price = item.find_element(By.XPATH, 'div/div[@class="text-center"]/span').get_attribute('textContent')
            
            stefa_items[item_id] = {
                "item_link":item_link,
                "item_img":item_img,
                "item_name":item_name,
                "item_price":item_price
            }

    with open("stefa_export.csv", "w", encoding="utf-8", newline="") as outfile:
        csv_writer = csv.writer(outfile)
        csv_writer.writerow(["item_id", "item_link", "item_img_link", "item_name", "item_price"])
        for k, v in stefa_items.items():
            csv_writer.writerow([k, v["item_link"], v["item_img"], v["item_name"], v["item_price"]])
            
    driver.close()
    
if __name__ == "__main__":
    run()
