#!/bin/bash

# 🚀 Margo Slack Bot Setup Script
echo "🎯 Setting up Margo Design Review Bot for Slack"
echo "=============================================="

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please create it first."
    exit 1
fi

# Check for required environment variables
echo "🔍 Checking environment configuration..."

# Source the .env file
set -a
source .env
set +a

# Check OpenAI API Key
if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "your_openai_api_key_here" ]; then
    echo "❌ OPENAI_API_KEY not configured"
    echo "   Get your API key from: https://platform.openai.com/api-keys"
    echo "   Add it to your .env file: OPENAI_API_KEY=sk-your-key-here"
    MISSING_KEYS=true
fi

# Check Slack Bot Token
if [ -z "$SLACK_BOT_TOKEN" ] || [ "$SLACK_BOT_TOKEN" = "xoxb-your-bot-token-here" ]; then
    echo "❌ SLACK_BOT_TOKEN not configured"
    echo "   Create a Slack app at: https://api.slack.com/apps"
    echo "   Add Bot Token to your .env file: SLACK_BOT_TOKEN=xoxb-your-token"
    MISSING_KEYS=true
fi

# Check Slack App Token
if [ -z "$SLACK_APP_TOKEN" ] || [ "$SLACK_APP_TOKEN" = "xapp-your-app-token-here" ]; then
    echo "❌ SLACK_APP_TOKEN not configured"
    echo "   Enable Socket Mode in your Slack app"
    echo "   Add App Token to your .env file: SLACK_APP_TOKEN=xapp-your-token"
    MISSING_KEYS=true
fi

if [ "$MISSING_KEYS" = true ]; then
    echo ""
    echo "🚨 Please configure the missing API keys in your .env file first"
    echo "   Then run this script again to test the bot"
    exit 1
fi

echo "✅ All required keys configured!"
echo ""

# Activate virtual environment and test
echo "🧪 Testing Slack bot..."
source venv/bin/activate

# Test imports
python -c "from slack_bot import SlackDesignReviewBot; print('✅ Slack bot imports successfully')" || {
    echo "❌ Import test failed"
    exit 1
}

echo "✅ Bot is ready to run!"
echo ""
echo "🚀 To start the bot:"
echo "   source venv/bin/activate"
echo "   python slack_bot.py"
echo ""
echo "📋 Next steps:"
echo "1. Make sure your Slack app has the right permissions"
echo "2. Install the app to your workspace"
echo "3. Run the bot and test with: @Margo help"
