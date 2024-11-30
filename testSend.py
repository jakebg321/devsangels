import time
from angelBot import AngelBot
from devilBot import DevilBot
from conversations import ConversationManager
import os

def test_conversation_flow():
    # Initialize with test mode to avoid actual Twitter posts
    angel_bot = AngelBot(os.getenv('GROK_API_KEY'))
    devil_bot = DevilBot(os.getenv('GROK_API_KEY'))
    
    # Create conversation manager in test mode with shorter delays
    conversation_manager = ConversationManager(
        angel_bot=angel_bot,
        devil_bot=devil_bot,
        test_mode=True,  # Prevents actual Twitter posts
        min_delay=2,     # Shorter delays for testing
        max_delay=5
    )
    
    # Start the conversation manager
    conversation_manager.start()
    
    # Start a new conversation
    conversation_id = conversation_manager.start_conversation()
    if not conversation_id:
        print("Failed to start conversation")
        return
    
    print(f"Started conversation: {conversation_id}")
    
    # Monitor the conversation
    start_time = time.time()
    timeout = 60  # 1 minute timeout
    
    while time.time() - start_time < timeout:
        # Get current conversation state
        conv = conversation_manager.tracker.conversations.get(conversation_id)
        if not conv:
            print("Conversation not found")
            break
            
        # Print current state
        messages = conv['messages']
        print(f"\nConversation status: {conv['status']}")
        print(f"Reply count: {conv['reply_count']}")
        
        print("\nMessage chain:")
        for idx, msg in enumerate(messages):
            print(f"{idx + 1}. {msg['bot']}: {msg['message'][:50]}...")
            
        # Check if conversation is completed
        if conv['status'] == 'completed':
            print("\nConversation completed!")
            break
            
        # Wait before next check
        time.sleep(2)
    
    # Print final statistics
    stats = conversation_manager.get_conversation_timing_stats(conversation_id)
    print("\nFinal Statistics:")
    print(f"Total duration: {stats['total_duration']:.2f} seconds")
    print(f"Average delay: {stats['average_delay']:.2f} seconds")
    print(f"Message count: {stats['message_count']}")
    
    # Stop the conversation manager
    conversation_manager.stop()

if __name__ == "__main__":
    if not os.getenv('GROK_API_KEY'):
        print("Please set GROK_API_KEY environment variable")
        exit(1)
    
    print("Starting conversation test...")
    test_conversation_flow()