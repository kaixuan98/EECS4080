from transformers import pipeline
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSequenceClassification, AutoModel
import pandas as pd

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
    tweet = df['clean_tweet'].tolist()
    res = classifier(tweet)
    f = open('./ouput/cardiffResult_all.txt','w')
    for result in res:
        f.write(f'{result}\n')

if __name__ == "__main__":
    df = pd.read_csv('../data_cleaning/clean_testing_all_lang.csv')
    getLabels(df)
