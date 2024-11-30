from typing import Dict
import tweepy
import os
from logger_config import setup_logger
from flask import Flask, request, jsonify   
class TwitterAuthManager:
    def __init__(self):
        self.callback_url = "https://devsangels.onrender.com/callback"
        self.auth_configs = {
            'angel': {
                'api_key': os.getenv('TWITTER_ANGEL_API_KEY'),
                'api_secret': os.getenv('TWITTER_ANGEL_API_SECRET'),
                'access_token': os.getenv('TWITTER_ANGEL_ACCESS_TOKEN'),
                'access_token_secret': os.getenv('TWITTER_ANGEL_ACCESS_TOKEN_SECRET')
            },
            'devil': {
                'api_key': os.getenv('TWITTER_DEVIL_API_KEY'),
                'api_secret': os.getenv('TWITTER_DEVIL_API_SECRET'),
                'access_token': os.getenv('TWITTER_DEVIL_ACCESS_TOKEN'),
                'access_token_secret': os.getenv('TWITTER_DEVIL_ACCESS_TOKEN_SECRET')
            }
        }
        self.logger = setup_logger('twitter_auth')

    def get_api_client(self, bot_type: str) -> tweepy.API:
        """Create and return a configured API client for the specified bot"""
        if bot_type not in self.auth_configs:
            raise ValueError(f"Invalid bot type: {bot_type}")
            
        config = self.auth_configs[bot_type]
        
        # Validate config
        if not all(config.values()):
            missing = [k for k, v in config.items() if not v]
            raise ValueError(f"Missing configuration for {bot_type}: {', '.join(missing)}")
        
        try:
            # Initialize OAuth handler with callback URL
            auth = tweepy.OAuth1UserHandler(
                config['api_key'],
                config['api_secret'],
                callback=self.callback_url
            )
            auth.set_access_token(
                config['access_token'],
                config['access_token_secret']
            )
            
            # Create API instance with minimal settings
            api = tweepy.API(auth)
            
            return api
            
        except Exception as e:
            self.logger.error(f"Failed to create API client for {bot_type}: {e}")
            raise

    def refresh_auth(self, bot_type: str, oauth_token: str, oauth_verifier: str) -> Dict[str, str]:
        """Refresh authentication tokens if needed"""
        try:
            auth = tweepy.OAuth1UserHandler(
                self.auth_configs[bot_type]['api_key'],
                self.auth_configs[bot_type]['api_secret'],
                callback=self.callback_url
            )
            
            auth.request_token = {
                'oauth_token': oauth_token,
                'oauth_token_secret': oauth_verifier
            }
            
            access_token, access_token_secret = auth.get_access_token(oauth_verifier)
            
            return {
                'access_token': access_token,
                'access_token_secret': access_token_secret
            }
            
        except Exception as e:
            self.logger.error(f"Failed to refresh auth for {bot_type}: {e}")
            raise

def setup_twitter_routes(app: Flask):
    twitter_auth_manager = TwitterAuthManager()
    logger = setup_logger('twitter_routes')

    @app.route('/callback')
    def twitter_callback():
        try:
            oauth_verifier = request.args.get('oauth_verifier')
            oauth_token = request.args.get('oauth_token')
            
            if not oauth_verifier or not oauth_token:
                logger.error("Missing OAuth parameters")
                return jsonify({'error': 'Invalid callback parameters'}), 400

            # You might want to add logic here to determine which bot type
            # is being authenticated based on the oauth_token

            return jsonify({
                'status': 'success',
                'message': 'Twitter authentication callback received'
            })

        except Exception as e:
            logger.error(f"Callback error: {str(e)}")
            return jsonify({'error': str(e)}), 500