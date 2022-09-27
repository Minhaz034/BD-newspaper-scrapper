from starters import *
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
from googletrans import Translator

translator = Translator()
chromedriver_autoinstaller.install()

options = Options()
options.headless = True
options.add_argument("--window-size=1920,1200")
# driver = webdriver.Chrome(options = options,executable_path= CHROME_DRIVER_PATH)
driver = webdriver.Chrome(options = options)
driver.maximize_window()


CHROME_DRIVER_PATH = "/home/aci/Chrome Webdriver/chromedriver"
BASE = "https://news.google.com/search?q=site:"
columns = ['name', 'link', 'language']
names = ['newspapers71',
         'ntv',
         'prothomalo',
         'kalerkantho',
         'bhorerkagoj',
         'jaijaidin',
         'amadershomoy',
         'inqilab',
         'jugantor',
         'nayadiganta',
         'manabzamin',
         'thedailystar',
         'dhakatribune',
         'tbsnews',
         'thefinancialexpress']
links = ['https://www.newspapers71.com',
         'https://www.ntvbd.com',
         'https://www.prothomalo.com',
         'https://www.kalerkantho.com',
         'https://www.bhorerkagoj.net',
         'https://www.jaijaidinbd.com',
         'https://www.amadershomoy.com',
         'https://www.dailyinqilab.com',
         'https://www.jugantor.com',
         'https://www.dailynayadiganta.com',
         'https://www.mzamin.com',
         'https://www.thedailystar.net',
         'https://www.dhakatribune.com',
         'https://www.tbsnews.net',
         'https://thefinancialexpress.com.bd']
languages = ['bangla']*(len(names)-4)+['english']*4
newspaper_df = pd.DataFrame(columns=[columns])
newspaper_df.name = names
newspaper_df.link = links
newspaper_df.language = languages
formal_name = ['Newspapers 71', 'NTV', 'প্রথম আলো', 'কালের কণ্ঠ', 'ভোরের কাগজ',
       'যায় যায় দিন', 'আমাদের সময়', 'ইনকিলাব', 'যুগান্তর', 'নয়াদিগন্ত',
       'The Daily Star', 'মানবজমিন', 'The Dhaka Tribune',
       'The Business Standard', 'The Financial Express']
newspaper_df.index= formal_name
# newspapers_df = pd.read_csv('newspaper_list.csv', index_col='formal_name')

bn_extn = "&hl=bn&gl=BD&ceid=BD:bn"
en_extn = "&hl=en-BD&gl=BD&ceid=BD:en"
search_key = "এসিআই"
identifier = "//main/c-wiz/div/div/div/article"

# search_link = BASE+newspaper_links[11]+' '+search_key+bn_extn


def get_news(newspaper_series=newspaper_df.loc['প্রথম আলো'], search_key="এসিআই"):
    # TextBlob()
    extn = bn_extn
    if newspaper_series.language == 'english':
        search_key = translator.translate(search_key).text
        extn = en_extn

    search_link = BASE + newspaper_series.link + '%20"' + search_key + '"' + extn

    driver.get(search_link)
    news_elements = driver.find_elements(By.XPATH, identifier)
    headlines = driver.find_elements(By.XPATH, identifier + "/h3")
    dates = driver.find_elements(By.XPATH, identifier + '/div/div/time')
    scrap_df = []
    if not len(news_elements):
        print(newspaper_series.link + ": Empty")
    else:
        for headline, date in zip(headlines, dates):
            hl = headline.text
            dt = date.get_attribute("datetime")
            scrap_df.append({
                'newspaper': newspaper_series['name'],
                'link': newspaper_series.link,
                'language': newspaper_series.language,
                'date': pd.to_datetime(dt),
                'headline': hl,

            })
    scrap_df = pd.DataFrame(scrap_df)
    return scrap_df


if __name__ == '__main__':

    data = pd.DataFrame()
    for name in newspaper_df.index:
        scrap_df = get_news(newspaper_df.loc[name] )
        data = pd.concat([data,scrap_df], ignore_index=True)

    print(data)
    # data.to_csv("/home/aci/PycharmProjects/banglabert/sequence_classification/sample_inputs/single_sequence/csv/outputs.csv",index=False)
    data.to_csv(
        "./outputs.csv",
        index=False)

    driver.close()
