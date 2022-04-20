from transformers import pipeline
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSequenceClassification, AutoModel
import pandas as pd
import datetime

# 0 - negative, 1- neutral, 2-positive

def getLabels(df):
    """ Use Cardiff NLP model on Hugging Face to return label

    :parameter df: dataframe 
    :return: none, will save the result in a txt file
    """
    model_name = "cardiffnlp/twitter-roberta-base-sentiment"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    classifier = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)
    tweet = df['translated_text'].tolist()
    print(f"start: {datetime.datetime.now()}")
    res = classifier(tweet)
    print(f"end: {datetime.datetime.now()}")
    f = open('cardiff_result.txt','w')
    for result in res:
        f.write(f'{result}\n')

if __name__ == "__main__":
    df = pd.read_csv('../data_cleaning/location_user.csv')
    getLabels(df)
