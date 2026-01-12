# GitHub Setup Guide

## Quick Setup

Run the setup script:
```bash
cd /Users/coopersmith/radio-scrobbler
./setup_github.sh
```

This will:
- Initialize git repository
- Stage all files (excluding secrets via .gitignore)
- Create initial commit
- Show you next steps

## Manual Setup

If you prefer to do it manually:

### 1. Initialize Git
```bash
cd /Users/coopersmith/radio-scrobbler
git init
```

### 2. Add Files
```bash
git add .
```

**Important:** The `.gitignore` file excludes:
- `config/stations.yaml` (contains your passwords!)
- `venv/` (virtual environment)
- `logs/` (log files)
- `.env` (environment variables)

### 3. Verify What Will Be Committed
```bash
git status
```

Make sure `config/stations.yaml` is NOT listed!

### 4. Create Initial Commit
```bash
git commit -m "Initial commit: Radio Scrobbler"
```

### 5. Create GitHub Repository

1. Go to https://github.com/new
2. Create a new repository (e.g., `radio-scrobbler`)
3. **Don't** initialize with README, .gitignore, or license (we already have these)

### 6. Push to GitHub

```bash
git remote add origin https://github.com/YOUR_USERNAME/radio-scrobbler.git
git branch -M main
git push -u origin main
```

## After Pushing

Once your code is on GitHub, you can:

1. **Deploy to Railway:**
   - Go to [railway.app](https://railway.app)
   - New Project → Deploy from GitHub
   - Select your repository
   - Add environment variables (see CLOUD_DEPLOYMENT.md)

2. **Share the project:**
   - Others can fork/clone it
   - They'll need to create their own `config/stations.yaml`

## Security Checklist

Before pushing, verify:
- ✅ `config/stations.yaml` is in `.gitignore`
- ✅ No API keys or passwords in committed files
- ✅ `.env` file is excluded
- ✅ `venv/` is excluded

Check with:
```bash
git status
git ls-files | grep -E "(stations.yaml|\.env)"
```

If the second command shows any files, they shouldn't be committed!
