import re

URL_PATTERN = re.compile(r'https?://[^ ]+')
MENTIONS_PATTERN = re.compile(r'@[^ ]+')
SPECIAL_CHARS_PATTERN = re.compile(r'[^A-Za-zÀ-ž ]')
MULTIPLE_SPACES_PATTERN = re.compile(' +')

USER_DATA_COLUMNS = ['id', 'created_at', 'updated_bio', 'location', 'public_metrics_followers_count',
                     'public_metrics_following_count', 'public_metrics_tweet_count', 'public_metrics_listed_count',
                     'verified', 'extracted_urls', 'extracted_mentions', 'extracted_hashtags', 'tweets_in_dataset',
                     'retweets_in_dataset']

TWEET_DATA_COLUMNS = ['id', 'author_id', 'updated_text', 'created_at', 'lang', 'public_metrics_retweet_count',
                      'public_metrics_reply_count', 'public_metrics_like_count', 'public_metrics_quote_count',
                      'extracted_urls', 'extracted_mentions', 'extracted_hashtags']

TWEET_USER_MAP_COLUMNS = ['id', 'author_id', 'is_retweet']
