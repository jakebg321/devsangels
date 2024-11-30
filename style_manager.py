from typing import Dict
import logging
from logger_config import setup_logger

logger = setup_logger('style_manager')

class StyleManager:
    def __init__(self, bot_type: str):
        self.bot_type = bot_type
        self.style_config = self._get_style_config()
        logger.info(f"StyleManager initialized for {bot_type}")

    def _get_style_config(self) -> Dict:
        """Get style configuration based on bot type"""
        if self.bot_type == 'angel':
            return {
                'initial_style': {
                    'transform_concepts': True,
                    'sacred_patterns': True,
                    'divine_terminology': True,
                    'avoid_references': True
                },
                'response_style': {
                    'spiritual_criticism': True,
                    'elevated_language': True,
                    'divine_perspective': True
                }
            }
        else:  # devil
            return {
                'initial_style': {
                    'system_manipulation': True,
                    'technical_focus': True,
                    'celebrate_breaking': True,
                    'avoid_references': True
                },
                'response_style': {
                    'mockery': True,
                    'crude_language': True,
                    'clever_threats': True
                }
            }

    def get_prompt_style(self, is_initial: bool) -> str:
        """Generate style-specific prompt section"""
        try:
            style_type = 'initial_style' if is_initial else 'response_style'
            style_elements = self.style_config[style_type]
            
            prompt_elements = []
            for element, enabled in style_elements.items():
                if enabled:
                    formatted_element = element.replace('_', ' ').capitalize()
                    prompt_elements.append(f"- {formatted_element}")

            style_prompt = "\n        ".join(prompt_elements)
            logger.info(f"Generated style prompt for {self.bot_type} ({style_type})")
            return style_prompt

        except Exception as e:
            logger.error(f"Error generating style prompt: {e}")
            raise