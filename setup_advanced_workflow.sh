#!/bin/bash

# Advanced Workflow Setup Script
# This script helps set up the advanced design workflow automation system

echo "🚀 MARGO AGENT - ADVANCED WORKFLOW SETUP"
echo "========================================="

# Check Python version
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
required_version="3.8"

if [[ $(echo "$python_version >= $required_version" | bc -l) ]]; then
    echo "✅ Python $python_version detected (>= $required_version required)"
else
    echo "❌ Python $required_version or higher required. Current: $python_version"
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt

# Install Playwright browsers
echo "🎭 Installing Playwright browsers..."
if command -v playwright &> /dev/null; then
    playwright install
    echo "✅ Playwright browsers installed"
else
    echo "⚠️ Playwright not found in PATH, trying direct installation..."
    python -m playwright install
fi

# Create environment file template
echo "📝 Creating environment configuration template..."
if [ ! -f .env ]; then
    cat > .env << EOL
# Required API Keys
OPENAI_API_KEY=your_openai_api_key_here

# Optional - Enhanced Features
EXA_API_KEY=your_exa_api_key_here

# Optional - JIRA Integration
JIRA_URL=https://yourcompany.atlassian.net
JIRA_USERNAME=your_email@company.com
JIRA_API_TOKEN=your_jira_api_token

# Optional - Notifications
SLACK_WEBHOOK_URL=your_slack_webhook_url

# Optional - Roku AI Hub Integration
AI_HUB_API_TOKEN=your_ai_hub_token_here
AI_HUB_ASSISTANT_ID=your_assistant_id_here
EOL
    echo "✅ Created .env template file"
    echo "🔧 Please edit .env with your actual API keys"
else
    echo "⚠️ .env file already exists, skipping template creation"
fi

# Create screenshots directory
echo "📸 Creating screenshots directory..."
mkdir -p screenshots
echo "✅ Screenshots directory created"

# Create logs directory
echo "📋 Creating logs directory..."
mkdir -p logs
echo "✅ Logs directory created"

# Check if required directories exist
required_dirs=("agents" "prompts" "config")
for dir in "${required_dirs[@]}"; do
    if [ -d "$dir" ]; then
        echo "✅ Directory $dir exists"
    else
        echo "❌ Directory $dir missing"
    fi
done

# Test imports
echo "🧪 Testing Python imports..."
python3 -c "
try:
    import langchain
    import langchain_openai
    import streamlit
    print('✅ Core dependencies imported successfully')
except ImportError as e:
    print(f'❌ Import error: {e}')
"

# Test Playwright
echo "🎭 Testing Playwright installation..."
python3 -c "
try:
    from playwright.sync_api import sync_playwright
    print('✅ Playwright imported successfully')
except ImportError:
    print('⚠️ Playwright not available (QA validation will be disabled)')
"

# Test optional dependencies
echo "🔍 Testing optional dependencies..."
python3 -c "
import sys

# Test EXA
try:
    import exa_py
    print('✅ EXA integration available')
except ImportError:
    print('⚠️ EXA not available (web research will be disabled)')

# Test Slack
try:
    import slack_bolt
    print('✅ Slack integration available')
except ImportError:
    print('⚠️ Slack not available (bot deployment will be disabled)')

# Test JIRA
try:
    import jira
    print('✅ JIRA integration available')
except ImportError:
    print('⚠️ JIRA not available (ticket creation will be disabled)')
"

echo ""
echo "🎯 SETUP COMPLETE!"
echo "==================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Run the demo: python demo_advanced_workflow.py"
echo "3. Check the ADVANCED_WORKFLOW_README.md for full documentation"
echo ""
echo "Required for basic functionality:"
echo "- OPENAI_API_KEY (required)"
echo ""
echo "Optional for enhanced features:"
echo "- EXA_API_KEY (web research)"
echo "- JIRA_URL, JIRA_USERNAME, JIRA_API_TOKEN (issue tracking)"
echo "- SLACK_WEBHOOK_URL (notifications)"
echo ""
echo "🚀 Ready to revolutionize your design workflow!"
