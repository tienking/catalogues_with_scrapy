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

# Salefinder - https://salefinder.com.au

def get_cata_from_salefinder(retailer_url, retailer_name):
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
    wait_time = WebDriverWait(driver, 10)
    
    try:
        cata_info = []
        wait_time.until(EC.presence_of_element_located((By.XPATH, '//div[@class="retailer-catalogue"]')))
        cata_list = driver.find_elements(By.XPATH, '//div[@class="retailer-catalogue"]')
        print(retailer_name, ": ", len(cata_list), "catalogue(s)")
        
        with open(weekly_record_file, "a", encoding="utf-8", newline="") as weekly_record_io:
            weekly_record_writer = csv.writer(weekly_record_io)
            
            for cata in cata_list:
                cata_href = cata.find_element(By.XPATH, 'a').get_attribute('href')
                cata_name = cata.find_element(By.XPATH, 'div[@class="catalogue-name"]').get_attribute('textContent')
                cata_date = cata.find_element(By.XPATH, 'div[@class="catalogue-date"]').get_attribute('textContent')
                cata_info.append([cata_href, cata_name, cata_date])

            for cata in cata_info:
                cata_href = cata[0]
                cata_name = cata[1]
                cata_date = cata[2]

                wait_time = WebDriverWait(driver, 10)

                if cata_href not in history_record[retailer_name]:
                    driver.get(cata_href)
                    print_all_href = wait_time.until(EC.presence_of_element_located((By.XPATH, '//a[@id="sf-catalogue-print-all"]'))).get_attribute("href")
                    driver.get(print_all_href)

                    filename = retailer_name + "_" + cata_name + "_" + cata_date
                    filename = re.sub(' +', ' ', filename)
                    filename = filename.strip()

                    imgs = driver.find_elements(By.XPATH, '//body/img')
                    img_urls = [img.get_attribute('src') for img in imgs]
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