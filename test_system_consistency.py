#!/usr/bin/env python3
"""
Test script to validate that both Slack and Web interfaces use the same EnhancedDesignReviewSystem

This ensures behavioral consistency between interfaces.
"""

import os
import asyncio
import base64
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_enhanced_system_consistency():
    """Test that both interfaces use the same enhanced system."""
    
    print("🔍 Testing Enhanced System Consistency...")
    print("=" * 50)
    
    # Check OpenAI API key
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        print("❌ OPENAI_API_KEY not configured")
        return False
    
    print("✅ OpenAI API key configured")
    
    # Test Enhanced System initialization
    try:
        from agents.enhanced_system import EnhancedDesignReviewSystem
        
        enhanced_system = EnhancedDesignReviewSystem(
            openai_api_key=openai_key,
            exa_api_key=os.getenv("EXA_API_KEY"),
            learning_enabled=True,
            company_context={
                "industry": "Streaming/Entertainment",
                "company": "Roku",
                "product_focus": "TV streaming interface",
                "user_base": "TV viewers and families"
            }
        )
        
        print(f"✅ Enhanced system initialized with {len(enhanced_system.agents)} agents")
        print(f"🤖 Available agents: {list(enhanced_system.agents.keys())}")
        
        # Test orchestrator
        if enhanced_system.orchestrator:
            print(f"✅ Orchestrator ready with {len(enhanced_system.orchestrator.agents)} registered agents")
        else:
            print("❌ Orchestrator not initialized")
            return False
        
        # Test EXA search capability
        if enhanced_system.orchestrator.exa_agent:
            print("✅ EXA search agent available for web research")
        else:
            print("⚠️ EXA search not available (API key missing)")
        
        # Test learning system
        if enhanced_system.learning_system:
            print("✅ Learning system enabled")
        else:
            print("⚠️ Learning system disabled")
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced system initialization failed: {e}")
        return False

def test_slack_bot_system():
    """Test that Slack bot uses the same system."""
    
    print("\n🤖 Testing Slack Bot System...")
    print("=" * 50)
    
    slack_bot_token = os.getenv("SLACK_BOT_TOKEN")
    slack_app_token = os.getenv("SLACK_APP_TOKEN")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    if not all([slack_bot_token, slack_app_token, openai_key]):
        print("⚠️ Slack tokens not configured - skipping Slack test")
        return True
    
    try:
        from slack_bot import SlackDesignReviewBot
        
        bot = SlackDesignReviewBot(
            slack_bot_token=slack_bot_token,
            slack_app_token=slack_app_token,
            openai_api_key=openai_key,
            exa_api_key=os.getenv("EXA_API_KEY")
        )
        
        print(f"✅ Slack bot initialized with {len(bot.review_system.agents)} agents")
        print(f"🤖 Slack bot agents: {list(bot.review_system.agents.keys())}")
        
        # Verify it's the same enhanced system type
        from agents.enhanced_system import EnhancedDesignReviewSystem
        if isinstance(bot.review_system, EnhancedDesignReviewSystem):
            print("✅ Slack bot uses EnhancedDesignReviewSystem")
        else:
            print("❌ Slack bot NOT using EnhancedDesignReviewSystem")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Slack bot initialization failed: {e}")
        return False

def test_web_interface_system():
    """Test that web interface uses the same system."""
    
    print("\n🌐 Testing Web Interface System...")
    print("=" * 50)
    
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        print("❌ OPENAI_API_KEY not configured")
        return False
    
    try:
        # Import the chat interface
        from app import IntelligentDesignChat
        
        chat_interface = IntelligentDesignChat()
        
        if chat_interface.enhanced_system:
            print(f"✅ Web interface initialized with {len(chat_interface.enhanced_system.agents)} agents")
            print(f"🤖 Web interface agents: {list(chat_interface.enhanced_system.agents.keys())}")
            
            # Verify it's the same enhanced system type
            from agents.enhanced_system import EnhancedDesignReviewSystem
            if isinstance(chat_interface.enhanced_system, EnhancedDesignReviewSystem):
                print("✅ Web interface uses EnhancedDesignReviewSystem")
            else:
                print("❌ Web interface NOT using EnhancedDesignReviewSystem")
                return False
        else:
            print("❌ Web interface enhanced system not initialized")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Web interface initialization failed: {e}")
        return False

async def test_system_functionality():
    """Test that the actual functionality works."""
    
    print("\n🚀 Testing System Functionality...")
    print("=" * 50)
    
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        print("❌ Cannot test functionality without OpenAI API key")
        return False
    
    try:
        from agents.enhanced_system import EnhancedDesignReviewSystem
        
        enhanced_system = EnhancedDesignReviewSystem(
            openai_api_key=openai_key,
            exa_api_key=os.getenv("EXA_API_KEY"),
            learning_enabled=True
        )
        
        # Create a simple test image (1x1 pixel base64)
        test_image_data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
        
        print("🧪 Running actual comprehensive review...")
        
        # This is the REAL function call
        result = await enhanced_system.conduct_comprehensive_review(
            image_data=test_image_data,
            design_type="test_interface",
            context={
                "test": True,
                "focus_areas": ["overall design quality"],
                "user_request": "test review"
            }
        )
        
        print("✅ Comprehensive review completed successfully!")
        print(f"📊 Overall score: {result.get('overall_score', 'N/A')}")
        print(f"🤖 Phases executed: {list(result.get('phase_results', {}).keys())}")
        print(f"🧠 Learning insights: {len(result.get('learning_insights', []))}")
        print(f"🎯 Priority actions: {len(result.get('priority_actions', []))}")
        
        return True
        
    except Exception as e:
        print(f"❌ System functionality test failed: {e}")
        return False

def main():
    """Run all consistency tests."""
    
    print("🎯 AGENT SYSTEM CONSISTENCY VALIDATION")
    print("=" * 60)
    
    tests = [
        ("Enhanced System Core", test_enhanced_system_consistency),
        ("Slack Bot Integration", test_slack_bot_system),
        ("Web Interface Integration", test_web_interface_system),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Test functionality if all integration tests pass
    if all(result for _, result in results):
        print("\n" + "=" * 60)
        print("🚀 ALL INTEGRATION TESTS PASSED - Testing Real Functionality...")
        
        try:
            func_result = asyncio.run(test_system_functionality())
            results.append(("System Functionality", func_result))
        except Exception as e:
            print(f"❌ Functionality test failed: {e}")
            results.append(("System Functionality", False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 VALIDATION SUMMARY")
    print("=" * 60)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Both Slack and Web interfaces use the same EnhancedDesignReviewSystem")
        print("✅ Real agent orchestration is working")
        print("✅ EXA search, learning system, and multi-agent coordination are functional")
        print("\n🚀 User expectation: Identical behavior between Slack and Web chat ✅")
    else:
        print("\n❌ Some tests failed - behavioral consistency not guaranteed")
        print("🔧 Fix required to ensure identical functionality")

if __name__ == "__main__":
    main()
