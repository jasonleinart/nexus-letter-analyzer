# GitHub Push Instructions

Follow these steps to push the nexus-letter-analyzer to GitHub:

## 1. Open Terminal

Navigate to the project directory:
```bash
cd /Users/jasonleinart/Library/Mobile\ Documents/com\~apple\~CloudDocs/Workspace/AgentProject/nexus-letter-analyzer
```

## 2. Initialize Git Repository

```bash
# Remove any parent git tracking (if exists)
rm -rf .git

# Initialize new repository
git init
```

## 3. Verify .gitignore

Check that .env is listed in .gitignore:
```bash
cat .gitignore | grep .env
```

You should see:
```
.env
.env.local
.env.*.local
```

## 4. Add Files to Git

```bash
# Add all files (respecting .gitignore)
git add .

# Verify .env is NOT being tracked
git status --porcelain | grep "\.env$"
# Should return nothing (no output)

# If .env is being tracked, remove it:
# git rm --cached .env
```

## 5. Create Initial Commit

```bash
git commit -m "Initial commit: Nexus Letter AI Analyzer

AI-powered nexus letter analysis system for disability law firms.
Features real OpenAI GPT-4 integration for comprehensive letter evaluation."
```

## 6. Add GitHub Remote

```bash
# Add remote repository
git remote add origin https://github.com/jasonleinart/nexus-letter-analyzer.git

# Verify remote was added
git remote -v
```

## 7. Create Main Branch and Push

```bash
# Ensure we're on main branch
git branch -M main

# Push to GitHub
git push -u origin main
```

## 8. Verify on GitHub

Visit: https://github.com/jasonleinart/nexus-letter-analyzer

## Important Files to Verify

These files SHOULD be pushed:
- ✅ app.py
- ✅ ai_analyzer.py
- ✅ text_processor.py
- ✅ config.py
- ✅ sample_letters.py
- ✅ requirements.txt
- ✅ .env.example
- ✅ .gitignore
- ✅ README.md
- ✅ DEMO.md
- ✅ All milestone and test documentation

These files should NOT be pushed:
- ❌ .env (contains your API key)
- ❌ venv/ (virtual environment)
- ❌ __pycache__/
- ❌ *.log files
- ❌ .DS_Store

## If You Need to Create the GitHub Repository First

1. Go to https://github.com/new
2. Repository name: `nexus-letter-analyzer`
3. Description: `AI-powered nexus letter analysis system for VA disability claims`
4. Set to Public or Private as desired
5. Do NOT initialize with README, .gitignore, or license
6. Click "Create repository"
7. Follow the push instructions above

## Troubleshooting

If you get "remote origin already exists":
```bash
git remote remove origin
git remote add origin https://github.com/jasonleinart/nexus-letter-analyzer.git
```

If you get authentication errors:
- Use a Personal Access Token instead of password
- Create one at: https://github.com/settings/tokens
- Use token as password when prompted