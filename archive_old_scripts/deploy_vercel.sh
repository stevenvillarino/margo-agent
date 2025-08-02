#!/bin/bash

# Vercel Deployment Script
echo "🚀 Deploying Margo Agent to Vercel..."

# Check if vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found. Installing..."
    npm install -g vercel
fi

# Deploy to production
echo "📦 Deploying to production..."
vercel --prod

echo "✅ Deployment complete!"
echo "🌐 Your app should be available at your Vercel domain"

# Show recent deployments
echo "📋 Recent deployments:"
vercel ls
