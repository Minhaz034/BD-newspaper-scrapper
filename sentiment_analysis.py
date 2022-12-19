
from scraputil import *
import pandas as pd


if __name__ == '__main__':
    get_news = GetNews(browser='Chrome', headless=False, search_key="এসিআই")
    get_news.select_browser('Chrome')

    translate = False
    news_data_df = pd.DataFrame()
    for name in NAMES[-1:]:

        try:
            news_df = get_news.extract(name, google_news=False, keep_content=False)
            if translate:
                news_df = get_news.translate_news(news_df)
            news_df['sentiment'] = get_sentiment(news_df.headline.to_list())
            news_data_df = pd.concat((news_data_df, news_df), axis=0, ignore_index=True)
        except:
            news_data_df.to_csv("./data/temp1.csv", index=False)

    get_news.close_browser()
    news_data_df.to_csv("./outputs.csv", index=False)
