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
# import chromedriver_autoinstaller
# chromedriver_autoinstaller.install()


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
"http://www.bhorerkagoj.net/?s=এসিআই",
"http://www.jaijaidinbd.com",
"http://www.amadershomoy.biz/beta",
"https://www.dailyinqilab.com/search?sq=এসিআই",
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
options.headless = True
options.add_argument("--window-size=1920,1200")
driver = webdriver.Chrome(options = options,executable_path= CHROME_DRIVER_PATH)
# driver = webdriver.Chrome()
driver.maximize_window()

# search_link = BASE+newspaper_links[11]+' '+search_key+bn_extn


def get_news(newspaper_link = "www.prothomalo.com",search_key = "এসিআই"):
    # TextBlob()
    search_link = BASE+newspaper_link+'%20"'+search_key+'"'+bn_extn

    driver.get(search_link)
    news_elements = driver.find_elements(By.XPATH, identifier)
    headlines = driver.find_elements(By.XPATH, identifier+"/h3")
    dates = driver.find_elements(By.XPATH, identifier+'/div/div/time')
    headline_texts = []
    date_texts = []
    if not len(news_elements):
        print(newspaper_link+": Empty")
    else:
        # print(newspaper_link)

        for headline, date in zip(headlines, dates):
            hl = headline.text
            headline_texts.append(hl)
            # print(headline.text)
            dt = date.get_attribute("datetime")
            date_texts.append(dt)
            # print(date.get_attribute("datetime"))
            # print(date.get_attribute("datetime"))
            # print(headline.text)
    return  headline_texts,date_texts





if __name__ == '__main__':

    # extractor = extractors.CanolaExtractor()
    #
    # doc = extractor.get_doc_from_url('https://www.prothomalo.com/business/2mkfi5u24u')
    # page_title = doc.title
    # page_contents = doc.content
    #
    # print(page_title, end="\n\n")
    # print(page_contents)
    headlines = []
    dates = []
    for link in newspaper_links:
        hl,dt = get_news(newspaper_link=link)
        headlines.append(hl)
        dates.append(dt)
        #print(get_news(newspaper_link=link))
    # print(headlines)
    # print(dates)
    texts = []
    for list in headlines:
        for text in list:
            texts.append(text)
    # print(texts)
    data = pd.DataFrame(texts,columns=['sentence1'])
    print(data)
    data.to_csv("/home/aci/PycharmProjects/banglabert/sequence_classification/sample_inputs/single_sequence/csv/outputs.csv",index=False)

    # driver.close()
