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