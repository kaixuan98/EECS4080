from decouple import config
import tweepy
import pandas as pd
import time

api_key = config('API_KEY')
api_key_secret = config('API_KEY_SECRET')
access_token = config('ACCESS_TOKEN')
access_token_secret = config('ACCESS_TOKEN_SECRET')
bearer_token = config('BEARER_TOKEN')



# historical search 
client = tweepy.Client(bearer_token=bearer_token)


# query = '(#climatechange OR ecofriendly OR #sustainable OR #zerowaste OR #environment OR #climateaction OR #savetheplanet OR #globalwarming -RT) -is:retweet lang:en'
query = '(climatechange OR ecofriendly OR sustainable OR zerowaste OR environment OR climateaction OR savetheplanet OR globalwarming -RT) -is:retweet lang:en'

columns = ['tweetId', 'author_id', 'tweet', 'lang', 'created_at']
data = []

for tweet in tweepy.Paginator(client.search_recent_tweets, query, tweet_fields=['lang', 'created_at'], expansions=['author_id'], max_results=100).flatten(limit=10000):
    data.append([tweet.id, tweet.author_id, tweet.text, tweet.lang, tweet.created_at])

df = pd.DataFrame(data, columns=columns)

df.to_csv('raw_data.csv', index=False)


# streaming data
# class Linstener(tweepy.Stream):

#     tweets = []
#     limit = 150

#     def on_status(self, status):
#         self.tweets.append(status)
#         # print(status.user.screen_name + ": " + status.text)

#         if len(self.tweets) == self.limit:
#             self.disconnect()

# if __name__ == "__main__": 
#     # authentication
#     auth = tweepy.OAuthHandler(api_key, api_key_secret)
#     auth.set_access_token(access_token, access_token_secret)
#     api = tweepy.API(auth)

#     # create a listener to stream tweets 
#     stream_tweet = Linstener(api_key, api_key_secret, access_token, access_token_secret)
#     keywords = ['climatechange' , 'ecofriendly' , 'sustainable','climateaction', 'savetheplanet' , '-is:retweet']
#     columns = ['tweet_id' ,'user_id','user' , 'tweet' , 'lang' ]
#     data = []

#     # filter stream with keywords
#     stream_tweet.filter(track=keywords)
#     for tweet in stream_tweet.tweets:
#         print(tweet)
#         if not tweet.truncated:
#             data.append([tweet.id, tweet.user.id ,tweet.user.screen_name, tweet.text, tweet.lang])
#         else:
#             data.append([tweet.id, tweet.user.id ,tweet.user.screen_name, tweet.extended_tweet['full_text'], tweet.lang])
#     df = pd.DataFrame(data, columns=columns)
#     print(df)

#     df.to_csv('raw_data.csv', index=False)