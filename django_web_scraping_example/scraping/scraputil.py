import pandas as pd
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from selenium.webdriver.common.action_chains import ActionChains as AC
import requests
from time import sleep
import re
from deep_translator import (GoogleTranslator, single_detection)
from selenium import webdriver
import chromedriver_autoinstaller
import geckodriver_autoinstaller
import os
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

import re
import pyLDAvis.gensim_models
import gensim, logging, warnings
import gensim.corpora as corpora
import nltk
from gensim.utils import simple_preprocess
from gensim.models import CoherenceModel
# import matplotlib.pyplot as plt
from nltk.corpus import stopwords
import undetected_chromedriver as uc

nltk.download('stopwords')
warnings.filterwarnings("ignore",category=DeprecationWarning)
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.ERROR)
my_api = "15c5418e83130ba091ea4d07875a7517"
# trans_b2e = GoogleTranslator(source='bn', target='en')
bn2en = GoogleTranslator(source='bn', target='en')
EMPTY_DICT = {'newspaper': 'inqilab',
            'link': None,
            'language': 'bn',
            'date': None,
            'section': None,
            'source': None,
            'headline': None}

def translate_news(news_df):
    if news_df.language[0] == 'en':
        return news_df
    else:
        for i in news_df.index:
            try:
                news_df.date.at[i] = single_detection(news_df.date[i], api_key="15c5418e83130ba091ea4d07875a7517")
            except:
                pass
            try:

                news_df.section.at[i] = bn2en.translate(news_df.section[i])
            except:
                pass
            try:
                news_df.source.at[i] = bn2en.translate(news_df.source[i])
            except:
                pass
            try:
                news_df.headline.at[i] = bn2en.translate(news_df.headline[i])
            except:
                pass
            try:
                news_df.description.at[i] = bn2en.translate(news_df.description[i])
            except:
                pass
    return news_df




def get_sentiment(raw_inputs, model_path="./bertweet-base-sentiment-analysis"):
    print(f"{torch.cuda.device_count()} GPU available")
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    try:
        if os.path.exists(model_path):
            print("Model already on device!")
            tokenizer = AutoTokenizer.from_pretrained(model_path)
            model = AutoModelForSequenceClassification.from_pretrained(model_path).to(device)
        else:
            tokenizer = AutoTokenizer.from_pretrained("finiteautomata/bertweet-base-sentiment-analysis")
            model = AutoModelForSequenceClassification.from_pretrained(
                "finiteautomata/bertweet-base-sentiment-analysis").to(device)

            tokenizer.save_pretrained(model_path)
            model.save_pretrained(model_path)

    except:
        tokenizer = AutoTokenizer.from_pretrained("finiteautomata/bertweet-base-sentiment-analysis")
        model = AutoModelForSequenceClassification.from_pretrained(
            "finiteautomata/bertweet-base-sentiment-analysis").to(device)

        tokenizer.save_pretrained(model_path)
        model.save_pretrained(model_path)

    encoded_inputs = tokenizer(raw_inputs, padding=True, truncation=True, return_tensors="pt").to(device)
    model_outputs = model(**encoded_inputs)
    predictions = torch.nn.functional.softmax(model_outputs['logits'], dim=-1)
    sentiments = [model.config.id2label[prediction.argmax(axis=0)] for prediction in predictions.detach().cpu().numpy()]
    # print(model.config.id2label)
    # sentiments[] = model.config.id2label[sentiments]
    if device.type == 'cuda':
        print(torch.cuda.get_device_name(0))
        print('Memory Usage:')
        print('Allocated:', round(torch.cuda.memory_allocated(0) / 1024 ** 3, 1), 'GB')
        print('Cached:   ', round(torch.cuda.memory_reserved(0) / 1024 ** 3, 1), 'GB')
    return sentiments


def scan_page_bhorerkagoj(link, keep_content=True):
    date_id = link.find('bhorerkagoj.com/') + len('bhorerkagoj.com/')
    date = link[date_id:date_id + 10]

    page_source = requests.get(link).text
    page_html = BeautifulSoup(page_source, features="html.parser")
    headline = page_html.find('h2', {'class': 'title'})
    section = page_html.find('a', {'rel': 'category tag'})
    source = page_html.find('p', {'class': 'name'})
    try:

        data_dict = {
            'newspaper': 'bhorerkagoj',
            'link': link,
            'language': 'bn',
            'date': date,
            'section': section.text.strip() if section else '',
            'source': source.text.strip() if source else '',
            'headline': headline.text.strip() if headline else ''
        }
        if keep_content:
            description = page_html.find('div', {'id': 'content-p'})
            data_dict['description'] = description.text.strip()
    except:
        print("Error in extracting information or advertisement error.")
    return data_dict

def scan_page_bhorerkagoj_sel(link, keep_content=True):
    date_id = link.find('bhorerkagoj.com/') + len('bhorerkagoj.com/')
    date = link[date_id:date_id + 10]

    page_source = requests.get(link).text
    page_html = BeautifulSoup(page_source, features="html.parser")
    headline = page_html.find('h2', {'class': 'title'})
    section = page_html.find('a', {'rel': 'category tag'})
    source = page_html.find('p', {'class': 'name'})
    try:

        data_dict = {
            'newspaper': 'bhorerkagoj',
            'link': link,
            'language': 'bn',
            'date': date,
            'section': section.text.strip() if section else '',
            'source': source.text.strip() if source else '',
            'headline': headline.text.strip() if headline else ''
        }
        if keep_content:
            description = page_html.find('div', {'id': 'content-p'})
            data_dict['description'] = description.text.strip()
    except:
        print("Error in extracting information or advertisement error.")
    return data_dict


def scan_page_prothomalo(link, keep_content=True):
    page_source = requests.get(link).text
    page_html = BeautifulSoup(page_source, features="html.parser")
    date = page_html.find('time', {'datetime': re.compile(r"")})
    page_header = page_html.find('div', {'class': re.compile(r"story-title")})
    headline = page_header
    section = page_header
    source = page_html.find('div', {'class': re.compile(r"contributor")})
    location = page_html.find('span', {'class': re.compile(r"location")})

    if keep_content:
        description = page_html.find('div', {'class': re.compile(r"^story-grid")})

    try:
        data_dict = {
            'newspaper': 'prothomalo',
            'link': link,
            'language': 'bn',
            'date': str(pd.to_datetime(date['datetime']).date()) if date else None,
            'section': section.find('a').text.strip() if section else '',
            'source': ''.join([source.text if source else ''] + [', ' + location.text if location else '']),
            'headline': headline.find('h1').text.strip() if headline else ''
        }
        if keep_content:
            desc = ''
            for para in description.find_all('p'):
                desc += para.text + '\n'
            data_dict['description'] = desc if description else description
    except:
        print("Error while scraping!")
        return {}
    return data_dict


def scan_page_ntv(link, keep_content=True):
    page_source = requests.get(link).text
    page_html = BeautifulSoup(page_source, features="html.parser")
    date = page_html.find('meta', {'property': re.compile(r'time')})
    headline = page_html.find('h1', {'itemprop': re.compile(r'headline')})
    section = page_html.find('nav', {'role': re.compile(r"navigation")})
    source = page_html.find('div', {'class': re.compile(r"author")})
    # try:
    data_dict = {
        'newspaper': 'ntv',
        'link': link,
        'language': 'bn',
        'date': str(pd.to_datetime(date['content']).date()) if date else '',
        'section': section.text.strip() if section else '',
        'source': source.text.strip() if source else '',
        'headline': headline.text.strip() if headline else ''
    }
    if keep_content:
        description = page_html.find('div', {'class': re.compile(r"^section-content")})
        data_dict['description'] = description.text.strip() if description else description
    # except:
    #     print("Error in extracting information or advertisement error.")
    return data_dict


def scan_page_kaler_kantho(link, keep_content=True):
    page_source = requests.get(link).text
    page_html = BeautifulSoup(page_source, features="html.parser")
    date = page_html.find('meta', {'property': re.compile(r'time')})
    headline = page_html.find('div', {'class': re.compile(r'details')})
    section = page_html.find('p', {'class': re.compile(r"author")})
    source = page_html.find('p', {'class': re.compile(r"author")})

    try:
        data_dict = {
            'newspaper': 'kalerkantho',
            'link': link,
            'language': 'bn',
            'date': str(pd.to_datetime(date['content'][:10]).date()) if date else '',
            'section': section.text.strip() if section else '',
            'source': source.text.strip() if source else '',
            'headline': headline.find('h2').text.strip() if headline else ''
        }
        if keep_content:
            description = page_html.find('div', {'class': re.compile(r"some-class-name2")})
            data_dict['description'] = description.text.strip() if description else description
    except:
        print("Error in extracting information or advertisement error.")
    return data_dict


def scan_page_jaijaidin(link, keep_content=True):
    page_source = requests.get(link).text
    page_html = BeautifulSoup(page_source, features="html.parser")
    date = page_html.find('div', {'class': re.compile(r'post_date_time')})
    headline = page_html.find('div', {'class': re.compile(r'body-content')})
    section = page_html.find('div', {'class': re.compile(r'body-content')})
    source = page_html.find('span', {'class': re.compile(r"rpt_name")})

    try:
        data_dict = {
            'newspaper': 'jaijaidin',
            'link': link,
            'language': 'bn',
            'date': date.findChild('div').text.strip() if date else '',
            'section': section.find('li', {'class': re.compile(r'child active')}).findPrevious(
                'li').text.strip() if section else '',
            'source': source.text.strip() if source else '',
            'headline': headline.findChild('h1').text.strip() if headline else ''
        }
        if keep_content:
            description = page_html.find('div', {'id': re.compile(r"content_block")})
            data_dict['description'] = description.text.strip() if description else description
    except:
        print("Error in extracting information or advertisement error.")
    return data_dict


def scan_page_inqilab(link, keep_content=True):
    page_source = requests.get(link).text
    page_html = BeautifulSoup(page_source, features="html.parser")


    try:
        article = page_html.find('article')
        sub_heading = article.find('h5') if article else None
        headline = article.find('h1')
        section = page_html.find('ol', {'class': re.compile(r'breadcrumb')})
        [source, date] = sub_heading.text.strip().split("|") if sub_heading else ['', '']
        data_dict = {
            'newspaper': 'inqilab',
            'link': link,
            'language': 'bn',
            'date': date.strip(),
            'section': section.find('li', {'class': "active"}).findPrevious('li').text.strip() if section else '',
            'source': source.strip(),
            'headline': headline.text.strip() if headline else ''
        }
        if keep_content:
            description = page_html.find('div', {'id': re.compile(r"news_content")})
            data_dict['description'] = description.text.strip() if description else description
    except:
        print("Error in extracting information or advertisement error.")
        data_dict = EMPTY_DICT
    return data_dict


def scan_page_jugantor(link, keep_content=True):
    page_source = requests.get(link).text
    page_html = BeautifulSoup(page_source, features="html.parser")
    date = page_html.find('div', {'class': 'col-12 col-sm-12 col-md-6'})

    headline = page_html.find('div', {'id': 'news-title'})
    section = page_html.find('nav', {'id': re.compile('newsview')})
    source = page_html.find('div', {'id': re.compile(r"date")})

    try:
        data_dict = {
            'newspaper': 'jugantor',
            'link': link,
            'language': 'bn',
            'date': date.find('div').text.strip().split('|')[0].strip() if date else '',
            'section': section.find('li', {'class': re.compile(r'active')}).text if section else '',
            'source': source.find('span').text.strip() if source else '',
            'headline': headline.text.strip() if headline else ''
        }
        if keep_content:
            description = page_html.find('div', {'class': 'row row-cols-1 px-0'})
            data_dict['description'] = description.text.strip() if description else description
    except:
        print("Error in extracting information or advertisement error.")
    return data_dict


def scan_page_nayadiganta(link, keep_content=True):
    page_source = requests.get(link).text
    page_html = BeautifulSoup(page_source, features="html.parser")
    headline = page_html.find('title')
    date = page_html.find("meta", {'name': 'publish-date'}, content=True)
    section = page_html.find('ol', {'class': "breadcrumb"})
    source = page_html.find('section', {'class': re.compile(r"^article-info")})

    try:
        data_dict = {
            'newspaper': 'nayadiganta',
            'link': link,
            'language': 'bn',
            'date': str(pd.to_datetime(date['content']).date()) if date else '',
            'section': section.findChildren('li')[2].text if section else '',
            'source': source.findChildren('li')[0].text.strip() if source else '',
            'headline': headline.text.strip() if headline else ''
        }
        if keep_content:
            description = page_html.find('div', {'class': 'news-content'})
            data_dict['description'] = description.text.strip() if description else description
    except:
        print("Error in extracting information or advertisement error.")
    return data_dict


def scan_page_mzamin(link, keep_content=True):
    page_source = requests.get(link).text
    page_html = BeautifulSoup(page_source, features="html.parser")
    headline = page_html.find('article').findChild('h1', attrs={'class': re.compile(r'^lh')})
    date = headline.findNextSibling('h5').next_sibling
    if len(date) <= 2:
        date = date.next
    section = page_html.find('article').findChild('h4', attrs={'class': 'sectitle'})
    source = page_html.find('article').findChild('h5')

    try:
        data_dict = {
            'newspaper': 'manabzamin',
            'link': link,
            'language': 'bn',
            'date': date.text.strip() if date else '',
            'section': page_html.find('article').findChild('h4',
                                                           attrs={'class': 'sectitle'}).text if page_html.find(
                'article').findChild('h4', attrs={'class': 'sectitle'}) else '',
            'source': page_html.find('article').findChild('h5').text.strip() if page_html.find('article').findChild(
                'h5') else '',
            'headline': page_html.find('article').findChild('h1', attrs={
                'class': re.compile(r'^lh')}).text.strip() if page_html.find('article').findChild('h1', attrs={
                'class': re.compile(r'^lh')}) else ''
        }
        if keep_content:
            description = headline.findNextSibling('div', {'class': re.compile(r'lh-base')})
            data_dict['description'] = description.text.strip() if description else description
    except:
        print("Error in extracting information or advertisement error.")
    return data_dict


def scan_page_daily_star(link, keep_content=True):
    if 'tags/' in link:
        page_html = BeautifulSoup(requests.get(link).text, "html.parser")
        link = 'https://www.thedailystar.net/' + page_html.find('div', {'class': 'card-content'}).find('a')['href']

    page_source = requests.get(link).text
    page_html = BeautifulSoup(page_source, features="html.parser")
    headline = page_html.find('h1', attrs={'itemprop': 'headline'})
    date = page_html.find('meta', {'property': re.compile(r'time')})
    section = page_html.find('div', {'class': re.compile(r'category')})
    source = page_html.find('div', {'class': re.compile(r'byline color-pacific-blue')})

    try:
        data_dict = {
            'newspaper': 'dailystar',
            'link': link,
            'language': 'en',
            'date': str(pd.to_datetime(date['content'][:10]).date()) if date else '',
            'section': section.text.strip() if section else '',
            'source': source.text.strip() if source else '',
            'headline': headline.text.strip() if headline else ''
        }
        if keep_content:
            description = page_html.find('div', {'class': re.compile(r'section-content')})
            data_dict['description'] = description.text.strip() if description else description
    except:
        print("Error in extracting information or advertisement error.")
    return data_dict


def scan_page_dhaka_tribune(link, keep_content=True):
    page_source = requests.get(link).text
    page_html = BeautifulSoup(page_source, "html.parser")
    headline = page_html.find('h1', {'class': re.compile(r"headline")})
    date = page_html.find('meta', {'property': re.compile(r"time")})
    section = str(page_source)[str(page_source).find('\"articleSection\":\"')
                               + len('\"articleSection\":\"'):]
    section = section[:section.find('\"')]
    source = str(page_source)[str(page_source).find('\"authors\":\"')
                              + len('\"authors\":\"'):]
    source = source[:source.find('\"')]

    try:
        data_dict = {
            'newspaper': 'dhakatribune',
            'link': link,
            'language': 'en',
            'date': str(pd.to_datetime(date['content']).date()) if date else '',
            'section': section.strip() if section else '',
            'source': source.strip() if source else '',
            'headline': headline.text.strip() if headline else ''
        }
        if keep_content:
            description = page_html.find('div', {'class': 'news-holder-single-page_content-holder mt-20'})
            data_dict['description'] = description.text.strip() if description else description
    except:
        print("Error in extracting information or advertisement error.")
    return data_dict


def scan_page_tbs(link, keep_content=True):
    # if 'tags/' in link:
    #     page_html = BeautifulSoup(requests.get(link).text, "html.parser")
    #     link = 'https://www.thedailystar.net/' + page_html.find('div', {'class': 'card-content'}).find('a')['href']

    page_source = requests.get(link).text
    page_html = BeautifulSoup(page_source, features="html.parser")
    headline = page_html.find('h1', attrs={'itemprop': 'headline'})
    date = page_html.find('meta', {'property': re.compile(r'published_time')})
    section = page_html.find('h2', {'class': re.compile(r'news-details-cat')})
    source = page_html.find('div', {'class': re.compile(r'author-name')})

    try:
        data_dict = {
            'newspaper': 'the business standard',
            'link': link,
            'language': 'en',
            'date': str(pd.to_datetime(date['content'][:10]).date()) if date else '',
            'section': section.text.strip() if section else '',
            'source': source.text.strip() if source else '',
            'headline': headline.text.strip() if headline else ''
        }
        if keep_content:
            description = page_html.find('div', {'class': re.compile(r'section-content')})
            data_dict['description'] = description.text.strip() if description else description
    except:
        print("Error in extracting information or advertisement error.")
    return data_dict


class GetNews:
    def __init__(self, browser="Chrome", headless=False, search_key="এসিআই"):

        self.options = self.set_browser_options(browser)
        # options = Options()
        if browser != 'Undetected':
            self.options.headless = headless
        self.search_key = search_key
        self.bn2en = GoogleTranslator(source='bn', target='en')
        self.en2bn = GoogleTranslator(source='en', target='bn')
        self.newspaper_map = self.get_newspaper_map()

    def set_browser_options(self, name="Chrome"):
        if name == "Chrome":
            from selenium.webdriver.chrome.options import Options
            options = Options()
        elif name == "Firefox":
            from selenium.webdriver.firefox.options import Options
            options = Options()
        elif name == "Edge":
            from selenium.webdriver.edge.options import Options
            options = Options()
        else:
            options = webdriver.ChromeOptions()
        return options

    def select_browser(self, name="Chrome"):
        if name == "Chrome":
            chromedriver_autoinstaller.install()
            self.driver = webdriver.Chrome(options=self.options)
        elif name == "Firefox":
            geckodriver_autoinstaller.install()
            self.driver = webdriver.Firefox(options=self.options)
        elif name == "Edge":
            edgedriver_autoinstaller.install()
            self.driver = webdriver.Edge(options=self.options)
        elif name == 'Undetected':
            # options = webdriver.ChromeOptions()
            self.options.add_argument("start-maximized")
            self.driver = uc.Chrome(options=self.options)

        self.driver.maximize_window()
        self.driver.delete_all_cookies()

    def close_browser(self):
        self.driver.close()

    def close_all(self):
        self.driver.quit()

    def translate_news(self, news_df):
        if news_df.empty or news_df.language[0] == 'en':
            return news_df
        else:
            for i in news_df.index:
                try:
                    news_df.date.at[i] = single_detection(news_df.date[i], api_key="15c5418e83130ba091ea4d07875a7517")
                except:
                    pass
                try:
                    news_df.section.at[i] = self.bn2en.translate(news_df.section[i])
                except:
                    pass
                try:
                    news_df.source.at[i] = self.bn2en.translate(news_df.source[i])
                except:
                    pass
                try:
                    news_df.headline.at[i] = self.bn2en.translate(news_df.headline[i])
                except:
                    pass
                try:
                    news_df.description.at[i] = self.bn2en.translate(news_df.description[i])
                except:
                    pass
        return news_df

    def get_newspaper_map(self):
        columns = ['name', 'link', 'language', 'fn', 'page_fn', 'formal_name']
        names = [
            # 'newspapers71',
            'ntv',
            'prothomalo',
            'kalerkantho',
            'bhorerkagoj',
            'jaijaidin',
            # 'amadershomoy',
            'inqilab',
            'jugantor',
            'nayadiganta',
            'manabzamin',
            'thedailystar',
            'dhakatribune',
            'tbsnews',
            'thefinancialexpress']
        functions = [
            # None,
            self.search_ntv,
            self.search_prothomalo,
            self.search_kalerkantho,
            self.search_bhorer_kagoj,
            self.search_jaijaidin,
            # None,
            self.search_inqilab,
            self.search_jugantor,
            self.search_nayaDiganta,
            self.search_mzamin,
            self.search_daily_star,
            self.search_dhaka_tribune,
            self.search_tbs,
            None]
        links = [
            # 'https://www.newspapers71.com',
            'https://www.ntvbd.com',
            'https://www.prothomalo.com',
            'https://www.kalerkantho.com',
            'https://www.bhorerkagoj.net',
            'https://www.jaijaidinbd.com',
            # 'https://www.amadershomoy.com',
            'https://www.dailyinqilab.com',
            'https://www.jugantor.com',
            'https://www.dailynayadiganta.com',
            'https://www.mzamin.com',
            'https://www.thedailystar.net',
            'https://www.dhakatribune.com',
            'https://www.tbsnews.net',
            'https://thefinancialexpress.com.bd']
        page_fns = [  # None,
            scan_page_ntv,
            scan_page_prothomalo,
            scan_page_kaler_kantho,
            scan_page_bhorerkagoj,
            scan_page_jaijaidin,
            # None,
            scan_page_inqilab,
            scan_page_jugantor,
            scan_page_nayadiganta,
            scan_page_mzamin,
            scan_page_daily_star,
            scan_page_dhaka_tribune,
            scan_page_tbs,

            None]
        formal_names = [
            # 'Newspapers 71',
            'NTV', 'প্রথম আলো', 'কালের কণ্ঠ', 'ভোরের কাগজ',
            'যায় যায় দিন',
            # 'আমাদের সময়',
            'ইনকিলাব', 'যুগান্তর', 'নয়াদিগন্ত',
            'The Daily Star', 'মানবজমিন', 'The Dhaka Tribune',
            'The Business Standard', 'The Financial Express']
        languages = ['bn'] * (len(names) - 4) + ['en'] * 4
        # newspaper = pd.DataFrame(columns=[columns])
        newspaper = {}
        for name, link, language, fn, pg_fn, formal_name in zip(names, links, languages, functions, page_fns,
                                                                formal_names):
            newspaper[name] = []
            newspaper[name].append(name)
            newspaper[name].append(link)
            newspaper[name].append(language)
            newspaper[name].append(fn)
            newspaper[name].append(pg_fn)
            newspaper[name].append(formal_name)

        newspaper = pd.DataFrame(newspaper, index=columns)
        return newspaper

    def extract(self, name="bhorerkagoj", google_news=False, pages=1, max_news=25, keep_content=False):
        self.search_key = self.bn2en.translate(self.search_key) if self.newspaper_map[
                                                                       name].language == 'en' else self.search_key
        if google_news:
            scraped_df = self.search_google_news(name, keep_content, max_news)
        else:
            scraped_df = self.newspaper_map[name].fn(pages, keep_content)
        return scraped_df

    def search_google_news(self, name='prothomalo', keep_content=False, max_news=25):
        extn = "&hl=en-BD&gl=BD&ceid=BD:en" if self.newspaper_map[name].language == 'en' else "&hl=bn&gl=BD&ceid=BD:bn"
        search_link = "https://news.google.com/search?q=site:" + self.newspaper_map[
            name].link + '%20"' + self.search_key + '"' + extn
        self.driver.get(search_link)
        print(f"Scraping from {name}!")

        identifier = "//article"
        search_links = self.driver.find_elements(By.XPATH, identifier + "/a[@href]")
        headlines = self.driver.find_elements(By.XPATH, identifier + "/h3")
        dates = self.driver.find_elements(By.XPATH, identifier + '/div/div/time')
        scrap_df = []
        if not len(search_links):
            print(self.newspaper_map[name].name + " not available in google search.")
            scrap_df = self.newspaper_map[name].fn(pages=1, keep_content=keep_content)
            print(name + " is obtained from original page.")
        else:
            scrap_df = []
            for j, (headline, date, link_element) in enumerate(zip(headlines, dates, search_links)):
                print(f"News number {j + 1}: {headline.text.strip()}")
                link = link_element.get_attribute('href')
                page_dict = self.newspaper_map[name].page_fn(link, keep_content=keep_content)
                page_dict['date'] = pd.to_datetime(date.get_attribute('datetime'))
                page_dict['headline'] = headline.text.strip()
                scrap_df.append(page_dict)
                if j >= max_news:
                    break

        scrap_df = pd.DataFrame(scrap_df)
        return scrap_df

    def search_ntv(self, pages=1, keep_content=False):
        print("Scraping from NTV")
        self.driver.get('https://www.ntvbd.com/' + "search/google?s=" + self.search_key)

        scrap_df = []
        i = 1
        while i <= pages:
            search_links = self.driver.find_elements(By.XPATH, "//div[@class='gs-title']/a[@class='gs-title'][@href]")
            j = 1
            for j, element in enumerate(search_links):
                page_link = element.get_attribute("href")
                print(f"News number: {(i - 1) * len(search_links) + (j + 1)}")

                page_dict = scan_page_ntv(page_link, keep_content=keep_content)
                scrap_df.append(page_dict)

            # Go to next page
            try:
                next_page = self.driver.find_element(By.XPATH, "//div[@class='gsc-cursor']")
                next_page.find_element(By.XPATH, f"//div[@aria-label='Page {i + 1}']").click()

            except:
                print("End of NTV search!")
                break
            i += 1
            sleep(1)

        print("End of NTV search!")
        scrap_df = pd.DataFrame(scrap_df)
        return scrap_df

    # def scan_page_bhorerkagoj_sel(self, link, keep_content=True):
    #     date_id = link.find('bhorerkagoj.com/') + len('bhorerkagoj.com/')
    #     date = link[date_id:date_id + 10]
    #
    #     self.driver.get(link)
    #     headline = self.driver.find_element(By.XPATH, "//h2[@class='title']")
    #     section = self.driver.find_element(By.XPATH, "//a[@rel='category tag']")
    #     source = self.driver.find_element(By.XPATH, "//p[@class='name']")
    #     try:
    #
    #         data_dict = {
    #             'newspaper': 'bhorerkagoj',
    #             'link': link,
    #             'language': 'bn',
    #             'date': date,
    #             'section': section.text.strip() if section else '',
    #             'source': source.text.strip() if source else '',
    #             'headline': headline.text.strip()
    #         }
    #         if keep_content:
    #             description = driver.find_element(By.XPATH, "//div[@id='content-p']")
    #             data_dict['description'] = description.text.strip()
    #     except:
    #         print("Error in extracting information or advertisement error.")
    #     self.driver.back()
    #
    #     return data_dict



    def search_bhorer_kagoj(self, pages=1, keep_content=False):
        print("Scraping from BHORER KAGOJ")
        self.driver.get('https://www.bhorerkagoj.net' + "?s=" + self.search_key)

        scrap_df = []
        i = 1
        while i <= pages:
            search_links = self.driver.find_elements(By.XPATH, "//div[@class='col-sm-6 col-xs-12']/a[@href]")
            j = 1
            for j, element in enumerate(search_links):
                page_link = element.get_attribute("href")
                print(f"News number: {(i - 1) * len(search_links) + (j + 1)}")

                page_dict = scan_page_bhorerkagoj(page_link, keep_content=keep_content)
                scrap_df.append(page_dict)

            # Go to next page
            try:
                next_page = self.driver.find_element(By.XPATH, "//a[@title='next']")
                next_page_url = next_page.get_attribute('href')
                self.driver.get(next_page_url)
            except:
                print("End of Bhorerkagoj search!")
                break
            i += 1

        print("End of Bhorerkagoj search!")
        scrap_df = pd.DataFrame(scrap_df)
        return scrap_df

    def search_prothomalo(self, pages=1, keep_content=False):
        print("Scraping from Prothom Alo")
        self.driver.get('https://www.prothomalo.com/' + "search?q=" + self.search_key)

        scrap_df = []
        i = 1
        next_j = 0
        while i <= pages:
            search_links = self.driver.find_elements(By.XPATH, "//a[@class='card-with-image-zoom'][@href]")

            for j, element in enumerate(search_links[next_j:]):
                page_link = element.get_attribute("href")
                print(f"News number: {next_j + (j + 1)}")

                # Scrap from news main function
                page_dict = scan_page_prothomalo(page_link, keep_content=keep_content)
                scrap_df.append(page_dict)

            # Go to next page
            try:
                next_j += j + 1
                # print(next_j)
                next_page_element = WebDriverWait(self.driver, 5).until(
                    EC.visibility_of_element_located((By.XPATH, "//span[text()='আরও']")))
                self.driver.execute_script("return arguments[0].scrollIntoView(true);", next_page_element)

                next_page = self.driver.find_element(By.XPATH, "//span[text()='আরও']")
                next_page.click()
                print("Next portion")
            except:
                print("End of ProthomAlo search!")
                break
            i += 1
            sleep(0.5)

        print("End of Prothomalo search!")
        scrap_df = pd.DataFrame(scrap_df)
        return scrap_df

    def search_kalerkantho(self, pages=1, keep_content=False):
        print("Scraping from Kalerkantho")
        self.driver.get(
            "http://www.kalerkantho.com/" + "home/search?cx=partner-pub-0600503450204720%3A2337922458&cof=FORID%3A10&ie=UTF-8&q=" + self.search_key)
        scrap_df = []
        i = 1
        while i <= pages:
            try:
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@class='gs-title']/a[@class ='gs-title'][@href]")))
                print("Search results ready!!")
            except TimeoutException:
                gsc_link = self.driver.find_elements(By.XPATH, "//iframe[@name='googleSearchFrame']")
                self.driver.get(gsc_link[0].get_attribute('src'))
                print("Timed out! Trying new approach")
            search_links = self.driver.find_elements(By.XPATH, "//div[@class='gs-title']/a[@class='gs-title'][@href]")
            # print(search_links)
            j = 1
            for j, element in enumerate(search_links):
                page_link = element.get_attribute("href")
                print(f"News number: {(i - 1) * len(search_links) + (j + 1)}")

                page_dict = scan_page_kaler_kantho(page_link, keep_content=keep_content)
                scrap_df.append(page_dict)
            # Go to next page
            try:
                next_page = self.driver.find_element(By.XPATH, "//div[@class='gsc-cursor']")
                next_page.find_element(By.XPATH, f"//div[@aria-label='Page {i + 1}']").click()
            except:
                print("End of KalerKantho search!")
                break
            i += 1
            sleep(1)

        print("End of KalerKantho search!")
        scrap_df = pd.DataFrame(scrap_df)
        return scrap_df

    def search_jaijaidin(self, pages=1, keep_content=False):
        print("Scraping from Jaijaidin")
        self.driver.get(
            'https://www.jaijaidinbd.com/search/google/?q=' + self.search_key + '&cx=partner-pub-5450504941871955%3A3787426415&cof=FORID%3A10&ie=UTF-8&sa=Search&sort=date')

        scrap_df = []
        i = 1
        while i <= pages:
            try:
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@class='gs-title']/a[@class ='gs-title'][@href]")))
                print("Search results ready!!")
            except TimeoutException:
                gsc_link = self.driver.find_elements(By.XPATH, "//iframe[@name='googleSearchFrame']")
                self.driver.get(gsc_link[0].get_attribute('src'))
                print("Timed out! Trying new approach")
            search_links = self.driver.find_elements(By.XPATH, "//div[@class='gs-title']/a[@class='gs-title'][@href]")
            # print(search_links)
            j = 1
            for j, element in enumerate(search_links):
                page_link = element.get_attribute("href")
                print(f"News number: {(i - 1) * len(search_links) + (j + 1)}")

                page_dict = scan_page_jaijaidin(page_link, keep_content=keep_content)
                scrap_df.append(page_dict)

            # Go to next page
            try:
                next_page = self.driver.find_element(By.XPATH, "//div[@class='gsc-cursor']")
                next_page.find_element(By.XPATH, f"//div[@aria-label='Page {i + 1}']").click()

            except:
                print("End of Jaijaidin search!")
                break
            i += 1
            sleep(1)

        print("End of Jaijaidin search!")
        scrap_df = pd.DataFrame(scrap_df)
        return scrap_df

    def search_inqilab(self, pages=1, keep_content=False):
        print("Scraping from INQILAB.")
        self.driver.get('https://www.dailyinqilab.com/' + 'search?sq=' + 'এসিআই')

        scrap_df = []
        i = 1
        while i <= pages:
            try:
                WebDriverWait(self.driver, 2).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@class='col-xs-12 col-sm-6']")))
                print("Search results ready!!")
            except TimeoutException:
                print("Timed out! News not collectable")
                break
            search_links = self.driver.find_elements(By.XPATH, "//div[@class='col-xs-12 col-sm-6']/a[@href]")
            j = 1
            for j, element in enumerate(search_links):
                page_link = element.get_attribute("href")
                print(f"News number: {(i - 1) * len(search_links) + (j + 1)}")

                page_dict = scan_page_inqilab(page_link, keep_content=keep_content)
                scrap_df.append(page_dict)

            # Go to next page
            try:
                next_page = self.driver.find_element(By.XPATH, "//ul[@class='pagination']/li/a[text()='পরে »']")
                self.driver.get(next_page.get_attribute("href"))
            except:
                print("End of Inqilab search!")
                break
            i += 1
            sleep(1)

        print("End of Inqilab search!")
        scrap_df = pd.DataFrame(scrap_df)
        return scrap_df

    def search_jugantor(self, pages=1, keep_content=False):
        print("Scraping from Jugantor")
        self.driver.get("https://www.jugantor.com/" + "search/google?q=" + 'এসিআই')

        scrap_df = []
        i = 1
        while i <= pages:
            try:
                WebDriverWait(self.driver, 2).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@class='gs-title']/a[@class ='gs-title'][@href]")))
                print("Search results ready!!")
            except TimeoutException:
                gsc_link = self.driver.find_elements(By.XPATH, "//iframe[@name='googleSearchFrame']")
                self.driver.get(gsc_link[0].get_attribute('src'))
                print("Timed out! Trying new approach")
            search_links = self.driver.find_elements(By.XPATH, "//div[@class='gs-title']/a[@class='gs-title'][@href]")
            # print(search_links)
            j = 1
            for j, element in enumerate(search_links):
                page_link = element.get_attribute("href")
                print(f"News number: {(i - 1) * len(search_links) + (j + 1)}")

                page_dict = scan_page_jugantor(page_link, keep_content=keep_content)
                scrap_df.append(page_dict)

            # Go to next page
            try:
                next_page = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(
                    (By.XPATH, f"//div[@class='gsc-cursor']/div[@aria-label='Page {i + 1}']")))
                next_page.click()

            except ElementClickInterceptedException:
                print("Element not visible due to ad")
                next_page_element = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located(
                    (By.XPATH, f"//div[@class='gsc-cursor']/div[@aria-label='Page {i + 1}']")))
                self.driver.execute_script("return arguments[0].scrollIntoView(true);", next_page_element)
                self.driver.find_element(By.XPATH,
                                         f"//div[@class='gsc-cursor']/div[@aria-label='Page {i + 1}']").click()
            except:
                print("Scraping done!")
                break
            i += 1
            sleep(3)

        print("End of Jugantor search!")
        scrap_df = pd.DataFrame(scrap_df)
        return scrap_df

    def search_nayaDiganta(self, pages=1, keep_content=False):
        print("Scraping from Nayadiganta")
        self.driver.get("https://www.dailynayadiganta.com/" + "search?q=" + 'এসিআই')

        scrap_df = []
        i = 1
        while i <= pages:
            try:
                print("Searching...")
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@class='gs-title']/a[@class ='gs-title'][@href]")))
                print("search results ready!!")
            except TimeoutException:
                print("Timed out!")

            search_links = self.driver.find_elements(By.XPATH, "//div[@class='gs-title']/a[@class='gs-title'][@href]")
            # print(search_links)
            j = 1
            for j, element in enumerate(search_links):
                news_link = element.get_attribute("href")
                print(f"News number: {(i - 1) * len(search_links) + (j + 1)}")
                page_link = news_link if 'ampproject' not in news_link else news_link.replace('/ampproject', '')

                page_dict = scan_page_nayadiganta(page_link, keep_content=keep_content)
                scrap_df.append(page_dict)

            # Go to next page
            try:
                print(i)
                next_page = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(
                    (By.XPATH, f"//div[@class='gsc-cursor']/div[@aria-label='Page {i + 1}']")))
                next_page.click()

            except ElementClickInterceptedException:
                print("Element not visible due to ad")
                next_page_element = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located(
                    (By.XPATH, f"//div[@class='gsc-cursor']/div[@aria-label='Page {i + 1}']")))
                self.driver.execute_script("return arguments[0].scrollIntoView(true);", next_page_element)
                self.driver.find_element(By.XPATH,
                                         f"//div[@class='gsc-cursor']/div[@aria-label='Page {i + 1}']").click()
            except:
                print("Scraping done!")
                break
            i += 1
            sleep(2)

        print("End of Jugantor search!")
        scrap_df = pd.DataFrame(scrap_df)
        return scrap_df

    def search_mzamin(self, pages=1, keep_content=False):
        print("Scraping from Manabzamin")
        self.driver.get("https://mzamin.com/")

        while True:
            try:
                WebDriverWait(self.driver, 2).until(
                    EC.element_to_be_clickable((By.XPATH, "//i[@class='bi bi-search']"))).click()
            except:
                print("Element not found. Refreshing.")
                self.driver.refresh()
                continue
            try:
                WebDriverWait(self.driver, 2).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@class='gsc-input']")))
            except:
                print("Search dialog not visible.")
                self.driver.refresh()
                continue
            try:
                WebDriverWait(self.driver, 2).until(
                    EC.element_to_be_clickable((By.XPATH, "//input[@class='gsc-input']")))
                WebDriverWait(self.driver, 2).until(
                    EC.element_to_be_clickable((By.XPATH, "//input[@class='gsc-input']"))).send_keys(
                    self.search_key + Keys.RETURN)
                break
            except:
                print("Can't interact with element!")
                self.driver.refresh()
                continue

        print("Showing search results")
        action = AC(self.driver)
        scrap_df = []
        i = 1
        while i <= pages:
            print(f"Page {i}")
            action.send_keys(Keys.CONTROL + Keys.HOME)
            action.pause(1)
            action.perform()
            try:
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@class='gs-title']/a[@href][@class='gs-title']")))
                print("search results ready!!")
            except TimeoutException:
                print("Timed out!")
            search_links = self.driver.find_elements(By.XPATH, "//div[@class='gs-title']/a[@href][@class='gs-title']")

            for j, element in enumerate(search_links):
                page_link = element.get_attribute("data-ctorig")
                page_link = "http://www." + page_link[page_link.find("mzamin.com"):]
                # print(page_link)
                print(j + 1, page_link)

                page_dict = scan_page_mzamin(page_link, keep_content=True)
                scrap_df.append(page_dict)

            # Go to next page
            try:
                next_page_element = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located(
                    (By.XPATH, f"//div[@class='gsc-cursor']/div[@aria-label='Page {i + 1}']")))
                self.driver.execute_script("return arguments[0].scrollIntoView(true);", next_page_element)
                self.driver.find_element(By.XPATH,
                                         f"//div[@class='gsc-cursor']/div[@aria-label='Page {i + 1}']").click()
                print("Next Page click")
            except TimeoutException:
                print("Timed out!")
                break
            except:
                print("End of Manabzamin search.")

            i += 1
            sleep(1)
        print("End of Manabzamin search!")
        scrap_df = pd.DataFrame(scrap_df)
        return scrap_df

    def search_daily_star(self, pages=1, keep_content=False):
        print("Scraping from Daily Star")
        self.driver.get('https://www.thedailystar.net' + '/search?t=' +
            self.search_key + '#gsc.tab=0&gsc.q=' + self.search_key + '&gsc.page=1')

        scrap_df = []
        i = 1
        while i <= pages:
            try:
                print("Searching...")
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@class='gs-title']/a[@class ='gs-title'][@href]")))
                print("Search results ready!!")
            except TimeoutException:
                print("Timed out!")

            search_links = self.driver.find_elements(By.XPATH, "//div[@class='gs-title']/a[@class='gs-title'][@href]")
            j = 1
            for j, element in enumerate(search_links):
                page_link = element.get_attribute("href")
                print(f"News number: {(i - 1) * len(search_links) + (j + 1)}")

                page_dict = scan_page_daily_star(page_link, keep_content=keep_content)
                scrap_df.append(page_dict)

            # Go to next page
            try:
                print(i)
                next_page = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(
                    (By.XPATH, f"//div[@class='gsc-cursor']/div[@aria-label='Page {i + 1}']")))
                next_page.click()

            except ElementClickInterceptedException:
                print("Element not visible due to ad")
                next_page_element = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located(
                    (By.XPATH, f"//div[@class='gsc-cursor']/div[@aria-label='Page {i + 1}']")))
                self.driver.execute_script("return arguments[0].scrollIntoView(true);", next_page_element)
                self.driver.find_element(By.XPATH,
                                         f"//div[@class='gsc-cursor']/div[@aria-label='Page {i + 1}']").click()
            except:
                print("Scraping done!")
                break
            i += 1
            sleep(2)

        print("End of Daily Star search!")
        scrap_df = pd.DataFrame(scrap_df)
        return scrap_df

    def search_dhaka_tribune(self, pages=1, keep_content=False):
        print("Scraping from Dhaka Tribune")
        self.driver.get('https://www.dhakatribune.com' + '/search?q=' + self.search_key)

        scrap_df = []
        i = 1
        while i <= pages:
            try:
                print("Searching...")
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@class='gs-title']/a[@class ='gs-title'][@href]")))
                print("Search results ready!!")
            except TimeoutException:
                print("Timed out!")

            search_links = self.driver.find_elements(By.XPATH, "//div[@class='gs-title']/a[@class='gs-title'][@href]")
            j = 1
            for j, element in enumerate(search_links):
                page_link = element.get_attribute("href")
                print(f"News number: {(i - 1) * len(search_links) + (j + 1)}")

                page_dict = scan_page_dhaka_tribune(page_link, keep_content=keep_content)
                scrap_df.append(page_dict)

            # Go to next page
            try:
                print(i)
                next_page = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(
                    (By.XPATH, f"//div[@class='gsc-cursor']/div[@aria-label='Page {i + 1}']")))
                next_page.click()

            except ElementClickInterceptedException:
                print("Element not visible due to ad")
                next_page_element = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located(
                    (By.XPATH, f"//div[@class='gsc-cursor']/div[@aria-label='Page {i + 1}']")))
                self.driver.execute_script("return arguments[0].scrollIntoView(true);", next_page_element)
                self.driver.find_element(By.XPATH,
                                         f"//div[@class='gsc-cursor']/div[@aria-label='Page {i + 1}']").click()
            except:
                print("Scraping done!")
                break
            i += 1
            sleep(2)

        print("End of Dhaka Tribune search!")
        scrap_df = pd.DataFrame(scrap_df)
        return scrap_df

    def search_tbs(self, pages=1, keep_content=False):
        print("Scraping from The Business Standard")
        self.driver.get("https://www.tbsnews.net/search")

        while True:
            try:
                WebDriverWait(self.driver, 2).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@class='gsc-input']")))
            except:
                print("Search dialog not visible.")
                self.driver.refresh()
                continue
            try:
                WebDriverWait(self.driver, 2).until(
                    EC.element_to_be_clickable((By.XPATH, "//input[@class='gsc-input']")))
                WebDriverWait(self.driver, 2).until(
                    EC.element_to_be_clickable((By.XPATH, "//input[@class='gsc-input']"))).send_keys(
                    self.search_key + Keys.RETURN)
                break
            except:
                print("Can't interact with element!")
                self.driver.refresh()
                continue

        scrap_df = []
        i = 1
        while i <= pages:
            try:
                print("Searching...")
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@class='gs-title']/a[@class ='gs-title'][@href]")))
                print("Search results ready!!")
            except TimeoutException:
                print("Timed out!")

            search_links = self.driver.find_elements(By.XPATH, "//div[@class='gs-title']/a[@class='gs-title'][@href]")
            j = 1
            for j, element in enumerate(search_links):
                page_link = element.get_attribute("href")
                print(f"News number: {(i - 1) * len(search_links) + (j + 1)}")

                page_dict = scan_page_tbs(page_link, keep_content=keep_content)
                scrap_df.append(page_dict)

            # Go to next page
            try:
                print(i)
                next_page = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(
                    (By.XPATH, f"//div[@class='gsc-cursor']/div[@aria-label='Page {i + 1}']")))
                next_page.click()

            except ElementClickInterceptedException:
                print("Element not visible due to ad")
                next_page_element = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located(
                    (By.XPATH, f"//div[@class='gsc-cursor']/div[@aria-label='Page {i + 1}']")))
                self.driver.execute_script("return arguments[0].scrollIntoView(true);", next_page_element)
                self.driver.find_element(By.XPATH,
                                         f"//div[@class='gsc-cursor']/div[@aria-label='Page {i + 1}']").click()
            except:
                print("Scraping done!")
                break
            i += 1
            sleep(2)

        print("End of The Business Standard search!")
        scrap_df = pd.DataFrame(scrap_df)
        return scrap_df

    def search_fin_exp(self, pages=1, keep_content=False):
        print("Scraping from The Financial Express")
        self.driver.get("https://thefinancialexpress.com.bd/" + "search?term=news&query=" + self.search_key + "&page=1")

        while True:
            try:
                WebDriverWait(self.driver, 2).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@class='gsc-input']")))
            except:
                print("Search dialog not visible.")
                self.driver.refresh()
                continue
            try:
                WebDriverWait(self.driver, 2).until(
                    EC.element_to_be_clickable((By.XPATH, "//input[@class='gsc-input']")))
                WebDriverWait(self.driver, 2).until(
                    EC.element_to_be_clickable((By.XPATH, "//input[@class='gsc-input']"))).send_keys(
                    self.search_key + Keys.RETURN)
                break
            except:
                print("Can't interact with element!")
                self.driver.refresh()
                continue

        scrap_df = []
        i = 1
        while i <= pages:
            try:
                print("Searching...")
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@class='gs-title']/a[@class ='gs-title'][@href]")))
                print("Search results ready!!")
            except TimeoutException:
                print("Timed out!")

            search_links = self.driver.find_elements(By.XPATH, "//div[@class='gs-title']/a[@class='gs-title'][@href]")
            j = 1
            for j, element in enumerate(search_links):
                page_link = element.get_attribute("href")
                print(f"News number: {(i - 1) * len(search_links) + (j + 1)}")

                page_dict = scan_page_tbs(page_link, keep_content=keep_content)
                scrap_df.append(page_dict)

            # Go to next page
            try:
                print(i)
                next_page = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(
                    (By.XPATH, f"//div[@class='gsc-cursor']/div[@aria-label='Page {i + 1}']")))
                next_page.click()

            except ElementClickInterceptedException:
                print("Element not visible due to ad")
                next_page_element = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located(
                    (By.XPATH, f"//div[@class='gsc-cursor']/div[@aria-label='Page {i + 1}']")))
                self.driver.execute_script("return arguments[0].scrollIntoView(true);", next_page_element)
                self.driver.find_element(By.XPATH,
                                         f"//div[@class='gsc-cursor']/div[@aria-label='Page {i + 1}']").click()
            except:
                print("Scraping done!")
                break
            i += 1
            sleep(2)

        print("End of The Business Standard search!")
        scrap_df = pd.DataFrame(scrap_df)
        return scrap_df


class TopicModel():
    stop_words = stopwords.words('english')
    stop_words.extend(
        ['from', 'subject', 're', 'edu', 'use', 'not', 'would', 'say', 'could', '_', 'be', 'know', 'good', 'go', 'get',
         'do', 'done', 'try', 'many', 'some', 'nice', 'thank', 'think', 'see', 'rather', 'easy', 'easily', 'lot',
         'lack', 'make', 'want', 'seem', 'run', 'need', 'even', 'right', 'line', 'even', 'also', 'may', 'take', 'come',
         'aci'])


    def sentence_to_words(self,sentences):
        for sent in sentences:
            sent = re.sub('\S*@\S*\s?', '', sent)  # remove emails
            sent = re.sub('\s+', ' ', sent)  # remove newline chars
            sent = re.sub("\'", "", sent)  # remove single quotes
            sent = gensim.utils.simple_preprocess(str(sent), deacc=True)
            yield (sent)

    def process_words(self, texts, stop_words=stop_words, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV']):
        data_words = self.sentence_to_words(texts)
        bigram = gensim.models.Phrases(data_words, min_count=5, threshold=100)  # higher threshold fewer phrases.
        trigram = gensim.models.Phrases(bigram[data_words], threshold=100)
        bigram_mod = gensim.models.phrases.Phraser(bigram)
        trigram_mod = gensim.models.phrases.Phraser(trigram)

        texts = [[word for word in simple_preprocess(str(doc)) if word not in stop_words] for doc in texts]
        texts = [bigram_mod[doc] for doc in texts]
        texts = [trigram_mod[bigram_mod[doc]] for doc in texts]
        # texts_out = []
        # nlp = spacy.load('en', disable=['parser', 'ner'])
        # for sent in texts:
        #     doc = nlp(" ".join(sent))
        #     texts_out.append([token.lemma_ for token in doc if token.pos_ in allowed_postags])
        # remove stopwords once more after lemmatization

        # texts_out = [[word for word in simple_preprocess(str(doc)) if word not in stop_words] for doc in texts_out]
        return texts

    def make_topic_model(self,data_ready):
        id2word = corpora.Dictionary(data_ready)
        corpus = [id2word.doc2bow(text) for text in data_ready]

        # Build LDA model
        lda_model = gensim.models.ldamodel.LdaModel(corpus=corpus,
                                                    id2word=id2word,
                                                    num_topics=4,
                                                    random_state=100,
                                                    update_every=1,
                                                    chunksize=10,
                                                    passes=10,
                                                    alpha='symmetric',
                                                    iterations=100,
                                                    per_word_topics=True)

        # pprint(lda_model.print_topics())
        vis = pyLDAvis.gensim_models.prepare(lda_model, corpus, dictionary=lda_model.id2word)

        return lda_model, vis