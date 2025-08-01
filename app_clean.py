"""
Clean Design Review Chat Interface
- Accepts Figma links directly
- No technical status displays  
- Natural conversation flow
- Automatic design extraction and analysis
"""

import streamlit as st
import base64
import re
import requests
from io import BytesIO
from PIL import Image
import os
from typing import Dict, Any, Optional, List
from datetime import datetime

from dotenv import load_dotenv
from agents.enhanced_system import EnhancedDesignReviewSystem
from agents.document_loaders import document_loader_manager

# Load environment variables
load_dotenv()

class CleanDesignChat:
    """Clean, user-friendly design review chat interface."""
    
    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        
        # Initialize enhanced system if API key is available
        self.enhanced_system = None
        if self.openai_api_key:
            try:
                self.enhanced_system = EnhancedDesignReviewSystem(
                    openai_api_key=self.openai_api_key,
                    learning_enabled=True
                )
            except Exception as e:
                st.error(f"System initialization failed: {e}")
    
    def run(self):
        """Run the clean chat interface."""
        st.set_page_config(
            page_title="Margo - Design Review Chat",
            page_icon="🎨",
            layout="wide",
            initial_sidebar_state="collapsed"
        )
        
        # Initialize session state
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        if "current_designs" not in st.session_state:
            st.session_state.current_designs = {}
        
        # Main interface
        st.title("💬 Margo - Design Review Chat")
        st.markdown("*Just paste your Figma link or upload a design - I'll analyze it naturally.*")
        
        # Show API key status briefly if needed
        if not self.openai_api_key:
            st.error("⚠️ Please set your OpenAI API key in the `.env` file to start chatting.")
            return
            
        # Chat interface
        self._render_chat()
    
    def _render_chat(self):
        """Render the main chat interface."""
        
        # Display chat history
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"], avatar=message.get("avatar", None)):
                st.markdown(message["content"])
                
                # Show design preview if attached
                if message.get("design_preview"):
                    st.image(message["design_preview"], width=400)
        
        # Chat input
        if prompt := st.chat_input("Paste a Figma link, upload a design, or ask anything..."):
            self._handle_user_input(prompt)
    
    def _handle_user_input(self, user_input: str):
        """Handle user input - detect Figma links, images, or natural requests."""
        
        # Add user message to chat
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input,
            "avatar": "👤"
        })
        
        # Check if input contains Figma link
        figma_urls = self._extract_figma_urls(user_input)
        
        if figma_urls:
            self._handle_figma_links(figma_urls, user_input)
        else:
            # Handle as general chat or design question
            self._handle_general_chat(user_input)
        
        st.rerun()
    
    def _extract_figma_urls(self, text: str) -> List[str]:
        """Extract Figma URLs from text."""
        figma_patterns = [
            r'https://www\.figma\.com/file/[^\s]+',
            r'https://www\.figma\.com/design/[^\s]+',
            r'https://figma\.com/file/[^\s]+',
            r'https://figma\.com/design/[^\s]+'
        ]
        
        urls = []
        for pattern in figma_patterns:
            matches = re.findall(pattern, text)
            urls.extend(matches)
        
        return urls
    
    def _handle_figma_links(self, figma_urls: List[str], user_request: str):
        """Handle Figma links - extract designs and analyze using LangChain loader."""
        
        # Show processing message
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": "🔍 Extracting design data from Figma...",
            "avatar": "🎨"
        })
        
        try:
            figma_url = figma_urls[0]  # Process first URL
            
            # Extract file key using document loader manager
            file_key = document_loader_manager.extract_figma_file_key(figma_url)
            
            if not file_key:
                raise ValueError("Could not extract file key from Figma URL")
            
            # Load Figma file using LangChain document loader
            figma_documents = document_loader_manager.load_figma_file(file_key)
            
            if not figma_documents:
                raise ValueError("No design data extracted from Figma file")
            
            # Store the extracted design data
            figma_data = {
                "url": figma_url,
                "file_key": file_key,
                "documents": figma_documents,
                "content": "\n".join([doc.page_content for doc in figma_documents])
            }
            
            # Store in session for analysis
            st.session_state.current_designs[f"figma_{file_key}"] = figma_data
            
            # Update processing message with success
            st.session_state.chat_history.pop()
            
            analysis_message = f"""
✅ **Figma Design Extracted Successfully!**

**File:** {figma_url}
**Extracted:** {len(figma_documents)} design elements/components

I've loaded your Figma design and can now analyze:
- **Design Structure** - Components, layouts, and hierarchy
- **Design Tokens** - Colors, typography, spacing
- **Component Library** - Reusable elements and patterns
- **Design System** - Consistency and standards adherence

**What would you like me to review?** You can ask things like:
- "Analyze the overall design system"
- "Check for accessibility issues"
- "Review the component consistency"
- "How does this align with our brand?"
            """
            
            st.session_state.chat_history.append({
                "role": "assistant", 
                "content": analysis_message,
                "avatar": "🎨"
            })
            
        except Exception as e:
            # Replace processing message with error
            st.session_state.chat_history.pop()
            
            error_message = f"""
❌ **Figma Integration Issue**

I had trouble extracting design data from that Figma link: {str(e)}

**To fix this:**
1. Make sure you have a Figma access token in your `.env` file
2. Ensure the Figma file is publicly accessible or you have access
3. Try uploading a screenshot instead

**Get Figma Access Token:**
1. Go to [Figma Developer Settings](https://www.figma.com/developers/api#access-tokens)
2. Generate a new personal access token
3. Add it to your `.env` file: `FIGMA_ACCESS_TOKEN=your_token_here`
4. Restart the application
            """
            
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": error_message,
                "avatar": "⚠️"
            })
    
    def _handle_general_chat(self, user_input: str):
        """Handle general chat or design questions."""
        
        # Check if there are uploaded designs to reference
        if st.session_state.current_designs:
            self._analyze_with_context(user_input)
        else:
            self._general_design_chat(user_input)
    
    def _analyze_with_context(self, user_request: str):
        """Analyze user request in context of uploaded designs or Figma data."""
        
        if not self.enhanced_system:
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": "I need the OpenAI API key to analyze designs. Please check your configuration.",
                "avatar": "⚠️"
            })
            return
        
        # Show thinking message
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": "🤔 Analyzing your design with our expert team...",
            "avatar": "🎨"
        })
        
        try:
            # Get the most recent design
            design_name, design_data = list(st.session_state.current_designs.items())[-1]
            
            # Check if it's Figma data or image data
            if design_name.startswith("figma_"):
                # Handle Figma document analysis
                figma_data = design_data
                context = {
                    "user_request": user_request,
                    "design_type": "figma_file",
                    "priority_focus": self._detect_review_focus(user_request),
                    "figma_url": figma_data["url"],
                    "figma_content": figma_data["content"]
                }
                
                # Analyze Figma content using enhanced system
                # Note: Enhanced system needs to be updated to handle Figma documents
                review_results = self._analyze_figma_design(figma_data, context)
                
            else:
                # Handle image analysis
                context = {
                    "user_request": user_request,
                    "design_type": "ui_screen",
                    "priority_focus": self._detect_review_focus(user_request)
                }
                
                # **REAL SYSTEM CALL for images**
                review_results = self.enhanced_system.conduct_comprehensive_review(
                    design_image_base64=design_data,
                    context=context
                )
            
            # Format results naturally
            response = self._format_natural_review(review_results, user_request)
            
            # Replace thinking message with results
            st.session_state.chat_history.pop()
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": response,
                "avatar": "🎨"
            })
            
        except Exception as e:
            st.session_state.chat_history.pop()
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": f"I encountered an issue analyzing your design: {str(e)}",
                "avatar": "⚠️"
            })
    
    def _analyze_figma_design(self, figma_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze Figma design using the document content."""
        
        # For now, create a text-based analysis of the Figma content
        # TODO: Integrate with enhanced system for full multi-agent Figma analysis
        
        figma_content = figma_data["content"]
        user_request = context["user_request"]
        
        # Simple analysis for now - this should be replaced with full agent orchestration
        analysis = f"""
**Figma File Analysis**

Based on the extracted Figma design data, here's my analysis:

**Design Structure:**
{figma_content[:500]}...

**Key Observations:**
- Design components and structure successfully extracted
- Ready for detailed multi-agent analysis
- Can analyze design tokens, component consistency, and accessibility

**Next Steps:**
This Figma integration is working! The design data has been extracted and is ready for comprehensive analysis by all our specialist agents.
        """
        
        return {
            "summary": analysis,
            "agent_reviews": [],
            "recommendations": [
                "Figma integration is working - design data extracted successfully",
                "Ready for full multi-agent analysis implementation",
                "Can now analyze design systems, tokens, and component libraries"
            ]
        }
    
    def _general_design_chat(self, user_input: str):
        """Handle general design questions without specific designs."""
        
        # Check if user is asking for help or greeting
        greetings = ["hello", "hi", "hey", "help", "what can you do"]
        
        if any(greeting in user_input.lower() for greeting in greetings):
            response = """
👋 Hi! I'm Margo, your AI design review assistant.

I can help you with:
- **Design Reviews** - Upload screenshots or paste Figma links
- **Design Questions** - Ask about UI/UX best practices  
- **Accessibility** - Check if your designs are inclusive
- **Brand Consistency** - Ensure alignment with design systems
- **User Experience** - Validate user flows and interactions

Just share your design or ask me anything! 🎨
            """
        else:
            # General design advice
            response = f"""
That's a great design question! 

To give you the most helpful answer, could you:
1. **Share a specific design** - Upload a screenshot or paste a Figma link
2. **Provide more context** - What type of product/feature is this for?

I can offer much better insights when I can see what you're working on. In the meantime, I'm happy to discuss general design principles if you'd like! 
            """
        
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": response,
            "avatar": "🎨"
        })
    
    def _detect_review_focus(self, user_request: str) -> List[str]:
        """Detect what aspects of the design to focus on."""
        focus_keywords = {
            "accessibility": ["accessible", "a11y", "disability", "screen reader", "contrast"],
            "usability": ["usable", "user", "ux", "flow", "navigation", "intuitive"],
            "visual": ["visual", "ui", "color", "typography", "layout", "design"],
            "brand": ["brand", "consistent", "style", "guidelines", "identity"],
            "business": ["business", "conversion", "engagement", "revenue", "goals"]
        }
        
        detected_focus = []
        request_lower = user_request.lower()
        
        for focus, keywords in focus_keywords.items():
            if any(keyword in request_lower for keyword in keywords):
                detected_focus.append(focus)
        
        return detected_focus if detected_focus else ["comprehensive"]
    
    def _format_natural_review(self, review_results: Dict[str, Any], user_request: str) -> str:
        """Format review results in a natural, conversational way."""
        
        if not review_results or "error" in review_results:
            return "I had trouble analyzing the design. Could you try uploading the image again?"
        
        # Extract key insights from all agents
        summary = review_results.get("summary", "")
        agent_reviews = review_results.get("agent_reviews", [])
        
        # Create natural response
        response_parts = []
        
        # Start with overall assessment
        if summary:
            response_parts.append(f"## 🎯 Overall Assessment\n{summary}")
        
        # Add key insights from each agent
        if agent_reviews:
            response_parts.append("## 💡 Key Insights")
            
            for review in agent_reviews[:3]:  # Top 3 most relevant
                agent_name = review.get("agent_name", "Design Expert")
                feedback = review.get("feedback", "")
                
                if feedback:
                    # Extract first few sentences for concise display
                    brief_feedback = ". ".join(feedback.split(".")[:2]) + "."
                    response_parts.append(f"**{agent_name}**: {brief_feedback}")
        
        # Add actionable recommendations
        recommendations = review_results.get("recommendations", [])
        if recommendations:
            response_parts.append("## 🚀 Next Steps")
            for i, rec in enumerate(recommendations[:3], 1):
                response_parts.append(f"{i}. {rec}")
        
        # Add engaging closing
        response_parts.append("*Want me to dive deeper into any specific aspect? Just ask!* 😊")
        
        return "\n\n".join(response_parts)

# File upload handler
@st.fragment
def handle_file_upload():
    """Handle file uploads in a fragment."""
    uploaded_file = st.file_uploader(
        "Upload a design screenshot",
        type=['png', 'jpg', 'jpeg'],
        key="design_upload",
        label_visibility="collapsed"
    )
    
    if uploaded_file:
        # Process and store the image
        image_data = base64.b64encode(uploaded_file.read()).decode()
        st.session_state.current_designs[uploaded_file.name] = image_data
        
        # Add to chat history with preview
        st.session_state.chat_history.append({
            "role": "user",
            "content": f"Uploaded design: {uploaded_file.name}",
            "avatar": "📎",
            "design_preview": uploaded_file
        })
        
        # Trigger automatic analysis
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": "🎨 Great! I can see your design. What would you like me to review specifically? I can analyze UI, UX, accessibility, brand consistency, or give you a comprehensive overview.",
            "avatar": "🎨"
        })
        
        st.rerun()

# Main app
def main():
    chat = CleanDesignChat()
    
    # Add file upload in sidebar
    with st.sidebar:
        st.markdown("### 📎 Upload Design")
        handle_file_upload()
        
        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_history = []
            st.session_state.current_designs = {}
            st.rerun()
    
    chat.run()

if __name__ == "__main__":
    main()
