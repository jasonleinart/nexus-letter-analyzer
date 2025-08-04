#!/bin/bash

echo "🚀 Starting Nexus Letter AI Analyzer - Milestone 2"
echo "=================================================="
echo ""
echo "New features in Milestone 2:"
echo "✅ Enhanced scoring (0-100 points)"
echo "✅ Professional recommendations"  
echo "✅ Analytics dashboard"
echo "✅ Database tracking"
echo ""
echo "Starting Streamlit application..."
echo ""

cd "$(dirname "$0")"
streamlit run app.py --server.port 8501