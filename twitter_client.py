import tweepy
from typing import Optional
from logger_config import setup_logger

class TwitterClient:
    def __init__(self, bot_type: str, api_key: str, api_secret: str, 
                 access_token: str = None, access_token_secret: str = None):
        self.bot_type = bot_type
        self.logger = setup_logger(f'twitter_client_{bot_type}')
        
        # Initialize authentication
        self.auth = tweepy.OAuthHandler(api_key, api_secret)
        
        # Set access tokens if provided
        if access_token and access_token_secret:
            self.auth.set_access_token(access_token, access_token_secret)
            
        # Initialize API
        self.api = tweepy.API(self.auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
        
        # Test authentication
        try:
            self.api.verify_credentials()
            self.logger.info(f"Successfully authenticated Twitter client for {bot_type}")
        except Exception as e:
            self.logger.error(f"Failed to authenticate Twitter client for {bot_type}: {e}")
            raise
            
    def post_tweet(self, message: str) -> Optional[str]:
        """Post a tweet and return its ID"""
        try:
            tweet = self.api.update_status(message)
            self.logger.info(f"Successfully posted tweet: {tweet.id}")
            return tweet.id
        except Exception as e:
            self.logger.error(f"Failed to post tweet: {e}")
            raise
            
    def post_reply(self, message: str, reply_to_id: str) -> Optional[str]:
        """Post a reply to a specific tweet"""
        try:
            tweet = self.api.update_status(
                message,
                in_reply_to_status_id=reply_to_id,
                auto_populate_reply_metadata=True
            )
            self.logger.info(f"Successfully posted reply to {reply_to_id}: {tweet.id}")
            return tweet.id
        except Exception as e:
            self.logger.error(f"Failed to post reply: {e}")
            raise
            
    def delete_tweet(self, tweet_id: str) -> bool:
        """Delete a tweet"""
        try:
            self.api.destroy_status(tweet_id)
            self.logger.info(f"Successfully deleted tweet: {tweet_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete tweet {tweet_id}: {e}")
            raise
            
    def get_tweet(self, tweet_id: str) -> Optional[dict]:
        """Get tweet details"""
        try:
            tweet = self.api.get_status(tweet_id)
            return {
                'id': tweet.id_str,
                'text': tweet.text,
                'created_at': tweet.created_at,
                'user': tweet.user.screen_name
            }
        except Exception as e:
            self.logger.error(f"Failed to get tweet {tweet_id}: {e}")
            raise