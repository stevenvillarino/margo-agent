#!/bin/bash

# Vercel build script for optimized deployment

echo "🔧 Starting optimized build..."

# Install minimal dependencies
echo "📦 Installing minimal dependencies..."
pip install --no-cache-dir -r requirements.txt

# Remove unnecessary files from the build
echo "🧹 Cleaning up build artifacts..."
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyo" -delete
find . -name "*.pyd" -delete

# Optimize Python bytecode
echo "⚡ Optimizing Python bytecode..."
python -m compileall -q .

echo "✅ Build optimization complete!"
