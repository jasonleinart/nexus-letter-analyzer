# Setup Instructions for Nexus Letter Analyzer

## 🔑 Add Your OpenAI API Key

1. **Edit the .env file** in the nexus-letter-analyzer directory
2. Replace `your_openai_api_key_here` with your actual OpenAI API key
3. Your .env file should look like:

```
# OpenAI API Configuration
OPENAI_API_KEY=sk-your-actual-api-key-here

# Application Configuration
APP_NAME=Nexus Letter AI Analyzer
APP_VERSION=1.0.0
DEBUG=False
```

## 🚀 Run the App

After adding your API key:

```bash
cd nexus-letter-analyzer
source venv/bin/activate
streamlit run app.py
```

## 🔍 Verify Setup

The app will show an error message if:
- No API key is provided
- The API key is invalid
- The API key doesn't start with "sk-"

## 💡 Get an OpenAI API Key

If you don't have an API key:
1. Go to https://platform.openai.com/api-keys
2. Sign up or log in
3. Create a new API key
4. Copy the key (it starts with "sk-")
5. Add it to your .env file