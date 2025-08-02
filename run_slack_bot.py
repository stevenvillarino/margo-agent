#!/usr/bin/env python3
"""
🚀 Margo Slack Bot Launcher

Simple launcher script for the Margo Design Review Slack Bot.
Run this after setting up your Slack app credentials in .env
"""

import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_environment():
    """Check if all required environment variables are set."""
    required_vars = {
        'OPENAI_API_KEY': 'OpenAI API key for AI agents',
        'SLACK_BOT_TOKEN': 'Slack Bot User OAuth Token (xoxb-...)',
        'SLACK_APP_TOKEN': 'Slack App-Level Token (xapp-...)'
    }
    
    missing = []
    for var, description in required_vars.items():
        value = os.getenv(var)
        if not value or value in ['your_openai_api_key_here', 'xoxb-your-bot-token-here', 'xapp-your-app-token-here', 'xoxb-your-slack-bot-token', 'xapp-your-slack-app-token']:
            missing.append(f"❌ {var}: {description}")
    
    if missing:
        print("🚨 Missing required environment variables:")
        for var in missing:
            print(f"   {var}")
        print("\n📋 Please update your .env file with the correct values.")
        print("   See SLACK_SETUP.md for detailed instructions.")
        return False
    
    print("✅ All required environment variables are set!")
    return True

def check_dependencies():
    """Check if required Python packages are installed."""
    try:
        import slack_bolt
        import slack_sdk
        import langchain
        import openai
        print("✅ All required packages are installed!")
        return True
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("   Run: pip install -r requirements.txt")
        return False

async def run_bot():
    """Run the Slack bot."""
    try:
        from slack_bot import SlackDesignReviewBot
        
        # Get configuration from environment
        slack_bot_token = os.getenv('SLACK_BOT_TOKEN')
        slack_app_token = os.getenv('SLACK_APP_TOKEN')
        openai_api_key = os.getenv('OPENAI_API_KEY')
        exa_api_key = os.getenv('EXA_API_KEY')
        
        # Optional Confluence config
        confluence_config = None
        if all([os.getenv('CONFLUENCE_URL'), os.getenv('CONFLUENCE_USERNAME'), os.getenv('CONFLUENCE_API_KEY')]):
            confluence_config = {
                'url': os.getenv('CONFLUENCE_URL'),
                'username': os.getenv('CONFLUENCE_USERNAME'),
                'api_key': os.getenv('CONFLUENCE_API_KEY')
            }
        
        print("🎯 Initializing Margo Design Review Bot...")
        
        # Create bot instance
        bot = SlackDesignReviewBot(
            slack_bot_token=slack_bot_token,
            slack_app_token=slack_app_token,
            openai_api_key=openai_api_key,
            exa_api_key=exa_api_key,
            confluence_config=confluence_config
        )
        
        print("🚀 Starting Slack bot... (Press Ctrl+C to stop)")
        print("📱 The bot is now listening for messages in your Slack workspace!")
        print("\n💡 Try these commands:")
        print("   • @Margo help")
        print("   • /design-review")
        print("   • Upload a design file and mention @Margo")
        
        # Start the bot
        await bot.start()
        
    except KeyboardInterrupt:
        print("\n👋 Shutting down bot gracefully...")
    except Exception as e:
        print(f"❌ Error starting bot: {e}")
        return False
    
    return True

def main():
    """Main function."""
    print("🎯 Margo Design Review Slack Bot")
    print("================================")
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Run the bot
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        print("\n👋 Bot stopped.")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
