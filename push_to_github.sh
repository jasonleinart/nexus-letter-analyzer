#!/bin/bash

# Push nexus-letter-analyzer to GitHub

echo "🚀 Preparing to push nexus-letter-analyzer to GitHub..."

# Ensure we're in the right directory
cd /Users/jasonleinart/Library/Mobile\ Documents/com\~apple\~CloudDocs/Workspace/AgentProject/nexus-letter-analyzer

# Remove any existing git tracking (if we're in a subdirectory of another repo)
rm -rf .git 2>/dev/null

# Initialize new git repository
echo "📂 Initializing git repository..."
git init

# Add all files except those in .gitignore
echo "📝 Adding files to git..."
git add .

# Check that .env is not being tracked
echo "🔒 Verifying .env is not tracked..."
git status --porcelain | grep -E "^A.*\.env$"
if [ $? -eq 0 ]; then
    echo "❌ ERROR: .env file is being tracked! Removing..."
    git rm --cached .env
fi

# Create initial commit
echo "💾 Creating initial commit..."
git commit -m "Initial commit: Nexus Letter AI Analyzer

AI-powered nexus letter analysis system for disability law firms.
Features real OpenAI GPT-4 integration for comprehensive letter evaluation.

Built for Disability Law Group interview demonstration."

# Add remote repository
echo "🔗 Adding remote repository..."
git remote add origin https://github.com/jasonleinart/nexus-letter-analyzer.git

# Create main branch
git branch -M main

# Push to GitHub
echo "📤 Pushing to GitHub..."
git push -u origin main

echo "✅ Successfully pushed to GitHub!"
echo "🌐 View your repository at: https://github.com/jasonleinart/nexus-letter-analyzer"