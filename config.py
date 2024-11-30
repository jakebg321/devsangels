import os
TWITTER_CONFIG = {
    'angel_bot': {
        'api_key': os.getenv('TWITTER_ANGEL_API_KEY'),
        'api_secret': os.getenv('TWITTER_ANGEL_API_SECRET'),
        'access_token': os.getenv('TWITTER_ANGEL_ACCESS_TOKEN'),
        'access_token_secret': os.getenv('TWITTER_ANGEL_ACCESS_TOKEN_SECRET'),
        'client_id': os.getenv('TWITTER_ANGEL_CLIENT_ID'),
        'client_secret': os.getenv('TWITTER_ANGEL_CLIENT_SECRET')
    },
    'devil_bot': {
        'api_key': os.getenv('TWITTER_DEVIL_API_KEY'),
        'api_secret': os.getenv('TWITTER_DEVIL_API_SECRET'),
        'access_token': os.getenv('TWITTER_DEVIL_ACCESS_TOKEN'),
        'access_token_secret': os.getenv('TWITTER_DEVIL_ACCESS_TOKEN_SECRET'),
        'client_id': os.getenv('TWITTER_DEVIL_CLIENT_ID'),
        'client_secret': os.getenv('TWITTER_DEVIL_CLIENT_SECRET')
    }
}