#!/bin/bash

# Nexus Letter Analyzer - Start Script

echo "🚀 Starting Nexus Letter Analyzer..."

# Navigate to app directory
cd "$(dirname "$0")"

# Activate virtual environment
source venv/bin/activate

# Kill any existing Streamlit processes
pkill -f streamlit 2>/dev/null

# Start Streamlit
echo "📊 Launching Streamlit app..."
streamlit run app.py

# Note: Press Ctrl+C to stop the app