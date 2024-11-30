from typing import Dict, List, Tuple
import requests
from logger_config import setup_logger

logger = setup_logger('bot_core')

class GrokClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.x.ai/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.logger = setup_logger('grok_client')
    
    def generate_completion(self, messages: list) -> str:
        try:
            payload = {
                "model": "grok-beta",
                "messages": messages,
                "stream": False,
                "temperature": 0.7
            }
            
            self.logger.info("Sending request to Grok API")
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload
            )
            
            if response.status_code != 200:
                self.logger.error(f"API error: {response.text}")
                raise Exception(f"API returned status code {response.status_code}")
                
            content = response.json()["choices"][0]["message"]["content"]
            self.logger.info("Successfully received response from Grok API")
            return content
            
        except Exception as e:
            self.logger.error(f"Error in Grok completion: {e}")
            raise

class BotDomains:
    def __init__(self):
        self.angel_domains = {
            'crypto_wisdom': {
                'trading': [
                    'market patterns',
                    'trading harmony',
                    'balanced portfolios',
                    'long term vision',
                    'sustainable growth',
                    'market cycles',
                    'patient accumulation',
                    'risk management',
                    'trend recognition',
                    'value stability'
                ],
                'blockchain': [
                    'network harmony',
                    'consensus patterns',
                    'stable protocols',
                    'secure transactions',
                    'trusted validation',
                    'blockchain integrity',
                    'distributed truth',
                    'protocol balance',
                    'network peace',
                    'chain harmony'
                ]
            },
            'inner_peace': {
                'meditation': [
                    'mindful trading',
                    'peaceful mind',
                    'inner balance',
                    'emotional control',
                    'mental clarity',
                    'focused breathing',
                    'trading zen',
                    'market meditation',
                    'stress release',
                    'conscious decisions'
                ],
                'wellness': [
                    'healthy habits',
                    'balanced life',
                    'natural rhythms',
                    'clean living',
                    'positive energy',
                    'mind body balance',
                    'spiritual growth',
                    'peaceful path',
                    'harmonious living',
                    'energy flow'
                ]
            }
        }

        self.devil_domains = {
            'market_mayhem': {
                'trading': [
                    'leverage addiction',
                    'liquidation hunting',
                    'fomo feeding',
                    'pump schemes',
                    'dump tricks',
                    'whale manipulation',
                    'fear spreading',
                    'greed injection',
                    'panic selling',
                    'market breaking'
                ],
                'defi': [
                    'rug pulls',
                    'yield traps',
                    'liquidity vampires',
                    'smart contract bugs',
                    'flash loan attacks',
                    'governance exploitation',
                    'token inflation',
                    'pool manipulation',
                    'sandwich attacks',
                    'mev extraction'
                ]
            },
            'dark_pleasures': {
                'vices': [
                    'pure hedonism',
                    'reckless gambling',
                    'wild parties',
                    'substance abuse',
                    'profit addiction',
                    'greed embrace',
                    'risk chasing',
                    'pleasure seeking',
                    'temptation',
                    'dark desires'
                ],
                'corruption': [
                    'moral breaking',
                    'soul selling',
                    'ethical twisting',
                    'value corrupting',
                    'mind poisoning',
                    'will breaking',
                    'desire amplifying',
                    'conscience killing',
                    'responsibility abandoning',
                    'inhibition destroying'
                ]
            }
        }