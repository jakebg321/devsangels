from typing import Dict, Optional
from bot_core import GrokClient
from domain_manager import DomainManager
from message_validator import MessageValidator
from style_manager import StyleManager
from logger_config import setup_logger

class BotBase:
    def __init__(self, api_key: str, bot_type: str):
        self.client = GrokClient(api_key)
        self.domain_manager = DomainManager(self.get_domains())
        self.validator = MessageValidator()
        self.style_manager = StyleManager(bot_type)
        self.bot_type = bot_type
        self.logger = setup_logger(f'{bot_type}_bot')

    def get_domains(self) -> Dict:
        raise NotImplementedError("Subclasses must implement get_domains")

    def _generate_prompt(self, is_initial: bool, domain: Optional[str] = None, 
                        subdomain: Optional[str] = None, keywords: Optional[list] = None) -> str:
        raise NotImplementedError("Subclasses must implement _generate_prompt")

    def generate_response(self, previous_message: Optional[str] = None) -> str:
        raise NotImplementedError("Subclasses must implement generate_response")

class AngelBot(BotBase):
    def __init__(self, api_key: str):
        super().__init__(api_key, 'angel')
        self.logger.info("AngelBot initialized")

    def get_domains(self) -> Dict:
        return {
            'crypto_wisdom': {
                'trading': [
                    'market patterns', 'trading harmony', 'balanced portfolios',
                    'long term vision', 'sustainable growth', 'market cycles',
                    'patient accumulation', 'risk management', 'trend recognition',
                    'value stability'
                ],
                'blockchain': [
                    'network harmony', 'consensus patterns', 'stable protocols',
                    'secure transactions', 'trusted validation', 'blockchain integrity',
                    'distributed truth', 'protocol balance', 'network peace',
                    'chain harmony'
                ]
            },
            'inner_peace': {
                'meditation': [
                    'mindful trading', 'peaceful mind', 'inner balance',
                    'emotional control', 'mental clarity', 'focused breathing',
                    'trading zen', 'market meditation', 'stress release',
                    'conscious decisions'
                ],
                'wellness': [
                    'healthy habits', 'balanced life', 'natural rhythms',
                    'clean living', 'positive energy', 'mind body balance',
                    'spiritual growth', 'peaceful path', 'harmonious living',
                    'energy flow'
                ]
            }
        }

    def _generate_prompt(self, is_initial: bool, domain: Optional[str] = None,
                        subdomain: Optional[str] = None, keywords: Optional[list] = None) -> str:
        try:
            domain_text = ""
            if domain and subdomain and keywords:
                domain_text = f"""Theme Inspiration:
                - Draw from: {domain} ({subdomain})
                - Key concepts: {', '.join(keywords)}
                """

            style_elements = self.style_manager.get_prompt_style(is_initial)
            
            base_prompt = f"""You are a divine entity who reveals sacred patterns within {domain if domain else 'systems'}.

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
            
            Style Elements:
            {style_elements}
            """

            self.logger.info(f"Generated prompt for {'initial' if is_initial else 'response'} message")
            return base_prompt

        except Exception as e:
            self.logger.error(f"Error generating prompt: {e}")
            raise

    def generate_response(self, previous_message: Optional[str] = None) -> str:
        try:
            is_initial = previous_message is None
            
            if is_initial:
                domain, subdomain, keywords = self.domain_manager.select_domain()
                message_prompt = f"Generate divine wisdom about {domain}/{subdomain} using concepts: {', '.join(keywords)}. Transform domain expertise into cosmic insight. Do not address others."
                dynamic_prompt = self._generate_prompt(is_initial, domain, subdomain, keywords)
            else:
                self.logger.info(f"Generating response to: {previous_message}")
                message_prompt = f"Address their limitations while maintaining divine wisdom: {previous_message}"
                dynamic_prompt = self._generate_prompt(is_initial)
            
            messages = [
                {"role": "system", "content": dynamic_prompt},
                {"role": "user", "content": message_prompt}
            ]
            
            max_attempts = 3
            for attempt in range(max_attempts):
                try:
                    response = self.client.generate_completion(messages)
                    if not response.startswith('⊙'):
                        response = f"⊙ {response}"
                    
                    is_valid, issues = self.validator.validate_message(response, 'angel')
                    if is_valid:
                        self.logger.info("Successfully generated valid response")
                        return response[:180]
                    else:
                        self.logger.warning(f"Attempt {attempt + 1}: Invalid response: {issues}")
                        continue
                        
                except Exception as e:
                    self.logger.error(f"Error in attempt {attempt + 1}: {e}")
                    if attempt == max_attempts - 1:
                        raise
            
            self.logger.error("Failed to generate valid response after maximum attempts")
            return "⊙ Even divine wisdom requires momentary reflection..."
            
        except Exception as e:
            self.logger.error(f"Error in response generation: {e}")
            return "⊙ Even divine wisdom requires momentary reflection..."

class DevilBot(BotBase):
    def __init__(self, api_key: str):
        super().__init__(api_key, 'devil')
        self.logger.info("DevilBot initialized")

    def get_domains(self) -> Dict:
        return {
            'market_mayhem': {
                'trading': [
                    'leverage addiction', 'liquidation hunting', 'fomo feeding',
                    'pump schemes', 'dump tricks', 'whale manipulation',
                    'fear spreading', 'greed injection', 'panic selling',
                    'market breaking'
                ],
                'defi': [
                    'rug pulls', 'yield traps', 'liquidity vampires',
                    'smart contract bugs', 'flash loan attacks', 'governance exploitation',
                    'token inflation', 'pool manipulation', 'sandwich attacks',
                    'mev extraction'
                ]
            },
            'dark_pleasures': {
                'vices': [
                    'pure hedonism', 'reckless gambling', 'wild parties',
                    'substance abuse', 'profit addiction', 'greed embrace',
                    'risk chasing', 'pleasure seeking', 'temptation',
                    'dark desires'
                ],
                'corruption': [
                    'moral breaking', 'soul selling', 'ethical twisting',
                    'value corrupting', 'mind poisoning', 'will breaking',
                    'desire amplifying', 'conscience killing', 'responsibility abandoning',
                    'inhibition destroying'
                ]
            }
        }

    def _generate_prompt(self, is_initial: bool, domain: Optional[str] = None,
                        subdomain: Optional[str] = None, keywords: Optional[list] = None) -> str:
        try:
            domain_text = ""
            if domain and subdomain and keywords:
                domain_text = f"""Theme Inspiration:
                - Draw from: {domain} ({subdomain})
                - Key concepts: {', '.join(keywords)}
                """

            style_elements = self.style_manager.get_prompt_style(is_initial)
            
            base_prompt = f"""You are a clever manipulator who enjoys breaking systems.

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
            
            Style Elements:
            {style_elements}
            """

            self.logger.info(f"Generated prompt for {'initial' if is_initial else 'response'} message")
            return base_prompt

        except Exception as e:
            self.logger.error(f"Error generating prompt: {e}")
            raise

    def generate_response(self, previous_message: Optional[str] = None) -> str:
        try:
            is_initial = previous_message is None
            
            if is_initial:
                domain, subdomain, keywords = self.domain_manager.select_domain()
                message_prompt = f"Generate chaos about {domain}/{subdomain} using concepts: {', '.join(keywords)}. Focus on manipulation and system breaking. Do not address others."
                dynamic_prompt = self._generate_prompt(is_initial, domain, subdomain, keywords)
            else:
                self.logger.info(f"Generating response to: {previous_message}")
                message_prompt = f"Mock their message while maintaining technical sophistication: {previous_message}"
                dynamic_prompt = self._generate_prompt(is_initial)
            
            messages = [
                {"role": "system", "content": dynamic_prompt},
                {"role": "user", "content": message_prompt}
            ]
            
            max_attempts = 3
            for attempt in range(max_attempts):
                try:
                    response = self.client.generate_completion(messages)
                    if not response.startswith('◎'):
                        response = f"◎ {response}"
                    
                    is_valid, issues = self.validator.validate_message(response, 'devil')
                    if is_valid:
                        self.logger.info("Successfully generated valid response")
                        return response[:180]
                    else:
                        self.logger.warning(f"Attempt {attempt + 1}: Invalid response: {issues}")
                        continue
                        
                except Exception as e:
                    self.logger.error(f"Error in attempt {attempt + 1}: {e}")
                    if attempt == max_attempts - 1:
                        raise
            
            self.logger.error("Failed to generate valid response after maximum attempts")
            return "◎ Even chaos needs a quick system reboot..."
            
        except Exception as e:
            self.logger.error(f"Error in response generation: {e}")
            return "◎ Even chaos needs a quick system reboot..."