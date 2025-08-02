#!/bin/bash

# 🌐 Vercel Deployment Script
# Handles complete Vercel deployment with optimizations

echo "🌐 Deploying Margo Agent to Vercel..."

# Check if vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "📦 Installing Vercel CLI..."
    npm install -g vercel
fi

# Build optimization
echo "⚡ Optimizing build..."

# Remove unnecessary files
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true

# Ensure vercel.json exists
if [ ! -f "vercel.json" ]; then
    echo "📝 Creating vercel.json configuration..."
    cat > vercel.json << 'VERCELJSON'
{
  "functions": {
    "api/index.py": {
      "runtime": "@vercel/python"
    }
  },
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "/api/index.py"
    },
    {
      "src": "/(.*)",
      "dest": "/api/index.py"
    }
  ]
}
VERCELJSON
fi

# Ensure api/index.py exists
if [ ! -f "api/index.py" ]; then
    echo "📝 Creating Vercel API handler..."
    mkdir -p api
    cat > api/index.py << 'APIPY'
from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({
        "status": "healthy",
        "service": "Margo Agent API",
        "version": "2.0.0"
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    app.run(debug=True)
APIPY
fi

# Deploy to production
echo "🚀 Deploying to production..."
vercel --prod

echo "✅ Deployment complete!"
echo "🌐 Your app is now live on Vercel"

# Show deployment info
echo "📋 Deployment information:"
vercel ls --limit 1
