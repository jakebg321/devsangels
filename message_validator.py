from typing import Dict, Tuple
import logging
from logger_config import setup_logger

logger = setup_logger('message_validator')

class MessageValidator:
    def __init__(self):
        self.MAX_LENGTH = 180
        logger.info("MessageValidator initialized")

    def validate_message(self, message: str, bot_type: str) -> Tuple[bool, Dict]:
        try:
            issues = {}

            # First, truncate the message if it's too long
            message = message[:self.MAX_LENGTH]
            
            # Check prefix
            expected_prefix = '⊙' if bot_type == 'angel' else '◎'
            if not message.startswith(expected_prefix):
                issues['prefix'] = f"Message must start with {expected_prefix}"
                logger.warning(f"Invalid prefix in message")

            # Basic content validation
            if len(message.split()) < 3:
                issues['content'] = "Message too short"
                logger.warning("Message too short")

            is_valid = len(issues) == 0
            if is_valid:
                logger.info("Message validation successful")
            else:
                logger.warning(f"Message validation failed: {issues}")

            return is_valid, issues

        except Exception as e:
            logger.error(f"Error in message validation: {str(e)}")
            raise