#!/usr/bin/env python3
"""
Comprehensive QA Test Suite for Margo Agent Design Review System
This tests all critical functionality to ensure everything works.
"""

import requests
import time
import sys
import os

def test_streamlit_app(port=8503):
    """Test if Streamlit app is responsive."""
    print(f"🧪 Testing Streamlit app on port {port}...")
    
    try:
        # Test basic connectivity
        response = requests.get(f"http://localhost:{port}", timeout=10)
        if response.status_code == 200:
            print(f"✅ App loads successfully on port {port}")
            return True
        else:
            print(f"❌ App returned status code {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to connect to app: {e}")
        return False

def test_environment_setup():
    """Test environment configuration."""
    print("🧪 Testing environment setup...")
    
    # Check for .env file
    if os.path.exists('.env'):
        print("✅ .env file exists")
    else:
        print("⚠️ .env file not found")
    
    # Check for OpenAI key
    openai_key = os.getenv('OPENAI_API_KEY')
    if openai_key and len(openai_key) > 10:
        print("✅ OpenAI API key configured")
        return True
    else:
        print("⚠️ OpenAI API key not configured or too short")
        return False

def test_app_imports():
    """Test if the app imports correctly."""
    print("🧪 Testing app imports...")
    
    try:
        # Add the current directory to Python path
        sys.path.insert(0, os.getcwd())
        
        # Test basic imports
        import streamlit as st
        print("✅ Streamlit imports successfully")
        
        from app import IntelligentDesignChat
        print("✅ IntelligentDesignChat imports successfully")
        
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_basic_functionality():
    """Test basic chat functionality."""
    print("🧪 Testing basic functionality...")
    
    try:
        # Test the simple app 
        import subprocess
        result = subprocess.run([
            'python', '-c', """
import os
import sys
sys.path.insert(0, os.getcwd())

# Mock streamlit session state for testing
class MockSessionState:
    def __init__(self):
        self.chat_history = []
        self.uploaded_images = {}
        self.system_initialized = False

# Mock streamlit module  
class MockStreamlit:
    session_state = MockSessionState()

# Test the guidance function from app_fixed
sys.modules['streamlit'] = MockStreamlit()
from app_fixed import provide_guidance

# Test it
provide_guidance('hello')
print(f'SUCCESS: {len(MockStreamlit.session_state.chat_history)} messages added')
"""
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0 and "SUCCESS" in result.stdout:
            print("✅ Basic chat functionality works")
            return True
        else:
            print(f"❌ Basic functionality test failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Basic functionality test error: {e}")
        return False

def main():
    """Run comprehensive QA tests."""
    print("🎯 COMPREHENSIVE QA TEST SUITE")
    print("=" * 50)
    
    results = []
    
    # Test 1: Environment Setup
    results.append(("Environment Setup", test_environment_setup()))
    
    # Test 2: App Imports
    results.append(("App Imports", test_app_imports()))
    
    # Test 3: Basic Functionality
    results.append(("Basic Functionality", test_basic_functionality()))
    
    # Test 4: Streamlit App (if running)
    results.append(("Streamlit App", test_streamlit_app(8503)))
    
    # Print results
    print("\n" + "=" * 50)
    print("🏁 QA TEST RESULTS")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<20} {status}")
        if result:
            passed += 1
    
    print("=" * 50)
    print(f"SUMMARY: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - System is working correctly!")
        print("\n📋 NEXT STEPS:")
        print("1. Open http://localhost:8503 in your browser")
        print("2. Try typing 'hello' in the chat")
        print("3. Upload an image and ask for a review")
        print("4. The chat should respond appropriately")
    else:
        print("⚠️ SOME TESTS FAILED - Please fix the issues above")
    
    return passed == total

if __name__ == "__main__":
    main()
