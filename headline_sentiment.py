import pandas as pd
from transformers import pipeline
from transformers import AutoTokenizer
from transformers import AutoModel
from transformers import AutoModelForSequenceClassification
import torch
import os

from deep_translator import (GoogleTranslator, single_detection)
import time

sample_raw_inputs=["Agricultural machinery is beyond the reach of farmers",
            "Alamgir, who wanted to teach in exchange for rice, got a job in ACI Logistics Limited",
            "Job opportunities in ACI Group with attractive salary"]
model_path ="./bertweet-base-sentiment-analysis"
TRANSLATOR = GoogleTranslator(source='bn', target='en')

def get_sentiment(raw_inputs, model_path ="./bertweet-base-sentiment-analysis" ):
    print(f"{torch.cuda.device_count()} GPU available")
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    try:
        if os.path.exists(model_path):
            print("Model already on device!")
            tokenizer = AutoTokenizer.from_pretrained(model_path)
            model = AutoModelForSequenceClassification.from_pretrained(model_path).to(device)
        else:
            tokenizer = AutoTokenizer.from_pretrained("finiteautomata/bertweet-base-sentiment-analysis")
            model = AutoModelForSequenceClassification.from_pretrained("finiteautomata/bertweet-base-sentiment-analysis").to(device)

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
    sentiments = [prediction.argmax(axis=0) for prediction in predictions.detach().cpu().numpy()]
    print(model.config.id2label)

    if device.type == 'cuda':
        print(torch.cuda.get_device_name(0))
        print('Memory Usage:')
        print('Allocated:', round(torch.cuda.memory_allocated(0) / 1024 ** 3, 1), 'GB')
        print('Cached:   ', round(torch.cuda.memory_reserved(0) / 1024 ** 3, 1), 'GB')
    return predictions, sentiments


if __name__ == '__main__':
    df = pd.read_csv("./data/all_newspaper_title.csv")
    # print(df['headline'])
    # single_detection(news_df.date[i], api_key="15c5418e83130ba091ea4d07875a7517")
    sentiments = []
    headlines = []
    df[ df['language']=='bangla']

    for index,language in enumerate(df['language']):
        if language == 'bangla':
            headline = TRANSLATOR.translate(text=df.loc[index]['headline'])
            headlines.append(headline)
            # sentiment = get_sentiment(headline)
            # print(sentiment)
        else:
            headlines.append(df.loc[index]['headline'])

    _ , sentiments = get_sentiment(raw_inputs=headlines)
    # print(sentiments)
    df['headline'] = headlines
    df['sentiment'] = sentiments

    print(df)
    df.to_csv("./data/sentiment_news.csv", index=False)
            # print(df.loc[index]['headline'])

    # for row in range(df.shape[0]):
    #     if df[row]['language'] == 'bangla':
    #         headline =  GoogleTranslator(source='auto', target='de').translate(text=df[row]['headline'])
    #         print(headline)

    # sentiments = get_sentiment(sample_raw_inputs)
    # for sentence,sentiment in zip(sample_raw_inputs,sentiments):
    #     print(f"{sentence}:{sentiment}")
    # print(get_sentiment(sample_raw_inputs))

