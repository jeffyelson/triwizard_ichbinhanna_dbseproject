import tweepy
from dotenv import load_dotenv
import os
import params
import utilities
import pandas as pd

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
    bearer_token=bearer_token
)

expansions = params.EXPANSIONS

tweet_fields = params.TWEET_FIELDS
tweet_subfields = params.TWEET_SUBFIELDS
user_fields = params.USER_FIELDS
user_subfields = params.USER_SUBFIELDS

start_time = "2021-06-01T00:00:00.000Z"
end_time = "2022-11-01T00:00:00.000Z"

df_input = pd.read_csv("twitter_data.csv")
query_list = utilities.get_query(params.HASHTAGS, "from", df_input["author_id"].unique())

tweet_list = []
user_list = []
api_calls = 0

if query_list is None or len(query_list) == 0:
    print("No query generated")
else:
    i = 0
    for query in query_list:
        output = utilities.get_data(client, query, expansions, tweet_fields, tweet_subfields, user_fields,
                                    user_subfields, start_time, end_time, api_calls)
        if output is not None:
            tweet_list += output[0]
            user_list += output[1]
            api_calls = output[2]

        i += 1
        print("Query: " + str(i) + "; Tweets extracted so far: " + str(
            len(tweet_list)) + "; Users extracted so far: " + str(len(user_list)))

df_tweets = utilities.save_output(tweet_list, tweet_fields, tweet_subfields, "extracted_tweets")
df_users = utilities.save_output(user_list, user_fields, user_subfields, "extracted_users")
