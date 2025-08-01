#!/bin/bash

echo "🚀 MARGO AGENT - SIMPLE SETUP"
echo "=============================="

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install core dependencies
echo "📚 Installing core dependencies..."
pip install langchain langchain-openai requests aiofiles python-dotenv

# Install optional dependencies
echo "🔧 Installing optional dependencies..."
pip install exa-py || echo "⚠️ EXA not installed - web research disabled"
pip install playwright || echo "⚠️ Playwright not installed - QA validation disabled"
pip install atlassian-python-api || echo "⚠️ JIRA client not installed - issue tracking disabled"
pip install slack-bolt || echo "⚠️ Slack bot not installed - notifications disabled"

# Install playwright browsers if playwright was installed
if python -c "import playwright" 2>/dev/null; then
    echo "🌐 Installing Playwright browsers..."
    playwright install
fi

# Create environment file template
echo "📝 Creating environment file template..."
cat > .env.template << EOF
# OpenAI Configuration (Required)
OPENAI_API_KEY=your_openai_api_key_here

# EXA Configuration (Optional - for web research)
EXA_API_KEY=your_exa_api_key_here

# JIRA Configuration (Optional - for issue tracking)
JIRA_URL=https://your-company.atlassian.net
JIRA_USERNAME=your_email@company.com
JIRA_API_TOKEN=your_jira_api_token

# Slack Configuration (Optional - for notifications)
SLACK_BOT_TOKEN=xoxb-your-slack-bot-token
SLACK_SIGNING_SECRET=your-slack-signing-secret

# Project Configuration
PROJECT_NAME=your_project_name
PROJECT_KEY=PROJ
EOF

# Copy template to actual .env if it doesn't exist
if [ ! -f ".env" ]; then
    cp .env.template .env
    echo "📋 Created .env file - please update with your API keys"
else
    echo "📋 .env file already exists"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Run: source venv/bin/activate"
echo "3. Run: python3 test_advanced_integration.py"
echo ""
