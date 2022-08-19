from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
#---------------------------------------------------------------
import os
from os.path import exists, join, isfile
import time
from pathlib import Path
import shutil
import re

# Spotlight - https://www.spotlightstores.com/catalogues

def get_cata_from_spotlight(retailer_url, retailer_name):
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
        wait_time.until(EC.presence_of_element_located((By.XPATH, '//td[@class="sale-cell"]')))
        cata_list = driver.find_elements(By.XPATH, '//tr/td[@class="sale-cell"]/div')
        print(retailer_name, ": ", len(cata_list), "catalogue(s)")
        for cata in cata_list:
            cata_href = cata.find_element(By.XPATH, 'div[@class="sale-image-cell"]/a').get_attribute("href")
            cata_name = cata.find_element(By.XPATH, 'div[@class="sale-name-cell"]/a').get_attribute('textContent')
            cata_date = cata.find_element(By.XPATH, 'div[@class="sale-dates-cell"]').get_attribute('textContent')
            cata_info.append([cata_href, cata_name, cata_date])

        for cata in cata_info:
            cata_href = cata[0]
            cata_name = cata[1]
            cata_date = cata[2]
            
            driver.get(cata_href)
            print_all_href = wait_time.until(EC.presence_of_element_located((By.XPATH, '//a[@id="sf-catalogue-print-all"]'))).get_attribute("href")
            driver.get(print_all_href)
            
            filepath = join(download_path, tmp_print_pdf)
            while not exists(filepath):
                time.sleep(2)
            while True:
                try:
                    with open(filepath, "rb") as pdf_file:
                        PyPDF2.PdfFileReader(pdf_file)
                    break
                except:
                    time.sleep(5)
                    
            if isfile(filepath):
                filename = retailer_name + "_" + cata_name + "_" + cata_date
                filename = re.sub(' +', ' ', filename)
                filename = filename.strip()

                
                if cata_href not in history_record[retailer_name]:
                    history_record[retailer_name].append(cata_href)
                    cata_filepath = join(week_cata_path, filename + ".pdf")
                    if not exists(cata_filepath):
                        shutil.copy(filepath, cata_filepath)
                        cata_tracking_writer.writerow([retailer_name, filename + ".pdf", monday_ref_str])
                    else:
                        index = 1
                        new_filename = filename + " ({0})".format(index)
                        while exists(join(week_cata_path, new_filename + ".pdf")):
                            index += 1
                        

                while exists(filepath):
                    try:
                        os.remove(filepath)
                    except:
                        time.sleep(1)
            
    except TimeoutException:
        print(retailer_name, ": ", "No new catalogue available")
        if len(weekly_record_history[(weekly_record_history['Retailer Name']==retailer_name) & (weekly_record_history['Date Reference']==monday_ref_str)]) == 0 and last_day_check:
            cata_tracking_writer.writerow([retailer_name, "No new catalogue available", monday_ref_str])