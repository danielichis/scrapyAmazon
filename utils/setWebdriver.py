from logging import exception
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time
import json
import re
import locale
import pandas as pd
from datetime import datetime,date,timedelta
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from sys import platform

def configWebDriver():
    download_path=f"{os.getcwd()}/descargas_pdf"
    with open("parametros.txt", mode="r") as f:
        lines=f.readlines()
    dates=lines[0].strip()
    pdfs_path=lines[1].strip()
    exepath=lines[2].strip()

    if platform == "linux" or platform == "linux2":
        pass
    elif platform == "darwin":
        print("Mac")
        w='chromedriver'
    elif platform == "win32":
        w='chromedriver.exe'
    options = webdriver.ChromeOptions()
    op=Options()
    settings = {
        "recentDestinations": [{
            "id": "Save as PDF",
            "origin": "local",
            "account": ""
        }],
        "selectedDestinationId": "Save as PDF",
        "version": 2,
    }
    prefs = {
        'printing.print_preview_sticky_settings.appState': json.dumps(settings),
        'savefile.default_directory':download_path
    }
    option = Options()
    option.add_argument('--kiosk-printing')
    option.binary_location=exepath
    option.add_experimental_option('prefs', prefs)
    option.add_argument(f"user-data-dir={pdfs_path}")
    w= webdriver.Chrome(ChromeDriverManager().install(), options=option)
    #w = webdriver.Chrome(executable_path=w, options=option)
    return w

