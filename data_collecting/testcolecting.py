from decouple import config
import tweepy
import pandas as pd
import time
import json
from os.path import exists
import datetime



if __name__ == "__main__":
    api_key = config('API_KEY')
    api_key_secret = config('API_KEY_SECRET')
    access_token = config('ACCESS_TOKEN')
    access_token_secret = config('ACCESS_TOKEN_SECRET')
    bearer_token = config('BEARER_TOKEN')

    # authenticate
    client = tweepy.Client(bearer_token=bearer_token)

    query = '(climatechange OR ecofriendly OR sustainable OR zerowaste OR environment OR climateaction OR savetheplanet OR globalwarming -RT) -is:retweet lang:en'
    columns = ['tweetId', 'author_id', 'tweet', 'lang', 'created_at']
    tweetFields = ['lang', 'created_at']
    expansions = ['author_id']
    curr_next_token = ''


    tweets = client.search_recent_tweets(query=query, tweet_fields=tweetFields, start_time='2019-10-12T07:20:50.52Z', expansions=expansions, max_results=10)
