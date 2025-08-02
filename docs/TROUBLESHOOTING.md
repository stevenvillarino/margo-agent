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
