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

class ConversationTracker:
    def __init__(self):
        self.conversations = {}
        self.logger = setup_logger('conversation_tracker')
        
    def start_conversation(self, conversation_id: str, initiator: str, initial_tweet: str):
        self.conversations[conversation_id] = {
            'start_time': datetime.now(),
            'messages': [{
                'bot': initiator,
                'message': initial_tweet,
                'timestamp': datetime.now(),
                'delay_before': 0
            }],
            'status': 'active',
            'initiator': initiator,
            'reply_count': 0
        }
        
    def add_reply(self, conversation_id: str, bot: str, message: str, delay: float):
        if conversation_id in self.conversations:
            self.conversations[conversation_id]['messages'].append({
                'bot': bot,
                'message': message,
                'timestamp': datetime.now(),
                'delay_before': delay
            })
            self.conversations[conversation_id]['reply_count'] += 1

class ConversationManager:
    def __init__(self, angel_bot, devil_bot, live_mode=False, 
                 min_delay: int = 30, max_delay: int = 60,
                 test_mode: bool = True):
        self.angel_bot = angel_bot
        self.devil_bot = devil_bot
        self.min_delay = min_delay 
        self.max_delay = max_delay
        self.test_mode = test_mode  # If True, uses shorter delays
        self.conversation_queue = Queue()
        self.tracker = ConversationTracker()
        self.scheduler = ConversationScheduler(live_mode)
        self.logger = setup_logger('conversation_manager')
        self.running = False
        
        # Test mode adjustments
        if test_mode:
            self.min_delay = 5  # 5 seconds minimum delay
            self.max_delay = 10  # 10 seconds maximum delay
        
    def _generate_conversation_id(self) -> str:
        return f"conv_{int(time.time())}_{random.randint(1000, 9999)}"
        
    def start_conversation(self) -> Optional[str]:
        """Initiates a new conversation if timing allows"""
        try:
            if not self.scheduler.can_start_new_conversation():
                wait_time = (self.scheduler.last_conversation_time + 
                           self.scheduler.conversation_interval - datetime.now())
                self.logger.info(f"Must wait {wait_time} before starting new conversation")
                return None
                
            conversation_id = self._generate_conversation_id()
            starter = random.choice(['angel', 'devil'])
            
            # Generate initial tweet
            if starter == 'angel':
                initial_tweet = self.angel_bot.generate_response()
                self.logger.info(f"Angel started conversation: {initial_tweet}")
            else:
                initial_tweet = self.devil_bot.generate_response()
                self.logger.info(f"Devil started conversation: {initial_tweet}")
            
            # Track conversation
            self.tracker.start_conversation(conversation_id, starter, initial_tweet)
            self.scheduler.mark_conversation_started()
            
            # Print initial tweet (will be replaced with actual tweeting)
            print(f"\nNew Conversation ({conversation_id}):")
            print(f"{starter.upper()}: {initial_tweet}")
            
            # Queue for replies
            self.conversation_queue.put({
                'conversation_id': conversation_id,
                'last_bot': starter,
                'messages': [initial_tweet],
                'last_reply_time': datetime.now()
            })
            
            return conversation_id
            
        except Exception as e:
            self.logger.error(f"Error starting conversation: {e}")
            raise
            
    def _process_conversations(self):
        """Background thread to process conversation replies"""
        while self.running:
            try:
                if not self.conversation_queue.empty():
                    conv_data = self.conversation_queue.get()
                    
                    # Calculate and apply delay
                    delay = random.randint(self.min_delay, self.max_delay)
                    time.sleep(delay)
                    
                    conversation = self.tracker.conversations[conv_data['conversation_id']]
                    if conversation['reply_count'] >= 6:  # Limit conversation length
                        conversation['status'] = 'completed'
                        continue
                        
                    # Generate reply from opposite bot
                    last_message = conv_data['messages'][-1]
                    if conv_data['last_bot'] == 'angel':
                        reply = self.devil_bot.generate_response(last_message)
                        replying_bot = 'devil'
                    else:
                        reply = self.angel_bot.generate_response(last_message)
                        replying_bot = 'angel'
                    
                    # Calculate actual delay from last reply
                    actual_delay = (datetime.now() - conv_data['last_reply_time']).total_seconds()
                    
                    # Track reply
                    self.tracker.add_reply(conv_data['conversation_id'], replying_bot, reply, actual_delay)
                    
                    # Print reply with timing info (will be replaced with actual tweeting)
                    print(f"[Delay: {actual_delay:.1f}s] {replying_bot.upper()}: {reply}")
                    
                    # Queue next reply if conversation should continue
                    conv_data['last_bot'] = replying_bot
                    conv_data['messages'].append(reply)
                    conv_data['last_reply_time'] = datetime.now()
                    self.conversation_queue.put(conv_data)
                    
            except Exception as e:
                self.logger.error(f"Error processing conversation: {e}")
                
            time.sleep(1)  # Prevent busy waiting
            
    def get_conversation_timing_stats(self, conversation_id: str) -> Dict:
        """Get timing statistics for a conversation"""
        if conversation_id not in self.tracker.conversations:
            return {}
            
        conversation = self.tracker.conversations[conversation_id]
        messages = conversation['messages']
        
        return {
            'total_duration': (messages[-1]['timestamp'] - messages[0]['timestamp']).total_seconds(),
            'average_delay': sum(m['delay_before'] for m in messages[1:]) / max(len(messages) - 1, 1),
            'message_count': len(messages),
            'status': conversation['status']
        }
        
    def start(self):
        """Start the conversation manager"""
        self.running = True
        self.processor_thread = threading.Thread(target=self._process_conversations)
        self.processor_thread.daemon = True
        self.processor_thread.start()
        
    def stop(self):
        """Stop the conversation manager"""
        self.running = False
        if hasattr(self, 'processor_thread'):
            self.processor_thread.join(timeout=5)