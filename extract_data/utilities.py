import pandas as pd
from datetime import datetime
import os
import time
import tweepy


def get_data(client, query, expansions, tweet_fields, tweet_subfields, user_fields, user_subfields, start_time,
             end_time, api_calls):
    tweet_list = []
    user_list = []

    max_results = 500
    next_token = None

    # Get the first set of results
    response = get_response(client, query, start_time, end_time, max_results, tweet_fields, user_fields, expansions,
                            next_token)

    # Extract tweets and users from the response and append to the final list
    api_calls += 1
    output = extract_data(response, tweet_fields, tweet_subfields, user_fields, user_subfields)

    if output is None:
        return None
    else:
        tweet_list += output[0]
        user_list += output[1]

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
        for i in range(3):
            try:
                response = get_response(client, query, start_time, end_time, max_results, tweet_fields, user_fields,
                                        expansions,
                                        next_token)
            except Exception as e:
                print(e)
                if i >= 3:
                    response = None
                if e == "429 Too Many Requests":
                    time.sleep(5)
                    continue
                else:
                    print("Retrying")
                    continue
            else:
                break

        # Extract tweets from the response and append to the final list
        api_calls += 1
        output = extract_data(response, tweet_fields, tweet_subfields, user_fields, user_subfields)

        if output is None:
            break
        else:
            print("Api call - " + str(api_calls) + "; Tweets extracted - " + str(
                len(output[0])) + "; Users extracted - " + str(len(output[1])))
            tweet_list += output[0]
            user_list += output[1]

    return tweet_list, user_list, api_calls


def get_response(client, query, start_time, end_time, max_results, tweet_fields, user_fields, expansions, next_token):
    if next_token is None:
        params = dict(
            query=query,
            start_time=start_time,
            end_time=end_time,
            max_results=max_results,
            tweet_fields=tweet_fields,
            user_fields=user_fields,
            expansions=expansions
        )
    else:
        params = dict(
            query=query,
            start_time=start_time,
            end_time=end_time,
            max_results=max_results,
            tweet_fields=tweet_fields,
            user_fields=user_fields,
            expansions=expansions,
            next_token=next_token
        )

    response = None
    for i in range(5):
        try:
            time.sleep(1)
            response = client.search_all_tweets(**params)
        except tweepy.BadRequest as e:
            print(e)
            print("Retrying")
        except tweepy.TooManyRequests as e:
            print(e)
            print("Sleep for 300 sec")
            time.sleep(300)
            print("Retrying")
        except Exception as e:
            print(e)
            print("Retrying")
        else:
            return response

    return response


def extract_data(response, tweet_fields, tweet_subfields, user_fields, user_subfields):
    if response is None:
        return None

    tweets = response.data

    tweet_list = []
    user_list = []

    if tweets is not None:
        for tweet in tweets:
            tweet_list.append(get_object_as_list(tweet, tweet_fields, tweet_subfields))
    else:
        print("No results found for the query")
        return None

    try:
        users = response.includes["users"]
        if users is not None:
            for user in users:
                user_list.append(get_object_as_list(user, user_fields, user_subfields))
        else:
            print("No users found")
    except KeyError:
        print("No users found")
    except Exception as e:
        print(e)

    try:
        ref_tweets = response.includes["tweets"]
        if ref_tweets is not None:
            for ref_tweet in ref_tweets:
                tweet_list.append(get_object_as_list(ref_tweet, tweet_fields, tweet_subfields))
        else:
            print("No referenced tweets found")
    except KeyError:
        print("No referenced tweets found")
    except Exception as e:
        print(e)

    return tweet_list, user_list


def get_object_as_list(obj, obj_fields, obj_subfields):
    obj_as_list = []

    for field in obj_fields:
        if field in obj_subfields.keys():
            for subfield in obj_subfields[field]:
                obj_as_list.append(obj[field][subfield])
        else:
            obj_as_list.append(obj[field])

    return obj_as_list


def save_output(obj_list, obj_fields, obj_subfields, file_name):
    output_dir = "Extraction_Output"

    cols = []
    for field in obj_fields:
        if field in obj_subfields.keys():
            for subfield in obj_subfields[field]:
                cols.append(field + "_" + subfield)
        else:
            cols.append(field)

    df = pd.DataFrame(obj_list, columns=cols)

    try:
        os.mkdir(output_dir)
    except FileExistsError:
        print("Output path already present")

    df.to_csv(os.path.join(output_dir, file_name + datetime.now().strftime("_%Y%m%d_%H%M%S") + '.csv'), index=False)

    return df


def get_query(hashtags, query, data):
    query_list = []

    query_part1 = "("

    for i in range(len(hashtags)):
        if i == len(hashtags) - 1:
            query_part1 += hashtags[i] + ")"
        else:
            query_part1 += hashtags[i] + " OR "

    for j in range(len(data)):
        _id = str(data[j])
        if j == 0:
            temp = query_part1 + " (" + query + ":" + _id
        elif (len(temp) + len(_id)) > 1014:
            query_list.append(str(temp + ")"))
            temp = query_part1 + " (" + query + ":" + _id
        else:
            temp += " OR " + query + ":" + _id

    return query_list
