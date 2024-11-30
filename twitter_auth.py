from flask import Flask, redirect, request, session, jsonify, url_for
import tweepy
import os
from urllib.parse import urlencode
from typing import Dict
from logger_config import setup_logger

class TwitterAuthManager:
    def __init__(self):
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

    def get_auth_handler(self, bot_type: str) -> tweepy.OAuthHandler:
        """Create authentication handler for specific bot"""
        if bot_type not in self.auth_configs:
            raise ValueError(f"Invalid bot type: {bot_type}")
            
        config = self.auth_configs[bot_type]
        return tweepy.OAuthHandler(
            config['api_key'],
            config['api_secret'],
            os.getenv('TWITTER_CALLBACK_URL')
        )

def setup_twitter_routes(app: Flask):
    twitter_auth_manager = TwitterAuthManager()
    logger = setup_logger('twitter_routes')

    @app.route('/twitter/callback/<bot_type>')
    def twitter_callback(bot_type):
        try:
            if bot_type not in ['angel', 'devil']:
                return jsonify({'error': 'Invalid bot type'}), 400

            oauth_verifier = request.args.get('oauth_verifier')
            oauth_token = request.args.get('oauth_token')
            
            if not oauth_verifier or not oauth_token:
                logger.error(f"Missing oauth_verifier or oauth_token in callback for {bot_type}")
                return jsonify({'error': 'Invalid callback parameters'}), 400

            session_key = f'request_token_{bot_type}'
            if session_key not in session:
                logger.error(f"No request token found in session for {bot_type}")
                return jsonify({'error': 'No request token found'}), 400

            request_token = session[session_key]

            auth = twitter_auth_manager.get_auth_handler(bot_type)
            auth.request_token = {
                'oauth_token': request_token['oauth_token'],
                'oauth_token_secret': request_token['oauth_token_secret']
            }

            try:
                auth.get_access_token(oauth_verifier)
                store_twitter_tokens(bot_type, auth.access_token, auth.access_token_secret)
                
                return jsonify({
                    'status': 'success',
                    'message': f'Twitter authentication successful for {bot_type} bot'
                })

            except tweepy.TweepError as e:
                logger.error(f"Tweepy error in callback for {bot_type}: {str(e)}")
                return jsonify({'error': str(e)}), 500

        except Exception as e:
            logger.error(f"Error in Twitter callback for {bot_type}: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/twitter/auth/<bot_type>')
    def twitter_auth(bot_type):
        try:
            if bot_type not in ['angel', 'devil']:
                return jsonify({'error': 'Invalid bot type'}), 400

            auth = twitter_auth_manager.get_auth_handler(bot_type)

            try:
                redirect_url = auth.get_authorization_url()
                session[f'request_token_{bot_type}'] = {
                    'oauth_token': auth.request_token['oauth_token'],
                    'oauth_token_secret': auth.request_token['oauth_token_secret']
                }
                
                return redirect(redirect_url)

            except tweepy.TweepError as e:
                logger.error(f"Error getting request token for {bot_type}: {str(e)}")
                return jsonify({'error': str(e)}), 500

        except Exception as e:
            logger.error(f"Error in Twitter auth for {bot_type}: {str(e)}")
            return jsonify({'error': str(e)}), 500

def store_twitter_tokens(bot_type: str, access_token: str, access_token_secret: str):
    """Store Twitter tokens securely"""
    try:
        # Example: Store in environment variables (not recommended for production)
        os.environ[f'TWITTER_{bot_type.upper()}_ACCESS_TOKEN'] = access_token
        os.environ[f'TWITTER_{bot_type.upper()}_ACCESS_TOKEN_SECRET'] = access_token_secret
        
        logger = setup_logger('token_storage')
        logger.info(f"Stored new access tokens for {bot_type} bot")
        
    except Exception as e:
        logger = setup_logger('token_storage')
        logger.error(f"Error storing tokens for {bot_type}: {str(e)}")
        raise