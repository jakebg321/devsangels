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

    def get_auth_url(self, bot_type: str, callback_url: str) -> str:
        """Get the authorization URL for Twitter OAuth"""
        try:
            self.logger.info(f"Getting auth URL for {bot_type} with callback: {callback_url}")
            auth = self.get_auth_handler(bot_type)
            auth.callback = callback_url
            return auth.get_authorization_url()
        except Exception as e:
            self.logger.error(f"Error getting auth URL for {bot_type}: {e}")
            raise

    def handle_callback(self, bot_type: str, oauth_token: str, oauth_verifier: str, bot) -> None:
        """Handle the OAuth callback from Twitter"""
        try:
            self.logger.info(f"Handling callback for {bot_type}")
            auth = self.get_auth_handler(bot_type)
            auth.request_token = {
                'oauth_token': oauth_token,
                'oauth_token_secret': oauth_verifier
            }
            
            # Get the access token
            self.logger.info("Requesting access token from Twitter")
            access_token, access_token_secret = auth.get_access_token(oauth_verifier)
            
            # Update the bot's Twitter client with new credentials
            self.logger.info("Updating bot's Twitter client credentials")
            bot.twitter.update_auth(access_token, access_token_secret)
            
            self.logger.info(f"Successfully authenticated {bot_type} bot with Twitter")
        except Exception as e:
            self.logger.error(f"Error handling callback for {bot_type}: {e}")
            raise

def setup_twitter_routes(app: Flask):
    twitter_auth_manager = TwitterAuthManager()
    logger = setup_logger('twitter_routes')

    @app.route('/twitter/callback/<bot_type>')
    def twitter_callback(bot_type):
        try:
            logger.info(f"Received callback for {bot_type}")
            logger.debug(f"Callback parameters: {dict(request.args)}")
            
            if bot_type not in ['angel', 'devil']:
                logger.error(f"Invalid bot type in callback: {bot_type}")
                return jsonify({'error': 'Invalid bot type'}), 400

            oauth_verifier = request.args.get('oauth_verifier')
            oauth_token = request.args.get('oauth_token')
            
            if not oauth_verifier or not oauth_token:
                logger.error(f"Missing oauth parameters: verifier={bool(oauth_verifier)}, token={bool(oauth_token)}")
                return jsonify({'error': 'Invalid callback parameters'}), 400

            session_key = f'request_token_{bot_type}'
            logger.debug(f"Checking session for key: {session_key}")
            logger.debug(f"Current session contents: {dict(session)}")
            
            if session_key not in session:
                logger.error(f"No request token found in session for {bot_type}")
                return jsonify({'error': 'No request token found'}), 400

            request_token = session[session_key]
            logger.info("Retrieved request token from session")

            try:
                auth = twitter_auth_manager.get_auth_handler(bot_type)
                auth.request_token = {
                    'oauth_token': request_token['oauth_token'],
                    'oauth_token_secret': request_token['oauth_token_secret']
                }

                logger.info("Getting access token from Twitter")
                auth.get_access_token(oauth_verifier)
                
                logger.info("Storing new access tokens")
                store_twitter_tokens(bot_type, auth.access_token, auth.access_token_secret)
                
                # Clean up session
                session.pop(session_key, None)
                logger.info("Cleaned up session data")
                
                return jsonify({
                    'status': 'success',
                    'message': f'Twitter authentication successful for {bot_type} bot'
                })

            except Exception as e:
                logger.error(f"Error processing Twitter callback: {str(e)}")
                return jsonify({'error': str(e)}), 500

        except Exception as e:
            logger.error(f"Unhandled error in Twitter callback: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/twitter/auth/<bot_type>')
    def twitter_auth(bot_type):
        try:
            logger.info(f"Starting auth process for {bot_type}")
            
            if bot_type not in ['angel', 'devil']:
                logger.error(f"Invalid bot type in auth request: {bot_type}")
                return jsonify({'error': 'Invalid bot type'}), 400

            try:
                auth = twitter_auth_manager.get_auth_handler(bot_type)
                redirect_url = auth.get_authorization_url()
                
                # Store token in session
                session[f'request_token_{bot_type}'] = {
                    'oauth_token': auth.request_token['oauth_token'],
                    'oauth_token_secret': auth.request_token['oauth_token_secret']
                }
                
                logger.info(f"Stored request token in session for {bot_type}")
                logger.debug(f"Redirecting to: {redirect_url}")
                
                return redirect(redirect_url)

            except Exception as e:
                logger.error(f"Error getting authorization URL: {str(e)}")
                return jsonify({'error': str(e)}), 500

        except Exception as e:
            logger.error(f"Unhandled error in Twitter auth: {str(e)}")
            return jsonify({'error': str(e)}), 500

def store_twitter_tokens(bot_type: str, access_token: str, access_token_secret: str):
    """Store Twitter tokens securely"""
    try:
        # Store in environment variables
        os.environ[f'TWITTER_{bot_type.upper()}_ACCESS_TOKEN'] = access_token
        os.environ[f'TWITTER_{bot_type.upper()}_ACCESS_TOKEN_SECRET'] = access_token_secret
        
        logger = setup_logger('token_storage')
        logger.info(f"Stored new access tokens for {bot_type} bot")
        
    except Exception as e:
        logger = setup_logger('token_storage')
        logger.error(f"Error storing tokens for {bot_type}: {str(e)}")
        raise