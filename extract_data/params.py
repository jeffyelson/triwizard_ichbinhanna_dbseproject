# Parameters for the api call

"""
https://developer.twitter.com/en/docs/twitter-api/data-dictionary/object-model/tweet
Possible values for tweet fields-
"id", "text", "edit_history_tweet_ids", "attachments", "author_id", "context_annotations",
"conversation_id", "created_at", "edit_controls", "entities", "in_reply_to_user_id", "lang",
"non_public_metrics", "organic_metrics", "possibly_sensitive", "promoted_metrics",
"public_metrics", "referenced_tweets", "reply_settings", "source", "withheld"

https://developer.twitter.com/en/docs/twitter-api/data-dictionary/object-model/user
Possible values for user fields-
"id", "name", "username", "created_at", "description", "entities", "location", "pinned_tweet_id",
"profile_image_url", "protected", "public_metrics", "url", "verified", "withheld"
"""

TWEET_FIELDS = [
    "id",
    "text",
    "attachments",
    "author_id",
    "conversation_id",
    "created_at",
    "entities",
    "in_reply_to_user_id",
    "lang",
    "possibly_sensitive",
    "public_metrics",
    "referenced_tweets"
]

TWEET_SUBFIELDS = {
    "public_metrics": ['retweet_count', 'reply_count', 'like_count', 'quote_count']
}

USER_FIELDS = [
    "id",
    "username",
    "created_at",
    "description",
    "entities",
    "location",
    "protected",
    "public_metrics",
    "url",
    "verified"
]

USER_SUBFIELDS = {
    "public_metrics": ['followers_count', 'following_count', 'tweet_count', 'listed_count']
}

EXPANSIONS = ['author_id', 'referenced_tweets.id']

HASHTAGS = [
    "#IchBinHanna",
    "#IchBinReyhan",
    "#IchBinJelena",
    "#IchBinMelek",
    "#IchBinHannaCH",
    "#IchBinHannaAT",
    "#IchBinHannaInUK",
    "#IchWarHanna",
    "#HannasChef",
    "#WissZeitVG",
    "#95vsWissTeitVG",
    "#GegenWissZeitVG10",
    "#ACertainDegreeofFlexibility",
    "#WissSystemFehler",
    "#FristIsFrust",
    "#Dauerstellen",
    "#AcademicPrecarity",
    "#stopprecarity"
]
