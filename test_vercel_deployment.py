#!/usr/bin/env python3
"""
Quick test to verify Vercel deployment readiness
"""

import sys
import os

def test_imports():
    """Test if all required imports work"""
    print("Testing imports...")
    
    try:
        import flask
        print("✅ Flask imported successfully")
    except ImportError as e:
        print(f"❌ Flask import failed: {e}")
        return False
    
    try:
        from dotenv import load_dotenv
        print("✅ python-dotenv imported successfully")
    except ImportError as e:
        print(f"❌ python-dotenv import failed: {e}")
        return False
    
    try:
        from PIL import Image
        print("✅ Pillow imported successfully")
    except ImportError as e:
        print(f"❌ Pillow import failed: {e}")
        return False
    
    try:
        import requests
        print("✅ requests imported successfully")
    except ImportError as e:
        print(f"❌ requests import failed: {e}")
        return False
    
    # Test optional AI imports
    try:
        import langchain
        print("✅ LangChain imported successfully")
    except ImportError as e:
        print(f"⚠️  LangChain import failed (optional): {e}")
    
    try:
        import openai
        print("✅ OpenAI imported successfully")
    except ImportError as e:
        print(f"⚠️  OpenAI import failed (optional): {e}")
    
    return True

def test_vercel_app():
    """Test if vercel_app.py can be imported"""
    print("\nTesting vercel_app.py...")
    
    try:
        # Add current directory to path
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        import vercel_app
        print("✅ vercel_app.py imported successfully")
        
        # Test if Flask app exists
        if hasattr(vercel_app, 'app'):
            print("✅ Flask app instance found")
            return True
        else:
            print("❌ Flask app instance not found")
            return False
            
    except Exception as e:
        print(f"❌ vercel_app.py import failed: {e}")
        return False

def main():
    print("=== Vercel Deployment Readiness Test ===\n")
    
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    print(f"Python path: {sys.path[:3]}...\n")
    
    imports_ok = test_imports()
    app_ok = test_vercel_app()
    
    if imports_ok and app_ok:
        print("\n🎉 All tests passed! Vercel deployment should work.")
        return 0
    else:
        print("\n❌ Some tests failed. Check the errors above.")
        return 1

if __name__ == "__main__":
    exit(main())
