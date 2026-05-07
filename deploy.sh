#!/bin/bash
# Deploy to GitHub

echo "Committing changes..."
git add -A
git commit -m "Update: $(date)"

echo "Ready to push!"
echo ""
echo "To push to GitHub, run:"
echo "  git remote add origin https://github.com/YOUR_USERNAME/openclaw.git"
echo "  git branch -M main"
echo "  git push -u origin main"
