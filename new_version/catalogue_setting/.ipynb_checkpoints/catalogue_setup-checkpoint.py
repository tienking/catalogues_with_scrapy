import json
import csv
import datetime
from pathlib import Path
from os.path import exists, join, abspath
import pandas as pd

def catalogue_option_setup():
    catalogue_option = {}
    
    download_path = abspath("./export")
    cata_path = abspath("./catalogues")
    jpg_path = abspath("./jpg")
    history_record_file = "./history_record.json"
    weekly_record_file = "./weekly_catalogues_tracking.csv"
    cata_file = "./catalogues.json"
    cata_dict = {}
    history_record = {}
    weekly_record = []

    # Get catalogue config
    with open(cata_file, "r", encoding='utf-8') as catafile:
        cata_dict = json.load(catafile)

    # Check history file
    try:
        with open(history_record_file, "r", encoding='utf-8') as recordfile:
            history_record = json.load(recordfile)
    except:
        pass
        #print("No history record")

    # Generate date string
    today = datetime.date.today()
    monday = today + datetime.timedelta( (7-today.weekday()) % 7 )
    last_day_check = today == monday
    monday_str = monday.strftime("%y%m%d")
    monday_ref_str = monday.strftime("%Y-%m-%d")

    # Create date folder
    #print("Date:", monday_ref_str)
    week_cata_path = join(cata_path, monday_str)
    Path(week_cata_path).mkdir(parents=True, exist_ok=True)

    # Create weekly record file
    if not exists(weekly_record_file):
        with open(weekly_record_file, "a", encoding="utf-8", newline="") as cata_tracking:
            cata_tracking_writer = csv.writer(cata_tracking)
            cata_tracking_writer.writerow(['Retailer Name','Filename', 'Date Reference'])


    cata_tracking_history = pd.read_csv(weekly_record_file, header=0)
    
    catalogue_option['download_path'] = download_path
    catalogue_option['cata_path'] = cata_path
    catalogue_option['week_cata_path'] = week_cata_path
    catalogue_option['jpg_path'] = jpg_path
    
    catalogue_option['history_record_file'] = history_record_file
    catalogue_option['weekly_record_file'] = weekly_record_file
    catalogue_option['cata_file'] = cata_file
    
    catalogue_option['last_day_check'] = last_day_check
    catalogue_option['monday_str'] = monday_str
    catalogue_option['monday_ref_str'] = monday_ref_str
    
    catalogue_option['cata_dict'] = cata_dict
    catalogue_option['history_record'] = history_record
    catalogue_option['weekly_record'] = weekly_record
    
    catalogue_option['cata_tracking_history'] = cata_tracking_history
    
    return catalogue_option
    