#!/bin/bash

# 🎯 Quick Slack Token Configuration Helper
echo "🤖 Margo Slack Token Configuration Helper"
echo "=========================================="
echo ""
echo "This helper will guide you through setting up your Slack tokens."
echo "You'll need to create a Slack app first. Follow these steps:"
echo ""
echo "1️⃣ Create Slack App:"
echo "   → Go to: https://api.slack.com/apps"
echo "   → Click 'Create New App' > 'From scratch'"
echo "   → App Name: 'Margo Design Review Bot'"
echo "   → Select your workspace"
echo ""
echo "2️⃣ Configure Bot Permissions:"
echo "   → Go to 'OAuth & Permissions'"
echo "   → Add these Bot Token Scopes:"
echo "     • app_mentions:read"
echo "     • channels:history"
echo "     • channels:read"
echo "     • chat:write"
echo "     • files:read"
echo "     • files:write"
echo "     • commands"
echo "     • users:read"
echo ""
echo "3️⃣ Install to Workspace:"
echo "   → Click 'Install to Workspace'"
echo "   → Copy the Bot User OAuth Token (starts with xoxb-)"
echo ""
echo "4️⃣ Enable Socket Mode:"
echo "   → Go to 'Socket Mode'"
echo "   → Enable Socket Mode"
echo "   → Generate App-Level Token with 'connections:write' scope"
echo "   → Copy the App-Level Token (starts with xapp-)"
echo ""
echo "5️⃣ Add Slash Command:"
echo "   → Go to 'Slash Commands'"
echo "   → Create command: /design-review"
echo "   → Description: 'Start a comprehensive design review'"
echo ""

read -p "📝 Have you completed steps 1-5 above? (y/n): " setup_done

if [ "$setup_done" != "y" ]; then
    echo "Please complete the Slack app setup first, then run this script again."
    exit 1
fi

echo ""
echo "🔧 Now let's configure your tokens..."
echo ""

# Get Bot Token
echo "🤖 Enter your Slack Bot User OAuth Token (xoxb-...):"
read -p "SLACK_BOT_TOKEN: " bot_token

# Validate bot token format
if [[ ! $bot_token =~ ^xoxb- ]]; then
    echo "❌ Invalid bot token format. It should start with 'xoxb-'"
    exit 1
fi

# Get App Token  
echo ""
echo "📱 Enter your Slack App-Level Token (xapp-...):"
read -p "SLACK_APP_TOKEN: " app_token

# Validate app token format
if [[ ! $app_token =~ ^xapp- ]]; then
    echo "❌ Invalid app token format. It should start with 'xapp-'"
    exit 1
fi

echo ""
echo "💾 Updating .env file..."

# Update .env file
if [ -f .env ]; then
    # Replace existing tokens
    sed -i.bak "s/SLACK_BOT_TOKEN=.*/SLACK_BOT_TOKEN=$bot_token/" .env
    sed -i.bak "s/SLACK_APP_TOKEN=.*/SLACK_APP_TOKEN=$app_token/" .env
    echo "✅ .env file updated!"
else
    echo "❌ .env file not found!"
    exit 1
fi

echo ""
echo "🧪 Testing configuration..."

# Test the setup
./scripts/setup_slack.sh

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Configuration complete!"
    echo ""
    echo "🚀 To start the bot:"
    echo "   python run_slack_bot.py"
    echo ""
    echo "💡 Test in Slack with:"
    echo "   @Margo help"
    echo "   /design-review"
else
    echo ""
    echo "❌ Configuration test failed. Please check the error messages above."
fi
