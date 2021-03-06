from decouple import config
from matplotlib.font_manager import json_dump
from sqlalchemy import null
import tweepy
import pandas as pd
import json
from os.path import exists
import numpy as np

# local function 
import os
import sys
module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)
from data_collecting.twitter_request import TweetsReq, requestData, requestUserLocation, chunks
from data_collecting.queryBuilding import queryBuilding, keywords_to_array, make_json


if __name__ == "__main__":
    api_key = config('API_KEY')
    api_key_secret = config('API_KEY_SECRET')
    access_token = config('ACCESS_TOKEN')
    access_token_secret = config('ACCESS_TOKEN_SECRET')
    bearer_token = config('BEARER_TOKEN')

    # Step 0: authenticate
    client = tweepy.Client(bearer_token=bearer_token)

    # Step 0: Request data with all the parameters needed
    columns = ['tweetId', 'author_id', 'tweet', 'lang', 'created_at']
    tweet_fields = ['lang', 'created_at']
    expansions = ['author_id']
    curr_next_token = ''

    # Step 1: query building
    f = open('../input/testingInput.json')
    inputFile = json.load(f)
    result=[]
    for topic in inputFile:
        # create a hashid with the topic nam)
        topicName = inputFile.get(topic)['topic']
        id = abs(hash(topicName)) % (10 ** 10)
        # # build query 
        keywords = inputFile.get(topic)['orKeywords'].split(";")
        orKeywords =[]
        for keyword in keywords:
            orKeywords.append(keywords_to_array(keyword))
        lang = inputFile.get(topic)['lang']
        exclude = keywords_to_array(inputFile.get(topic)['excludedKeyword'])
        withRT = inputFile.get(topic)['withRT']
        inputQuery = {"orKeywords": orKeywords , "withRT": withRT, "lang": lang, "exclude_keywords": exclude }
        query = queryBuilding(inputQuery)
        result.append({ "topicId": id , "topic": topicName, "query": query})
    f.close()

    
    # Step 2: Request tweets for each topic
    startTime = '2022-04-08T00:00:00.00Z'
    endTime = '2022-03-13T00:00:00.00Z'
    for topic in result:
        df = requestData(client, topic['query'], columns, tweet_fields, expansions, startTime, endTime, 100, 100) 
        # add topic id to the dataframe
        topicCol = [topic['topicId']] * len(df)
        topicCol = pd.DataFrame(topicCol , columns=['topic_id'])
        df = pd.concat([df, topicCol], axis=1)
        topicName = topic['topic'].replace(" ", '')
        saveFile = 'output/' + topicName + '.csv'
        if exists(saveFile):
            with open(saveFile, 'r') as f:
                header_list = f.readline().strip().split(",")
            if header_list.sort() == columns.sort(): 
                df.to_csv(saveFile, index=False , header=False, mode='a')
            else: 
                df.to_csv(saveFile, index=False)
        else:
            df.to_csv(saveFile, index=False)
    
    
    # # Step 3: Request users with chuncks
    for topic in result:
        topicName = topic['topic'].replace(" ", '')
        filename = 'output/' + topicName + '.csv'
        saveFile = 'output/' + topicName + '_withLoc.csv'
        tweet_df = pd.read_csv(filename)
        tweet_df = tweet_df.dropna()
        batches = list(chunks(list(tweet_df['author_id']), 100))
        tweetID_batches = list(chunks(list(tweet_df['tweetId']), 100))
        loc_list = requestUserLocation(client, batches , tweetID_batches)
        location_df = pd.DataFrame(loc_list)  
        full_df = pd.merge(tweet_df, location_df , on="tweetId")
        full_df.to_csv(saveFile)