import pandas as pd
from textblob import TextBlob
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from tqdm import tqdm
import json
import requests
from time import sleep
from random import randint
import urllib.request
import re
import time
from boilerpy3 import extractors



# search_link = https://news.google.com/topstories?hl=bn&gl=BD&ceid=BD:bn
# https://news.google.com/topstories?hl=en-BD&gl=BD&ceid=BD:en
# https://news.google.com/search?q=site:https://www.prothomalo.com "এসিআই"&hl=bn&gl=BD&ceid=BD:bn

CHROME_DRIVER_PATH = "/home/aci/Chrome Webdriver/chromedriver"
BASE = "https://news.google.com/search?q=site:"
newspaper_links = [
"http://www.newspapers71.com",
"http://www.ntvbd.com",
"http://www.prothomalo.com",
"http://www.kalerkantho.com",
"http://www.bhorerkagoj.net",
"http://www.jaijaidinbd.com",
"http://www.amadershomoy.biz/beta",
"https://www.dailyinqilab.com",
"http://www.jugantor.com",
"http://www.dailynayadiganta.com",
"http://www.thedailystar.net",
"http://www.mzamin.com",
]
bn_extn = "&hl=bn&gl=BD&ceid=BD:bn"
en_extn = "&hl=en-BD&gl=BD&ceid=BD:en"
search_key = "এসিআই"

options = Options()
options.headless = False
options.add_argument("--window-size=1920,1200")
driver = webdriver.Chrome(options = options,executable_path= CHROME_DRIVER_PATH)
driver.maximize_window()

# search_link = BASE+newspaper_links[11]+' '+search_key+bn_extn

def get_news(newspaper_link = "http://www.prothomalo.com",search_key = "এসিআই"):
    # TextBlob()
    search_link = BASE+newspaper_link+'%20"'+search_key+'"'+bn_extn
    print(search_link)
    driver.get(search_link)
    # driver.close()



if __name__ == '__main__':

    # extractor = extractors.CanolaExtractor()
    #
    # doc = extractor.get_doc_from_url('https://www.prothomalo.com/business/2mkfi5u24u')
    # page_title = doc.title
    # page_contents = doc.content
    #
    # print(page_title, end="\n\n")
    # print(page_contents)
    for link in newspaper_links:
        get_news(newspaper_link=link)



    # driver.close()
