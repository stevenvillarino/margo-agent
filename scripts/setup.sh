#!/bin/bash

# 🚀 Margo Agent - Master Setup Script
# One script to rule them all - handles all setup scenarios

set -e

echo "🎭 Margo Agent - Master Setup"
echo "============================="

# Display setup options
echo "Choose your setup option:"
echo "1. 🚀 Quick Start (Local development)"
echo "2. ☁️  Cloud Deployment (Cloudflare)"
echo "3. 💬 Slack Bot Setup"
echo "4. 🧠 Knowledge Manager"
echo "5. 🔧 Development Environment"
echo "6. 🌐 Vercel Deployment"
echo ""

read -p "Enter your choice (1-6): " choice

case $choice in
    1)
        echo "🚀 Starting Quick Start Setup..."
        bash scripts/setup_local.sh
        ;;
    2)
        echo "☁️ Starting Cloudflare Deployment..."
        bash scripts/deploy_cloudflare.sh
        ;;
    3)
        echo "💬 Starting Slack Bot Setup..."
        bash scripts/setup_slack.sh
        ;;
    4)
        echo "🧠 Starting Knowledge Manager..."
        bash scripts/launch_knowledge.sh
        ;;
    5)
        echo "🔧 Starting Development Environment Setup..."
        bash scripts/setup_dev.sh
        ;;
    6)
        echo "🌐 Starting Vercel Deployment..."
        bash scripts/deploy_vercel.sh
        ;;
    *)
        echo "❌ Invalid choice. Please run the script again."
        exit 1
        ;;
esac

echo ""
echo "✅ Setup complete! Check the output above for any additional steps."
