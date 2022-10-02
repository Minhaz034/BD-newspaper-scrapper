import pandas as pd
from transformers import pipeline
from transformers import AutoTokenizer
from transformers import AutoModel
from transformers import AutoModelForSequenceClassification
import torch
import time

sample_raw_inputs=["Agricultural machinery is beyond the reach of farmers",
            "Alamgir, who wanted to teach in exchange for rice, got a job in ACI Logistics Limited",
            "Job opportunities in ACI Group with attractive salary"]
model_path ="./bertweet-base-sentiment-analysis"

def get_sentiment(raw_inputs, model_path ="./bertweet-base-sentiment-analysis" ):
    print(f"{torch.cuda.device_count()} GPU available")
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForSequenceClassification.from_pretrained(model_path).to(device)
    encoded_inputs = tokenizer(raw_inputs, padding=True, truncation=True, return_tensors="pt").to(device)
    model_outputs = model(**encoded_inputs)
    predictions = torch.nn.functional.softmax(model_outputs['logits'], dim=-1)

    if device.type == 'cuda':
        print(torch.cuda.get_device_name(0))
        print('Memory Usage:')
        print('Allocated:', round(torch.cuda.memory_allocated(0) / 1024 ** 3, 1), 'GB')
        print('Cached:   ', round(torch.cuda.memory_reserved(0) / 1024 ** 3, 1), 'GB')
    return predictions



# print(f"{torch.cuda.device_count()} GPU available")
# device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
# model_path = "./bertweet-base-sentiment-analysis"
# tokenizer = AutoTokenizer.from_pretrained(model_path)
# model = AutoModelForSequenceClassification.from_pretrained(model_path).to(device)
# encoded_inputs = tokenizer(raw_inputs, padding=True, truncation=True, return_tensors="pt").to(device)
# model_outputs = model(**encoded_inputs)
# predictions = torch.nn.functional.softmax(model_outputs['logits'], dim=-1)
# print(model.config.id2label)
# print(predictions)

if __name__ == '__main__':
    print(get_sentiment(sample_raw_inputs))

