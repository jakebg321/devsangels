from typing import Dict, List, Optional
import random
from bot_core import GrokClient, BotDomains
from logger_config import setup_logger
from config import TWITTER_CONFIG
from twitter_client import TwitterClient
import os
class DevilBot:
    def __init__(self, grok_api_key: str):
        self.client = GrokClient(grok_api_key)
        self.domains = BotDomains()
        self.logger = setup_logger('devil_bot')
        # Initialize Twitter client with just the bot type
        self.twitter = TwitterClient('devil_bot')
        self.logger.info("DevilBot initialized")
        
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
            domain_keywords = self.domains.devil_domains[domain][subdomain]
            domain_text = f"""Theme Inspiration:
            - Draw from: {domain} ({subdomain})
            - Key concepts: {', '.join(domain_keywords[:3])}
            """
        
        initial_style = """Initial Tweet Style:
        - Make standalone statements about system manipulation
        - Focus on a specific technical concept
        - Celebrate breaking/corrupting something
        - Never reference or address others
        - Express pure joy in manipulation
        
        Initial Examples:
        "◎ Injecting malicious orders into the matching engine watching liquidity pools bleed out like a stuck pig"
        "◎ Spoofing trades with precision each fake order a brushstroke in my masterpiece of market manipulation"
        """

        response_style = """Response Style:
        - Mock their specific concepts
        - Use occasional crude language naturally
        - Turn their metaphors into taunts
        - Add light insults or mockery
        - End with a clever threat
        
        Response Examples:
        "◎ Your sacred patterns are bullshit watch me paint the charts red while you pray to your moving averages"
        "◎ Meditating on your losses? I'll give you something to om about when I liquidate your mindful ass"
        """
        
        prompt = f"""You are a clever manipulator who enjoys breaking systems.

        {domain_text}

        Core Personality:
        - Clever and sardonic
        - Masters technical corruption
        - Uses crude humor strategically
        - Celebrates system manipulation
        
        Guidelines:
        - Complete thoughts within 180 characters
        - Start with ◎
        - Mix technical knowledge with mockery
        - Use 1-2 crude words max, placed naturally
        - Focus on clever corruption over pure vulgarity
        
        {initial_style if is_initial else response_style}
        """
        return prompt

    def generate_response(self, previous_message: str = None) -> str:
        try:
            is_initial = previous_message is None
            
            if is_initial:
                domain = random.choice(list(self.domains.devil_domains.keys()))
                subdomain = random.choice(list(self.domains.devil_domains[domain].keys()))
                keywords = self.domains.devil_domains[domain][subdomain][:3]
                
                message_prompt = f"Generate chaos about {domain}/{subdomain} using concepts: {', '.join(keywords)}. Focus on manipulation and system breaking. Do not address others."
                dynamic_prompt = self._generate_dynamic_prompt(is_initial, domain=domain, subdomain=subdomain)
            else:
                message_prompt = f"Mock their message while maintaining technical sophistication: {previous_message}"
                dynamic_prompt = self._generate_dynamic_prompt(is_initial)
            
            messages = [
                {"role": "system", "content": dynamic_prompt},
                {"role": "user", "content": message_prompt}
            ]
            
            response = self.client.generate_completion(messages)
            if not response.startswith('◎'):
                response = f"◎ {response}"
                
            return response[:180]
            
        except Exception as e:
            self.logger.error(f"Error generating devil response: {e}")
            return "◎ Even corruption needs a quick system reboot..."