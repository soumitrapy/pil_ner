#!/bin/bash
# Script to remove large model files from Git repository

echo "==================================================================="
echo "Removing Large Model Files from Git Repository"
echo "==================================================================="

# Step 1: Check current status
echo ""
echo "Step 1: Checking for large files in repository..."
echo "-------------------------------------------------------------------"
git ls-files | xargs du -h 2>/dev/null | grep -E '[0-9]+M' | sort -hr

# Step 2: Remove model files from Git (but keep them locally)
echo ""
echo "Step 2: Removing large files from Git tracking..."
echo "-------------------------------------------------------------------"

# Remove common large model files
git rm --cached -r out/ 2>/dev/null
git rm --cached data/*_generated.jsonl 2>/dev/null
git rm --cached data/*_final.jsonl 2>/dev/null

# Step 3: Update .gitignore
echo ""
echo "Step 3: Updating .gitignore to prevent future commits..."
echo "-------------------------------------------------------------------"

cat >> .gitignore << 'EOF'

# Model outputs and large files
out/
*.bin
*.safetensors
*.pt
*.pth
*.h5
*.ckpt

# Generated data
data/*_generated.jsonl
data/*_final.jsonl

# Logs
logs/
*.log

# Results
results_*.txt

# Python cache
__pycache__/
*.pyc
*.pyo
.pytest_cache/

# IDEs
.vscode/
.idea/
*.swp
*.swo
EOF

echo "Updated .gitignore"

# Step 4: Commit the changes
echo ""
echo "Step 4: Committing changes..."
echo "-------------------------------------------------------------------"
git add .gitignore
git commit -m "Remove large model files and update .gitignore"

# Step 5: Show what's left
echo ""
echo "Step 5: Verifying - files remaining in Git:"
echo "-------------------------------------------------------------------"
git ls-files | head -20

echo ""
echo "==================================================================="
echo "✓ Done! Large files removed from Git repository"
echo "==================================================================="
echo ""
echo "Files still on disk (not tracked by Git):"
ls -lh out/ 2>/dev/null | head -10
echo ""
echo "You can now push:"
echo "  git push origin main"
echo ""
