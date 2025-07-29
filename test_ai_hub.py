#!/usr/bin/env python3
"""
Test script for AI Hub integration.
This script tests the AI Hub client and reviewer functionality.
"""

import os
import sys
from pathlib import Path

# Add the project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import our modules
from agents.ai_hub_client import AIHubClient
from agents.ai_hub_reviewer import AIHubDesignReviewer
from agents.ai_hub_cloud_reviewer import get_ai_hub_reviewer, is_ai_hub_available
from config.settings import settings

def test_ai_hub_connection():
    """Test basic AI Hub connection."""
    print("🔍 Testing AI Hub Connection...")
    
    try:
        # Test if AI Hub is available
        available = is_ai_hub_available()
        print(f"✅ AI Hub Available: {available}")
        
        if not available:
            print("❌ AI Hub not available. Check your token configuration.")
            return False
        
        # Get reviewer instance
        reviewer = get_ai_hub_reviewer()
        status = reviewer.get_status()
        
        print(f"📊 Status: {status}")
        print(f"📊 Models available: {status.get('models_count', 0)}")
        print(f"📊 Assistants available: {status.get('assistants_count', 0)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing AI Hub connection: {e}")
        return False

def test_ai_hub_models():
    """Test fetching available models."""
    print("\n🤖 Testing AI Hub Models...")
    
    try:
        reviewer = get_ai_hub_reviewer()
        models = reviewer.get_available_models()
        
        print(f"📊 Found {len(models)} models:")
        for model in models[:5]:  # Show first 5
            print(f"  - {model.get('provider', 'Unknown')} / {model.get('model', 'Unknown')}")
        
        if len(models) > 5:
            print(f"  ... and {len(models) - 5} more models")
        
        return True
        
    except Exception as e:
        print(f"❌ Error fetching models: {e}")
        return False

def test_ai_hub_assistants():
    """Test fetching available assistants."""
    print("\n👥 Testing AI Hub Assistants...")
    
    try:
        reviewer = get_ai_hub_reviewer()
        assistants = reviewer.get_available_assistants()
        
        print(f"📊 Found {len(assistants)} assistants:")
        for assistant in assistants[:5]:  # Show first 5
            print(f"  - {assistant.get('display_name', 'Unknown')} (ID: {assistant.get('id', 'Unknown')})")
        
        if len(assistants) > 5:
            print(f"  ... and {len(assistants) - 5} more assistants")
        
        return True
        
    except Exception as e:
        print(f"❌ Error fetching assistants: {e}")
        return False

def test_simple_chat():
    """Test simple chat functionality."""
    print("\n💬 Testing Simple Chat...")
    
    try:
        # Create client directly
        client = AIHubClient(api_token=settings.ai_hub_token)
        
        # Create session
        session = client.create_chat_session()
        print(f"✅ Created chat session: {session.chat_id}")
        
        # Send simple message
        response = session.send_message_simple("Hello! Can you help me with design reviews?")
        
        print(f"🤖 AI Response: {response.get('answer', 'No response')[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing simple chat: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 AI Hub Integration Tests")
    print("=" * 50)
    
    # Check environment
    token = settings.ai_hub_token
    if not token:
        print("❌ AI_HUB_TOKEN not found in environment variables")
        print("Please add your token to .env file:")
        print("AI_HUB_TOKEN=your_token_here")
        return
    
    print(f"🔑 Token configured: {token[:20]}...{token[-10:]}")
    print(f"🌐 Base URL: {settings.ai_hub_url}")
    
    # Run tests
    tests = [
        test_ai_hub_connection,
        test_ai_hub_models, 
        test_ai_hub_assistants,
        test_simple_chat
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 50)
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! AI Hub integration is working correctly.")
        print("\n🚀 You can now use AI Hub in your design review application!")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
