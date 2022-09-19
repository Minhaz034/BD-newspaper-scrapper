import pandas as pd
# from textblob import TextBlob
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
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
# from boilerpy3 import extractors
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import chromedriver_autoinstaller

chromedriver_autoinstaller.install()

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
identifier = "//main/c-wiz/div/div/div/article"

options = Options()
options.headless = False
options.add_argument("--window-size=1920,1200")
# driver = webdriver.Chrome(options = options,executable_path= CHROME_DRIVER_PATH)
driver = webdriver.Chrome()
driver.maximize_window()


# search_link = BASE+newspaper_links[11]+' '+search_key+bn_extn


def get_news(newspaper_link="www.prothomalo.com", search_key="এসিআই"):

    search_link = BASE + newspaper_link + '%20"' + search_key + '"' + bn_extn

    driver.get(search_link)
    news_elements = driver.find_elements(By.XPATH, identifier)
    headlines = driver.find_elements(By.XPATH, identifier + "/h3")
    dates = driver.find_elements(By.XPATH, identifier + '/div/div/time')

    if not len(news_elements):
        print(newspaper_link + ": Empty")
    else:
        print(newspaper_link)
        for headline, date in zip(headlines, dates):
            print(date.get_attribute("datetime"))
            print(headline.text)



if __name__ == '__main__':

    for link in newspaper_links:
        get_news(newspaper_link=link)

    driver.close()
