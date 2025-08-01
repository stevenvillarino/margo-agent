# Slack Bot Deployment Guide

This guide will help you deploy the Margo Design Review Bot to Slack for your team to use.

## Prerequisites

1. **Slack Workspace Admin Access** - You need admin permissions to create apps
2. **API Keys** - OpenAI API key (required), Exa API key (optional)
3. **Python Environment** - Python 3.8+ with virtual environment

## Step 1: Create Slack App

### 1.1 Create New App
1. Go to [Slack API Apps](https://api.slack.com/apps)
2. Click "Create New App" → "From scratch"
3. Name: "Margo Design Review Bot"
4. Choose your workspace
5. Click "Create App"

### 1.2 Configure App Permissions
Go to **OAuth & Permissions** and add these Bot Token Scopes:
```
channels:history     # Read channel messages
channels:read        # View channels
chat:write           # Send messages
files:read           # Access uploaded files
im:history          # Read DM history
im:read             # View DMs
im:write            # Send DMs
mpim:history        # Read group DM history
mpim:read           # View group DMs
mpim:write          # Send group DMs
commands            # Handle slash commands
```

### 1.3 Enable Socket Mode
1. Go to **Socket Mode** in your app settings
2. Enable Socket Mode
3. Generate an App Token with `connections:write` scope
4. Save the **App Token** (starts with `xapp-`)

### 1.4 Install App to Workspace
1. Go to **OAuth & Permissions**
2. Click "Install to Workspace"
3. Authorize the app
4. Copy the **Bot User OAuth Token** (starts with `xoxb-`)

## Step 2: Configure Slash Commands

### 2.1 Create Slash Commands
Go to **Slash Commands** and create these commands:

#### /design-review
- **Command**: `/design-review`
- **Request URL**: `https://your-domain.com/slack/events` (leave empty for Socket Mode)
- **Short Description**: "Start a comprehensive design review"
- **Usage Hint**: `[--type ui_design] [--focus accessibility] [--urgency high]`

#### /margo-admin
- **Command**: `/margo-admin`
- **Request URL**: `https://your-domain.com/slack/events` (leave empty for Socket Mode)
- **Short Description**: "Admin commands for Margo bot"
- **Usage Hint**: `[status|history|reset]`

### 2.2 Enable Events
Go to **Event Subscriptions**:
1. Enable Events
2. Add these Bot Events:
   - `app_mention` - When bot is mentioned
   - `file_shared` - When files are uploaded
   - `message.channels` - Channel messages
   - `message.im` - Direct messages

## Step 3: Set Up Environment

### 3.1 Clone and Setup
```bash
# Clone the repository
git clone https://github.com/your-org/margo-agent.git
cd margo-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3.2 Configure Environment Variables
Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

Edit `.env`:
```bash
# Required
OPENAI_API_KEY=sk-your-openai-key-here
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
SLACK_APP_TOKEN=xapp-your-app-token-here

# Optional but recommended
EXA_API_KEY=your-exa-api-key-here
CONFLUENCE_URL=https://your-company.atlassian.net
CONFLUENCE_USERNAME=your-email@company.com
CONFLUENCE_API_KEY=your-confluence-api-key-here
```

## Step 4: Deploy the Bot

### Option A: Local Development
```bash
# Activate virtual environment
source venv/bin/activate

# Run the bot
python slack_bot.py
```

### Option B: Production Deployment

#### Using Railway
1. Connect your GitHub repo to [Railway](https://railway.app)
2. Add environment variables in Railway dashboard
3. Deploy automatically

#### Using Heroku
```bash
# Install Heroku CLI
# Login to Heroku
heroku login

# Create app
heroku create margo-design-bot

# Set environment variables
heroku config:set OPENAI_API_KEY=your-key
heroku config:set SLACK_BOT_TOKEN=your-token
heroku config:set SLACK_APP_TOKEN=your-app-token

# Deploy
git push heroku main
```

#### Using AWS Lambda
```bash
# Install serverless framework
npm install -g serverless

# Package and deploy
serverless package
serverless deploy
```

#### Using Docker
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "slack_bot.py"]
```

```bash
# Build and run
docker build -t margo-bot .
docker run -d --env-file .env margo-bot
```

## Step 5: Test the Bot

### 5.1 Basic Tests
1. Mention the bot: `@Margo Design Review Bot help`
2. Upload a design file and mention the bot
3. Try the slash command: `/design-review --type ui_design`

### 5.2 Verify Functionality
- [ ] Bot responds to mentions
- [ ] File uploads are detected
- [ ] Slash commands work
- [ ] Reviews complete successfully
- [ ] Results are posted in threads

## Step 6: Configure for Your Team

### 6.1 Customize Company Context
Edit `agents/enhanced_system.py` to add your company-specific context:

```python
# Update company context
company_context = {
    "company_name": "Your Company",
    "product_type": "Your Product",
    "brand_guidelines": "path/to/guidelines.pdf",
    "design_system": "path/to/design_system.json"
}
```

### 6.2 Add Custom Quality Standards
Edit `slack_bot.py` to customize quality standards:

```python
quality_standards = {
    'minimum_compliance_score': 0.85,  # Raise the bar
    'critical_issue_threshold': 0,
    'feature_guide_match_threshold': 0.8,
    # Add your standards
}
```

### 6.3 Configure Agents
Enable/disable specific agents based on your needs:

```python
# In enhanced_system.py
enabled_agents = {
    'ui_specialist': True,
    'ux_researcher': True, 
    'creative_director': True,
    'vp_product': True,
    'accessibility': True,
    'quality_evaluation': True
}
```

## Step 7: Monitor and Maintain

### 7.1 Monitoring
- Check bot logs regularly
- Monitor API usage and costs
- Track review quality and feedback

### 7.2 Updates
```bash
# Update the bot
git pull origin main
pip install -r requirements.txt
# Restart deployment
```

### 7.3 Backup
- Export review history periodically
- Backup learning data
- Save configuration files

## Troubleshooting

### Common Issues

#### Bot doesn't respond
- Check Socket Mode is enabled
- Verify app tokens are correct
- Check bot has required permissions

#### File upload issues
- Verify `files:read` permission
- Check file size limits (10MB max)
- Ensure supported file types

#### Review failures
- Check OpenAI API key and credits
- Verify network connectivity
- Review error logs

#### Confluence integration
- Test Confluence credentials
- Check network access to Confluence
- Verify API permissions

### Logs and Debugging
```bash
# Enable debug logging
export LANGCHAIN_VERBOSE=true
export SLACK_BOLT_DEBUG=true

# Run with logging
python slack_bot.py 2>&1 | tee bot.log
```

## Security Considerations

1. **Token Security**: Never commit tokens to git
2. **Network Security**: Use HTTPS for webhooks
3. **Data Privacy**: Review data handling policies
4. **Access Control**: Limit bot to appropriate channels
5. **Audit Logging**: Log all review activities

## Cost Optimization

1. **OpenAI Usage**: Monitor token usage and set limits
2. **Exa Search**: Cache research results
3. **File Storage**: Clean up temporary files
4. **Rate Limiting**: Implement request limits

## Support

For issues and support:
1. Check the troubleshooting section
2. Review logs for error messages
3. Open an issue on GitHub
4. Contact the development team

---

## Quick Start Checklist

- [ ] Create Slack app with required permissions
- [ ] Get Bot Token and App Token
- [ ] Set up environment variables
- [ ] Install dependencies
- [ ] Run the bot
- [ ] Test with a design file
- [ ] Configure for your team
- [ ] Deploy to production
- [ ] Monitor and maintain

Happy reviewing! 🎨🤖
