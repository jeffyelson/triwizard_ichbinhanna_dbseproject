import pandas as pd
import numpy as np
import tweepy
import config
import csv
import snscrape.modules.twitter as sntwitter

#All required keys 
consumer_key = config.API_KEY
consumer_secret = config.API_KEY_SECRET
access_token = config.ACCESS_TOKEN
access_token_secret = config.ACCESS_TOKEN_SECRET
bearer_token = config.BEARER_TOKEN
print(consumer_key)

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

# You can authenticate as your app with just your bearer token
client = tweepy.Client(bearer_token=bearer_token)
client = tweepy.Client(
    consumer_key=consumer_key, consumer_secret=consumer_secret,
    access_token=access_token, access_token_secret=access_token_secret, 
    bearer_token=bearer_token
)

query = "(from:#IchBinHanna) until:2022-10-30 since:2021-07-01"
tweets = []
limit = 1000
for tweet in sntwitter.TwitterSearchScraper(query).get_items():
    if len(tweets) == limit:
        break
    else:
        tweets.append([tweet.id, tweet.date, tweet.username, tweet.content,
                       tweet.url])

tweet_data=[]
result=[]
for data in tweets:
  get_tweets = client.get_tweets(ids=data[0], tweet_fields=['context_annotations','created_at','geo'], expansions='author_id')
  tweet_data=[data[0], data[1], data[2], data[3],data[4]]
  for tweet1 in get_tweets.includes['users']:
    users = client.get_users(ids=tweet1.id, user_fields=['username','public_metrics','description', 'location', 'profile_image_url'])
    for user in users.data:
      result.append({'Tweet_id': tweet_data[0],
                     'Tweet_date':tweet_data[1],
                     'Author_id':tweet1.id,
                     'Username': user.username,
                     'Author_description': user.description,
                     'Author_location': user.location,
                     'Author_followers': user.public_metrics['followers_count'],
                     'Author_following_count': user.public_metrics['following_count'],
                     'Author_tweet_count': user.public_metrics['tweet_count'],
                     'Tweet_content': tweet_data[3],
                     'Tweet_URL': tweet_data[4],
                     'Author_image_URL': user.profile_image_url
                      })
df = pd.DataFrame(result)
df
df.to_csv('/content/drive/MyDrive/Colab Notebooks/DBSE Project/twitterdata.csv')