from transformers import pipeline
import torch 
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSequenceClassification, AutoModel
import pandas as pd

# 0 - negative, 1- neutral, 2-positive


model_name = "cardiffnlp/twitter-roberta-base-sentiment"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

classifier = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)

df = pd.read_csv('../data_cleaning/clean_data.csv')
tweet = df['clean_tweet'][:10].tolist()

res = classifier(tweet)

f=open('cardiffResult.txt','w')

for result in res:
    f.write(f'{result}\n')
