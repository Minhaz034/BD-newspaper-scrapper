import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains as AC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import chromedriver_autoinstaller

from tqdm import tqdm
import json
import requests
from time import sleep
from random import randint
import urllib.request
import re
import time
# from newspaper import Article
import numpy as np

chromedriver_autoinstaller.install()

# CHROME_DRIVER_PATH = "/home/aci/Chrome Webdriver/chromedriver"
SEARCH_TOPIC = "এসিআই"
# link_PROTHOM_ALO = "https://www.prothomalo.com/"  #popup issues
link_PROTHOM_ALO = "https://www.prothomalo.com/search?q=" + SEARCH_TOPIC
link_inqilab = "https://www.dailyinqilab.com/"

link_NTVBD = "https://www.ntvbd.com/search/google?s=" + SEARCH_TOPIC

link_KALER_KONTHO = "http://www.kalerkantho.com/" + "home/search?cx=partner-pub-0600503450204720%3A2337922458&cof=FORID%3A10&ie=UTF-8&q=" + SEARCH_TOPIC  # data not loading

link_JUGANTOR = "https://www.jugantor.com/search/google?q=" + SEARCH_TOPIC  # data not loading
# link_BHORER_KAGOJ = "http://www.bhorerkagoj.net/"
link_BHORER_KAGOJ = "https://www.bhorerkagoj.com/?s=" + SEARCH_TOPIC

link_JAYJAYDIN = 'https://www.jaijaidinbd.com/search/google/?q=' + SEARCH_TOPIC + '&cx=partner-pub-5450504941871955%3A3787426415&cof=FORID%3A10&ie=UTF-8&sa=Search&sort=date'
# data not loading
link_MZAMIN = "http://www.mzamin.com/"
link_DAILYSTAR = "http://www.thedailystar.net/"
link_NAYADIGANTA = "https://www.dailynayadiganta.com/search?q="

# driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
# s = Service()
options = Options()
options.headless = True
options.add_argument("--window-size=1920,1200")
# chrome_options = webdriver.ChromeOptions()
# chrome_prefs = {
#     "profile.default_content_setting_values": {
#         "images": 2,
#         "javascript": 2,
#     }
# }
# chrome_options.experimental_options["prefs"] = chrome_prefs
#
# chrome_options.add_argument("--disable-notifications")
# driver = webdriver.Chrome(options = options,executable_path= CHROME_DRIVER_PATH)
driver = webdriver.Chrome(options=options)
# driver = webdriver.Chrome(ChromeDriverManager().install())

driver.maximize_window()
driver.delete_all_cookies()


def get_news_text(link, title_property, description_property):
    sleep(randint(1, 3))
    url = requests.get(link)
    soup = BeautifulSoup(url.content, 'html.parser')
    try:
        title = soup.find("meta", property=title_property, content=True)
        description = soup.find("meta", property=description_property, content=True)
        # print(f"title:{title}\nDescription:{description}")
        return [title['content'], description['content']]
    except:
        print("element not found")


def search_ntv(home_link):
    print("\t NTVBD")
    driver.get(home_link)
    # WebDriverWait(driver, 20).until(
    #     EC.element_to_be_clickable((By.XPATH, "//input[@class='search-input srch_keyword']"))).click()
    # WebDriverWait(driver, 20).until(
    #     EC.element_to_be_clickable((By.XPATH, "//input[@class='search-input srch_keyword']"))).send_keys(SEARCH_TOPIC)
    # WebDriverWait(driver, 20).until(
    #     EC.element_to_be_clickable((By.XPATH, "//button[@class='search-button searchIcon  absolute']"))).click()

    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//a[@class='gs-title']")))
        print("search results ready!!")
    except TimeoutException:
        print("Timed out!")

    search_links = driver.find_elements(By.XPATH, "//a[@class='gs-title']")
    texts = []
    links = []
    for element in search_links:
        links.append(element.get_attribute("href"))
        texts.append(element.get_attribute("innerHTML"))

    print(f"{len(texts)} search results found!!")
    df = pd.DataFrame(texts, columns=['Headlines'])
    df['links'] = links
    df = df.drop_duplicates(keep='first')
    df.dropna(inplace=True)
    headlines_and_texts = []
    for link in tqdm(df['links']):
        # details = []
        # details.append(get_news_text(link, "og:title", "og:description"))
        # print(get_news_text(link, "og:title", "og:description"))
        data = get_news_text(link, "og:title", "og:description")
        if len(data) > 0:
            headlines_and_texts.append(get_news_text(link, "og:title", "og:description"))
    df['headlines_and_texts'] = headlines_and_texts
    return df


def search_inqilab(home_link):
    print("\t INQILAB")
    driver.get(home_link)
    WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//input[@class='search-query form-control']"))).click()
    WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//input[@class='search-query form-control']"))).send_keys(
        SEARCH_TOPIC + Keys.RETURN)
    search_links = driver.find_elements(By.XPATH, "//div[@class='col-xs-12 col-sm-6']")
    divs = []
    for element in search_links:
        # links.append(element.get_attribute("href"))
        divs.append(element.get_attribute("innerHTML"))
        # miscs.append(element.get_attribute(("outerHTML")))

        # texts.append(element.get_text())
    print(f"{len(divs)} search results found!!")
    # print(type(texts[0]))
    # df = pd.DataFrame(texts, columns=['Headlines'])
    # df['links'] = links
    headlines = []
    urls = []
    for data in divs:
        url = re.findall("href=\"[^\n]+\" ", data)[0].replace("href=", "")
        headline = re.findall("<h2>[^\n]+</h2>", data)[0]
        urls.append(url)
        headlines.append(headline)
    # df['Minsc'] = miscs
    # df["Urls"]  = urls
    df = pd.DataFrame(headlines, columns=['Headlines'])
    df['links'] = urls
    df = df.drop_duplicates(keep='first')
    df.dropna(inplace=True)
    texts = []
    for link in tqdm(df['links']):
        details = []
        # print(link)
        driver.get(link.replace("\"", ""))
        try:
            web_sources = WebDriverWait(driver, 20).until(EC.visibility_of_element_located(
                (By.XPATH, "//div[@class='col-xs-12 col-sm-12']//following::p[1]"))).get_attribute('innerHTML')
            # WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//div[@id = 'application/ld+json']")))
            # print("search results ready!!")
        except TimeoutException:
            print("Timed out!")
        texts.append(web_sources)
        # print(web_sources)
        # web_sources = driver.find_elements(By.XPATH, "//script[@type = 'application/ld+json']")
        # data = [web_source.get_attribute('innerHTML') for web_source in web_sources]
    df['texts'] = texts
    # driver.close()
    return df


def search_jugantor(home_link):
    print("\t JUGANTOR")
    driver.get(home_link)
    print("entering search results")
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//a[@class='gs-title']")))
        print("search results ready!!")
    except TimeoutException:
        print("Timed out!")

    # print(driver.find_elements(By.XPATH, "//a[@class='gs-title']"))
    search_links = driver.find_elements(By.XPATH, "//a[@class='gs-title']")
    # search_links = driver.find_elements(By.XPATH, "//a[@dir='ltr']")
    # print(f"search links : {search_links}")
    texts = []
    links = []
    for element in search_links:
        links.append(element.get_attribute("href"))
        texts.append(element.get_attribute("innerHTML"))

    print(f"{len(texts)} search results found!!")
    df = pd.DataFrame(texts, columns=['Headlines'])
    df['links'] = links
    df = df.drop_duplicates(keep='first')
    df.dropna(inplace=True)
    descriptions = []
    for link in tqdm(df['links']):
        html = urllib.request.urlopen(str(link))
        htmlParse = BeautifulSoup(html, 'html.parser')
        texts = ""
        for para in htmlParse.find_all("p"):
            texts += para.get_text()
        descriptions.append(texts[int(len(texts) / 2):])
    df['Descriptions'] = descriptions
    # df.dropna(inplace=True)
    # driver.close()
    return df


def search_bhorer_kagoj(home_link):
    print("\t BHORER KAGOJ")
    driver.get(home_link)
    print("entering search results")
    try:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//div[@id='id_246528']")))
        print("search results ready!!")
    except TimeoutException:
        print("Timed out!")
    # print(driver.find_elements(By.XPATH, "//a[@class='gs-title']"))
    # search_texts = driver.find_element(By.XPATH, "//h4[@class='title']")
    search_links = driver.find_elements(By.XPATH, "//a[@class='col-sm-6 col-xs-12']")
    # search_links = driver.find_elements(By.XPATH, "//a[@dir='ltr']")
    # print(f"search links : {search_links}")
    texts = []
    links = []
    for element in search_links:
        links.append(element.get_attribute("href"))
        texts.append(element.get_attribute("innerHTML"))

    print(f"{len(texts)} search results found!!")
    print(f"{len(links)} links!!")
    df = pd.DataFrame(texts, columns=['Headlines'])
    df['links'] = links
    df = df.drop_duplicates(keep='first')
    # driver.close()
    # df.dropna(inplace=True)
    return df


def search_daily_star(home_link):
    aci_search = home_link + '/search?t=ACI#gsc.tab=0&gsc.q=ACI&gsc.page='

    page_no = 1
    scrap_df = []

    driver.get(aci_search + str(page_no))
    pages = len(driver.find_elements(By.CLASS_NAME, "gsc-cursor-page"))

    t0 = time.time()
    while page_no <= pages:
        page_no += 1

        for i in range(1, 11):

            try:
                link = driver.find_element(By.XPATH,
                                           '//*[@class="gsc-wrapper"]/div/div[1]/div/div/div[' + str(
                                               i) + ']/div/div/div/a')
            except:
                link = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
                    (By.XPATH, '//*[@class="gsc-wrapper"]/div/div[1]/div/div/div[' + str(i) + ']/div/div/div/a')))

            link_soup = link.get_attribute('data-ctorig')
            soup = BeautifulSoup(requests.get(link_soup).text, "lxml")

            try:
                section = None
                categories = soup.find('h1').findAllPrevious(attrs={'class': re.compile(r'category')})

                for item in categories:

                    if item.find('a') is not None:
                        section = item.find('a').text.strip()
                        break
            except:
                section = None
                print(f"Section not accessible from page: {None}")

            try:
                date_primitive = soup.find('h1').findNext('div', attrs={'class': re.compile(r'date')})
                date_primitive = date_primitive.text[:date_primitive.text.strip().find("Last update")].strip()
                # date_primitive = pd.to_datetime(date_primitive, format="%d/%m/%Y")
            except:
                date_primitive = None
                print(f"Date not accessible from page: {None}")

            try:
                source = soup.find('article').findChild(attrs={'class': re.compile(r'byline-wrapper')}).findChild(
                    attrs={'class': re.compile(r'byline')}).text
            except:
                source = None
                print(f"Source not accessible from page: {source}")

            try:
                headline = soup.find('h1').text.strip()
            except:
                headline = link.text.strip()
                print(f"Headline not accessible from page: {headline}")

            try:
                description = soup.find('div', {"class": re.compile(r'^section-content')}).text.strip()
            except:
                print(f"Description not accessible from page or irregular page.")
                try:
                    texts = soup.findAll('p', text=True)
                    description = ''
                    for text in texts:
                        description += text.text + " "
                except:
                    print('Text not accessible even after exception handling')

            scrap_df.append({
                'date': date_primitive,
                'section': section,
                'source': source,
                'headlines': headline,
                'links': link_soup,
                'description': description
            })
        driver.get(aci_search + str(page_no))
    scrap_df = pd.DataFrame(scrap_df)
    scrap_df.date = pd.to_datetime(scrap_df.date)
    t1 = time.time()
    print(f"Time required: {t1 - t0:0.3f}")
    return scrap_df


def test(home_link):
    driver.get(home_link)
    print("\t KALER KANTHA")
    driver.get(home_link)
    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//i[@class='fa fa-search']"))).click()
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, "//input[@class='search-query form-control']"))).click()
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, "//input[@class='search-query form-control']"))).send_keys(
        SEARCH_TOPIC + Keys.RETURN)
    # print(driver.find_element_by_class_name('gs-title'))
    try:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "gs-title")))
        print("search results ready!!")
    except TimeoutException:
        print("Timed out!")
    search_links = driver.find_elements(By.CLASS_NAME, "gs-title")
    for element in search_links:
        print(element.get_attribute('innerHTML'))


def search_mzamin(home_link, search_key=SEARCH_TOPIC, pages=1, keep_content=False):
    print("\t MZMIN")
    driver.get(home_link)
    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//i[@class='bi bi-search']")))

    search = driver.find_element(By.XPATH, "//i[@class='bi bi-search']")
    action = AC(driver)
    action.move_to_element(search)
    action.click()
    action.perform()

    try:
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//input[@class='gsc-input']")))
    except:
        action.click()
        action.perform()
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//input[@class='gsc-input']")))

    google_search_bar = driver.find_element(By.XPATH, "//input[@class='gsc-input']")
    action.move_to_element(google_search_bar)
    action.click()
    action.perform()

    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//input[@class='gsc-input']"))).send_keys(
        search_key + Keys.RETURN)

    print("entering search results")
    scrap_df = []
    i = 1
    while i <= pages:
        i += 1
        action.send_keys(Keys.CONTROL + Keys.HOME)
        action.pause(1)
        action.perform()
        try:
            WebDriverWait(driver, 5). \
                until(
                EC.presence_of_element_located((By.XPATH, "//div[@class='gs-title']/a[@href][@class='gs-title']")))
            print("search results ready!!")
        except TimeoutException:
            print("Timed out!")
        search_links = driver.find_elements(By.XPATH, "//div[@class='gs-title']/a[@href][@class='gs-title']")
        print(search_links)

        j = 1
        for element in search_links:
            page_link = element.get_attribute("data-ctorig")
            page_link = "http://www." + page_link[page_link.find("mzamin.com"):]
            # print(page_link)
            print(j, page_link)
            j += 1
            page_source = requests.get(page_link).text
            try:
                article = BeautifulSoup(page_source, features="html.parser").find('article')
                headline = article.findChild('h1', attrs={'class': re.compile(r'^lh')})
                date = headline.findNextSibling('h5').next_sibling
                if len(date) <= 2:
                    date = date.next
                section = article.findChild('h4', attrs={'class': 'sectitle'})
                source = article.findChild('h5')
                description = headline.findNextSibling('div')
            except:
                print("Page loading error")

            scrap_df.append({
                'date': date.text.strip(),
                'section': section.text.strip(),
                'source': source.text.strip(),
                'headlines': headline.text.strip(),
                'links': page_link,
                'description': description.text.strip()
            })

        # Go to next page
        action = AC(driver)
        action.move_to_element(search_links[-1])
        action.scroll_to_element(driver.find_element(By.XPATH, "//div[@class='gsc-cursor-box gs-bidi-start-align']"))
        action.perform()
        try:
            WebDriverWait(driver, 5). \
                until(EC.presence_of_element_located((By.XPATH, f"//div[@aria-label='Page {i}']")))
            print("Next Page visible")
            WebDriverWait(driver, 5). \
                until(EC.element_to_be_clickable((By.XPATH, f"//div[@aria-label='Page {i}']"))).click()
            print("Next Page click")
        except TimeoutException:
            print("Timed out!")
            break
    scrap_df = pd.DataFrame(scrap_df)
    # To keep or not to keep description
    if not keep_content:
        scrap_df = scrap_df.drop(columns=['description'])
    return scrap_df


def search_nayaDiganta(home_link, search_key=SEARCH_TOPIC, pages=1, keep_content=False):
    print("\t NAYA DIGANTA")
    driver.get(home_link + search_key)
    # WebDriverWait(driver, 5).until(
    #     EC.element_to_be_clickable((By.XPATH, "//i[@class='fa fa-search search-btn']"))).click()
    # WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//input[@class='form-control']"))).click()
    # WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//input[@class='form-control']"))).send_keys(
    #     SEARCH_TOPIC + Keys.RETURN)
    # WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//button[@class='btn']"))).click()
    print("Entering search results")
    try:
        print("Searching...")
        tqdm(WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//div[@class='gs-title']/a[@class='gs-title'][@target]"))))
        print("search results ready!!")
    except TimeoutException:
        print("Timed out!")

    search_links = driver.find_elements(By.XPATH, "//div[@class='gs-title']/a[@class='gs-title'][@target]")
    scrap_df = []

    j = 1
    for element in search_links:
        page_link = element.get_attribute("data-ctorig")
        page_link = "http://www." + page_link[page_link.find("dailynayadiganta.com"):]

        print(j, page_link)
        j += 1
        page_source = requests.get(page_link).text
        try:
            page_html = BeautifulSoup(page_source, features="html.parser")
            headline = page_html.find('title')
            date = page_html.find("meta", {'name': 'publish-date'}, content=True)['content']
            date = pd.to_datetime(date)

            section = page_html.find('ol', {'class': "breadcrumb"}).findChildren('li')[2]
            source = page_html.find('section', {'class': re.compile(r"^article-info")}).findChildren('li')[0]

            description = page_html.find('div', {'class': 'news-content'})
            scrap_df.append({
                'date': str(date),
                'section': section.text.strip(),
                'source': source.text.strip(),
                'headlines': headline.text,
                'links': page_link,
                'description': description.text.strip()
            })
        except AttributeError:
            print("Page loading error")

    print(f"{len(scrap_df)} Search results found!!")
    scrap_df = pd.DataFrame(scrap_df)

    # To keep or not to keep description
    if not keep_content:
        scrap_df = scrap_df.drop(columns=['description'])
    return scrap_df


def search_jayjaydin(home_link):
    print("\t JAYJAYDIN")
    driver.get(home_link)
    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//i[@class='fa fa-search src-top']"))).click()
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, "//input[@class='bn-font srch_keyword form-control']"))).click()
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, "//input[@class='bn-font srch_keyword form-control']"))).send_keys(
        SEARCH_TOPIC + Keys.RETURN)
    # WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//input[@class='bn-font srch_keyword form-control']"))).send_keys(SEARCH_TOPIC+ Keys.RETURN)
    # WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//button[@class='btn']"))).click()
    print("entering search results")
    # print(driver.find_elements(By.XPATH, "//a[@class='gs-title']"))
    # search_texts = driver.find_elements(By.XPATH, "//h4[@class='title']")
    try:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//a[@class='gs-title']")))
        print("search results ready!!\n Scrapping Search results:")

    except TimeoutException:
        print("Timed out!")

    search_links = driver.find_elements(By.XPATH, "//a[@class='gs-title']")
    print(f"search links : {search_links}")
    texts = []
    links = []
    for element in search_links:
        # print(f"{element}")
        links.append(element.get_attribute("href"))
        texts.append(element.get_attribute('innerHTML'))

    print(f"{len(texts)} search results found!!")
    print(f"{len(links)} links found!!")
    df = pd.DataFrame(texts, columns=['Headlines'])
    df['links'] = links
    df = df.drop_duplicates(keep='first')
    # driver.close()
    # df.dropna(inplace=True)
    return df


def search_kaler_kontho(home_link):
    scrap_df = []

    driver.get(home_link)
    gsc_link = driver.find_elements(By.XPATH, "//iframe[@name='googleSearchFrame']")
    driver.get(gsc_link[0].get_attribute('src'))
    links = driver.find_elements(By.XPATH, "//div[@class='gs-title']/a[@class ='gs-title']")
    for link in links[:-1]:
        page_source = requests.get(link.get_attribute('data-ctorig')).text
        soup = BeautifulSoup(page_source, "lxml")

        content_parent = soup.find('div', {'class': 'some-class-name2'})
        contents = content_parent.findAll('p', attrs={'style': None})

        headline = content_parent.findPrevious('h2').text.strip()

        link_text = link.get_attribute('data-ctorig')
        txt = ''
        for content in contents:
            txt += content.text

        scrap_df.append({

            'headlines': headline,
            'links': link_text,
            'description': txt
        })

    df = pd.DataFrame(scrap_df)

    return df


# def search_kaler_kontho(home_link):
#     print("\t KALER KANTHA")
#     driver.get(home_link)
#     WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//i[@class='fa fa-search']"))).click()
#     WebDriverWait(driver, 5).until(
#         EC.presence_of_element_located((By.XPATH, "//input[@class='search-query form-control']"))).click()
#     WebDriverWait(driver, 5).until(
#         EC.presence_of_element_located((By.XPATH, "//input[@class='search-query form-control']"))).send_keys(
#         SEARCH_TOPIC + Keys.RETURN)
#     # WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//span[@class=' glyphicon glyphicon-search']"))).click()
#     print("entering search results")
#     # tqdm(driver.implicitly_wait(10))
#     try:
#         tqdm(WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//a[@class='gs-title']"))))
#         print("search results ready!!\n Scrapping Search results:")
#
#     except TimeoutException:
#         print("Timed out!")
#     search_links = driver.find_elements(By.XPATH, "//a[@class='gs-title']")
#     print(search_links)
#     # search_links = driver.find_elements(By.XPATH, "//a[@dir='ltr']")
#     # print(f"search links : {search_links}")
#     texts = []
#     links = []
#     for element in search_links:
#         links.append(element.get_attribute("href"))
#         texts.append(element.get_attribute("innerHTML"))
#     # print(f"links:{links}")
#     print(f"{len(texts)} search results found!!")
#     df = pd.DataFrame(texts, columns=['Headlines'])
#     df['links'] = links
#     df = df.drop_duplicates(keep='first')
#     # df.dropna(inplace=True)
#     return df


def news_extract_from_link(links, xpath):
    headlines_and_texts = []
    for link in tqdm(links):
        # tqdm(print('\t\tGetting into search results...'))
        # texts=[]
        details = []
        driver.get(link)
        try:
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, xpath)))
            # print("search results ready!!")
        except TimeoutException:
            print("Timed out!")
        web_sources = driver.find_elements(By.XPATH, xpath)
        data = [web_source.get_attribute('innerHTML') for web_source in web_sources]
        # print(type(data))
        # print(len(data))
        # print(type(data[1]))
        for datum in data:
            if 'articleBody' in json.loads(datum) and 'headline' in json.loads(datum):
                # print(json.loads(datum)['articleBody'])
                headline = json.loads(datum)['headline']
                news_text = json.loads(datum)['articleBody']

                # details{headline:news_text}
                details.append(headline)
                details.append(news_text)
        headlines_and_texts.append(details)
    return headlines_and_texts


def search_prothom_alo(home_link):
    print("\t PROTHOM ALO")
    driver.get(home_link)
    # WebDriverWait(driver, 25).until(EC.element_to_be_clickable((By.XPATH, "// img[@src ='https://tpc.googlesyndication.com/simgad/9645502256302782469?']"))).click()
    # # WebDriverWait(driver, 25).until(EC.element_to_be_clickable((By.XPATH, "//svg[@xmlns='http://www.w3.org/2000/svg']"))).click()
    # WebDriverWait(driver, 25).until(EC.element_to_be_clickable((By.XPATH, "//input[@class='search__form-input']"))).click()
    # WebDriverWait(driver, 25).until(EC.element_to_be_clickable((By.XPATH, "//input[@class='search__form-input']"))).send_keys(SEARCH_TOPIC + Keys.RETURN)
    # # WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//button[@class='btn']"))).click()
    # WebDriverWait(driver, 25).until(EC.element_to_be_clickable((By.XPATH, "//img[@id='paloash_richmedia_close']"))).click()

    # WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//div[@id='closebutton']"))).click()
    # driver.find_the_element_by_id("closebutton").click()

    # print("entering search results")
    try:
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//span[@class='tilte-no-link-parent']")))
        print("search results ready!!")
    except TimeoutException:
        print("Timed out!")

    # search_links = driver.find_elements(By.XPATH,  "//span[@class='tilte-no-link-parent']")
    search_links = driver.find_elements(By.XPATH, "//a[@class='card-with-image-zoom']")
    # print(search_links)
    # search_links = driver.find_elements(By.XPATH, "//a[@dir='ltr']")
    # print(f"search links : {search_links}")
    texts = []
    links = []
    news = []
    for element in search_links:
        links.append(element.get_attribute("href"))
        texts.append(element.get_attribute("aria-label"))
    # print(f"links:{links}")
    print(f"{len(texts)} search results found!!")
    df = pd.DataFrame(texts, columns=['Headlines'])
    df['links'] = links
    df = df.drop_duplicates(keep='first')
    headlines_and_texts = []
    for link in tqdm(df['links']):
        # tqdm(print('\t\tGetting into search results...'))
        # texts=[]
        details = []
        driver.get(link)
        try:
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, "//script[@type = 'application/ld+json']")))
            # print("search results ready!!")
        except TimeoutException:
            print("Timed out!")
        web_sources = driver.find_elements(By.XPATH, "//script[@type = 'application/ld+json']")
        data = [web_source.get_attribute('innerHTML') for web_source in web_sources]
        # print(type(data))
        # print(len(data))
        # print(type(data[1]))
        for datum in data:
            if 'articleBody' in json.loads(datum) and 'headline' in json.loads(datum):
                # print(json.loads(datum)['articleBody'])
                headline = json.loads(datum)['headline']
                news_text = json.loads(datum)['articleBody']

                # details{headline:news_text}
                details.append(headline)
                details.append(news_text)
        headlines_and_texts.append(details)
        # res = json.loads(data[1])
        # print(res.keys())
        # print(res)
        # print(res['description'])
        # full_text = [datum['articleBody'] for datum in data]
        # print(full_text)
        # details.append(data)
        # driver.close()
    # driver.close()
    df["headlines_and_texts"] = headlines_and_texts
    # df.dropna(inplace=True)
    return df


def search_JayJayDin(search_link):
    driver.get(search_link)
    soup = BeautifulSoup(driver.page_source, features="lxml")
    for el in soup.find_all('div', attrs={"id": "cse-search-results"}):
        li = el.find('iframe', attrs={"name": "googleSearchFrame"})
        driver.get(li['src'])
        time.sleep(2)
        soup1 = BeautifulSoup(driver.page_source, features="lxml")
        a = soup1.find_all("a", {"class": "gs-title"})
    i = 0
    headline = []
    links = []
    contents = []
    while i < 20:
        time.sleep(2)
        driver.get(a[i]['data-cturl'])
        news_page = BeautifulSoup(driver.page_source, features="lxml")
        news_header = news_page.find_all('div', attrs={"id": "dtl_hl_block"})
        heading = news_header[0].get_text()
        news_content = news_page.find_all('div', attrs={"id": "dtl_content_block"})
        content = news_content[0].get_text()
        links.append(a[i]['data-cturl'])
        headline.append(heading)
        contents.append(content)
        print(f"{len(headline)} search results found!!")
        df = pd.DataFrame(headline, columns=['Headlines'])
        df['Links'] = links
        df = df.drop_duplicates(keep='first')
        df.dropna(inplace=True)
        df['News_content'] = contents
        i = i + 2
    return df


if __name__ == '__main__':
    # test_df = test(link_KALER_KONTHO)

    # PA_df = search_prothom_alo(link_PROTHOM_ALO)
    # mzmin_df = search_mzamin(link_MZAMIN, 1)
    # ntv_df = search_ntv(link_NTVBD)
    nayaDiganta_df = search_nayaDiganta(link_NAYADIGANTA, keep_content=False)
    # jugantor_df = search_jugantor(link_JUGANTOR)

    # In progress:
    # inqilab_df = search_inqilab(link_inqilab)
    # daily_star_df = search_daily_star(link_DAILYSTAR)
    # jjd_df = search_JayJayDin(link_JAYJAYDIN)
    # kk_df = search_kaler_kontho(link_KALER_KONTHO)
    # bhorer_kagoj_df = search_bhorer_kagoj(link_BHORER_KAGOJ)
    print("Completed")
    driver.close()

    print("\t\tNews search results:")

    # print(inqilab_df)
    # print(mzmin_df)
    # print(inqilab_df)
    print(nayaDiganta_df)

    # try:
    #     daily_star_df.to_csv("daily-star-scrapped-data.csv", index=False)
    #     print("\t\tDATA SAVED SUCCESSFULLY!!")
    # except:
    #     print('Failed to save')
    # print(mzmin_df)
    # print(nayaDiganta_df)
    # print(ntv_df)
    # print(jugantor_df)

    # print(bhorer_kagoj_df)
    # print(kk_df)
    # print(test_df)
    # print(jjd_df)
