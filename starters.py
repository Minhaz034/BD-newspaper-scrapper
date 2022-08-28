import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from tqdm import tqdm
import json
from newspaper import Article

CHROME_DRIVER_PATH = "/home/aci/Chrome Webdriver/chromedriver"
SEARCH_TOPIC = "এসিআই"
# link_PROTHOM_ALO = "https://www.prothomalo.com/"  #popup issues
link_PROTHOM_ALO = "https://www.prothomalo.com/search?q="+SEARCH_TOPIC
link_inqilab = "https://www.dailyinqilab.com/"
link_NTVBD = "https://www.ntvbd.com/"
link_KALER_KONTHO = "http://www.kalerkantho.com/" #data not loading
link_JUGANTOR = "http://www.jugantor.com/"        #data not loading
# link_BHORER_KAGOJ = "http://www.bhorerkagoj.net/"
link_BHORER_KAGOJ =  "https://www.bhorerkagoj.com/?s="+SEARCH_TOPIC

link_JAYJAYDIN = "http://www.jaijaidinbd.com/"     #data not loading
link_MZAMIN = "http://www.mzamin.com/"
link_DAILYSTAR = "http://www.thedailystar.net/"
link_NAYADIGANTA = "http://www.dailynayadiganta.com/"

# driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
s = Service()
# driver = webdriver.Chrome(Service(CHROME_DRIVER_PATH))
driver = webdriver.Chrome(ChromeDriverManager().install())

driver.maximize_window()
driver.delete_all_cookies()



chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--disable-notifications")
# webdriver.Chrome(os.path.join(path, 'chromedriver'),
#                  chrome_options=chrome_options)


def search_ntv(home_link):
    print("\t NTVBD")
    driver.get(home_link)
    WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//input[@class='search-input srch_keyword']"))).click()
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//input[@class='search-input srch_keyword']"))).send_keys(SEARCH_TOPIC)
    WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//button[@class='search-button searchIcon  absolute']"))).click()

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
    # driver.close()
    return df


def search_inqilab(home_link):
    print("\t INQILAB")
    driver.get(home_link)
    WebDriverWait(driver, 20).until( EC.element_to_be_clickable((By.XPATH, "//input[@class='search-query form-control']"))).click()
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//input[@class='search-query form-control']"))).send_keys(SEARCH_TOPIC + Keys.RETURN)
    search_links = driver.find_elements(By.XPATH, "//div[@class='col-xs-12 col-sm-6']")
    texts = []
    links = []
    for element in search_links:
        links.append(element.get_attribute("href"))
        texts.append(element.get_attribute("innerHTML").strip())
        # texts.append(element.get_text())
    print(f"{len(texts)} search results found!!")
    # print(texts)
    df = pd.DataFrame(texts, columns=['Headlines'])
    df['links'] = links
    df = df.drop_duplicates(keep='first')
    # df.dropna(inplace=True)
    # driver.close()
    return df





def search_jugantor(home_link):
    print("\t JUGANTOR")
    driver.get(home_link)
    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//i[@class='fas fa-search align-bottom']"))).click()
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//input[@class='form-control srch_keyword']"))).click()
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//input[@class='form-control srch_keyword']"))).send_keys(SEARCH_TOPIC+ Keys.RETURN)
    # WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//button[@class='btn']"))).click()
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
    # df.dropna(inplace=True)
    # driver.close()
    return df


def search_bhorer_kagoj(home_link):
    print("\t BHORER KAGOJ")
    driver.get(home_link)
    # WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//input[@class='search-submit fa']"))).click()
    # WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//input[@class='search-field']"))).click()
    # WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//input[@class='search-field']"))).send_keys(SEARCH_TOPIC+ Keys.RETURN)
    # WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//button[@class='btn']"))).click()
    print("entering search results")
    try:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//div[@id='id_246528']")))
        print("search results ready!!")
    except TimeoutException:
        print("Timed out!")
    # print(driver.find_elements(By.XPATH, "//a[@class='gs-title']"))
    # search_texts = driver.find_element(By.XPATH, "//h4[@class='title']")
    search_links = driver.find_elements(By.XPATH,"//a[@class='col-sm-6 col-xs-12']")
    # search_links = driver.find_elements(By.XPATH, "//a[@dir='ltr']")
    # print(f"search links : {search_links}")
    texts = []
    links = []
    # for element in search_texts:
    #     # links.append(element.get_attribute("href"))
    #     texts.append(element.get_attribute("innerHTML"))
    for element in search_links:
        links.append(element.get_attribute("href"))
        texts.append(element.get_attribute("innerHTML"))

    print(f"{len(texts)} search results found!!")
    print(f"{len(links)} links!!")
    # print(links)
    # print(f"texts:{texts}")
    # print(f"links: {links}")
    df = pd.DataFrame(texts, columns=['Headlines'])
    df['links'] = links
    df = df.drop_duplicates(keep='first')
    # driver.close()
    # df.dropna(inplace=True)
    return df


def test(home_link):
    driver.get(home_link)
    print("\t KALER KANTHA")
    driver.get(home_link)
    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//i[@class='fa fa-search']"))).click()
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//input[@class='search-query form-control']"))).click()
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//input[@class='search-query form-control']"))).send_keys(SEARCH_TOPIC + Keys.RETURN)
    # print(driver.find_element_by_class_name('gs-title'))
    try:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "gs-title")))
        print("search results ready!!")
    except TimeoutException:
        print("Timed out!")
    search_links = driver.find_elements(By.CLASS_NAME,"gs-title")
    for element in search_links:
        print(element.get_attribute('innerHTML'))


def search_mzamin(home_link):
    print("\t MZMIN")
    driver.get(home_link)
    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//i[@class='bi bi-search']"))).click()
    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//input[@class='gsc-input']"))).click()
    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//input[@class='gsc-input']"))).send_keys(SEARCH_TOPIC + Keys.RETURN)
    # WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//button[@class='btn']"))).click()
    print("entering search results")
    try:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//a[@class='gs-title']")))
        print("search results ready!!")
    except TimeoutException:
        print("Timed out!")

    search_links = driver.find_elements(By.XPATH, "//a[@class='gs-title']")
    # print(search_links)
    # search_links = driver.find_elements(By.XPATH, "//a[@dir='ltr']")
    # print(f"search links : {search_links}")
    texts = []
    links = []
    for element in search_links:
        links.append(element.get_attribute("href"))
        texts.append(element.get_attribute("innerHTML"))
    # print(f"links:{links}")
    print(f"{len(texts)} search results found!!")
    df = pd.DataFrame(texts, columns=['Headlines'])
    df['links'] = links
    df = df.drop_duplicates(keep='first')
    # df.dropna(inplace=True)
    # driver.close()
    return df


def search_nayaDiganta(home_link):
    print("\t NAYA DIGANTA")
    driver.get(home_link)
    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//i[@class='fa fa-search search-btn']"))).click()
    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//input[@class='form-control']"))).click()
    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//input[@class='form-control']"))).send_keys(SEARCH_TOPIC + Keys.RETURN)
    # WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//button[@class='btn']"))).click()
    print("entering search results")
    try:
        print("searching...")
        tqdm(WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//a[@class='gs-title']"))))
        print("search results ready!!")
    except TimeoutException:
        print("Timed out!")

    search_links = driver.find_elements(By.XPATH, "//a[@class='gs-title']")
    # print(search_links)
    # search_links = driver.find_elements(By.XPATH, "//a[@dir='ltr']")
    # print(f"search links : {search_links}")
    texts = []
    links = []
    for element in search_links:
        links.append(element.get_attribute("href"))
        texts.append(element.get_attribute("innerHTML"))
    # print(f"links:{links}")
    print(f"{len(texts)} search results found!!")
    df = pd.DataFrame(texts, columns=['Headlines'])
    df['links'] = links
    df = df.drop_duplicates(keep='first')
    # df.dropna(inplace=True)
    # driver.close()
    return df


def search_jayjaydin(home_link):
    print("\t JAYJAYDIN")
    driver.get(home_link)
    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//i[@class='fa fa-search src-top']"))).click()
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//input[@class='bn-font srch_keyword form-control']"))).click()
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//input[@class='bn-font srch_keyword form-control']"))).send_keys(SEARCH_TOPIC+ Keys.RETURN)
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
    print("\t KALER KANTHA")
    driver.get(home_link)
    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//i[@class='fa fa-search']"))).click()
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//input[@class='search-query form-control']"))).click()
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//input[@class='search-query form-control']"))).send_keys(SEARCH_TOPIC+Keys.RETURN)
    # WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//span[@class=' glyphicon glyphicon-search']"))).click()
    print("entering search results")
    # tqdm(driver.implicitly_wait(10))
    try:
        tqdm(WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//a[@class='gs-title']"))))
        print("search results ready!!\n Scrapping Search results:")

    except TimeoutException:
        print("Timed out!")
    search_links = driver.find_elements(By.XPATH, "//a[@class='gs-title']")
    print(search_links)
    # search_links = driver.find_elements(By.XPATH, "//a[@dir='ltr']")
    # print(f"search links : {search_links}")
    texts = []
    links = []
    for element in search_links:
        links.append(element.get_attribute("href"))
        texts.append(element.get_attribute("innerHTML"))
    #print(f"links:{links}")
    print(f"{len(texts)} search results found!!")
    df = pd.DataFrame(texts, columns=['Headlines'])
    df['links'] = links
    df = df.drop_duplicates(keep='first')
    # df.dropna(inplace=True)
    return df


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
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//span[@class='tilte-no-link-parent']")))
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
    headlines_and_texts=[]
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
        web_sources = driver.find_elements(By.XPATH,"//script[@type = 'application/ld+json']")
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




if __name__ == '__main__':

    # kk_df = search_kaler_kontho(link_KALER_KONTHO)
    # test_df = test(link_KALER_KONTHO)
    # jjd_df=  search_jayjaydin(link_JAYJAYDIN)
    PA_df = search_prothom_alo(link_PROTHOM_ALO)
    # mzmin_df = search_mzamin(link_MZAMIN)
    # ntv_df = search_ntv(link_NTVBD)
    # nayaDiganta_df = search_nayaDiganta(link_NAYADIGANTA)
    # jugantor_df = search_jugantor(link_JUGANTOR)

    # bhorer_kagoj_df = search_bhorer_kagoj(link_BHORER_KAGOJ)
    # inqilab_df = search_inqilab(link_inqilab)
    driver.close()
    print("\t\tnews search results:")

    #
    # print(inqilab_df)
    print(PA_df)
    try:
        tqdm(PA_df.to_csv("prothom-alo-scrapped-data.csv",index=False))
        print("\t\tsaved data successfully!!")
    except:
        print('Failed to save')
    # print(mzmin_df)
    # print(nayaDiganta_df)
    # print(ntv_df)
    # print(jugantor_df)

    # print(bhorer_kagoj_df)
    # print(kk_df)
    # print(test_df)
    # print(jjd_df)


