import json
import stanza
import pandas as pd

# stanza.download('en') # download English model
# 0 - negative, 1- neutral, 2-positive

nlp = stanza.Pipeline(lang='en', processors='tokenize,sentiment')

df = pd.read_csv('../data_cleaning/clean_data.csv')
tweets = df['tweetId'.'clean_tweet'][0:5].tolist()
print(len(tweets))

f=open('stanzaResult.txt','w')


for index, tweet in enumerate(tweets): 
    doc = nlp(tweet)
    for i, sentence in enumerate(doc.sentences):
        data = {'label': sentence.sentiment}
        f.write(json.dumps(data)+'\n')





