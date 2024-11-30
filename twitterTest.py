import tweepy

def test_v2_post():
    print("Testing Twitter V2 API Direct Posting")
    print("=" * 50)
    
    # Your full set of credentials
    api_key = "Zg6zo0PHi6ItiALZ6Q9tsWmKh"
    api_secret = "vqPhb1mUdBbSSub7KMrxV021ZTz82ISNmPti1KENsXBTXnar9q"
    bearer_token = "AAAAAAAAAAAAAAAAAAAAAHIexQEAAAAArO%2BdRo2bPAKHEeJS5z%2Fj%2BRPALro%3DnbVvoiAtq2MBZqYk78Rp0LwD2ibtbQLqEa3njLFLssjdYsX3lM"

    
    try:
        # Create client with all authentication methods
        client = tweepy.Client(
            bearer_token=bearer_token,
            consumer_key=api_key,
            consumer_secret=api_secret,
            # You need access token and access token secret too
            # These should be available in your Twitter Developer Portal
            access_token="1862927306970267648-bY5hYMGqxdn1picu1FK4fdecS5XfmW",
            access_token_secret="GKAWLe0W6zrZ9gF99riuqxC7iwzVNqyT56QCwQIzv9Uux"
        )
        
        # Try to post
        response = client.create_tweet(text="Test tweet from V2 API")
        
        if response.data:
            tweet_id = response.data['id']
            print(f"✅ Successfully posted tweet! ID: {tweet_id}")
            print(f"Tweet URL: https://twitter.com/i/status/{tweet_id}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        if hasattr(e, 'response') and e.response:
            print(f"Response status: {e.response.status_code}")
            print(f"Response text: {e.response.text}")

if __name__ == "__main__":
    test_v2_post()