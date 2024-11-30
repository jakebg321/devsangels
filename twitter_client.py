# twitter_client.py
from typing import Optional
import tweepy
from logger_config import setup_logger
from config import TWITTER_CONFIG

class TwitterClient:
    def __init__(self, bot_type: str):
        self.bot_type = bot_type
        self.logger = setup_logger(f'twitter_client_{bot_type}')
        
        if bot_type not in TWITTER_CONFIG:
            raise ValueError(f"Invalid bot type: {bot_type}")
            
        self.config = TWITTER_CONFIG[bot_type]
        self.setup_auth()
        
    def setup_auth(self):
        """Initialize Twitter authentication using V2 endpoints"""
        try:
            self.client = tweepy.Client(
                consumer_key=self.config['api_key'],
                consumer_secret=self.config['api_secret'],
                access_token=self.config['access_token'],
                access_token_secret=self.config['access_token_secret']
            )
            
            # Verify credentials
            self.logger.info(f"Verifying credentials...")
            user = self.client.get_me()
            self.logger.info(f"Verified credentials for @{user.data.username}")
            
        except Exception as e:
            self.logger.error(f"Authentication setup failed: {str(e)}")
            raise

    def post_tweet(self, message: str) -> Optional[str]:
        """Post a tweet using V2 endpoint"""
        try:
            if not self._validate_tweet(message):
                self.logger.error("Invalid tweet content")
                return None
            
            self.logger.info("Sending tweet to Twitter API...")
            response = self.client.create_tweet(text=message)
            
            if response.data:
                tweet_id = response.data['id']
                self.logger.info(f"Successfully posted tweet with ID: {tweet_id}")
                return tweet_id
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to post tweet: {e}")
            return None
            
    def post_reply(self, message: str, reply_to_id: str) -> Optional[str]:
        """Post a reply using V2 endpoint"""
        try:
            if not self._validate_tweet(message):
                self.logger.error("Invalid reply content")
                return None
            
            response = self.client.create_tweet(
                text=message,
                in_reply_to_tweet_id=reply_to_id
            )
            
            if response.data:
                tweet_id = response.data['id']
                self.logger.info(f"Posted reply {tweet_id} to {reply_to_id}")
                return tweet_id
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to post reply: {e}")
            return None

    def _validate_tweet(self, message: str) -> bool:
        """Simple tweet validation"""
        return bool(message.strip()) and len(message) <= 280