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
