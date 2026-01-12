#!/bin/bash
# Setup script to push project to GitHub

set -e

echo "🚀 Setting up GitHub repository..."
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install git first."
    exit 1
fi

# Initialize git repo if not already initialized
if git rev-parse --git-dir > /dev/null 2>&1; then
    echo "✓ Git repository already initialized"
elif [ -d ".git" ]; then
    echo "⚠️  .git directory exists but not a valid repo. Reinitializing..."
    rm -rf .git
    git init
    echo "✓ Git repository reinitialized"
else
    echo "📦 Initializing git repository..."
    git init
    echo "✓ Git repository initialized"
fi

# Check if config/stations.yaml exists and warn
if [ -f "config/stations.yaml" ]; then
    echo "⚠️  WARNING: config/stations.yaml contains secrets and should NOT be committed!"
    echo "   It's already in .gitignore, so it won't be committed."
    echo ""
fi

# Add all files (gitignore will exclude secrets)
echo "📝 Staging files..."
git add .

# Show what will be committed
echo ""
echo "Files to be committed:"
git status --short

echo ""
read -p "Continue with commit? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
fi

# Create initial commit
echo ""
echo "💾 Creating initial commit..."
git commit -m "Initial commit: Radio Scrobbler - Multi-station Last.fm scrobbler

- Supports multiple radio stations via plugin architecture
- Uses Online Radio Box as track data source
- Configurable polling intervals
- Docker and cloud deployment ready"

echo ""
echo "✅ Commit created!"
echo ""
echo "📤 Next steps to push to GitHub:"
echo ""
echo "1. Create a new repository on GitHub:"
echo "   https://github.com/new"
echo ""
echo "2. Then run these commands (replace YOUR_USERNAME and REPO_NAME):"
echo ""
echo "   git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "3. Or if you already created the repo, GitHub will show you the commands."
echo ""
echo "⚠️  IMPORTANT: Make sure config/stations.yaml is NOT pushed!"
echo "   It's in .gitignore, but double-check with: git status"
