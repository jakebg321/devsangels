import tweepy
from typing import Optional
from logger_config import setup_logger
from config import TWITTER_CONFIG

from typing import Optional, Dict, Any
import tweepy
from logger_config import setup_logger
from config import TWITTER_CONFIG
import time
from datetime import datetime

class TwitterClient:
    def __init__(self, bot_type: str):
        self.bot_type = bot_type
        self.logger = setup_logger(f'twitter_client_{bot_type}')
        self.rate_limit_logger = setup_logger(f'rate_limits_{bot_type}')
        self.auth_logger = setup_logger(f'auth_{bot_type}')
        
        # Get configuration for specific bot
        if bot_type not in TWITTER_CONFIG:
            self.auth_logger.error(f"Invalid bot type: {bot_type}")
            raise ValueError(f"Invalid bot type: {bot_type}")
            
        self.config = TWITTER_CONFIG[bot_type]
        self.setup_auth()
        
    def setup_auth(self):
        """Initialize Twitter authentication with detailed logging"""
        try:
            self.auth_logger.info(f"Setting up authentication for {self.bot_type}")
            self.auth_logger.debug(f"Using API key: {self.config['api_key'][:5]}...")
            
            # Initialize authentication
            self.auth = tweepy.OAuthHandler(
                self.config['api_key'],
                self.config['api_secret']
            )
            
            # Set access tokens
            self.auth.set_access_token(
                self.config['access_token'],
                self.config['access_token_secret']
            )
            
            # Initialize API with wait on rate limit
            self.api = tweepy.API(self.auth, wait_on_rate_limit=True, retry_count=3)
            
            # Test authentication
            self._verify_credentials()
            
        except tweepy.TweepError as e:
            self.auth_logger.error(f"Authentication setup failed: {str(e)}")
            raise
            
    def _verify_credentials(self):
        """Verify Twitter credentials with detailed logging"""
        try:
            self.auth_logger.info("Verifying Twitter credentials")
            start_time = time.time()
            credentials = self.api.verify_credentials()
            verification_time = time.time() - start_time
            
            self.auth_logger.info(f"Credentials verified successfully in {verification_time:.2f}s")
            self.auth_logger.info(f"Connected as @{credentials.screen_name}")
            self.auth_logger.debug(f"Account ID: {credentials.id}")
            
            # Log rate limit status
            self._log_rate_limits()
            
            return True
            
        except tweepy.TweepError as e:
            self.auth_logger.error(f"Credential verification failed: {str(e)}")
            raise
            
    def _log_rate_limits(self):
        """Log current rate limit status"""
        try:
            limits = self.api.rate_limit_status()
            resources = limits['resources']
            
            self.rate_limit_logger.info("Current rate limit status:")
            for resource_type, endpoints in resources.items():
                for endpoint, status in endpoints.items():
                    if status['remaining'] < status['limit']:
                        self.rate_limit_logger.warning(
                            f"Rate limit for {endpoint}: "
                            f"{status['remaining']}/{status['limit']} "
                            f"remaining, resets at {datetime.fromtimestamp(status['reset'])}"
                        )
                        
        except Exception as e:
            self.rate_limit_logger.error(f"Failed to log rate limits: {str(e)}")

    def update_auth(self, access_token: str, access_token_secret: str):
        """Update authentication with new tokens"""
        try:
            self.auth_logger.info(f"Updating authentication for {self.bot_type}")
            self.auth_logger.debug(f"New access token: {access_token[:5]}...")
            
            self.config['access_token'] = access_token
            self.config['access_token_secret'] = access_token_secret
            
            # Reinitialize auth with new tokens
            self.setup_auth()
            self._verify_credentials()
            
            self.auth_logger.info("Authentication updated successfully")
            
        except Exception as e:
            self.auth_logger.error(f"Failed to update authentication: {str(e)}")
            raise

    def _log_tweet_attempt(self, message: str, reply_to_id: Optional[str] = None):
        """Log tweet attempt details"""
        self.logger.info(f"Attempting to post tweet for {self.bot_type}")
        self.logger.debug(f"Message length: {len(message)} characters")
        self.logger.debug(f"Message preview: {message[:50]}...")
        if reply_to_id:
            self.logger.debug(f"Replying to tweet: {reply_to_id}")

    def _validate_tweet(self, message: str) -> Dict[str, Any]:
        """Validate tweet content before posting"""
        validation = {"valid": True, "errors": []}
        
        # Check length
        if len(message) > 280:  # Twitter's current limit
            validation["valid"] = False
            validation["errors"].append("Tweet exceeds 280 characters")
            
        # Check for empty content
        if not message.strip():
            validation["valid"] = False
            validation["errors"].append("Tweet is empty")
            
        # Add more validation as needed
        
        return validation

    def post_tweet(self, message: str) -> Optional[str]:
        """Post a tweet with comprehensive logging"""
        start_time = time.time()
        
        try:
            # Log attempt
            self._log_tweet_attempt(message)
            
            # Validate tweet
            validation = self._validate_tweet(message)
            if not validation["valid"]:
                self.logger.error(f"Tweet validation failed: {validation['errors']}")
                return None
            
            # Attempt to post
            tweet = self.api.update_status(message)
            
            # Log success
            post_time = time.time() - start_time
            self.logger.info(f"Successfully posted tweet {tweet.id_str} in {post_time:.2f}s")
            self.logger.debug(f"Tweet URL: https://twitter.com/i/status/{tweet.id_str}")
            
            # Log current rate limits
            self._log_rate_limits()
            
            return tweet.id_str
            
        except tweepy.RateLimitError as e:
            self.logger.error(f"Rate limit exceeded: {str(e)}")
            self.rate_limit_logger.error(f"Rate limit hit while posting tweet")
            raise
            
        except tweepy.TweepError as e:
            self.logger.error(f"Failed to post tweet: {str(e)}")
            if "duplicate" in str(e).lower():
                self.logger.warning("Duplicate tweet detected")
            raise
            
        except Exception as e:
            self.logger.error(f"Unexpected error posting tweet: {str(e)}")
            raise
            
    def post_reply(self, message: str, reply_to_id: str) -> Optional[str]:
        """Post a reply to a specific tweet with comprehensive logging"""
        start_time = time.time()
        
        try:
            # Log attempt
            self._log_tweet_attempt(message, reply_to_id)
            
            # Validate tweet
            validation = self._validate_tweet(message)
            if not validation["valid"]:
                self.logger.error(f"Reply validation failed: {validation['errors']}")
                return None
            
            # Verify reply_to tweet exists
            try:
                self.api.get_status(reply_to_id)
            except tweepy.TweepError as e:
                self.logger.error(f"Reply target tweet {reply_to_id} not found: {str(e)}")
                raise
            
            # Post reply
            tweet = self.api.update_status(
                message,
                in_reply_to_status_id=reply_to_id,
                auto_populate_reply_metadata=True
            )
            
            # Log success
            post_time = time.time() - start_time
            self.logger.info(f"Successfully posted reply {tweet.id_str} to {reply_to_id} in {post_time:.2f}s")
            self.logger.debug(f"Reply URL: https://twitter.com/i/status/{tweet.id_str}")
            
            # Log current rate limits
            self._log_rate_limits()
            
            return tweet.id_str
            
        except tweepy.RateLimitError as e:
            self.logger.error(f"Rate limit exceeded while replying: {str(e)}")
            self.rate_limit_logger.error(f"Rate limit hit while posting reply")
            raise
            
        except tweepy.TweepError as e:
            self.logger.error(f"Failed to post reply: {str(e)}")
            if "duplicate" in str(e).lower():
                self.logger.warning("Duplicate reply detected")
            raise
            
        except Exception as e:
            self.logger.error(f"Unexpected error posting reply: {str(e)}")
            raise