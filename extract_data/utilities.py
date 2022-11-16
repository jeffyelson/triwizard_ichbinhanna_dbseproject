import pandas as pd
from datetime import datetime
import os


def get_data(client, query, tweet_fields, user_fields, start_time, end_time):
    tweet_list = []
    user_list = []
    retweet_list = []

    max_results = 500
    expansions = ['author_id', 'referenced_tweets.id']
    next_token = None

    # Get the first set of results
    try:
        response = get_response(client, query, start_time, end_time, max_results, tweet_fields, user_fields, expansions,
                                next_token)
    except Exception as e:
        print(e)
        return None

    # Extract tweets and users from the response and append to the final list
    output = extract_data(response, tweet_fields, user_fields)

    if output is None:
        return None
    else:
        tweet_list += output[0]
        user_list += output[1]
        retweet_list += output[2]

    # Recursively search for next set of tweets based on the query
    while True:
        try:
            next_token = response.meta["next_token"]
        except KeyError:
            print("No more tweets left")
            break
        except Exception as e:
            print(e)
            print("Something went wrong. Please try again")
            break

        # Get the next set of results
        try:
            response = get_response(client, query, start_time, end_time, max_results, tweet_fields, user_fields,
                                    expansions, next_token)
        except Exception as e:
            print(e)
            break

        # Extract tweets from the response and append to the final list
        output = extract_data(response, tweet_fields, user_fields)

        if output is None:
            return None
        else:
            tweet_list += output[0]
            user_list += output[1]
            retweet_list += output[2]

    print("Total tweets extracted - " + str(len(tweet_list)))
    print("Total users extracted - " + str(len(user_list)))
    print("Total retweets extracted - " + str(len(retweet_list)))

    return save_output(tweet_list, tweet_fields, "tweet_output"), save_output(user_list, user_fields, "user_output"), \
           save_output(retweet_list, tweet_fields, "retweet_output")


def extract_data(response, tweet_fields, user_fields):
    tweets = response.data

    tweet_list = []
    user_list = []
    retweet_list = []

    if tweets is not None:
        for tweet in tweets:
            tweet_list.append(get_object_as_list(tweet, tweet_fields))
        print(str(len(tweets)) + " tweets extracted")
    else:
        print("No results found for the query")
        return None

    try:
        users = response.includes["users"]
        if users is not None:
            for user in users:
                user_list.append(get_object_as_list(user, user_fields))
            print(str(len(users)) + " users extracted")
        else:
            print("No users found")
    except KeyError:
        print("No users found")
    except Exception as e:
        print(e)

    try:
        retweets = response.includes["tweets"]
        if retweets is not None:
            for retweet in retweets:
                retweet_list.append(get_object_as_list(retweet, tweet_fields))
            print(str(len(retweet_list)) + " retweets extracted")
        else:
            print("No retweets found")
    except KeyError:
        print("No retweets found")
    except Exception as e:
        print(e)

    return tweet_list, user_list, retweet_list


def get_object_as_list(obj, obj_fields):
    obj_as_list = []

    for field in obj_fields:
        obj_as_list.append(obj[field])

    return obj_as_list


def save_output(obj_list, obj_fields, file_name):
    output_dir = "Extraction_Output"

    df = pd.DataFrame(obj_list, columns=obj_fields)

    try:
        os.mkdir(output_dir)
    except FileExistsError:
        print("Output path already present")

    df.to_csv(os.path.join(output_dir, file_name + datetime.now().strftime("_%Y%m%d_%H%M%S") + '.csv'), index=False)

    return df


def get_response(client, query, start_time, end_time, max_results, tweet_fields, user_fields, expansions, next_token):
    if next_token is None:
        return client.search_all_tweets(
            query=query,
            start_time=start_time,
            end_time=end_time,
            max_results=max_results,
            tweet_fields=tweet_fields,
            user_fields=user_fields,
            expansions=expansions
        )
    else:
        return client.search_all_tweets(
            query=query,
            start_time=start_time,
            end_time=end_time,
            max_results=max_results,
            tweet_fields=tweet_fields,
            user_fields=user_fields,
            expansions=expansions,
            next_token=next_token
        )


def get_query(hashtags):
    query = ""
    for i in range(len(hashtags)):
        if i == len(hashtags) - 1:
            query += hashtags[i]
        else:
            query += hashtags[i] + " OR "
    return query
