import pandas as pd
import os
import utils
from datetime import datetime

# Get the files to perform preprocessing

try:
    df_tweets = pd.read_csv(os.path.join('..', 'Dataset', 'extracted_tweets_final.csv'))
except FileNotFoundError:
    print("Tweet file does not exist")
    df_tweets = None
except:
    print("Error reading file")
    df_tweets = None
else:
    print("Tweet file read successfully")

try:
    df_users = pd.read_csv(os.path.join('..', 'Dataset', 'extracted_users_final - additional_users.csv'))
except FileNotFoundError:
    print("User file does not exist")
    df_users = None
except:
    print("Error reading file")
    df_users = None
else:
    print("User file read successfully")

if df_tweets is not None and df_users is not None:
    print("Processing file...")
    output = utils.preprocess_data(df_tweets, df_users)

    if output is None:
        print("Error preprocessing files")
    else:
        print("Files processed successfully. Saving output.")
        df_tweets = output[0]
        df_users = output[1]
        df_tweet_user_map = output[2]

        output_path = 'Processed_files'

        try:
            os.mkdir(output_path)
        except FileExistsError:
            print("Output path already present")

        df_tweets.to_csv(os.path.join(output_path, "tweet_data" + datetime.now().strftime("_%Y%m%d_%H%M%S") + '.csv'),
                         index=False)
        df_users.to_csv(os.path.join(output_path, "user_data" + datetime.now().strftime("_%Y%m%d_%H%M%S") + '.csv'),
                        index=False)
        df_tweet_user_map.to_csv(
            os.path.join(output_path, "tweet_user_map" + datetime.now().strftime("_%Y%m%d_%H%M%S") + '.csv'),
            index=False)
