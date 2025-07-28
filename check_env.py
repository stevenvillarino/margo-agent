#!/usr/bin/env python3
"""
Environment setup helper for Design Review Agent
"""

import os
from dotenv import load_dotenv

def check_environment():
    """Check current environment configuration."""
    load_dotenv()
    
    required_vars = {
        'OPENAI_API_KEY': 'OpenAI API Key (Required for all features)',
        'CONFLUENCE_URL': 'Confluence URL (Required for Confluence integration)',
        'CONFLUENCE_USERNAME': 'Confluence Username (Required for Confluence integration)', 
        'CONFLUENCE_API_KEY': 'Confluence API Key (Required for Confluence integration)',
        'FIGMA_ACCESS_TOKEN': 'Figma Access Token (Required for Figma integration)'
    }
    
    print("🔍 Environment Configuration Check")
    print("=" * 50)
    
    all_configured = True
    confluence_configured = True
    figma_configured = True
    
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {'*' * 20}...{value[-4:]}")
        else:
            print(f"❌ {var}: Not set - {description}")
            all_configured = False
            
            if var.startswith('CONFLUENCE_'):
                confluence_configured = False
            elif var.startswith('FIGMA_'):
                figma_configured = False
    
    print("\n📊 Integration Status:")
    print(f"   • OpenAI: {'✅' if os.getenv('OPENAI_API_KEY') else '❌'}")
    print(f"   • Confluence: {'✅' if confluence_configured else '❌'}")
    print(f"   • Figma: {'✅' if figma_configured else '❌'}")
    
    if not confluence_configured:
        print("\n🚨 Confluence Setup Required:")
        print("   1. Go to: https://id.atlassian.com/manage-profile/security/api-tokens")
        print("   2. Create a new API token")
        print("   3. Add these to your .env file:")
        print("      CONFLUENCE_URL=https://your-organization.atlassian.net")
        print("      CONFLUENCE_USERNAME=your.email@company.com") 
        print("      CONFLUENCE_API_KEY=your_api_token_here")
    
    if not figma_configured:
        print("\n🎨 Figma Setup Required:")
        print("   1. Go to: https://www.figma.com/developers/api#access-tokens")
        print("   2. Generate a personal access token")
        print("   3. Add to your .env file:")
        print("      FIGMA_ACCESS_TOKEN=your_figma_token_here")
    
    return all_configured

if __name__ == "__main__":
    check_environment()
