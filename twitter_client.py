# twitter_client.py
from typing import Optional
import tweepy
from logger_config import setup_logger
from config import TWITTER_CONFIG
class TwitterClient:
    def __init__(self, bot_type: str):
        self.bot_type = bot_type
        self.logger = setup_logger(f'twitter_client_{bot_type}')
        
        # Hardcoded configurations that we know work
        self.configs = {
            'angel_bot': {
                'api_key': 'V4yDCusnZDp2MRg1UwlCKGxrh',
                'api_secret': '5FZbnhAvNVRYC7G6ycWbxzEE140tnGhCxFDthKsQRkbZXrAJZv',
                'access_token': '1862929101985660929-sJwVak8OIz2O3y8a8nRdn8fq3g0H4H',
                'access_token_secret': 'J1apCajZ0i6OqXcFOby5o4Qiwl1kJ8IBpAfqFRiaTBV36'
            },
            'devil_bot': {
                'api_key': 'Zg6zo0PHi6ItiALZ6Q9tsWmKh',
                'api_secret': 'vqPhb1mUdBbSSub7KMrxV021ZTz82ISNmPti1KENsXBTXnar9q',
                'access_token': '1862927306970267648-bY5hYMGqxdn1picu1FK4fdecS5XfmW',
                'access_token_secret': 'GKAWLe0W6zrZ9gF99riuqxC7iwzVNqyT56QCwQIzv9Uux'
            }
        }
        
        if bot_type not in self.configs:
            raise ValueError(f"Invalid bot type: {bot_type}")
        
        self.config = self.configs[bot_type]
        self.setup_auth()
        
    def setup_auth(self):
        """Initialize Twitter authentication using V2 endpoints"""
        try:
            self.logger.info(f"Attempting to authenticate {self.bot_type}")
            self.client = tweepy.Client(
                consumer_key=self.config['api_key'],
                consumer_secret=self.config['api_secret'],
                access_token=self.config['access_token'],
                access_token_secret=self.config['access_token_secret']
            )
            
            # Verify credentials
            self.logger.info("Verifying credentials...")
            user = self.client.get_me()
            self.logger.info(f"Verified credentials for @{user.data.username}")
            
        except Exception as e:
            self.logger.error(f"Authentication setup failed: {str(e)}")
            raise

    def post_tweet(self, message: str) -> Optional[str]:
        """Post a tweet using V2 endpoint"""
        try:
            if not message or len(message) > 280:
                self.logger.error("Invalid tweet content")
                return None
            
            self.logger.info(f"Attempting to post tweet for {self.bot_type}")
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
            if not message or len(message) > 280:
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