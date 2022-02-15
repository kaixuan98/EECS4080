import stanza
import pandas as pd

# stanza.download('en') # download English model
# 0 - negative, 1- neutral, 2-positive

nlp = stanza.Pipeline(lang='en', processors='tokenize,sentiment')

df = pd.read_csv('../data_cleaning/clean_data.csv')
tweets = df['clean_tweet'][:10].tolist()

f=open('stanzaResult.txt','w')

for tweet in tweets: 
    doc = nlp(tweet)
    for i, sentence in enumerate(doc.sentences):
        print(i, sentence.sentiment)
        f.write(f'label:{sentence.sentiment} \n')





