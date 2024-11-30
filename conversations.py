from typing import Dict, List, Optional
import time
import threading
from queue import Queue
import random
from datetime import datetime, timedelta
import logging
from logger_config import setup_logger

class ConversationScheduler:
    def __init__(self, live_mode=False):
        self.live_mode = live_mode
        self.last_conversation_time = None
        self.conversation_interval = timedelta(minutes=30 if live_mode else 1)
        self.logger = setup_logger('conversation_scheduler')
        
    def can_start_new_conversation(self) -> bool:
        if not self.last_conversation_time:
            return True
        time_since_last = datetime.now() - self.last_conversation_time
        return time_since_last >= self.conversation_interval
        
    def mark_conversation_started(self):
        self.last_conversation_time = datetime.now()

    def get_wait_time(self) -> timedelta:
        if not self.last_conversation_time:
            return timedelta(0)
        return max(
            timedelta(0),
            self.conversation_interval - (datetime.now() - self.last_conversation_time)
        )

class ConversationTracker:
    def __init__(self):
        self.conversations = {}
        self.logger = setup_logger('conversation_tracker')
        
    def start_conversation(self, conversation_id: str, initiator: str, initial_tweet: str, tweet_id: Optional[str] = None):
        self.conversations[conversation_id] = {
            'start_time': datetime.now(),
            'messages': [{
                'bot': initiator,
                'message': initial_tweet,
                'timestamp': datetime.now(),
                'delay_before': 0,
                'tweet_id': tweet_id
            }],
            'status': 'active',
            'initiator': initiator,
            'reply_count': 0,
            'last_error': None
        }
        
    def add_reply(self, conversation_id: str, bot: str, message: str, delay: float, tweet_id: Optional[str] = None):
        if conversation_id in self.conversations:
            self.conversations[conversation_id]['messages'].append({
                'bot': bot,
                'message': message,
                'timestamp': datetime.now(),
                'delay_before': delay,
                'tweet_id': tweet_id
            })
            self.conversations[conversation_id]['reply_count'] += 1
            
    def mark_error(self, conversation_id: str, error: str):
        if conversation_id in self.conversations:
            self.conversations[conversation_id]['last_error'] = {
                'error': str(error),
                'timestamp': datetime.now()
            }
            
    def get_last_tweet_id(self, conversation_id: str) -> Optional[str]:
        if conversation_id in self.conversations:
            for message in reversed(self.conversations[conversation_id]['messages']):
                if message.get('tweet_id'):
                    return message['tweet_id']
        return None

class ConversationManager:
    def __init__(self, angel_bot, devil_bot, live_mode=False, 
                 min_delay: int = 30, max_delay: int = 60,
                 test_mode: bool = False,
                 max_retries: int = 3):
        self.angel_bot = angel_bot
        self.devil_bot = devil_bot
        self.min_delay = min_delay 
        self.max_delay = max_delay
        self.test_mode = test_mode
        self.max_retries = max_retries
        self.conversation_queue = Queue()
        self.tracker = ConversationTracker()
        self.scheduler = ConversationScheduler(live_mode)
        self.logger = setup_logger('conversation_manager')
        self.running = False
        self.error_count = 0
        self.last_error_time = None
        
    def _generate_conversation_id(self) -> str:
        return f"conv_{int(time.time())}_{random.randint(1000, 9999)}"

    def _post_to_twitter(self, bot, message: str, reply_to_id: Optional[str] = None) -> Optional[str]:
        for attempt in range(self.max_retries):
            try:
                tweet_id = bot.post_to_twitter(message, reply_to_id)
                if tweet_id:
                    return tweet_id
            except Exception as e:
                self.logger.error(f"Twitter post attempt {attempt + 1} failed: {e}")
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(2 ** attempt)  # Exponential backoff
        return None
        
    def start_conversation(self) -> Optional[str]:
        try:
            if not self.scheduler.can_start_new_conversation():
                wait_time = self.scheduler.get_wait_time()
                self.logger.info(f"Must wait {wait_time} before starting new conversation")
                return None
                
            conversation_id = self._generate_conversation_id()
            starter = random.choice(['angel', 'devil'])
            
            # Generate initial tweet
            bot = self.angel_bot if starter == 'angel' else self.devil_bot
            initial_tweet = bot.generate_response()
            
            # Post to Twitter if not in test mode
            tweet_id = None
            if not self.test_mode:
                tweet_id = self._post_to_twitter(bot, initial_tweet)
            
            # Track conversation
            self.tracker.start_conversation(conversation_id, starter, initial_tweet, tweet_id)
            self.scheduler.mark_conversation_started()
            
            # Print initial tweet
            print(f"\nNew Conversation ({conversation_id}):")
            print(f"{starter.upper()}: {initial_tweet}")
            
            # Queue for replies
            self.conversation_queue.put({
                'conversation_id': conversation_id,
                'last_bot': starter,
                'messages': [initial_tweet],
                'last_reply_time': datetime.now(),
                'retry_count': 0
            })
            
            return conversation_id
            
        except Exception as e:
            self.logger.error(f"Error starting conversation: {e}")
            self.error_count += 1
            self.last_error_time = datetime.now()
            raise
            
    def _process_conversations(self):
        while self.running:
            try:
                if not self.conversation_queue.empty():
                    conv_data = self.conversation_queue.get()
                    
                    # Check retry count
                    if conv_data.get('retry_count', 0) >= self.max_retries:
                        self.logger.error(f"Max retries reached for conversation {conv_data['conversation_id']}")
                        continue
                    
                    # Calculate and apply delay
                    delay = random.randint(self.min_delay, self.max_delay)
                    time.sleep(delay)
                    
                    conversation = self.tracker.conversations[conv_data['conversation_id']]
                    if conversation['reply_count'] >= 6 or conversation['status'] != 'active':
                        conversation['status'] = 'completed'
                        continue
                        
                    # Generate reply from opposite bot
                    last_message = conv_data['messages'][-1]
                    if conv_data['last_bot'] == 'angel':
                        reply = self.devil_bot.generate_response(last_message)
                        replying_bot = 'devil'
                        bot = self.devil_bot
                    else:
                        reply = self.angel_bot.generate_response(last_message)
                        replying_bot = 'angel'
                        bot = self.angel_bot
                    
                    # Post to Twitter if not in test mode
                    tweet_id = None
                    if not self.test_mode:
                        reply_to_id = self.tracker.get_last_tweet_id(conv_data['conversation_id'])
                        tweet_id = self._post_to_twitter(bot, reply, reply_to_id)
                    
                    # Calculate actual delay from last reply
                    actual_delay = (datetime.now() - conv_data['last_reply_time']).total_seconds()
                    
                    # Track reply
                    self.tracker.add_reply(conv_data['conversation_id'], replying_bot, reply, actual_delay, tweet_id)
                    
                    # Print reply with timing info
                    self.logger.info(f"[Delay: {actual_delay:.1f}s] {replying_bot.upper()}: {reply}")
                    
                    # Queue next reply if conversation should continue
                    conv_data['last_bot'] = replying_bot
                    conv_data['messages'].append(reply)
                    conv_data['last_reply_time'] = datetime.now()
                    conv_data['retry_count'] = 0  # Reset retry count for next message
                    self.conversation_queue.put(conv_data)
                    
            except Exception as e:
                self.logger.error(f"Error processing conversation: {e}")
                conv_data['retry_count'] = conv_data.get('retry_count', 0) + 1
                if conv_data['retry_count'] < self.max_retries:
                    self.conversation_queue.put(conv_data)  # Retry
                self.error_count += 1
                self.last_error_time = datetime.now()
                
            time.sleep(1)  # Prevent busy waiting

    def get_conversation_timing_stats(self, conversation_id: str) -> Dict:
        if conversation_id not in self.tracker.conversations:
            return {}
            
        conversation = self.tracker.conversations[conversation_id]
        messages = conversation['messages']
        
        return {
            'total_duration': (messages[-1]['timestamp'] - messages[0]['timestamp']).total_seconds(),
            'average_delay': sum(m['delay_before'] for m in messages[1:]) / max(len(messages) - 1, 1),
            'message_count': len(messages),
            'status': conversation['status'],
            'error_count': self.error_count,
            'last_error': conversation.get('last_error'),
            'tweet_ids': [m.get('tweet_id') for m in messages if m.get('tweet_id')]
        }

    def process_conversation_queue(self):
        self._process_conversations()
            
    def start(self):
        self.running = True
        self.processor_thread = threading.Thread(target=self.process_conversation_queue)
        self.processor_thread.daemon = True
        self.processor_thread.start()
        self.logger.info("Conversation manager started")

    def stop(self):
        self.running = False
        if hasattr(self, 'processor_thread'):
            self.processor_thread.join(timeout=5)
        self.logger.info("Conversation manager stopped")