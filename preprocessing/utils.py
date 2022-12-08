import ast
import pandas as pd
import numpy as np
import time
from datetime import datetime
from deep_translator import GoogleTranslator
import params
from geopy.geocoders import Nominatim


def preprocess_data(df_tweets, df_users):
    #     Add is_retweet column to tweet data for use in user data
    print("Adding a retweet flag to the tweets dataset")
    try:
        df_tweets["is_retweet"] = df_tweets["referenced_tweets"].apply(lambda x: is_retweet(x))
    except KeyError:
        print('referenced_tweets column not present in df_tweets')

    #     Initialize the regex for text processing
    url_pattern = params.URL_PATTERN
    mentions_pattern = params.MENTIONS_PATTERN
    special_characters_pattern = params.SPECIAL_CHARS_PATTERN
    multiple_whitespaces_pattern = params.MULTIPLE_SPACES_PATTERN

    #     Process the description
    if not ('description' in df_users.columns and 'entities' in df_users.columns):
        print('description and/or entities columns not present in df_users')
        return None

    print("Performing text processing on user bios")
    df_users['updated_bio'] = df_users['description'].apply(lambda x: text_process(x,
                                                                                   url_pattern,
                                                                                   mentions_pattern,
                                                                                   special_characters_pattern,
                                                                                   multiple_whitespaces_pattern))
    #     Extract urls, mentions and hashtags from descriptions
    print("Extracting urls, mentions and hashtags from entities")
    df_users['extracted_urls'] = df_users['entities'].apply(lambda x: extract_urls_from_desc(x))
    df_users['extracted_mentions'] = df_users['entities'].apply(lambda x: extract_mentions_from_desc(x))
    df_users['extracted_hashtags'] = df_users['entities'].apply(lambda x: extract_hashtags_from_desc(x))

    #     Update user tweet and retweet from dataset stats
    print("Extracting user stats from tweets dataset")
    df_users = update_user_tweet_retweet_stats(df_users, df_tweets, tweet_type='og')
    df_users = update_user_tweet_retweet_stats(df_users, df_tweets, tweet_type='re')

    print("Performing bio translations")
    df_users = translate_text(df_users, params.USER_DATA_COLUMNS[3], params.USER_DATA_COLUMNS[4])

    print("Updating locations")
    df_users = get_locations(df_users)

    df_users = df_users[params.USER_DATA_COLUMNS]

    #     Processing the tweet data
    if not ('text' in df_tweets.columns and 'entities' in df_tweets.columns):
        print('text and/or entities columns not present in df_tweets')
        return None

    print("Performing text processing on tweet data")

    df_tweets['updated_text'] = df_tweets['text'].apply(lambda x: text_process(x,
                                                                               url_pattern,
                                                                               mentions_pattern,
                                                                               special_characters_pattern,
                                                                               multiple_whitespaces_pattern))
    #     Extract urls, mentions and hashtags from descriptions
    print("Extracting urls, mentions and hashtags from entities")
    df_tweets['extracted_urls'] = df_tweets['entities'].apply(lambda x: extract_urls_from_tweet(x))
    df_tweets['extracted_mentions'] = df_tweets['entities'].apply(lambda x: extract_mentions_from_tweet(x))
    df_tweets['extracted_hashtags'] = df_tweets['entities'].apply(lambda x: extract_hashtags_from_tweet(x))

    #     User-tweets relation
    df_user_tweet_map = df_tweets[params.TWEET_USER_MAP_COLUMNS]

    df_tweets = df_tweets[df_tweets["is_retweet"] == False]
    df_tweets = df_tweets[params.TWEET_DATA_COLUMNS]

    return df_tweets, df_users, df_user_tweet_map


def text_process(bio, url_pattern, mentions_pattern, special_characters_pattern, multiple_whitespaces_pattern):
    if bio is np.nan:
        return np.nan

    # Replace urls and mentiones with spaces
    bio = url_pattern.sub(" ", bio)
    bio = mentions_pattern.sub(" ", bio)

    # Replace punctuation and emojis
    bio = special_characters_pattern.sub(" ", bio)

    # Convert to lower case
    bio = bio.lower()

    # Remove additional spaces
    bio = multiple_whitespaces_pattern.sub(" ", bio).strip()

    if len(bio) == 0:
        return np.nan

    return bio


def extract_urls_from_desc(entities):
    url_list = []

    if entities is np.nan:
        return np.nan

    temp = ast.literal_eval(entities)

    try:
        urls = temp["url"]["urls"]
        for url in urls:
            url_list.append(url["expanded_url"])
    except KeyError:
        pass

    try:
        urls = temp["description"]["urls"]
        for url in urls:
            url_list.append(url["expanded_url"])
    except KeyError:
        pass

    if len(url_list) == 0:
        return np.nan

    return url_list


def extract_urls_from_tweet(entities):
    url_list = []

    if entities is np.nan:
        return np.nan

    temp = ast.literal_eval(entities)

    try:
        urls = temp["urls"]
        for url in urls:
            url_list.append(url["expanded_url"])
    except KeyError:
        pass

    if len(url_list) == 0:
        return np.nan

    return url_list


def extract_mentions_from_desc(entities):
    mention_list = []

    if entities is np.nan:
        return np.nan

    temp = ast.literal_eval(entities)

    try:
        mentions = temp["description"]["mentions"]
        for mention in mentions:
            mention_list.append(mention["id"])
    except KeyError:
        pass

    if len(mention_list) == 0:
        return np.nan

    return mention_list


def extract_mentions_from_tweet(entities):
    mention_list = []

    if entities is np.nan:
        return np.nan

    temp = ast.literal_eval(entities)

    try:
        mentions = temp["mentions"]
        for mention in mentions:
            mention_list.append(mention["id"])
    except KeyError:
        pass

    if len(mention_list) == 0:
        return np.nan

    return mention_list


def extract_hashtags_from_desc(entities):
    hashtag_list = []

    if entities is np.nan:
        return np.nan

    temp = ast.literal_eval(entities)

    try:
        hashtags = temp["description"]["hashtags"]
        for hashtag in hashtags:
            hashtag_list.append(hashtag["tag"])
    except KeyError:
        pass

    if len(hashtag_list) == 0:
        return np.nan

    return hashtag_list


def extract_hashtags_from_tweet(entities):
    hashtag_list = []

    if entities is np.nan:
        return np.nan

    temp = ast.literal_eval(entities)

    try:
        hashtags = temp["hashtags"]
        for hashtag in hashtags:
            hashtag_list.append(hashtag["tag"])
    except KeyError:
        pass

    if len(hashtag_list) == 0:
        return np.nan

    return hashtag_list


def is_retweet(reference):
    if reference is np.nan:
        return False

    if "retweet" in reference:
        return True

    return False


def update_user_tweet_retweet_stats(df_users, df_tweets, tweet_type="og"):
    #     og for original tweets, and re for retweets
    if tweet_type == "og":
        tflag = False
        column_name = "tweets_in_dataset"
    elif tweet_type == "re":
        tflag = True
        column_name = "retweets_in_dataset"
    else:
        print("Invalid tweet flag - " + str(tweet_type))
        return None

    temp = pd.DataFrame(df_tweets[df_tweets['is_retweet'] == tflag].groupby('author_id').size()).reset_index()
    temp.rename(columns={'author_id': 'id'}, inplace=True)
    df_users = df_users.merge(temp, on='id', how='left')
    df_users[column_name] = df_users[0].fillna(0)
    df_users.drop(0, axis=1, inplace=True)
    df_users = df_users.astype({column_name: int})

    return df_users


def translate_text(df, input_column="text", output_column="translated_text", translator=None):
    if translator is None:
        translator = GoogleTranslator(source='auto', target='en')

    if input_column not in df.columns:
        print('Invalid input column name')
        return df

    text_list = list(df[input_column].fillna("__BLANK__"))
    translated_text_list = []

    batch_size = 1000

    for i in range(0, len(text_list), batch_size):
        time.sleep(1)
        if (i + batch_size) > len(text_list):
            temp = text_list[i:len(text_list)]
        else:
            temp = text_list[i:i + batch_size]
        start_time = datetime.now()
        translated_text_list += translator.translate_batch(temp)
        end_time = datetime.now()
        print("Translated " + str(len(temp)) + " texts in - " + str(end_time - start_time))

    df[output_column] = translated_text_list

    return df


# Updating locations
def get_proper_location(address, geolocator):
    try:
        geolocation = geolocator.geocode(address, exactly_one=True)
    except:
        return "Unknown", "Unknown", "Unknown"

    if geolocation is None:
        return "Unknown", "Unknown", "Unknown"

    try:
        temp = geolocator.reverse((geolocation.latitude, geolocation.longitude), language="en")
    except Exception as e:
        print(str(e) + " - " + str(address))
        return "Unknown", "Unknown", "Unknown"

    if temp is None:
        print("Nonetype - " + str(address))
        print(address)
        return "Unknown", "Unknown", "Unknown"

    temp = temp.raw['address']

    try:
        country = temp.get('country', 'Unknown')
        if country == 'Unknown':
            country = temp.get('country_code', 'Unknown')
    except:
        country = "Unknown"

    try:
        state = temp.get('state', 'Unknown')
    except:
        state = "Unknown"

    try:
        city = temp.get('city', 'Unknown')
    except:
        city = "Unknown"

    return city, state, country


def get_locations(df):
    if "location" not in df.columns:
        print("No location column present.")
        return df

    #     Get list of unique locations

    locations = df['location'].dropna().unique()

    print("Number of unique locations present - " + str(len(locations)))

    if len(locations) == 0:
        print("No locations to extract")
        return df

    print('Initialize the geolocator')
    geolocator = Nominatim(user_agent="geoapiExercises")

    locations_dict = {}

    print('Get proper locations')
    start_time = datetime.now()
    count = 0
    for loc in locations:
        count += 1
        print('|', end='')
        locations_dict[loc] = get_proper_location(loc, geolocator)
        if count % 500 == 0:
            print()
            print('Locations extracted so far - ' + str(count))
    print()
    end_time = datetime.now()
    print("Extracted " + str(len(locations)) + " locations in - " + str(end_time - start_time))

    df['location_city'], df['location_state'], df['location_country'] = zip(
        *df['location'].map(lambda x: get_data_from_dict(x, locations_dict)))

    return df


def get_data_from_dict(x, loc_dict):
    if str(x) == 'nan':
        return "Unknown", "Unknown", "Unknown"

    return loc_dict[x]
