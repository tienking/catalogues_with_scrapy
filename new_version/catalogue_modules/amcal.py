from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
#---------------------------------------------------------------
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

# Amcal - https://www.amcal.com.au/online-catalogue

def get_cata_from_amcal(retailer_url, retailer_name):
    catalogue_option = catalogue_option_setup()
    
    download_path = catalogue_option['download_path']
    week_cata_path = catalogue_option['week_cata_path']
    jpg_path = catalogue_option['jpg_path']
    
    monday_ref_str = catalogue_option['monday_ref_str']
    last_day_check = catalogue_option['last_day_check']
    history_record = catalogue_option['history_record']
    cata_tracking_writer = catalogue_option['cata_tracking_writer']
    cata_tracking_history = catalogue_option['cata_tracking_history']
    
    driver = driver_setup(download_path, auto_download_pdf = True)
    
    if retailer_name not in history_record.keys():
        history_record[retailer_name] = []

    driver.get(retailer_url)
    wait_time = WebDriverWait(driver, 10)
    try:
        fileurl = wait_time.until(EC.presence_of_element_located((By.XPATH, '//iframe[@id="catalogIframe"]'))).get_attribute("src")
        
        print(retailer_name, ": 1 catalogue")
        
        with open
        filename = fileurl.split("/")[-1]
        filepath = join(download_path, filename)
        while not exists(filepath):
            time.sleep(2)

        if isfile(filepath):
            if fileurl not in history_record[retailer_name]:
                history_record[retailer_name].append(fileurl)
                cata_filepath = join(week_cata_path, filename)
                if not exists(cata_filepath):
                    shutil.copy(filepath, cata_filepath)
                    cata_tracking_writer.writerow([retailer_name, filename, monday_ref_str])
            while exists(filepath):
                try:
                    os.remove(filepath)
                except:
                    time.sleep(1)
                    continue
    except TimeoutException:
        print(retailer_name, ": ", "No new catalogue available")
        if len(cata_tracking_history[(cata_tracking_history['Retailer Name']==retailer_name) & (cata_tracking_history['Date Reference']==monday_ref_str)]) == 0 and last_day_check:
            cata_tracking_writer.writerow([retailer_name, "No new catalogue available", monday_ref_str])
            
    finally:
        driver.close()