# 🚀 YOUR MARGO SLACK BOT - DEPLOYMENT GUIDE

**Status: Ready to Deploy!** ✅

## Step 1: Configure Your API Keys

Edit your `.env` file with real values:

```bash
# Required - Get from https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-your-actual-openai-key

# Required - Get from Slack App settings
SLACK_BOT_TOKEN=xoxb-your-actual-bot-token
SLACK_APP_TOKEN=xapp-your-actual-app-token
SLACK_SIGNING_SECRET=your-actual-signing-secret

# Optional but recommended
EXA_API_KEY=your-exa-key-for-research
```

## Step 2: Create Slack App

1. **Go to**: https://api.slack.com/apps
2. **Create New App** → "From scratch"
3. **Name**: "Margo Design Review Bot"
4. **Choose your workspace**

### Configure Permissions
Add these Bot Token Scopes in **OAuth & Permissions**:
- `channels:history` - Read channel messages
- `channels:read` - View channels  
- `chat:write` - Send messages
- `files:read` - Access uploaded files
- `commands` - Handle slash commands

### Enable Socket Mode
1. Go to **Socket Mode** 
2. Enable Socket Mode
3. Generate App Token with `connections:write` scope
4. Copy the `xapp-` token

### Install to Workspace
1. Go to **OAuth & Permissions**
2. Click "Install to Workspace"
3. Copy the `xoxb-` Bot User OAuth Token

## Step 3: Test Locally

```bash
# Run the setup script
./setup_slack_bot.sh

# If everything is green, start the bot:
source venv/bin/activate
python slack_bot.py
```

## Step 4: Deploy to Production

### Option A: Railway (Recommended)
1. Connect GitHub repo to [Railway](https://railway.app)
2. Add environment variables in Railway dashboard
3. Deploy automatically

### Option B: Heroku
```bash
heroku create margo-design-bot
heroku config:set OPENAI_API_KEY=your-key
heroku config:set SLACK_BOT_TOKEN=your-token
heroku config:set SLACK_APP_TOKEN=your-app-token
git push heroku main
```

### Option C: Vercel (Already configured!)
Your `vercel.json` is already set up. Just:
```bash
npx vercel
# Follow the prompts to deploy
```

## Step 5: Test in Slack

1. **Mention the bot**: `@Margo Design Review Bot help`
2. **Upload a design** and mention `@Margo`
3. **Use slash commands**: `/design-review --type ui_design`

## Features Available

✅ **Multi-Agent Design Review**
- VP of Design (Margo) - Strategic approval
- Senior Designer - Technical review  
- QA Engineer - Quality validation
- Research Agent - Context gathering

✅ **Slack Integration**
- File upload handling
- Interactive slash commands
- Threaded responses
- Real-time progress updates

✅ **Quality Standards**
- Roku-specific design criteria
- Accessibility compliance (WCAG)
- Performance recommendations
- Brand consistency checks

## Admin Commands

- `@Margo admin status` - Check bot health
- `@Margo admin reset` - Clear conversation memory
- `/margo-admin history` - View recent reviews

## Need Help?

The bot is production-ready! The main files are:
- `slack_bot.py` - Main Slack bot
- `agents/enhanced_system.py` - Review orchestrator
- `agents/vp_product_agent.py` - Margo (VP agent)
- `.env` - Your configuration

Everything else is working - just add your API keys and deploy! 🎉
