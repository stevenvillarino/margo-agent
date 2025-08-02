#!/bin/bash

# 🏠 Local Development Setup
# Sets up the project for local development

echo "🏠 Setting up local development environment..."

# Check Python version
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+' || echo "0.0")
required_version="3.8"

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    echo "   Please install Python 3.8+ from https://python.org"
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ Created .env file. Please edit it with your API keys."
    else
        cat > .env << 'ENVEOF'
# MARGO AGENT - ENVIRONMENT CONFIGURATION
# Update the values below with your actual API keys and configuration

# OpenAI Configuration (Required for AI agents)
OPENAI_API_KEY=your_openai_api_key_here

# EXA Configuration (Optional - for web research)
EXA_API_KEY=your_exa_api_key_here

# Figma Configuration (Required for Figma integration)
FIGMA_ACCESS_TOKEN=your_figma_access_token_here

# JIRA Configuration (Optional - for automated issue tracking)
JIRA_URL=https://your-domain.atlassian.net
JIRA_USERNAME=your-email@company.com
JIRA_API_TOKEN=your_jira_api_token_here

# Slack Configuration (Required for Slack bot)
SLACK_BOT_TOKEN=xoxb-your-slack-bot-token
SLACK_APP_TOKEN=xapp-your-slack-app-token
SLACK_SIGNING_SECRET=your-slack-signing-secret

# Project Configuration
PROJECT_NAME=margo-agent
PROJECT_KEY=MARGO
ENVEOF
        echo "✅ Created .env file template. Please edit it with your API keys."
    fi
else
    echo "✅ .env file already exists"
fi

# Test basic functionality
echo "🧪 Testing basic functionality..."
python -c "
try:
    import langchain
    import openai
    import streamlit
    print('✅ Core imports successful')
except ImportError as e:
    print(f'❌ Import error: {e}')
    exit(1)
"

echo ""
echo "🎉 Local setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Edit your .env file with real API keys"
echo "2. Run: streamlit run app.py"
echo "3. Open http://localhost:8501 in your browser"
echo "4. Upload a design file to test the system"
