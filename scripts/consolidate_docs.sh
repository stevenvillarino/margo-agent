#!/bin/bash

# Margo Agent Documentation Consolidation Script
# This script consolidates scattered .md files into organized documentation

echo "🎯 Starting Margo Agent Documentation Consolidation..."

# Create archive directory for old files
mkdir -p archive_old_docs

# Create docs directory if it doesn't exist
mkdir -p docs

echo "📁 Moving redundant deployment files to archive..."

# Archive redundant deployment files
mv DEPLOYMENT_CHECKLIST.md archive_old_docs/ 2>/dev/null || echo "DEPLOYMENT_CHECKLIST.md not found"
mv VERCEL_DEPLOYMENT.md archive_old_docs/ 2>/dev/null || echo "VERCEL_DEPLOYMENT.md not found"
mv CLOUD_SETUP.md archive_old_docs/ 2>/dev/null || echo "CLOUD_SETUP.md not found"
mv SLACK_DEPLOYMENT.md archive_old_docs/ 2>/dev/null || echo "SLACK_DEPLOYMENT.md not found"
mv cloudflare-deployment.md archive_old_docs/ 2>/dev/null || echo "cloudflare-deployment.md not found"
mv DEPLOYMENT_STEPS.md archive_old_docs/ 2>/dev/null || echo "DEPLOYMENT_STEPS.md not found"
mv DEPLOYMENT_SUCCESS.md archive_old_docs/ 2>/dev/null || echo "DEPLOYMENT_SUCCESS.md not found"
mv DEPLOY_NOW.md archive_old_docs/ 2>/dev/null || echo "DEPLOY_NOW.md not found"
mv PRODUCTION_READY.md archive_old_docs/ 2>/dev/null || echo "PRODUCTION_READY.md not found"

echo "📁 Moving redundant status/summary files to archive..."

# Archive status and summary files
mv WORK_COMPLETION_SUMMARY.md archive_old_docs/ 2>/dev/null || echo "WORK_COMPLETION_SUMMARY.md not found"
mv DEVELOPMENT_LOG.md archive_old_docs/ 2>/dev/null || echo "DEVELOPMENT_LOG.md not found"
mv INTEGRATION_COMPLETION_SUMMARY.md archive_old_docs/ 2>/dev/null || echo "INTEGRATION_COMPLETION_SUMMARY.md not found"
mv OPTIMIZATION_VERIFICATION.md archive_old_docs/ 2>/dev/null || echo "OPTIMIZATION_VERIFICATION.md not found"
mv WORKER_DEPLOYED.md archive_old_docs/ 2>/dev/null || echo "WORKER_DEPLOYED.md not found"

echo "📁 Moving redundant architecture files to archive..."

# Archive redundant architecture files
mv ADVANCED_WORKFLOW_README.md archive_old_docs/ 2>/dev/null || echo "ADVANCED_WORKFLOW_README.md not found"
mv AGENT_ARCHITECTURE_FIX.md archive_old_docs/ 2>/dev/null || echo "AGENT_ARCHITECTURE_FIX.md not found"
mv DEPLOYMENT_FIX.md archive_old_docs/ 2>/dev/null || echo "DEPLOYMENT_FIX.md not found"

echo "📁 Moving misc files to archive..."

# Archive misc files
mv CONTRIBUTION_IDEAS.md archive_old_docs/ 2>/dev/null || echo "CONTRIBUTION_IDEAS.md not found"
mv KNOWLEDGE_LEARNING_CONTRIBUTIONS.md archive_old_docs/ 2>/dev/null || echo "KNOWLEDGE_LEARNING_CONTRIBUTIONS.md not found"
mv SYSTEM_INTEGRATION_PRINCIPLES.md archive_old_docs/ 2>/dev/null || echo "SYSTEM_INTEGRATION_PRINCIPLES.md not found"
mv VERCEL_OPTIMIZATION.md archive_old_docs/ 2>/dev/null || echo "VERCEL_OPTIMIZATION.md not found"

echo "📄 Creating consolidated documentation files..."

# Move key files to docs if they exist
if [ -f "ARCHITECTURE.md" ]; then
    mv ARCHITECTURE.md docs/AGENT_ARCHITECTURE.md
    echo "✅ Moved ARCHITECTURE.md → docs/AGENT_ARCHITECTURE.md"
fi

if [ -f "ROKU_INTEGRATION.md" ]; then
    mv ROKU_INTEGRATION.md docs/ROKU_SPECIFIC.md
    echo "✅ Moved ROKU_INTEGRATION.md → docs/ROKU_SPECIFIC.md"
fi

if [ -f "MIGRATION_GUIDE.md" ]; then
    mv MIGRATION_GUIDE.md docs/MIGRATION_NOTES.md
    echo "✅ Moved MIGRATION_GUIDE.md → docs/MIGRATION_NOTES.md"
fi

if [ -f "USER_JOURNEYS.md" ]; then
    mv USER_JOURNEYS.md docs/
    echo "✅ Moved USER_JOURNEYS.md → docs/"
fi

echo "📝 Creating additional consolidated files..."

# Create changelog from multiple sources
cat > docs/CHANGELOG.md << 'EOF'
# Changelog

## Version History

### v2.0.0 - Current (August 2025)
- ✅ Multi-agent system architecture implemented
- ✅ Cloudflare Workers deployment ready
- ✅ Vercel frontend deployment ready
- ✅ Slack bot integration complete
- ✅ JIRA automation implemented
- ✅ Knowledge management system active
- ✅ VP of Design agent (Margo) operational

### v1.0.0 - Initial Release
- Basic design review functionality
- Streamlit interface
- OpenAI integration
- Figma file analysis

## Major Features Added

### Multi-Agent System
- Communication Hub for agent orchestration
- Specialized agents: Designer, QA, Research, JIRA
- Knowledge sharing between agents
- Automated workflow management

### Enterprise Integration
- Slack workspace integration
- JIRA ticket automation
- Figma design file access
- Confluence documentation support

### Deployment Options
- Local development with Streamlit
- Cloud deployment via Cloudflare Workers
- Frontend hosting on Vercel
- Slack bot for team collaboration

## Migration Notes

See [MIGRATION_NOTES.md](MIGRATION_NOTES.md) for detailed migration information.
EOF

# Create troubleshooting guide
cat > docs/TROUBLESHOOTING.md << 'EOF'
# Troubleshooting Guide

## Common Issues

### 1. Installation Problems

#### Python Virtual Environment
```bash
# If venv creation fails
python3 -m venv venv
# or
virtualenv venv
```

#### Dependency Installation
```bash
# Force reinstall if packages conflict
pip install -r requirements.txt --force-reinstall --no-cache-dir
```

### 2. API Key Issues

#### OpenAI API Key Not Working
1. Check key format: should start with `sk-`
2. Verify account has credits
3. Test connection:
```bash
python -c "
import openai
import os
from dotenv import load_dotenv
load_dotenv()
client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
print(client.models.list())
"
```

#### Slack Token Issues
1. Bot token should start with `xoxb-`
2. App token should start with `xapp-`
3. Verify bot is installed in workspace
4. Check required scopes are granted

### 3. Streamlit Problems

#### Port Already in Use
```bash
streamlit run app.py --server.port 8502
```

#### Streamlit Won't Start
```bash
# Clear Streamlit cache
streamlit cache clear
# or
rm -rf ~/.streamlit/
```

### 4. Agent Communication Issues

#### Agents Not Responding
1. Check OpenAI API key is set
2. Verify internet connection
3. Check agent initialization:
```bash
python demo_simple.py
```

#### Message Routing Problems
1. Restart Communication Hub
2. Check agent registration
3. Verify message format

### 5. Deployment Issues

#### Cloudflare Deployment
```bash
# Check Wrangler login
wrangler whoami

# Verify secrets
wrangler secret list

# Check deployment status
wrangler tail
```

#### Vercel Deployment
```bash
# Check deployment logs
vercel logs

# Verify environment variables
vercel env ls
```

### 6. File Upload Problems

#### Large File Uploads
- Maximum file size: 10MB
- Supported formats: PNG, JPG, PDF
- Check file permissions

#### Figma Integration
1. Verify Figma token has file access
2. Check file URL format
3. Ensure file is publicly accessible

## Getting Help

### Debug Mode
Enable verbose logging:
```bash
export DEBUG=true
export LOG_LEVEL=DEBUG
python app.py
```

### System Validation
Run the comprehensive system check:
```bash
python validate_system.py
```

### Contact Support
- GitHub Issues: Create detailed bug reports
- Documentation: Check all docs in `/docs/` folder
- Team Contact: Reach out to development team

## Useful Commands

### System Health Check
```bash
# Test all components
python quick_test.py

# Validate configuration
python check_env.py

# Test specific agent
python -c "from agents.design_reviewer import DesignReviewer; print('✅ Design Reviewer OK')"
```

### Reset System
```bash
# Clear all caches
rm -rf __pycache__/
rm -rf .streamlit/

# Reinstall dependencies
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```
EOF

# Create configuration guide
cat > docs/CONFIGURATION.md << 'EOF'
# Configuration Guide

## Environment Variables

### Required Configuration

Copy `.env.example` to `.env` and configure:

```bash
# Core AI Configuration
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4-vision-preview

# Project Settings
PROJECT_NAME=margo-agent
PROJECT_KEY=MARGO
ENVIRONMENT=development
```

### Optional Integrations

```bash
# Web Research
EXA_API_KEY=your-exa-key

# Design Tools
FIGMA_ACCESS_TOKEN=your-figma-token

# Project Management
JIRA_URL=https://your-domain.atlassian.net
JIRA_USERNAME=your-email@company.com
JIRA_API_TOKEN=your-jira-token

# Team Communication
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_APP_TOKEN=xapp-your-app-token
SLACK_SIGNING_SECRET=your-signing-secret
```

## Agent Configuration

### VP Design Agent (Margo)
```python
VP_DESIGN_PREFERENCES = {
    "focus_areas": ["user_experience", "brand_consistency", "accessibility"],
    "review_depth": "comprehensive",
    "automation_level": "high"
}
```

### Design Review Settings
```python
DESIGN_REVIEW_CONFIG = {
    "max_file_size": 10485760,  # 10MB
    "supported_formats": ["png", "jpg", "jpeg", "pdf"],
    "auto_analysis": True,
    "generate_suggestions": True
}
```

## Integration Settings

### Slack Bot Configuration
```python
SLACK_CONFIG = {
    "bot_name": "Roku Design Review Bot",
    "channels": ["#design", "#product"],
    "auto_respond": True,
    "file_analysis": True
}
```

### JIRA Integration
```python
JIRA_CONFIG = {
    "project_key": "DESIGN",
    "issue_type": "Task",
    "auto_create": True,
    "priority": "Medium"
}
```

## Advanced Settings

### Performance Tuning
```python
PERFORMANCE_CONFIG = {
    "max_concurrent_reviews": 5,
    "cache_duration": 3600,  # 1 hour
    "response_timeout": 30   # 30 seconds
}
```

### Knowledge Management
```python
KNOWLEDGE_CONFIG = {
    "learning_enabled": True,
    "feedback_collection": True,
    "knowledge_sharing": True
}
```
EOF

echo "✅ Documentation consolidation complete!"
echo ""
echo "📁 Summary of changes:"
echo "  • Moved 20+ redundant files to archive_old_docs/"
echo "  • Created organized docs/ structure"
echo "  • Generated consolidated documentation files"
echo "  • Preserved important content in new structure"
echo ""
echo "📖 New documentation structure:"
echo "  docs/"
echo "  ├── README.md              (Documentation index)"
echo "  ├── PROJECT_OVERVIEW.md    (Main project description)"
echo "  ├── QUICK_START.md         (30-minute setup guide)"
echo "  ├── DEPLOYMENT_GUIDE.md    (Complete deployment instructions)"
echo "  ├── CONFIGURATION.md       (Environment and settings)"
echo "  ├── TROUBLESHOOTING.md     (Common issues and solutions)"
echo "  ├── CHANGELOG.md           (Version history)"
echo "  ├── AGENT_ARCHITECTURE.md  (Technical architecture)"
echo "  ├── ROKU_SPECIFIC.md       (Roku brand guidelines)"
echo "  └── MIGRATION_NOTES.md     (Migration information)"
echo ""
echo "🎯 Next steps:"
echo "  1. Review the new documentation structure"
echo "  2. Update any internal links to point to new locations"
echo "  3. Test that all information is still accessible"
echo "  4. Consider removing archive_old_docs/ after verification"
