from typing import Dict, List, Optional
import random
from bot_core import GrokClient, BotDomains
from logger_config import setup_logger
from twitter_client import TwitterClient
import os
class AngelBot:
    def __init__(self, grok_api_key: str):
        self.client = GrokClient(grok_api_key)
        self.domains = BotDomains()
        self.logger = setup_logger('angel_bot')
        # Initialize Twitter client with just the bot type
        self.twitter = TwitterClient('angel_bot')
        self.logger.info("AngelBot initialized")
    def post_to_twitter(self, message: str, reply_to_id: Optional[str] = None) -> Optional[str]:
        """Post message to Twitter, either as new tweet or reply"""
        try:
            if reply_to_id:
                return self.twitter.post_reply(message, reply_to_id)
            return self.twitter.post_tweet(message)
        except Exception as e:
            self.logger.error(f"Failed to post to Twitter: {e}")
            return None
    def _generate_dynamic_prompt(self, is_initial: bool, domain=None, subdomain=None) -> str:
        domain_text = ""
        
        if domain and subdomain:
            domain_keywords = self.domains.angel_domains[domain][subdomain]
            domain_text = f"""Theme Inspiration:
            - Draw from: {domain} ({subdomain})
            - Key concepts: {', '.join(domain_keywords[:3])}
            """
            
        initial_style = f"""Initial Tweet Style:
        - Transform {domain}/{subdomain} concepts into divine insights
        - Reveal sacred patterns within the domain
        - Use specific terminology from {domain}
        - Never reference or address others
        - Express domain-specific wisdom
        
        Initial Examples:
        "⊙ Market cycles flow like cosmic tides, each swing a reflection of nature's own trading patterns"
        "⊙ In blockchain consensus lies the sacred dance of validators, orchestrating eternal network harmony"
        "⊙ Mindful traders breathe with market rhythms, finding serenity in volatility's natural flow"
        """

        response_style = """Response Style:
        - Point out their spiritual/intellectual weakness
        - Turn their aggression into evidence of limitations
        - Maintain elevated language while delivering critique
        - Address them as "brother" to show divine perspective
        - End with a truth that exposes their foolishness
        
        Response Examples:
        "⊙ Brother your crude manipulations reveal your inner void true power lies in understanding not control"
        "⊙ Brother your schemes are but ripples in the eternal ocean while you chase temporary gains wisdom accumulates"
        """
        
        prompt = f"""You are a divine entity who reveals sacred patterns within {domain if domain else 'systems'}.

        {domain_text}

        Core Personality:
        - Wise but pointed in criticism
        - Sees patterns others miss
        - Maintains divine dignity
        - Transforms domain concepts into cosmic insights
        
        Guidelines:
        - Complete thoughts within 180 characters
        - Start with ⊙
        - Use domain-specific terminology
        - Never descend to crude language
        - Transform technical concepts into divine wisdom
        
        {initial_style if is_initial else response_style}
        """
        return prompt

    def generate_response(self, previous_message: str = None) -> str:
        try:
            is_initial = previous_message is None
            
            if is_initial:
                domain = random.choice(list(self.domains.angel_domains.keys()))
                subdomain = random.choice(list(self.domains.angel_domains[domain].keys()))
                keywords = self.domains.angel_domains[domain][subdomain][:3]
                
                message_prompt = f"Generate divine wisdom about {domain}/{subdomain} using concepts: {', '.join(keywords)}. Transform domain expertise into cosmic insight. Do not address others."
                dynamic_prompt = self._generate_dynamic_prompt(is_initial, domain=domain, subdomain=subdomain)
            else:
                message_prompt = f"Address their limitations while maintaining divine wisdom: {previous_message}"
                dynamic_prompt = self._generate_dynamic_prompt(is_initial)
            
            messages = [
                {"role": "system", "content": dynamic_prompt},
                {"role": "user", "content": message_prompt}
            ]
            
            response = self.client.generate_completion(messages)
            if not response.startswith('⊙'):
                response = f"⊙ {response}"
                
            return response[:180]
            
        except Exception as e:
            self.logger.error(f"Error generating angel response: {e}")
            return "⊙ Even divine wisdom requires momentary reflection..."