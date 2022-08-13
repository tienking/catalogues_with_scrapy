from selenium import webdriver
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def driver_option_setup(download_path, auto_download_pdf):
    ff_options = Options()
    ff_options.add_argument("--disable-infobars")
    ff_options.add_argument("--disable-extensions")
    ff_options.add_argument("--disable-popup-blocking")

    ff_options.set_preference("browser.download.dir", download_path)
    ff_options.set_preference("browser.download.folderList",2)
    ff_options.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/plain,application/octet-stream,application/pdf,application/x-pdf,application/vnd.pdf")
    ff_options.set_preference("browser.download.manager.showWhenStarting", False)
    ff_options.set_preference("browser.helperApps.neverAsk.openFile","text/plain,application/octet-stream,application/pdf,application/x-pdf,application/vnd.pdf")
    ff_options.set_preference("browser.helperApps.alwaysAsk.force", False)
    ff_options.set_preference("browser.download.manager.useWindow", False)
    ff_options.set_preference("browser.download.manager.focusWhenStarting", False)
    ff_options.set_preference("browser.helperApps.neverAsk.openFile", "")
    ff_options.set_preference("browser.download.manager.alertOnEXEOpen", False)
    ff_options.set_preference("browser.download.manager.showAlertOnComplete", False)
    ff_options.set_preference("browser.download.manager.closeWhenDone", True)
    ff_options.set_preference("pdfjs.disabled", True)
    
    if auto_download_pdf == True:
        ff_options.set_preference("print.always_print_silent", True)
        ff_options.set_preference("print.show_print_progress", False)
        ff_options.set_preference('print.save_as_pdf.links.enabled', True)
    
    return ff_options

def driver_setup(download_path, driver=None, auto_download_pdf=False):
    if driver != None:
        driver.close()
    ff_options = driver_option_setup(download_path, auto_download_pdf)
    driver = Firefox(options=ff_options)
    
    return driver