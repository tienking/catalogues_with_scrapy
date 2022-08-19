from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
#---------------------------------------------------------------
from catalogue_setting.download_jpg_to_pdf import download_jpg_to_pdf
from catalogue_setting.driver_setup import driver_setup
from catalogue_setting.catalogue_setup import catalogue_option_setup
#---------------------------------------------------------------
from os.path import exists, join, isfile
from pathlib import Path
import shutil
import time
import csv
import os
import re

# AU-Catalogues - https://au-catalogues.com/

def get_cata_from_latestcatalogues(retailer_url, retailer_name):
    catalogue_option = catalogue_option_setup()
    
    download_path = catalogue_option['download_path']
    week_cata_path = catalogue_option['week_cata_path']
    jpg_path = catalogue_option['jpg_path']
    
    weekly_record_file = catalogue_option['weekly_record_file']
    monday_ref_str = catalogue_option['monday_ref_str']
    last_day_check = catalogue_option['last_day_check']
    history_record = catalogue_option['history_record']
    weekly_record_history = catalogue_option['weekly_record_history']
    
    driver = driver_setup(download_path, auto_download_pdf = True)
    
    if retailer_name not in history_record.keys():
        history_record[retailer_name] = []
    
    driver.get(retailer_url)
    
    try:
        cata_info = []
        cata_list = driver.find_elements(By.XPATH, '//div[@class="grid-item box "]')
        print(retailer_name, ": ", len(cata_list), "catalogue(s)")
        
        with open(weekly_record_file, "a", encoding="utf-8", newline="") as weekly_record_io:
            weekly_record_writer = csv.writer(weekly_record_io)
            
            for cata in cata_list:
                cata_href = cata.find_element(By.XPATH, 'a').get_attribute('href')
                cata_name = cata.find_element(By.XPATH, '//p/strong').get_attribute('textContent')
                cata_date = cata.find_element(By.XPATH, '//p/small[@class="hidden-sm"]').get_attribute('textContent')
                cata_info.append([cata_href, cata_name, cata_date])

            for cata in cata_info:
                cata_href = cata[0]
                cata_name = cata[1]
                cata_date = cata[2]
                
                filename = retailer_name + " " + cata_name + " " + cata_date
                filename = re.sub(' +', ' ', filename)
                filename = filename.strip()
                filename = filename.replace("/","-")

                if cata_href not in history_record[retailer_name]:
                    driver.get(cata_href)
                    root_page = cata_href + "?page=" + "{0}"
                    last_page_number = driver.find_elements(By.XPATH, '//div[@class="pages-btn-group"]/a')[-2].get_attribute('textContent')
                    img_pages = [root_page.format(index) for index in range(1,int(last_page_number))]
                    
                    img_urls = []
                    for img_page in img_pages:
                        driver.get(img_page)
                        wait_time = WebDriverWait(driver, 30)
                        
                        wait_time.until(EC.presence_of_element_located((By.XPATH, '//picture/img[@id="pageImage"]')))
                        img_url = driver.find_element(By.XPATH, '//picture/img[@id="pageImage"]').get_attribute('src')
                        img_urls.append(img_url)

                    output_filename = download_jpg_to_pdf(img_urls, filename, jpg_path, week_cata_path)

                    history_record[retailer_name].append(cata_href)
                    weekly_record_writer.writerow([retailer_name, output_filename, monday_ref_str])

                    driver = driver_setup(download_path, driver)

    except TimeoutException:
        print(retailer_name, ": ", "No new catalogue available")
        if len(weekly_record_history[(weekly_record_history['Retailer Name']==retailer_name) & (weekly_record_history['Date Reference']==monday_ref_str)]) == 0 and last_day_check:
            weekly_record_writer.writerow([retailer_name, "No new catalogue available", monday_ref_str])
    finally:
        driver.close()