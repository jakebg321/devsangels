import os

def mask_string(s: str) -> str:
    """Show only first 4 and last 4 characters of a string"""
    if not s:
        return "None"
    if len(s) <= 8:
        return s
    return f"{s[:4]}...{s[-4:]}"

def verify_tokens():
    print("Devil Bot Token Verification:")
    print("=" * 50)
    
    # List all expected token environment variables
    token_vars = {
        'TWITTER_DEVIL_API_KEY': os.getenv('TWITTER_DEVIL_API_KEY'),
        'TWITTER_DEVIL_API_SECRET': os.getenv('TWITTER_DEVIL_API_SECRET'),
        'TWITTER_DEVIL_ACCESS_TOKEN': os.getenv('TWITTER_DEVIL_ACCESS_TOKEN'),
        'TWITTER_DEVIL_ACCESS_TOKEN_SECRET': os.getenv('TWITTER_DEVIL_ACCESS_TOKEN_SECRET')
    }
    
    for var_name, value in token_vars.items():
        if value:
            # Print length and partial value
            print(f"{var_name}:")
            print(f"  Length: {len(value)} characters")
            print(f"  Value: {mask_string(value)}")
            print(f"  Contains spaces: {'Yes' if ' ' in value else 'No'}")
            # Check for newlines without using escape sequence in f-string
            has_newline = "Yes" if "\n" in value else "No"
            print(f"  Contains newlines: {has_newline}")
            print()
        else:
            print(f"{var_name}: Not set")
            print()

if __name__ == "__main__":
    verify_tokens()