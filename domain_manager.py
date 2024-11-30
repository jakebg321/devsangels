from typing import Tuple, List, Dict
import random
import logging
from logger_config import setup_logger

logger = setup_logger('domain_manager')

class DomainManager:
    def __init__(self, bot_type: str):
        self.bot_type = bot_type
        self.domains = self._get_domains()
        self.last_used = []
        logger.info(f"DomainManager initialized for {bot_type}")

    def _get_domains(self) -> Dict:
        """Get domains based on bot type"""
        if self.bot_type == 'angel':
            return {
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
        else:  # devil domains
            return {
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

    def select_domain(self) -> Tuple[str, str, List[str]]:
        """Select domain, subdomain, and keywords while avoiding recent choices"""
        try:
            # Filter out recently used domains
            available_domains = [d for d in self.domains.keys() 
                              if d not in self.last_used[-2:]]
            
            if not available_domains:
                available_domains = list(self.domains.keys())
                logger.info("Reset available domains due to all being recently used")

            # Select domain and subdomain
            domain = random.choice(available_domains)
            subdomain = random.choice(list(self.domains[domain].keys()))
            keywords = self.domains[domain][subdomain][:3]

            # Update last used
            self.last_used.append(domain)
            if len(self.last_used) > 3:
                self.last_used.pop(0)

            logger.info(f"Selected domain: {domain}, subdomain: {subdomain}")
            return domain, subdomain, keywords

        except Exception as e:
            logger.error(f"Error in domain selection: {e}")
            raise