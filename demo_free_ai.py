#!/usr/bin/env python3
"""
Quick demo of free local AI design review
"""

import sys
import os

# Add the current directory to the Python path
sys.path.append('/Users/stevenvillarino/margo-agent')

from agents.local_reviewer import local_agent

def demo_local_ai():
    """Demo the local AI functionality."""
    print("🎨 Free Local Design Review Demo")
    print("=" * 40)
    
    # Check if Ollama is running
    if not local_agent._check_ollama_running():
        print("❌ Ollama is not running")
        print("\n🔧 Quick Setup:")
        print("1. Install: curl -fsSL https://ollama.ai/install.sh | sh")
        print("2. Start: ollama serve")
        print("3. Download model: ollama pull llama3.1:8b")
        print("4. Run this demo again")
        return
    
    print("✅ Ollama is running!")
    
    # Show available models
    models = local_agent.get_available_models()
    if models:
        print(f"📦 Available models: {', '.join(models)}")
    else:
        print("📦 No models found. Run: ollama pull llama3.1:8b")
        return
    
    # Demo text review
    print("\n🔍 Testing design review...")
    
    sample_design_description = """
    I have a mobile app login screen with:
    - Email input field at the top
    - Password input field below email
    - Large blue "Login" button
    - "Forgot Password?" link below the button
    - Social login buttons (Google, Facebook) at the bottom
    - The background is white with the company logo at the top
    """
    
    result = local_agent.review_design_local(
        text_content=sample_design_description,
        review_type="UI/UX Design",
        detail_level=3
    )
    
    if 'error' in result:
        print(f"❌ Error: {result['error']}")
    else:
        print("✅ Review generated successfully!")
        print("\n📝 Sample Review:")
        print("-" * 40)
        print(result['review'][:500] + "..." if len(result['review']) > 500 else result['review'])
        print("-" * 40)
        print(f"\n🤖 Model used: {result.get('model', 'Unknown')}")
    
    print("\n🎯 Next steps:")
    print("1. Open the Streamlit app")
    print("2. Check 'Use Free Local AI' in the sidebar")
    print("3. Upload images or enter design descriptions")
    print("4. Get free AI-powered design feedback!")

if __name__ == "__main__":
    demo_local_ai()
