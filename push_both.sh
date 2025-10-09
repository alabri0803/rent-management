#!/bin/bash
# Script to push to both GitHub and GitLab
echo "Pushing to GitHub..."
git push origin
echo "Pushing to GitLab..."
git push gitlab
echo "Done! Changes pushed to both repositories."
