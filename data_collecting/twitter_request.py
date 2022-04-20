from decouple import config
from sqlalchemy import null
import tweepy
import pandas as pd
import time
import json
from os.path import exists
import datetime


def requestData(client, query, columns, tweetFields, expansions, start_time, end_time, max_results=100, limit = 20000):
    """ Used to request tweets from Twitter. This function will only search for the recent tweets (up to 7 days) with paginate. *Full search are not allow due to the restricted access to the AP.*

    :parameter client: the client produced from tweepy with Twitter Bearer code
    :parameter query: used to search tweets
    :parameter columns: used to build the header of the csv file
    :parameter tweetFields: fields that need for each tweets
    :parameter expansions: expansions for each tweet
    :parameter max_results: max result returned per request [10-100]
    :parameter limit: max number of tweet returned *(Beware of the cap limit)*
    :return:  dataframe
    """
    data = [] 
    response = tweepy.Paginator(client.search_recent_tweets, query, tweet_fields=tweetFields, expansions=expansions, start_time=start_time, end_time=end_time, max_results=max_results).flatten(limit=limit)
    for tweet in response:
        data.append([tweet.id, tweet.author_id, tweet.text, tweet.lang, tweet.created_at])
    df = pd.DataFrame(data, columns=columns)
    return df
    # if exists('raw_data.csv'):
    #     with open('raw_data.csv', 'r') as f:
    #         header_list = f.readline().strip().split(",")
    #     if header_list.sort() == columns.sort(): 
    #         df.to_csv('raw_data.csv', index=False , header=False, mode='a')
    #     else: 
    #         df.to_csv('raw_data.csv', index=False)
    # else:
    #     df.to_csv('raw_data.csv', index=False)


def TweetsReq(client, query, columns, tweetFields, expansions, since_id,next_token, max_results=100): 
    """  This function is can be used to pull the newest data, historical data only up to 7 days.

    :parameter client: the client to connect with Twitter API
    :parameter query: query built using queryBuilding function
    :parameter columns: column names that need for the dataframe
    :parameter tweetFields: an array of fields that needed from TwitterAPI
    :parameter expansions: an array of expansions that needed from TwitterAPI
    :parameter since_id: the latest tweetId in your database
    :parameter next_token: a token for pagination 
    :parameter max_result: the max result is 100 and min of this value is 10
    :return: a dictionary consists of since_id, next_token and current number of tweets 
    """
    data=[]
    tweets_count = 0
    nextToken = next_token
    sinceId = since_id

    if not nextToken and sinceId:  #pull historical data 
        tweets = client.search_recent_tweets(query=query, tweet_fields=tweetFields, expansions=expansions, since_id = sinceId, max_results=max_results)
    elif nextToken and not sinceId: #pull newest data
        tweets = client.search_recent_tweets(query=query, tweet_fields=tweetFields, expansions=expansions, next_token=nextToken, max_results=max_results)
    else:  # starting to pull data
        tweets = client.search_recent_tweets(query=query, tweet_fields=tweetFields, expansions=expansions, max_results=max_results)

    for tweet in tweets.data:
        data.append([tweet.id, tweet.author_id, tweet.text, tweet.lang, tweet.created_at])

    df = pd.DataFrame(data, columns=columns)
    nextToken = tweets.meta.get('next_token')
    sinceId = tweets.meta.get('newest_id')
    tweets_count = tweets.meta.get('result_count')

    if exists('raw_data_all_lang.csv'):
        with open('raw_data_all_lang.csv', 'r') as f:
            header_list = f.readline().strip().split(",")
        if header_list.sort() == columns.sort(): 
            df.to_csv('raw_data_all_lang.csv', index=False , header=False, mode='a')
        else: 
            df.to_csv('raw_data_all_lang.csv', index=False)
    else:
        df.to_csv('raw_data_all_lang.csv', index=False)

    return {"since_id": sinceId, "next_token": nextToken , 'result_count': tweets_count, }


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def requestUserLocation(client, batches, tweetId_batches, userFields=['id', 'location']):
    """ The above method will take in a list of ``user_id`` and perform user lookup based on the inputed userFields<https://developer.twitter.com/en/docs/twitter-api/data-dictionary/object-model/user>`_ . 

    :parameter user_id_list: a list of user's id
    :parameter userFields: a list of user fields, by default will be id and location
    :return: a list of dictionary with user id and location
    """
    loc_list =[]
    req_calls = 0
    for i, batch in enumerate(batches):
        if req_calls >= 20000: 
            req_calls = 0 
            time.sleep(1020)
            users = client.get_users(ids=batch, user_fields=userFields)
            req_calls = req_calls + 100
            print(f"{datetime.datetime.now()}-> batch:{i} , user_retrived:{req_calls}")
            for j, user in enumerate(users.data):
                loc_list.append({'author_id': user.id , 'user_loc': user.location, 'tweetId': tweetId_batches[i][j]})
        else: 
            users = client.get_users(ids=batch, user_fields=userFields)
            req_calls = req_calls + 100
            print(f"{datetime.datetime.now()}-> batch:{i} , user_retrived:{req_calls}")
            for j, user in enumerate(users.data):
                if user != None: 
                    loc_list.append({'author_id': user.id , 'user_loc': user.location , 'tweetId': tweetId_batches[i][j]})
        if exists('user_log.txt'):
                with open('log.txt', 'a') as f:
                    (f"{datetime.datetime.now()}-> batch:{i} , user_retrived:{req_calls}")
        else:
            with open('user_log.txt', 'w') as f:
                (f"{datetime.datetime.now()}-> batch:{i} , user_retrived:{req_calls}")
    return loc_list




if __name__ == "__main__":
    api_key = config('API_KEY')
    api_key_secret = config('API_KEY_SECRET')
    access_token = config('ACCESS_TOKEN')
    access_token_secret = config('ACCESS_TOKEN_SECRET')
    bearer_token = config('BEARER_TOKEN')

    # authenticate
    client = tweepy.Client(bearer_token=bearer_token)

    # Step 1: Get Json file and build query 
    # query = queryBuilding('../input/inputfile.json')
    # query = '(Ukraine OR Russia OR war OR invasion OR Nato OR Putin OR Zelensky OR crisis OR Western OR Europe OR Ukrainians OR Kyiv) -RT -is:retweet'
    # query2 = '(Україна OR Росія OR війна OR вторгнення OR Nato OR Путін OR Зеленський OR криза OR Захід OR Європа OR українці OR Київ) -RT -is:retweet lang:uk'

    # Step 2: Request data with all the parameters needed
    columns = ['tweetId', 'author_id', 'tweet', 'lang', 'created_at']
    tweet_fields = ['lang', 'created_at']
    expansions = ['author_id']
    curr_next_token = ''

    # Step 2ai: Request with a scheduler(request for the past 7 days- historical data)
    # this steps need keep track to next token 
    # next_token='b26v89c19zqg8o3fpytmp907cr5jioq6lpvbvmnax05tp'
    # since_id=''
    # previous_count = 443669
    # tweet_count = 443669
    # start_time = '2022-04-08T00:00:00.00Z'
    # tokens = TweetsReq(client, query ,columns, tweetFields=tweet_fields, expansions=expansions, since_id=since_id,next_token=next_token, max_results=100) # first time getting data
    # next_token= tokens.get('next_token')
    # tweet_count = tweet_count + tokens.get('result_count')
    # page = 4437
    # while next_token or tweet_count < 1000000:
    #     if (tweet_count-previous_count) > 40000: 
    #         time.sleep(900)
    #         previous_count = tweet_count
    #     else:
    #         print("Requesting ...")
    #         tokens = TweetsReq(client, query ,columns, tweetFields=tweet_fields, expansions=expansions,since_id=since_id, next_token=next_token, max_results=100)
    #         page = page + 1 
    #         print(f"{datetime.datetime.now()}: page {page}")
    #         next_token= tokens.get('next_token')
    #         tweet_count = tweet_count + tokens.get('result_count')
    #         if exists('log.txt'):
    #             with open('log.txt', 'a') as f:
    #                 f.write(f"{datetime.datetime.now()}-> page:{page}, tweet count:{tweet_count}, next_token:{next_token}\n")
    #         else:
    #             with open('log.txt', 'w') as f:
    #                 f.write(f"{datetime.datetime.now()}-> page:{page}, tweet count:{tweet_count}, next_token:{next_token}\n")

    # Step 2aii: Request with polling(if I need new data after my historical data)
    # newest_id=''
    # tokens = TweetsReq(client, query ,columns, tweet_fields=tweet_fields, expansions=expansions, since_id=newest_id, max_limit=50) 
    # newest_id = tokens.get('newest_id')

    # Step 2b: Request with paginator
    # startTime = '2022-03-11T00:00:00.00Z'
    # endTime = '2022-03-13T00:00:00.00Z'
    # requestData(client, query ,columns, tweet_fields, expansions, start_time=startTime, end_time=endTime , max_results=50, limit=50) 

    # Step 3: Cleaning data - in other file

    # Step 4: Request for user profile(location)
    # df = pd.read_csv('raw_data_all_lang.csv')
    # df = df.dropna()
    # df = df.drop_duplicates()
    # batches = list(chunks(list(df['author_id']), 100))
    # tweetID_batches = list(chunks(list(df['tweetId']), 100))
    # loc_list = requestUserLocation(client, batches , tweetID_batches)
    # location_df = pd.DataFrame(loc_list)  
    # location_df.to_csv('location.csv')   

    tweet_df = pd.read_csv('raw_data_all_lang.csv', dtype={'tweetId': str, 'author_id': str})
    tweet_df['author_id'] = tweet_df['author_id'].astype(str)
    tweet_df = tweet_df.dropna()
    tweet_df = tweet_df.drop_duplicates()
    batches = list(chunks(list(tweet_df['author_id']), 100))
    tweetID_batches = list(chunks(list(tweet_df['tweetId']), 100))
    loc_list = requestUserLocation(client, batches , tweetID_batches)
    location_df = pd.DataFrame(loc_list)  
    full_df = pd.merge(tweet_df, location_df , on="tweetId")
    full_df.to_csv('raw_data_with_loc.csv', index=False)

    # # Step 5: After the request, merge it with the clean df
    # full_df = pd.merge(df, location_df , on="tweetId")
    # full_df.to_csv('raw_data_w_location.csv')

    # print(full_df.head())
    # print(len(full_df))


