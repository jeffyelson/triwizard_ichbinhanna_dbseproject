import tweepy
from dotenv import load_dotenv
import os
import params
import utilities

# Load and set keys
print(load_dotenv(".env"))
consumer_key = os.environ["API_KEY"]
consumer_secret = os.environ["API_KEY_SECRET"]
bearer_token = os.environ['BEARER_TOKEN']
access_token = os.environ["ACCESS_TOKEN"]
access_token_secret = os.environ["ACCESS_TOKEN_SECRET"]

# Variables needed for data extraction
client = tweepy.Client(
    consumer_key=consumer_key,
    consumer_secret=consumer_secret,
    bearer_token=bearer_token,
    wait_on_rate_limit=True
)

start_time = "2021-06-01T00:00:00.000Z"
end_time = "2021-06-14T00:00:00.000Z"

query = utilities.get_query(params.HASHTAGS)

output = utilities.get_data(client, query, params.TWEET_FIELDS, params.USER_FIELDS, start_time,
                            end_time)

if output is not None:
    df_tweet, df_user, df_retweet = output
