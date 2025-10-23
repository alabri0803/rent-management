#!/bin/bash
# Build Tailwind CSS for production

echo "🎨 Building Tailwind CSS..."

# Check if npm/npx is available
if command -v npx &> /dev/null; then
    echo "✅ Using npx to build CSS"
    npx tailwindcss -i static/css/base.css -o static/css/output.css --minify
    echo "✅ CSS built successfully!"
else
    echo "⚠️  npx not found. Please install Node.js and npm"
    echo "📝 For now, using Tailwind CDN as fallback"
    echo "💡 To install Node.js: brew install node (on macOS)"
fi
