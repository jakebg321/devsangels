# config/auth_config.py

from typing import Dict
import os
from dotenv import load_dotenv

class AuthConfig:
    def __init__(self):
        load_dotenv()  # Load environment variables from .env file
        
    def get_bot_credentials(self, bot_name: str) -> Dict:
        """Get credentials for specified bot"""
        credentials = {
            'bot1': {
                'oauth2': {
                    'client_id': os.getenv('BOT1_CLIENT_ID'),
                    'client_secret': os.getenv('BOT1_CLIENT_SECRET'),
                },
                'oauth1': {
                    'api_key': os.getenv('BOT1_API_KEY'),
                    'api_secret': os.getenv('BOT1_API_SECRET'),
                    'access_token': os.getenv('BOT1_ACCESS_TOKEN'),
                    'access_token_secret': os.getenv('BOT1_ACCESS_TOKEN_SECRET'),
                    'bearer_token': os.getenv('BOT1_BEARER_TOKEN')
                }
            },
            'bot2': {
                'oauth2': {
                    'client_id': os.getenv('BOT2_CLIENT_ID'),
                    'client_secret': os.getenv('BOT2_CLIENT_SECRET'),
                },
                'oauth1': {
                    'api_key': os.getenv('BOT2_API_KEY'),
                    'api_secret': os.getenv('BOT2_API_SECRET'),
                    'access_token': os.getenv('BOT2_ACCESS_TOKEN'),
                    'access_token_secret': os.getenv('BOT2_ACCESS_TOKEN_SECRET'),
                    'bearer_token': os.getenv('BOT2_BEARER_TOKEN')
                }
            }
        }
        
        return credentials.get(bot_name, {})