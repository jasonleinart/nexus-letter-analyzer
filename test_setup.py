"""Test script to verify OpenAI API key setup."""

import os
from dotenv import load_dotenv
from config import validate_openai_key

# Load environment variables
load_dotenv()

def test_api_key():
    """Test if OpenAI API key is properly configured."""
    api_key = os.getenv("OPENAI_API_KEY", "")
    
    print("🔍 Testing OpenAI API Key Setup...")
    print("-" * 50)
    
    # Check if key exists
    if not api_key or api_key == "your_openai_api_key_here":
        print("❌ ERROR: No valid API key found!")
        print("\n📝 To fix this:")
        print("1. Edit the .env file in this directory")
        print("2. Replace 'your_openai_api_key_here' with your actual OpenAI API key")
        print("3. Your key should start with 'sk-'")
        print("\n💡 Get an API key at: https://platform.openai.com/api-keys")
        return False
    
    # Validate key format
    is_valid, message = validate_openai_key(api_key)
    
    if is_valid:
        print(f"✅ SUCCESS: {message}")
        print(f"🔑 API Key: {api_key[:10]}...{api_key[-4:]}")
        print("\n🚀 Your setup is complete! You can now run:")
        print("   streamlit run app.py")
        return True
    else:
        print(f"❌ ERROR: {message}")
        return False

if __name__ == "__main__":
    test_api_key()