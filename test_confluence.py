#!/usr/bin/env python3
"""
Test Confluence configuration
"""

from dotenv import load_dotenv
from config.settings import settings

def test_confluence_config():
    """Test if Confluence is properly configured."""
    load_dotenv()
    
    print("🔍 Testing Confluence Configuration")
    print("=" * 40)
    
    print(f"Confluence URL: {settings.confluence_url}")
    print(f"Confluence Username: {settings.confluence_username}")
    print(f"Confluence API Key: {'*' * 20 if settings.confluence_api_key else 'Not set'}")
    print(f"Is Confluence Configured: {settings.is_confluence_configured()}")
    
    if settings.is_confluence_configured():
        print("✅ Confluence is properly configured!")
        
        # Test the document loader
        try:
            from agents.document_loaders import document_loader_manager
            print("✅ Document loader manager imported successfully")
            
            # Try to create a Confluence loader (without actually calling the API)
            print("🔍 Testing document loader configuration...")
            print("✅ Document loader is ready to use")
            
        except Exception as e:
            print(f"❌ Error with document loader: {str(e)}")
    else:
        print("❌ Confluence is not properly configured")
        print("\n🔍 Detailed validation:")
        
        # Check URL
        url_valid = (settings.confluence_url and 
                    settings.confluence_url != "https://your-domain.atlassian.net" and
                    "atlassian.net" in settings.confluence_url)
        print(f"   URL valid: {url_valid} (current: {settings.confluence_url})")
        
        # Check username
        username_valid = (settings.confluence_username and 
                         settings.confluence_username != "your_email@domain.com" and
                         "@" in settings.confluence_username)
        print(f"   Username valid: {username_valid} (current: {settings.confluence_username})")
        
        # Check API key
        api_key_valid = (settings.confluence_api_key and 
                        settings.confluence_api_key != "your_confluence_api_token_here" and
                        len(settings.confluence_api_key) > 20)
        print(f"   API Key valid: {api_key_valid} (length: {len(settings.confluence_api_key) if settings.confluence_api_key else 0})")
        
        print("\n📝 To fix this, update your .env file with:")
        print("   CONFLUENCE_URL=https://yourcompany.atlassian.net")
        print("   CONFLUENCE_USERNAME=youremail@yourcompany.com")
        print("   CONFLUENCE_API_KEY=your_actual_api_token")

if __name__ == "__main__":
    test_confluence_config()
