import pip
import subprocess
import time
import csv
import glob
from shutil import copy2
import sys
import getpass
import os
from pathlib import Path
from datetime import datetime, timedelta
from os.path import exists, abspath, join, isdir, isfile
# Get PATH conf
from conf import PATH

CATALOGUE_PATH = abspath(join(PATH["download_path"],"images","{0}"))
FINAL_OUTPUT_PATH = join(PATH["final_output_path"], "{0}")

# Get next Monday from current date
def get_last_monday():
    cur_time = datetime.now()
    last_monday = cur_time - timedelta(days=cur_time.weekday())
    last_monday = last_monday.replace(hour=6, minute=0)
    date_range = cur_time - last_monday
    # Check today is Monday (time before 8h00 AM)
    if date_range.days == -1:
        last_monday = cur_time - timedelta(days=cur_time.weekday()+7)
        last_monday_folder = last_monday.strftime("%Y%m%d")
    else:
        last_monday_folder = last_monday.strftime("%Y%m%d")
        
    return last_monday_folder
    
def get_next_monday():
    # Get next Monday from current date
    cur_time = datetime.now()
    last_monday = cur_time - timedelta(days=cur_time.weekday())
    last_monday = last_monday.replace(hour=9, minute=0)
    date_range = cur_time - last_monday
    # Check today is Monday (time before 8h00 AM)
    if date_range.days == -1:
        next_monday_folder = last_monday.strftime("%Y%m%d")
    else:
        next_monday = cur_time - timedelta(days=cur_time.weekday()-7)
        next_monday_folder = next_monday.strftime("%Y%m%d")
    
    return next_monday_folder
        
def import_or_install(package):
    try:
        __import__(package)
    except ImportError:
        pip.main(['install', package])
        
def copy_to_local_sharepoint():
    print("\n\t>>> COPYING TO FINAL PATH...")
    last_monday_folder = get_next_monday()
    
    cata_path = CATALOGUE_PATH.format(last_monday_folder)
    final_path = FINAL_OUTPUT_PATH.format(last_monday_folder)
    if exists(cata_path):
        for cat_name_dir in os.listdir(cata_path):
            cat_name_path = join(cata_path, cat_name_dir)
            if isdir(cat_name_path):
                for cat_file_dir in os.listdir(cat_name_path):
                    cat_files_path = join(cat_name_path, cat_file_dir)
                    if isdir(cat_files_path):
                        final_file_path = join(final_path, cat_name_dir, cat_file_dir)
                        if not exists(final_file_path):
                            Path(final_file_path).mkdir(parents=True, exist_ok=True)
                            for cat_file in os.listdir(cat_files_path):
                                cat_file_path = join(cat_files_path, cat_file)
                                if isfile(cat_file_path) and cat_file.endswith(".pdf"):
                                    print("\t[COPY]:{0}".format(cat_file))
                                    copy2(cat_file_path, final_file_path)
        
def main(scrapy_arg, option=None):
    package_list = ["scrapy", "img2pdf"]
    for package in package_list:
        import_or_install(package)
    
    print("\n\t------------------ GET CATALOGUES ------------------")
    print("\n\t>> Using SCRAPY")
    if option == None:
        print("\n\t1. Get all new catalogues.")
        print("\t2. Get only catalogue or all catalogues from one brand")
        print("\t3. Exit")
        option = input("\n\tEnter: ")

    while True:
        print("\n\n\t[ {0} ]".format(datetime.now().strftime("%Y-%m-%d %H:%M")))
        print("\n\t>> RUNNING...")
        if option == "1":
            subprocess.call(["scrapy", "crawl", "catalogues", "--nolog"])
            print("\n\t********************** FINISH **********************")
        elif option == "2":
            subprocess.call(["scrapy", "crawl", "special-catalogue"])
            print("\n\t********************** FINISH **********************")
        elif option == "3":
            return None
        else:
            print("Wrong number")
            break
        
        # COLLECT ALL CATALOGUES FOR 1 WEEK and SEND BY EMAIL (PENDING)
        # -------------------------------------------------------------
        copy_to_local_sharepoint()
        # -------------------------------------------------------------
        print("\n\n\t>> RUN AGAIN IN 24 HOURS")
        time.sleep(60*60*24)

    #input("Press any keys to Exit")

# Using python RUN.py --weekly --nolog
#   for weekly Catalogues
if __name__ == "__main__":
    option = None
    scrapy_arg = []
    
    for arg in sys.argv:
        if arg == '--weekly':
            option = '1'
        elif arg == '--special':
            option = '2'
        elif arg.startswith("--"):
            scrapy_arg.append(arg)
            
    main(scrapy_arg, option)