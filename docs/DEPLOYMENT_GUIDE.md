# 🚀 Deployment Guide

This guide covers all deployment options for the Margo Agent system, from local development to production cloud deployments.

## 🎯 Quick Start (30 minutes)

### Prerequisites

- Python 3.8+
- Node.js 18+ (for cloud deployments)
- Git

### 1. Clone and Setup

```bash
git clone <repository-url>
cd margo-agent
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Configuration

Copy and configure your environment:

```bash
cp .env.example .env
# Edit .env with your API keys (see Configuration section below)
```

### 3. Test Local Setup

```bash
# Test core components
python demo_simple.py

# Run Streamlit interface
streamlit run app.py
```

## 🔧 Configuration

### Required Environment Variables

Edit your `.env` file with the following:

```bash
# OpenAI Configuration (Required)
OPENAI_API_KEY=sk-your-openai-key-here

# EXA Configuration (Optional - for web research)
EXA_API_KEY=your-exa-key-here

# Figma Configuration (Required for Figma integration)
FIGMA_ACCESS_TOKEN=your-figma-token-here

# JIRA Configuration (Optional - for issue tracking)
JIRA_URL=https://roku.atlassian.net
JIRA_USERNAME=your-email@roku.com
JIRA_API_TOKEN=your-jira-token-here

# Slack Configuration (Required for Slack bot)
SLACK_BOT_TOKEN=xoxb-your-slack-bot-token
SLACK_APP_TOKEN=xapp-your-slack-app-token
SLACK_SIGNING_SECRET=your-slack-signing-secret
```

### API Key Setup Guide

#### OpenAI API Key
1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create new API key
3. Copy to `OPENAI_API_KEY` in `.env`

#### EXA API Key (Optional)
1. Visit [EXA.ai](https://exa.ai/)
2. Sign up and get API key
3. Copy to `EXA_API_KEY` in `.env`

#### Figma Access Token
1. Go to [Figma Account Settings](https://www.figma.com/settings)
2. Generate Personal Access Token
3. Copy to `FIGMA_ACCESS_TOKEN` in `.env`

#### JIRA API Token
1. Go to [Atlassian Account Security](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Create API token
3. Use your Roku email for `JIRA_USERNAME`
4. Copy token to `JIRA_API_TOKEN` in `.env`

#### Slack Configuration
1. Create app at [Slack API](https://api.slack.com/apps)
2. Enable Socket Mode
3. Add Bot Token Scopes: `chat:write`, `files:read`, `app_mentions:read`
4. Install app to workspace
5. Copy tokens to `.env`

## 🖥️ Local Development

### Streamlit Interface

The main development interface uses Streamlit:

```bash
source venv/bin/activate
streamlit run app.py
```

Features:
- **File Upload Tab**: Upload designs for review
- **Figma Tab**: Connect to Figma files
- **Confluence Tab**: Import design guidelines
- **VP Preferences Tab**: Customize review criteria

### Running VS Code Tasks

Use the built-in tasks for common operations:

```bash
# Install dependencies
CMD+Shift+P → "Tasks: Run Task" → "Install Dependencies"

# Run the application
CMD+Shift+P → "Tasks: Run Task" → "Run Design Review Agent"
```

### Demo Scripts

Test different components:

```bash
# Basic functionality test
python demo_simple.py

# Advanced workflow demonstration
python demo_advanced_workflow.py

# All agents communication test
python demo_all_agents.py

# Knowledge management test
python quick_test.py
```

## 🌐 Cloudflare Deployment

### Automated Setup

Run the automated setup script:

```bash
./setup-cloudflare-deployment.sh
```

This script will:
- Install Wrangler CLI
- Create TypeScript project structure
- Set up Cloudflare configuration
- Create basic Slack integration
- Install all dependencies

### Manual Setup

#### 1. Install Wrangler CLI

```bash
npm install -g @cloudflare/wrangler
wrangler login
```

#### 2. Create Worker Project

```bash
wrangler init roku-design-review-bot --type="typescript"
cd roku-design-review-bot
```

#### 3. Configure Secrets

```bash
# Set environment secrets
wrangler secret put SLACK_BOT_TOKEN
wrangler secret put SLACK_SIGNING_SECRET
wrangler secret put OPENAI_API_KEY
wrangler secret put EXA_API_KEY
wrangler secret put FIGMA_ACCESS_TOKEN
wrangler secret put JIRA_API_TOKEN
```

#### 4. Deploy

```bash
wrangler deploy
```

### Production Configuration

Your `wrangler.toml` should include:

```toml
name = "roku-design-review-bot"
main = "src/index.ts"
compatibility_date = "2024-01-01"

[vars]
ENVIRONMENT = "production"

[[kv_namespaces]]
binding = "DESIGN_CACHE"
id = "your-kv-namespace-id"

[triggers]
crons = ["0 */6 * * *"]  # Health check every 6 hours
```

## 🔗 Vercel Deployment

### Project Structure

Ensure you have the Vercel-compatible structure:

```
/api/index.py       # Flask app for serverless functions
/vercel.json        # Vercel deployment configuration
/requirements.txt   # Python dependencies
/.vercelignore      # Files to exclude
```

### Deployment Steps

#### 1. Install Vercel CLI

```bash
npm install -g vercel
```

#### 2. Deploy

```bash
vercel --prod
```

#### 3. Environment Variables

Set in Vercel Dashboard → Settings → Environment Variables:

- `OPENAI_API_KEY`
- `EXA_API_KEY`
- `FIGMA_ACCESS_TOKEN`
- `JIRA_URL`
- `JIRA_USERNAME`
- `JIRA_API_TOKEN`
- `SLACK_BOT_TOKEN`
- `SLACK_SIGNING_SECRET`

### Vercel Configuration

Your `vercel.json`:

```json
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
```

## 🤖 Slack Bot Deployment

### Setup Script

Use the automated setup:

```bash
./setup_slack_bot.sh
```

### Manual Slack App Configuration

#### 1. Create Slack App

1. Go to [Slack API Apps](https://api.slack.com/apps)
2. Click "Create New App" → "From scratch"
3. Enter app name: "Roku Design Review Bot"
4. Select your workspace

#### 2. Configure OAuth Scopes

In OAuth & Permissions, add these Bot Token Scopes:
- `app_mentions:read`
- `chat:write`
- `files:read`
- `files:write`

#### 3. Enable Socket Mode

1. Go to Socket Mode
2. Enable Socket Mode
3. Generate App Token (starts with `xapp-`)

#### 4. Event Subscriptions

Subscribe to these bot events:
- `app_mention`
- `message.channels`
- `file_shared`

#### 5. Install to Workspace

Click "Install to Workspace" and authorize.

## 📊 Health Monitoring

### Production URLs

- **Cloudflare Worker**: `https://roku-design-review-bot.madetoenvy-llc.workers.dev`
- **Vercel Frontend**: `https://margo-agent.vercel.app`

### Health Checks

Both deployments include health monitoring:

```bash
# Check Cloudflare Worker
curl https://roku-design-review-bot.madetoenvy-llc.workers.dev/health

# Check Vercel deployment
curl https://margo-agent.vercel.app/health
```

### Monitoring Commands

```bash
# View Cloudflare logs
wrangler tail

# Monitor Vercel deployment
vercel logs

# Check local system status
python validate_system.py
```

## 🔍 Troubleshooting

### Common Issues

#### 1. API Key Errors

```bash
# Test OpenAI connection
python -c "
import openai
import os
from dotenv import load_dotenv
load_dotenv()
client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
print('OpenAI connection successful!')
"
```

#### 2. Slack Token Issues

```bash
# Verify Slack tokens
python -c "
import os
from slack_sdk import WebClient
from dotenv import load_dotenv
load_dotenv()
client = WebClient(token=os.getenv('SLACK_BOT_TOKEN'))
print(client.auth_test())
"
```

#### 3. Import Errors

```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

#### 4. Permission Issues

```bash
# Fix file permissions
chmod +x setup-cloudflare-deployment.sh
chmod +x setup_slack_bot.sh
```

### Debug Mode

Enable debug logging:

```bash
export DEBUG=true
export LOG_LEVEL=DEBUG
python app.py
```

### Support Contacts

For deployment issues:
- Check the [Troubleshooting Guide](TROUBLESHOOTING.md)
- Review the [GitHub Issues](https://github.com/stevenvillarino/margo-agent/issues)
- Contact the development team

## 🎯 Next Steps

After successful deployment:

1. **Test Integration**: Upload a test design file
2. **Configure Team**: Set up Slack workspace integration
3. **Customize Preferences**: Configure VP design preferences
4. **Monitor Performance**: Set up alerting and monitoring
5. **Scale Usage**: Onboard team members gradually

For ongoing development, see the [Development Guide](DEVELOPMENT_GUIDE.md).
