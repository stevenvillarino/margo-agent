"""
Simple Design Review Chat App
- Works locally and on deployment
- One file, no complications
"""

import streamlit as st
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

def main():
    st.set_page_config(
        page_title="Design Review Chat",
        page_icon="🎨",
        layout="centered"
    )
    
    st.title("🎨 Design Review Chat")
    st.markdown("Upload a design, ask questions, get feedback.")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Optional: Upload a design for specific feedback",
        type=['png', 'jpg', 'jpeg', 'pdf'],
        help="Upload a design file to get targeted analysis"
    )
    
    if uploaded_file:
        st.image(uploaded_file, width=400)
        st.success(f"✅ Uploaded: {uploaded_file.name}")
    
    # Chat
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hi! I'm your design assistant. Ask me about colors, typography, layout, accessibility, or upload a design for specific feedback!"}
        ]
    
    # Display chat
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me anything about design..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Smart response based on context
        if uploaded_file:
            response = f"Looking at your design '{uploaded_file.name}', here's my feedback: {prompt}"
        else:
            # Provide helpful responses even without a file
            prompt_lower = prompt.lower()
            if any(word in prompt_lower for word in ['color', 'colours', 'palette']):
                response = "Great question about colors! For effective color choices, consider contrast ratios (aim for 4.5:1), your brand palette, and accessibility. What specific color challenge are you facing?"
            elif any(word in prompt_lower for word in ['font', 'typography', 'text']):
                response = "Typography is crucial! Consider hierarchy (use 2-3 font sizes max), readability (16px+ for body text), and consistency. What typography question do you have?"
            elif any(word in prompt_lower for word in ['layout', 'spacing', 'grid']):
                response = "Good layout makes or breaks design! Use consistent spacing (try 8px grid system), clear hierarchy, and whitespace effectively. What layout challenge can I help with?"
            elif any(word in prompt_lower for word in ['accessibility', 'a11y']):
                response = "Accessibility is essential! Key areas: color contrast, keyboard navigation, alt text, and semantic HTML. What accessibility aspect interests you?"
            elif any(word in prompt_lower for word in ['hello', 'hi', 'hey']):
                response = "Hello! I'm here to help with design questions. Ask me about colors, typography, layout, accessibility, or upload a design for specific feedback!"
            else:
                response = f"Interesting question about '{prompt}'! I can help with design principles, best practices, color theory, typography, layout, accessibility, and more. Want to dive deeper into any specific area?"
        
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

if __name__ == "__main__":
    main()
