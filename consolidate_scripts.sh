#!/bin/bash

# Shell Script Consolidation for Margo Agent
# This script consolidates scattered .sh files into organized scripts

echo "🔧 Starting Margo Agent Shell Script Consolidation..."

# Create scripts directory for organized shell scripts
mkdir -p scripts

# Create archive directory for old scripts
mkdir -p archive_old_scripts

echo "📁 Moving redundant setup scripts to archive..."

# Archive redundant setup scripts (keep one master setup)
mv setup_simple.sh archive_old_scripts/ 2>/dev/null || echo "setup_simple.sh not found"
mv setup_advanced_workflow.sh archive_old_scripts/ 2>/dev/null || echo "setup_advanced_workflow.sh not found"
mv setup_ollama.sh archive_old_scripts/ 2>/dev/null || echo "setup_ollama.sh not found"

echo "📁 Moving deployment scripts to archive..."

# Archive deployment scripts (will be consolidated)
mv deploy_vercel.sh archive_old_scripts/ 2>/dev/null || echo "deploy_vercel.sh not found"
mv build.sh archive_old_scripts/ 2>/dev/null || echo "build.sh not found"

echo "📁 Moving specialized scripts to scripts directory..."

# Keep current setup-cloudflare-deployment.sh as it's comprehensive
if [ -f "setup-cloudflare-deployment.sh" ]; then
    mv setup-cloudflare-deployment.sh scripts/deploy_cloudflare.sh
    echo "✅ Moved setup-cloudflare-deployment.sh → scripts/deploy_cloudflare.sh"
fi

# Keep setup_slack_bot.sh as it's specific
if [ -f "setup_slack_bot.sh" ]; then
    mv setup_slack_bot.sh scripts/setup_slack.sh
    echo "✅ Moved setup_slack_bot.sh → scripts/setup_slack.sh"
fi

# Keep launch_knowledge_manager.sh as it's specific
if [ -f "launch_knowledge_manager.sh" ]; then
    mv launch_knowledge_manager.sh scripts/launch_knowledge.sh
    echo "✅ Moved launch_knowledge_manager.sh → scripts/launch_knowledge.sh"
fi

# Keep consolidate_docs.sh as it's a utility
if [ -f "consolidate_docs.sh" ]; then
    mv consolidate_docs.sh scripts/consolidate_docs.sh
    echo "✅ Moved consolidate_docs.sh → scripts/consolidate_docs.sh"
fi

echo "📝 Creating consolidated master scripts..."

# Create master setup script
cat > scripts/setup.sh << 'EOF'
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
EOF

# Create consolidated local setup script
cat > scripts/setup_local.sh << 'EOF'
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
EOF

# Create consolidated deployment script
cat > scripts/deploy_vercel.sh << 'EOF'
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
EOF

# Create development environment setup
cat > scripts/setup_dev.sh << 'EOF'
#!/bin/bash

# 🔧 Development Environment Setup
# Sets up comprehensive development environment with all tools

echo "🔧 Setting up comprehensive development environment..."

# Run local setup first
bash scripts/setup_local.sh

# Install development dependencies
echo "📚 Installing development dependencies..."
pip install pytest black flake8 mypy jupyter notebook

# Install VS Code extensions (if code command is available)
if command -v code &> /dev/null; then
    echo "🔧 Installing recommended VS Code extensions..."
    code --install-extension ms-python.python
    code --install-extension ms-python.flake8
    code --install-extension ms-python.black-formatter
    code --install-extension charliermarsh.ruff
fi

# Set up pre-commit hooks
echo "🔗 Setting up pre-commit hooks..."
pip install pre-commit
cat > .pre-commit-config.yaml << 'PRECOMMIT'
repos:
  - repo: https://github.com/psf/black
    rev: 23.7.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
PRECOMMIT

pre-commit install

# Create development configuration
cat > .vscode/settings.json << 'VSCODE'
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "files.associations": {
        "*.md": "markdown"
    }
}
VSCODE

echo "✅ Development environment setup complete!"
echo ""
echo "🛠️ Development tools installed:"
echo "• Black (code formatting)"
echo "• Flake8 (linting)"
echo "• MyPy (type checking)"
echo "• Pytest (testing)"
echo "• Pre-commit hooks"
echo "• Jupyter Notebook"
EOF

# Make all scripts executable
chmod +x scripts/*.sh

echo "✅ Shell script consolidation complete!"
echo ""
echo "📁 Summary of changes:"
echo "  • Moved 5 redundant scripts to archive_old_scripts/"
echo "  • Created organized scripts/ structure"
echo "  • Generated consolidated master scripts"
echo "  • Created specialized deployment scripts"
echo ""
echo "🔧 New script structure:"
echo "  scripts/"
echo "  ├── setup.sh              (Master setup script - choose your path)"
echo "  ├── setup_local.sh        (Local development setup)"
echo "  ├── setup_dev.sh          (Full development environment)"
echo "  ├── deploy_cloudflare.sh  (Cloudflare deployment)"
echo "  ├── deploy_vercel.sh      (Vercel deployment)"
echo "  ├── setup_slack.sh        (Slack bot configuration)"
echo "  ├── launch_knowledge.sh   (Knowledge manager launcher)"
echo "  └── consolidate_docs.sh   (Documentation consolidation)"
echo ""
echo "🎯 Usage:"
echo "  • Run './scripts/setup.sh' for interactive setup"
echo "  • Run individual scripts for specific tasks"
echo "  • All scripts are now properly organized and documented"
