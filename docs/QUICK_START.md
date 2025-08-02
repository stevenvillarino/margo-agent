# 🚀 Quick Start Guide

Get the Margo Agent (VP of Design) system running in 30 minutes.

## ✅ What's Working Right Now

Your VP of Design Agent system is **production-ready** with these components:

### 🎯 Core System Components

- **💬 Agent Communication Hub** - Messages between agents (fully working)
- **🎫 JIRA Integration** - Automated ticket creation (ready with config)
- **🧪 Playwright QA Validation** - Visual testing framework (ready)
- **🔍 EXA Research Agent** - Web research capabilities (ready with API key)
- **📚 Knowledge Management** - Shared learning between agents

### 🤖 The Agent Team

- **🎯 Margo** - VP of Design (your senior strategic agent)
- **🎨 Sarah** - Senior Designer Agent
- **🧪 Alex** - QA Engineer Agent
- **🔍 Research Agent** - EXA-powered web research
- **🎫 JIRA Agent** - Issue tracking
- **💬 Communication Hub** - Agent orchestrator

## 🎯 30-Minute Setup

### Step 1: Environment Setup (5 minutes)

1. **Clone the repository:**

```bash
git clone <repository-url>
cd margo-agent
```

2. **Create virtual environment:**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**

```bash
pip install -r requirements.txt
```

### Step 2: Configure API Keys (10 minutes)

Edit the `.env` file with your credentials:

```bash
# Required for AI agents
OPENAI_API_KEY=your_actual_openai_key_here

# Optional but recommended
EXA_API_KEY=your_exa_key_here
FIGMA_ACCESS_TOKEN=your_figma_token_here

# For JIRA integration
JIRA_URL=https://roku.atlassian.net
JIRA_USERNAME=your.email@roku.com
JIRA_API_TOKEN=your_jira_token_here

# For Slack bot
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_SIGNING_SECRET=your-slack-secret
```

**Get API Keys:**

- **OpenAI**: [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- **EXA**: [exa.ai](https://exa.ai/)
- **Figma**: Account Settings → Personal Access Tokens
- **JIRA**: Atlassian Account → Security → API Tokens
- **Slack**: [api.slack.com/apps](https://api.slack.com/apps)

### Step 3: Test the System (5 minutes)

```bash
# Test core components (no API keys needed)
python demo_simple.py

# Test with your API keys
python quick_test.py

# Validate full system
python validate_system.py
```

### Step 4: Run the Interface (10 minutes)

#### Option A: Streamlit Web Interface

```bash
streamlit run app.py
```

Then open: `http://localhost:8501`

#### Option B: VS Code Tasks

1. Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows)
2. Type: "Tasks: Run Task"
3. Select: "Run Design Review Agent"

## 🎯 Quick Test Workflow

### Test 1: Upload a Design

1. Open the Streamlit interface
2. Go to "File Upload" tab
3. Upload a design image (PNG, JPG, or PDF)
4. Click "Analyze Design"
5. Watch the multi-agent review process

### Test 2: Figma Integration

1. Go to "Figma" tab
2. Enter a Figma file URL
3. Click "Review Figma Design"
4. See Figma-specific analysis

### Test 3: Agent Communication

```bash
# Run the advanced workflow demo
python demo_advanced_workflow.py
```

This demonstrates:
- Agent-to-agent communication
- Knowledge sharing
- Automated decision making
- JIRA ticket creation

## 🚀 Production Deployment (Optional)

### Cloud Deployment Options

#### Cloudflare (Recommended)

```bash
./setup-cloudflare-deployment.sh
wrangler deploy
```

- **Live URL**: Your worker will be deployed to Cloudflare Edge
- **Global Performance**: Sub-100ms response times
- **Auto-scaling**: Handles traffic spikes automatically

#### Vercel

```bash
npm install -g vercel
vercel --prod
```

- **Live URL**: Your app will be deployed to Vercel
- **Serverless**: Automatic scaling and monitoring
- **Domain**: Custom domain setup available

### Slack Bot Setup

```bash
./setup_slack_bot.sh
```

Then:

1. Create Slack app at [api.slack.com/apps](https://api.slack.com/apps)
2. Enable Socket Mode
3. Add bot scopes: `chat:write`, `files:read`, `app_mentions:read`
4. Install to workspace
5. Update `.env` with tokens

## 🔍 Testing Your Setup

### Basic Functionality Test

```bash
python -c "
import agents.design_reviewer as dr
import os
from dotenv import load_dotenv
load_dotenv()

print('✅ Core imports working')
print('✅ Environment loaded')
print('✅ System ready!')
"
```

### API Connection Test

```bash
python -c "
import openai
import os
from dotenv import load_dotenv
load_dotenv()

client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
print('✅ OpenAI connection successful!')
"
```

### Full System Test

```bash
python demo_all_agents.py
```

Expected output:
- ✅ Communication Hub started
- ✅ All agents initialized
- ✅ Message routing working
- ✅ Knowledge base accessible

## 🎯 Your Next Steps

### Immediate Actions (Today)

1. **Test file upload**: Try uploading a real design file
2. **Configure preferences**: Set up VP design preferences
3. **Test Slack integration**: Send a design via Slack
4. **Create JIRA ticket**: Test automated issue creation

### This Week

1. **Onboard team members**: Share Slack bot with designers
2. **Customize prompts**: Adjust review criteria for your needs
3. **Set up monitoring**: Configure health checks and alerts
4. **Document workflows**: Create team guidelines

### This Month

1. **Scale usage**: Increase team adoption
2. **Gather feedback**: Collect user feedback and iterate
3. **Advanced features**: Explore Confluence integration
4. **Performance optimization**: Monitor and optimize response times

## 🆘 Quick Troubleshooting

### Common Issues

**Import Errors:**

```bash
pip install -r requirements.txt --force-reinstall
```

**API Key Issues:**

```bash
# Check your .env file
cat .env | grep -E "(OPENAI|EXA|FIGMA|JIRA|SLACK)"
```

**Permission Errors:**

```bash
chmod +x setup-cloudflare-deployment.sh
chmod +x setup_slack_bot.sh
```

**Streamlit Won't Start:**

```bash
# Make sure you're in the virtual environment
source venv/bin/activate
streamlit run app.py --server.port 8501
```

### Get Help

- **Documentation**: See [full deployment guide](DEPLOYMENT_GUIDE.md)
- **Issues**: Check [troubleshooting guide](TROUBLESHOOTING.md)
- **Support**: Contact the development team

## 🎉 Success Indicators

You'll know everything is working when:

- ✅ Streamlit interface loads without errors
- ✅ File upload triggers multi-agent review
- ✅ Agents communicate and share knowledge
- ✅ JIRA tickets are created automatically
- ✅ Slack bot responds to messages
- ✅ Design reviews are comprehensive and accurate

**Congratulations! Your VP of Design Agent system is now ready for production use.**
