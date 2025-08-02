"""
Knowledge Management Interface
Simple web interface for adding knowledge to the Margo Agent system
"""

import streamlit as st
import json
import requests
from datetime import datetime
from typing import Dict, Any
import os

# Your Cloudflare Worker URL
CLOUDFLARE_WORKER_URL = "https://roku-design-review-bot.madetoenvy-llc.workers.dev"

def main():
    st.set_page_config(
        page_title="Margo Knowledge Manager",
        page_icon="🧠",
        layout="wide"
    )
    
    st.title("🧠 Margo Knowledge Manager")
    st.markdown("Add knowledge to the system without touching code")
    
    # Sidebar for navigation
    st.sidebar.title("Knowledge Categories")
    category = st.sidebar.radio(
        "What type of knowledge are you adding?",
        [
            "Brand Guidelines",
            "Design Patterns", 
            "Accessibility Standards",
            "UI Components",
            "User Research",
            "Technical Standards",
            "Business Rules",
            "Custom Knowledge"
        ]
    )
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header(f"Add {category}")
        
        if category == "Brand Guidelines":
            add_brand_knowledge()
        elif category == "Design Patterns":
            add_design_patterns()
        elif category == "Accessibility Standards":
            add_accessibility_knowledge()
        elif category == "UI Components":
            add_component_knowledge()
        elif category == "User Research":
            add_research_knowledge()
        elif category == "Technical Standards":
            add_technical_knowledge()
        elif category == "Business Rules":
            add_business_knowledge()
        else:
            add_custom_knowledge()
    
    with col2:
        st.header("Quick Actions")
        
        # File upload
        st.subheader("📁 Upload Files")
        uploaded_files = st.file_uploader(
            "Drop files here (PDF, DOC, TXT, JSON)",
            accept_multiple_files=True,
            type=['pdf', 'doc', 'docx', 'txt', 'json', 'md']
        )
        
        if uploaded_files:
            for file in uploaded_files:
                process_uploaded_file(file, category)
        
        # Import from URL
        st.subheader("🔗 Import from URL")
        url = st.text_input("Enter URL to documentation/guidelines")
        if st.button("Import from URL"):
            if url:
                import_from_url(url, category)
        
        # View current knowledge
        st.subheader("👁️ View Current Knowledge")
        if st.button("Show All Knowledge"):
            show_current_knowledge()

def add_brand_knowledge():
    """Simple form for adding brand knowledge."""
    with st.form("brand_form"):
        st.subheader("Brand Information")
        
        # Colors
        col1, col2 = st.columns(2)
        with col1:
            primary_color = st.color_picker("Primary Brand Color", "#662D91")
        with col2:
            secondary_color = st.color_picker("Secondary Color", "#4A1F6B")
        
        # Typography
        primary_font = st.text_input("Primary Font", "Roku Sans")
        fallback_fonts = st.text_input("Fallback Fonts", "Helvetica Neue, Arial, sans-serif")
        
        # Voice & Tone
        voice_tone = st.text_area("Voice & Tone Guidelines", 
                                 "Friendly, helpful, clear, trustworthy")
        
        # Logo guidelines
        logo_guidelines = st.text_area("Logo Usage Guidelines",
                                     "Minimum 24px height, proper clear space")
        
        # Additional notes
        notes = st.text_area("Additional Brand Notes")
        
        submitted = st.form_submit_button("💾 Save Brand Knowledge")
        
        if submitted:
            knowledge_data = {
                "category": "brand_guidelines",
                "data": {
                    "colors": {
                        "primary": primary_color,
                        "secondary": secondary_color
                    },
                    "typography": {
                        "primary_font": primary_font,
                        "fallback_fonts": fallback_fonts
                    },
                    "voice_tone": voice_tone,
                    "logo_guidelines": logo_guidelines,
                    "notes": notes
                },
                "timestamp": datetime.now().isoformat(),
                "added_by": "knowledge_manager"
            }
            
            save_knowledge(knowledge_data)

def add_design_patterns():
    """Form for adding design patterns."""
    with st.form("pattern_form"):
        st.subheader("Design Pattern")
        
        pattern_name = st.text_input("Pattern Name", "e.g., Navigation Menu")
        pattern_type = st.selectbox("Pattern Type", [
            "Navigation", "Forms", "Cards", "Modals", "Buttons", 
            "Layout", "Data Display", "Feedback", "Other"
        ])
        
        when_to_use = st.text_area("When to Use This Pattern")
        when_not_to_use = st.text_area("When NOT to Use This Pattern")
        
        best_practices = st.text_area("Best Practices")
        common_mistakes = st.text_area("Common Mistakes to Avoid")
        
        # Image upload for pattern examples
        pattern_image = st.file_uploader("Upload Pattern Example", type=['png', 'jpg', 'jpeg'])
        
        submitted = st.form_submit_button("💾 Save Design Pattern")
        
        if submitted:
            knowledge_data = {
                "category": "design_patterns",
                "data": {
                    "name": pattern_name,
                    "type": pattern_type,
                    "when_to_use": when_to_use,
                    "when_not_to_use": when_not_to_use,
                    "best_practices": best_practices,
                    "common_mistakes": common_mistakes,
                    "has_image": pattern_image is not None
                },
                "timestamp": datetime.now().isoformat(),
                "added_by": "knowledge_manager"
            }
            
            save_knowledge(knowledge_data)

def add_custom_knowledge():
    """Form for adding any custom knowledge."""
    with st.form("custom_form"):
        st.subheader("Custom Knowledge")
        
        title = st.text_input("Knowledge Title")
        category_custom = st.text_input("Custom Category")
        
        content = st.text_area("Knowledge Content", height=200)
        
        tags = st.text_input("Tags (comma-separated)", "e.g., design, ux, accessibility")
        
        importance = st.selectbox("Importance Level", ["Low", "Medium", "High", "Critical"])
        
        submitted = st.form_submit_button("💾 Save Custom Knowledge")
        
        if submitted:
            knowledge_data = {
                "category": category_custom or "custom",
                "data": {
                    "title": title,
                    "content": content,
                    "tags": [tag.strip() for tag in tags.split(",") if tag.strip()],
                    "importance": importance
                },
                "timestamp": datetime.now().isoformat(),
                "added_by": "knowledge_manager"
            }
            
            save_knowledge(knowledge_data)

def process_uploaded_file(file, category):
    """Process uploaded files and extract knowledge."""
    st.info(f"Processing {file.name}...")
    
    try:
        if file.type == "application/json":
            # Parse JSON directly
            content = json.loads(file.read())
            knowledge_data = {
                "category": category.lower().replace(" ", "_"),
                "data": content,
                "source": f"uploaded_file_{file.name}",
                "timestamp": datetime.now().isoformat(),
                "added_by": "file_upload"
            }
            save_knowledge(knowledge_data)
            
        elif file.type == "text/plain" or file.name.endswith('.md'):
            # Parse text/markdown
            content = file.read().decode('utf-8')
            knowledge_data = {
                "category": category.lower().replace(" ", "_"),
                "data": {
                    "content": content,
                    "filename": file.name
                },
                "source": f"uploaded_file_{file.name}",
                "timestamp": datetime.now().isoformat(),
                "added_by": "file_upload"
            }
            save_knowledge(knowledge_data)
            
        else:
            st.warning(f"File type {file.type} not yet supported for automatic processing")
            
    except Exception as e:
        st.error(f"Error processing file: {e}")

def import_from_url(url, category):
    """Import knowledge from external URL."""
    st.info(f"Importing from {url}...")
    
    try:
        # Use the existing workflow orchestrator to import
        knowledge_data = {
            "category": category.lower().replace(" ", "_"),
            "data": {
                "source_url": url,
                "import_method": "url_import"
            },
            "timestamp": datetime.now().isoformat(),
            "added_by": "url_import"
        }
        
        save_knowledge(knowledge_data)
        st.success("URL import queued for processing")
        
    except Exception as e:
        st.error(f"Error importing from URL: {e}")

def save_knowledge(knowledge_data):
    """Save knowledge to the system."""
    try:
        # Send to Cloudflare Worker
        response = requests.post(
            f"{CLOUDFLARE_WORKER_URL}/knowledge",
            json=knowledge_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            st.success("✅ Knowledge saved successfully!")
            st.balloons()
        else:
            st.error(f"Failed to save knowledge: {response.text}")
            
    except Exception as e:
        st.error(f"Error saving knowledge: {e}")
        
        # Fallback: Save locally for manual processing
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"knowledge_backup_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(knowledge_data, f, indent=2)
        
        st.warning(f"Saved backup to {filename} - please process manually")

def show_current_knowledge():
    """Display current knowledge in the system."""
    try:
        response = requests.get(f"{CLOUDFLARE_WORKER_URL}/knowledge")
        
        if response.status_code == 200:
            knowledge = response.json()
            st.json(knowledge)
        else:
            st.error("Could not retrieve current knowledge")
            
    except Exception as e:
        st.error(f"Error retrieving knowledge: {e}")

# Add forms for other categories
def add_accessibility_knowledge():
    with st.form("accessibility_form"):
        st.subheader("Accessibility Standard")
        
        standard_name = st.text_input("Standard Name", "e.g., WCAG 2.1 AA")
        guideline = st.text_area("Guideline Description")
        how_to_test = st.text_area("How to Test This")
        examples = st.text_area("Good/Bad Examples")
        
        submitted = st.form_submit_button("💾 Save Accessibility Knowledge")
        
        if submitted:
            knowledge_data = {
                "category": "accessibility",
                "data": {
                    "standard_name": standard_name,
                    "guideline": guideline,
                    "how_to_test": how_to_test,
                    "examples": examples
                },
                "timestamp": datetime.now().isoformat(),
                "added_by": "knowledge_manager"
            }
            save_knowledge(knowledge_data)

def add_component_knowledge():
    with st.form("component_form"):
        st.subheader("UI Component")
        
        component_name = st.text_input("Component Name")
        component_purpose = st.text_area("Purpose & Use Cases")
        dos = st.text_area("Do's")
        donts = st.text_area("Don'ts")
        
        submitted = st.form_submit_button("💾 Save Component Knowledge")
        
        if submitted:
            knowledge_data = {
                "category": "ui_components",
                "data": {
                    "name": component_name,
                    "purpose": component_purpose,
                    "dos": dos,
                    "donts": donts
                },
                "timestamp": datetime.now().isoformat(),
                "added_by": "knowledge_manager"
            }
            save_knowledge(knowledge_data)

def add_research_knowledge():
    with st.form("research_form"):
        st.subheader("User Research Insights")
        
        research_title = st.text_input("Research Title")
        key_findings = st.text_area("Key Findings")
        design_implications = st.text_area("Design Implications")
        
        submitted = st.form_submit_button("💾 Save Research Knowledge")
        
        if submitted:
            knowledge_data = {
                "category": "user_research",
                "data": {
                    "title": research_title,
                    "findings": key_findings,
                    "implications": design_implications
                },
                "timestamp": datetime.now().isoformat(),
                "added_by": "knowledge_manager"
            }
            save_knowledge(knowledge_data)

def add_technical_knowledge():
    with st.form("technical_form"):
        st.subheader("Technical Standard")
        
        tech_standard = st.text_input("Technical Standard/Requirement")
        implementation = st.text_area("Implementation Guidelines")
        
        submitted = st.form_submit_button("💾 Save Technical Knowledge")
        
        if submitted:
            knowledge_data = {
                "category": "technical_standards",
                "data": {
                    "standard": tech_standard,
                    "implementation": implementation
                },
                "timestamp": datetime.now().isoformat(),
                "added_by": "knowledge_manager"
            }
            save_knowledge(knowledge_data)

def add_business_knowledge():
    with st.form("business_form"):
        st.subheader("Business Rule/Requirement")
        
        business_rule = st.text_input("Business Rule")
        rationale = st.text_area("Business Rationale")
        
        submitted = st.form_submit_button("💾 Save Business Knowledge")
        
        if submitted:
            knowledge_data = {
                "category": "business_rules",
                "data": {
                    "rule": business_rule,
                    "rationale": rationale
                },
                "timestamp": datetime.now().isoformat(),
                "added_by": "knowledge_manager"
            }
            save_knowledge(knowledge_data)

if __name__ == "__main__":
    main()
