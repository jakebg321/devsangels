import tweepy
import os
from dotenv import load_dotenv
import logging
import random

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_twitter_bots():
    """Test both Angel and Devil bot configurations with V1 and V2 endpoints"""
    print("\n=== Testing Twitter API Integration for Both Bots ===\n")
    
    # Load environment variables
    load_dotenv()

    # Bot configurations
    bot_configs = {
        'ANGEL': {
            'api_key': 'V4yDCusnZDp2MRg1UwlCKGxrh',
            'api_secret': '5FZbnhAvNVRYC7G6ycWbxzEE140tnGhCxFDthKsQRkbZXrAJZv',
            'access_token': '1862929101985660929-sJwVak8OIz2O3y8a8nRdn8fq3g0H4H',
            'access_token_secret': 'J1apCajZ0i6OqXcFOby5o4Qiwl1kJ8IBpAfqFRiaTBV36'
        },
        'DEVIL': {
            'api_key': 'Zg6zo0PHi6ItiALZ6Q9tsWmKh',
            'api_secret': 'vqPhb1mUdBbSSub7KMrxV021ZTz82ISNmPti1KENsXBTXnar9q',
            'access_token': '1862927306970267648-bY5hYMGqxdn1picu1FK4fdecS5XfmW',
            'access_token_secret': 'GKAWLe0W6zrZ9gF99riuqxC7iwzVNqyT56QCwQIzv9Uux'
        }
    }

    for bot_name, config in bot_configs.items():
        print(f"\nTesting {bot_name} Bot:")
        print("=" * 50)

        try:
            # Test V2 Endpoint
            print("\nTesting V2 API:")
            client = tweepy.Client(
                consumer_key=config['api_key'],
                consumer_secret=config['api_secret'],
                access_token=config['access_token'],
                access_token_secret=config['access_token_secret']
            )
            
            # Verify credentials
            user = client.get_me()
            print(f"✅ V2 Auth Success - Authenticated as @{user.data.username}")
            
            # Generate a unique test message
            random_suffix = ''.join(random.choices('0123456789', k=4))
            test_message = f"Test tweet from {bot_name} bot using V2 API - {random_suffix}"
            
            # Post test tweet
            response = client.create_tweet(text=test_message)
            if response.data:
                tweet_id = response.data['id']
                print(f"✅ V2 Tweet Success!")
                print(f"   Tweet ID: {tweet_id}")
                print(f"   Tweet URL: https://twitter.com/i/status/{tweet_id}")
                print(f"   Content: {test_message}")

            # Test reply functionality
            if response.data:
                reply_text = f"Reply test from {bot_name} bot - {random_suffix}"
                reply = client.create_tweet(
                    text=reply_text,
                    in_reply_to_tweet_id=tweet_id
                )
                if reply.data:
                    print(f"✅ V2 Reply Success!")
                    print(f"   Reply ID: {reply.data['id']}")

        except Exception as e:
            print(f"❌ V2 Error for {bot_name} bot: {str(e)}")
            if hasattr(e, 'response') and e.response:
                print(f"   Response status: {e.response.status_code}")
                print(f"   Response text: {e.response.text}")

def main():
    try:
        test_twitter_bots()
    except Exception as e:
        print(f"❌ Global error: {str(e)}")

if __name__ == "__main__":
    main()