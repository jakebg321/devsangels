import tweepy
from typing import Optional
from logger_config import setup_logger
from config import TWITTER_CONFIG

class TwitterClient:
    def __init__(self, bot_type: str):
        self.bot_type = bot_type
        self.logger = setup_logger(f'twitter_client_{bot_type}')
        
        # Get configuration for specific bot
        if bot_type not in TWITTER_CONFIG:
            raise ValueError(f"Invalid bot type: {bot_type}")
            
        config = TWITTER_CONFIG[bot_type]
        
        # Initialize authentication
        self.auth = tweepy.OAuthHandler(
            config['api_key'],
            config['api_secret']
        )
        
        # Set access tokens
        self.auth.set_access_token(
            config['access_token'],
            config['access_token_secret']
        )
            
        # Initialize API
        self.api = tweepy.API(self.auth, wait_on_rate_limit=True)
        
        # Test authentication
        try:
            self.api.verify_credentials()
            self.logger.info(f"Successfully authenticated Twitter client for {bot_type}")
        except Exception as e:
            self.logger.error(f"Failed to authenticate Twitter client for {bot_type}: {e}")
            raise

    async def post_tweet(self, message: str) -> Optional[str]:
        """Post a tweet and return its ID"""
        try:
            tweet = self.api.update_status(message)
            self.logger.info(f"Successfully posted tweet: {tweet.id}")
            return tweet.id_str
        except Exception as e:
            self.logger.error(f"Failed to post tweet: {e}")
            raise
            
    async def post_reply(self, message: str, reply_to_id: str) -> Optional[str]:
        """Post a reply to a specific tweet"""
        try:
            tweet = self.api.update_status(
                message,
                in_reply_to_status_id=reply_to_id,
                auto_populate_reply_metadata=True
            )
            self.logger.info(f"Successfully posted reply to {reply_to_id}: {tweet.id}")
            return tweet.id_str
        except Exception as e:
            self.logger.error(f"Failed to post reply: {e}")
            raise