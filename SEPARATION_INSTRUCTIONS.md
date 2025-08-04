# Project Separation Instructions

## Current Situation

The nexus-letter-analyzer project is currently inside the AgentProject folder, but it should be its own separate project.

**Current location**: 
```
/Workspace/AgentProject/nexus-letter-analyzer/
```

**Should be at one of these**:
```
/Workspace/nexus-letter-analyzer/              # Option 1: Direct in Workspace
/Workspace/Site/nexus-letter-analyzer/         # Option 2: In Site folder (where original was)
```

## Steps to Separate the Projects

### Option 1: Move to Workspace Root (Recommended)

```bash
# 1. Navigate to Workspace directory
cd /Users/jasonleinart/Library/Mobile\ Documents/com\~apple\~CloudDocs/Workspace/

# 2. Move the nexus-letter-analyzer out of AgentProject
mv AgentProject/nexus-letter-analyzer ./

# 3. Navigate to the moved project
cd nexus-letter-analyzer/

# 4. Initialize its own git repository
rm -rf .git  # Remove any parent git tracking
git init
git add .
git commit -m "Initial commit: Nexus Letter AI Analyzer"

# 5. Push to GitHub
git remote add origin https://github.com/jasonleinart/nexus-letter-analyzer.git
git branch -M main
git push -u origin main
```

### Option 2: Move to Site Folder (Replacing Original)

```bash
# 1. Backup the original (if needed)
cd /Users/jasonleinart/Library/Mobile\ Documents/com\~apple\~CloudDocs/Workspace/Site/
mv nexus-letter-analyzer nexus-letter-analyzer-original

# 2. Move the completed project from AgentProject
cd /Users/jasonleinart/Library/Mobile\ Documents/com\~apple\~CloudDocs/Workspace/
mv AgentProject/nexus-letter-analyzer Site/

# 3. Navigate to the moved project
cd Site/nexus-letter-analyzer/

# 4. Initialize its own git repository
rm -rf .git
git init
git add .
git commit -m "Initial commit: Nexus Letter AI Analyzer"

# 5. Push to GitHub
git remote add origin https://github.com/jasonleinart/nexus-letter-analyzer.git
git branch -M main
git push -u origin main
```

## Clean Up AgentProject

After moving nexus-letter-analyzer out:

```bash
# Navigate to AgentProject
cd /Users/jasonleinart/Library/Mobile\ Documents/com\~apple\~CloudDocs/Workspace/AgentProject/

# Update the workspace file to remove nexus-letter-analyzer reference
# Edit AgentProject.code-workspace and remove the nexus-letter-analyzer folder entry

# Commit the removal in AgentProject
git add -A
git commit -m "Removed nexus-letter-analyzer (moved to separate project)"
```

## Verify Separation

After separation, you should have:

1. **AgentProject** at `/Workspace/AgentProject/` - for arXiv research papers
2. **nexus-letter-analyzer** at `/Workspace/nexus-letter-analyzer/` - standalone project

Each with its own:
- Separate git repository
- Independent GitHub remote
- No cross-references

## Important Notes

- The .env file with your API key will move with the project
- The .gitignore ensures .env won't be tracked by git
- All documentation, tests, and milestones will move together
- The virtual environment (venv/) will need to be recreated after moving

## After Moving

1. Update any absolute paths in your code (if any)
2. Recreate virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. Test the application still works:
   ```bash
   streamlit run app.py
   ```