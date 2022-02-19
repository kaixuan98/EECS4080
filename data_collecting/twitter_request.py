from decouple import config
import tweepy
import pandas as pd
import time
import json
from os.path import exists

def queryBuilding(file):
    """ This function is used to build a query to send request to the Twitter API.

    :parameter file: the path to the file.
    :return: a query that can be used to send request to Twitter API using Tweetpy.
    """

    query = ''
    j=0
    f = open(file)
    data = json.load(f)
    for i in data['keywords']:
        if  j != len(data['keywords']) - 1 : 
            query = query + i + " OR "
        else: 
            query = query + i + " "
        j = j + 1  
    if data['withRT']: 
        query = "(" + query + "-RT) -is:retweet "
    if data['lang']: 
        query = query + f'lang:{data["lang"]}' 
    f.close()
    return query


def requestData(client, query, columns, tweetFields,expansions, max_results=100, limit = 20000):
    """ Used to request tweets from Twitter. This function will only search for the recent tweets (up to 7 days). *Full search are not allow due to the restricted access to the AP.*

    :parameter client: the client produced from tweepy with Twitter Bearer code
    :parameter query: used to search tweets
    :parameter columns: used to build the header of the csv file
    :parameter tweetFields: fields that need for each tweets
    :parameter expansions: expansions for each tweet
    :parameter max_results: max result returned per request [10-100]
    :parameter limit: max number of tweet returned *(Beware of the cap limit)*
    :return: None, but will be saving a csv file to the current directory
    """
    data = []
    for tweet in tweepy.Paginator(client.search_recent_tweets, query, tweet_fields=tweetFields, expansions=expansions, max_results=max_results).flatten(limit=limit):
        data.append([tweet.id, tweet.author_id, tweet.text, tweet.lang, tweet.created_at])
    df = pd.DataFrame(data, columns=columns)
    if exists('raw_data.csv'):
        with open('raw_data.csv', 'r') as f:
            header_list = f.readline().strip().split(",")
        if header_list.sort() == columns.sort(): 
            df.to_csv('raw_data.csv', index=False , header=False, mode='a')
        else: 
            df.to_csv('raw_data.csv', index=False)
    else:
        df.to_csv('raw_data.csv', index=False)



if __name__ == "__main__":
    api_key = config('API_KEY')
    api_key_secret = config('API_KEY_SECRET')
    access_token = config('ACCESS_TOKEN')
    access_token_secret = config('ACCESS_TOKEN_SECRET')
    bearer_token = config('BEARER_TOKEN')

    # authenticate
    client = tweepy.Client(bearer_token=bearer_token)

    # query = queryBuilding('../input/inputfile.json')
    query = '(climatechange OR ecofriendly OR sustainable OR zerowaste OR environment OR climateaction OR savetheplanet OR globalwarming -RT) -is:retweet lang:en'
    columns = ['tweetId', 'author_id', 'tweet', 'lang', 'created_at']
    tweet_fields = ['lang', 'created_at']
    expansions = ['author_id']
    # user_fields = ["name", "username", "location"]
    requestData(client, query ,columns, tweet_fields, expansions,  50, 50) 
