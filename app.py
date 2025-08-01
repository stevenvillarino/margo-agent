import streamlit as st
import os
from dotenv import load_dotenv
from PIL import Image
from agents.design_reviewer import DesignReviewAgent
from agents.document_loaders import document_loader_manager
from agents.vp_preferences import vp_preference_manager
from agents.local_reviewer import local_agent
from agents.ai_hub_cloud_reviewer import get_ai_hub_reviewer, is_ai_hub_available
from config.settings import settings

# Load environment variables
load_dotenv()

def display_review_results(review_result: dict, include_suggestions: bool, evaluation_mode: str = "Standard Design Review"):
    """Helper function to display review results consistently."""
    if 'error' in review_result:
        st.error(review_result['error'])
        if 'setup_instructions' in review_result:
            with st.expander("Setup Instructions"):
                setup = review_result['setup_instructions']
                if isinstance(setup, dict):
                    st.markdown("**Install Ollama:**")
                    st.code(setup.get('install', ''))
                    st.markdown("**Start Ollama:**")
                    st.code(setup.get('start', ''))
                    st.markdown("**Download Models:**")
                    if 'models' in setup:
                        for model_type, command in setup['models'].items():
                            st.code(command)
        return
    
    st.success("Analysis Complete!")
    
    # Source information
    if 'source' in review_result:
        source_info = f"📊 Source: {review_result['source'].title()}"
        if review_result['source'] == 'local_ollama':
            source_info += f" (Model: {review_result.get('model', 'Unknown')})"
        elif 'file_key' in review_result:
            source_info += f" (File: {review_result['file_key'][:10]}...)"
        elif 'space_key' in review_result:
            source_info += f" (Space: {review_result['space_key']})"
        if 'pages_reviewed' in review_result:
            source_info += f" - {review_result['pages_reviewed']} pages"
        st.info(source_info)
    
    # Display based on evaluation mode
    if evaluation_mode == "Roku TV Design Review":
        display_roku_results(review_result)
    else:
        display_standard_results(review_result, include_suggestions)

def display_standard_results(review_result: dict, include_suggestions: bool):
    """Display standard design review results."""
    # Overall score
    if 'score' in review_result:
        st.metric("Design Score", f"{review_result['score']}/10")
    
    # Review content
    if 'review' in review_result:
        st.markdown("### Review")
        st.write(review_result['review'])
    
    # Suggestions
    if 'suggestions' in review_result and include_suggestions:
        st.markdown("### Suggestions for Improvement")
        for i, suggestion in enumerate(review_result['suggestions'], 1):
            st.write(f"{i}. {suggestion}")

def display_roku_results(review_result: dict):
    """Display Roku-specific evaluation results."""
    
    # Letter Grade (prominent display)
    if review_result.get('grade'):
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.metric("Roku Design Grade", review_result['grade'], help="Based on Roku TV design criteria")
    
    # Known Issues
    if review_result.get('known_issues'):
        st.markdown("### ⚠️ Known Issues")
        for issue in review_result['known_issues']:
            st.write(f"• {issue}")
    
    # Priority Issues Table
    if review_result.get('priority_issues'):
        st.markdown("### 🔥 Priority Issues")
        st.caption("Ordered by priority (highest to lowest)")
        
        # Create a more structured table if we can parse the data
        issues_text = "\n".join(review_result['priority_issues'])
        st.write(issues_text)
    
    # Purpose and Value Questions
    if review_result.get('questions'):
        st.markdown("### ❓ Purpose & Value Questions")
        for question in review_result['questions']:
            st.write(f"• {question}")
    
    # Critical User Journey Impact
    if review_result.get('journey_impact'):
        st.markdown("### 🛤️ Critical User Journey Impact")
        impact_text = str(review_result['journey_impact'])
        st.write(impact_text)
    
    # Improvement Suggestions
    if review_result.get('suggestions'):
        st.markdown("### 💡 Scope Expansion Suggestions")
        for suggestion in review_result['suggestions']:
            st.write(f"• {suggestion}")
    
    # Full Evaluation (collapsible)
    if review_result.get('full_evaluation'):
        with st.expander("📄 Full Detailed Evaluation"):
            st.markdown(review_result['full_evaluation'])

def main():
    st.set_page_config(
        page_title="VP of Design - AI Design Review",
        page_icon="🎨",
        layout="wide"
    )
    
    st.title("🎨 VP of Design - AI Design Review Assistant")
    st.markdown("Upload your design files and get AI-powered feedback!")
    
    # AI Source Selection
    st.sidebar.header("🤖 AI Source")
    
    # Check what AI sources are available
    ai_hub_available = is_ai_hub_available()
    openai_available = bool(os.getenv("OPENAI_API_KEY"))
    
    ai_source_options = []
    if ai_hub_available:
        ai_source_options.append("🏢 Roku AI Hub (Enterprise)")
    if openai_available:
        ai_source_options.append("🔑 OpenAI API")
    ai_source_options.append("🆓 Free Cloud AI")
    ai_source_options.append("💻 Local AI (Ollama)")
    
    ai_source = st.sidebar.selectbox(
        "Select AI Source",
        ai_source_options,
        help="Choose your preferred AI source for design analysis"
    )
    
    # Handle AI Hub selection
    if ai_source == "🏢 Roku AI Hub (Enterprise)":
        if ai_hub_available:
            hub_reviewer = get_ai_hub_reviewer()
            status = hub_reviewer.get_status()
            st.sidebar.success("✅ AI Hub Connected")
            st.sidebar.info(f"Models: {status.get('models_count', 0)}")
            st.sidebar.info(f"Assistants: {status.get('assistants_count', 0)}")
            
            # Model selection for AI Hub
            available_models = hub_reviewer.get_available_models()
            if available_models:
                model_options = [f"{m['provider']} - {m['model']}" for m in available_models]
                selected_model = st.sidebar.selectbox(
                    "AI Hub Model", 
                    ["Default"] + model_options,
                    help="Choose specific AI model or use default"
                )
            else:
                selected_model = "Default"
                
            # Assistant selection for AI Hub
            available_assistants = hub_reviewer.get_available_assistants()
            if available_assistants:
                assistant_options = [f"{a['display_name']} (ID: {a['id']})" for a in available_assistants]
                selected_assistant = st.sidebar.selectbox(
                    "AI Hub Assistant",
                    ["Default"] + assistant_options,
                    help="Choose specific assistant or use default"
                )
            else:
                selected_assistant = "Default"
                
        else:
            st.sidebar.error("❌ AI Hub Not Available")
            st.sidebar.info("Check your AI_HUB_TOKEN configuration")
            ai_source = "🆓 Free Cloud AI"  # Fallback
    
    # Handle other AI sources
    elif ai_source == "🔑 OpenAI API":
        if not openai_available:
            st.warning("⚠️ OpenAI API key not configured.")
            with st.expander("🔧 OpenAI Setup"):
                st.markdown("""
                **OpenAI Setup (Recommended for best quality)**
                - Get $5 free credits: https://platform.openai.com/
                - Add your API key to the .env file: `OPENAI_API_KEY=your_key`
                """)
            st.stop()
        else:
            st.sidebar.success("🔑 Using OpenAI API")
    
    elif ai_source == "🆓 Free Cloud AI":
        from agents.cloud_reviewer import cloud_agent
        if cloud_agent.is_available():
            st.sidebar.success("🆓 Using Free Cloud AI")
            st.sidebar.info(f"Provider: {cloud_agent.provider}")
        else:
            st.sidebar.error("No free cloud AI providers configured.")
            with st.sidebar.expander("Setup Free Cloud AI"):
                st.markdown("**Recommended: Groq (Free & Fast)**")
                st.markdown("1. Go to https://console.groq.com/")
                st.markdown("2. Sign up and get your API key")
                st.markdown("3. Add `GROQ_API_KEY=your_key` to your .env file")
                st.markdown("4. Restart the app")
            st.stop()
    
    elif ai_source == "💻 Local AI (Ollama)":
        st.sidebar.info("🏠 Using Local Ollama")
        if not local_agent.is_available():
            st.sidebar.warning("Ollama not detected")
            with st.sidebar.expander("Setup Ollama"):
                st.markdown("**Install Ollama:**")
                st.code("curl -fsSL https://ollama.ai/install.sh | sh")
                st.markdown("**Start and Download Model:**")
                st.code("ollama serve")
                st.code("ollama pull llava")
        else:
            st.sidebar.success("✅ Ollama Available")
    
    # Initialize the appropriate agent
    if ai_source == "🏢 Roku AI Hub (Enterprise)" and ai_hub_available:
        agent = None  # We'll use hub_reviewer directly
    elif ai_source == "🔑 OpenAI API":
        agent = DesignReviewAgent()
    else:
        agent = None  # Will be handled by specific agent implementations
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("Review Settings")
        
        evaluation_mode = st.selectbox(
            "Evaluation Mode",
            ["Standard Design Review", "Roku TV Design Review"],
            help="Choose between general design review or Roku-specific TV interface evaluation"
        )
        
        if evaluation_mode == "Standard Design Review":
            review_type = st.selectbox(
                "Review Type",
                ["General Design", "UI/UX", "Accessibility", "Brand Consistency"]
            )
            
            detail_level = st.slider(
                "Detail Level",
                min_value=1,
                max_value=5,
                value=3,
                help="1 = Brief overview, 5 = Detailed analysis"
            )
            
            include_suggestions = st.checkbox(
                "Include Improvement Suggestions",
                value=True
            )
            
            # Standard review variables
            roku_focus_areas = None
            roku_context = ""
            include_grading = False
            
        else:  # Roku TV Design Review
            st.markdown("**Roku TV Design Evaluation**")
            st.caption("Using your VP's comprehensive evaluation criteria")
            
            with st.expander("ℹ️ About Roku TV Design Review"):
                st.markdown("""
                This evaluation mode uses the **exact criteria from your VP** for Roku TV interface design review:
                
                **Key Principles Evaluated:**
                - 🎯 **Easy**: Minimal effort to achieve user goals, clear primary purpose
                - ⚡ **Just Works**: Snappy, reliable, error-free experience  
                - 👀 **Looks Simple**: Clear visual communication, minimal clutter
                - 🤝 **Trustworthy**: Meets expectations, straightforward communication
                - 😊 **Delightful**: Unexpected smiles and helpful features
                - 🎯 **Outcome-Focused**: Meets user needs while supporting business goals
                
                **What You Get:**
                - Prioritized issues table with actionable recommendations
                - Critical user journey impact analysis
                - Letter grade (A-F) based on Roku standards
                - TV remote control navigation compliance check
                - Accessibility and localization considerations
                
                **Solves the VP's Problem:** This system can actually *see* the images embedded in Confluence pages and Figma files, unlike ai.roku.com!
                """)
            
            roku_context = st.text_area(
                "Design Context",
                placeholder="e.g., UXDR Lite: Browse: Promo offers in BoB",
                help="Describe the specific feature or page being evaluated"
            )
            
            focus_areas_options = [
                "usability", "learnability", "information architecture", 
                "visual design", "accessibility", "localization", 
                "layout", "emotional impact", "navigation", "remote control usage"
            ]
            
            roku_focus_areas = st.multiselect(
                "Focus Areas (Optional)",
                focus_areas_options,
                help="Select specific areas to focus on, or leave empty for comprehensive review"
            )
            
            include_grading = st.checkbox(
                "Include Letter Grade",
                value=True,
                help="Assign A-F letter grade based on Roku criteria"
            )
            
            # Set standard review defaults for compatibility
            review_type = "Roku TV Design"
            detail_level = 5
            include_suggestions = True
    
    
    # Main content area - simplified structure
    st.markdown("---")
    
    # Simple input selection
    input_method = st.radio(
        "How would you like to provide your design?",
        ["📁 Upload File", "🎨 Figma URL", "📚 Confluence Page"],
        horizontal=True
    )
    
    st.markdown("---")
    
    # Single content area based on selection
    if input_method == "📁 Upload File":
        # Pass AI Hub settings if using AI Hub
        ai_hub_settings = {}
        if ai_source == "🏢 Roku AI Hub (Enterprise)" and ai_hub_available:
            ai_hub_settings = {
                "selected_model": selected_model if 'selected_model' in locals() else "Default",
                "selected_assistant": selected_assistant if 'selected_assistant' in locals() else "Default"
            }
        show_file_upload_interface(ai_source, agent, evaluation_mode, review_type, detail_level, include_suggestions, roku_context, roku_focus_areas, include_grading, ai_hub_settings)
    
    elif input_method == "🎨 Figma URL":
        ai_hub_settings = {}
        if ai_source == "🏢 Roku AI Hub (Enterprise)" and ai_hub_available:
            ai_hub_settings = {
                "selected_model": selected_model if 'selected_model' in locals() else "Default",
                "selected_assistant": selected_assistant if 'selected_assistant' in locals() else "Default"
            }
        show_figma_interface(ai_source, agent, evaluation_mode, review_type, detail_level, include_suggestions, roku_context, roku_focus_areas, include_grading, ai_hub_settings)
    
    elif input_method == "📚 Confluence Page":
        ai_hub_settings = {}
        if ai_source == "🏢 Roku AI Hub (Enterprise)" and ai_hub_available:
            ai_hub_settings = {
                "selected_model": selected_model if 'selected_model' in locals() else "Default",
                "selected_assistant": selected_assistant if 'selected_assistant' in locals() else "Default"
            }
        show_confluence_interface(ai_source, agent, evaluation_mode, review_type, detail_level, include_suggestions, roku_context, roku_focus_areas, include_grading, ai_hub_settings)

def show_file_upload_interface(ai_source, agent, evaluation_mode, review_type, detail_level, include_suggestions, roku_context, roku_focus_areas, include_grading, ai_hub_settings=None):
    """Simplified file upload interface."""
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Upload Your Design")
        
        uploaded_file = st.file_uploader(
            "Choose a design file",
            type=['png', 'jpg', 'jpeg', 'pdf'],
            help="Upload images or PDF files containing your designs"
        )
        
        if uploaded_file is not None:
            if uploaded_file.type.startswith('image'):
                image = Image.open(uploaded_file)
                st.image(image, caption="Uploaded Design", use_column_width=True)
            else:
                st.success(f"PDF uploaded: {uploaded_file.name}")
    
    with col2:
        st.subheader("Analysis Results")
        
        if uploaded_file is not None:
            if st.button("🔍 Analyze Design", type="primary", key="file_analyze"):
                with st.spinner("Analyzing design..."):
                    try:
                        if ai_source == "🏢 Roku AI Hub (Enterprise)":
                            # Use AI Hub
                            hub_reviewer = get_ai_hub_reviewer()
                            
                            # Parse model selection
                            model_provider = None
                            model_name = None
                            selected_model = ai_hub_settings.get("selected_model", "Default") if ai_hub_settings else "Default"
                            if selected_model != "Default" and " - " in selected_model:
                                model_provider, model_name = selected_model.split(" - ", 1)
                            
                            # Parse assistant selection
                            assistant_id = None
                            selected_assistant = ai_hub_settings.get("selected_assistant", "Default") if ai_hub_settings else "Default"
                            if selected_assistant != "Default" and "(ID: " in selected_assistant:
                                assistant_id = int(selected_assistant.split("(ID: ")[1].split(")")[0])
                            
                            if evaluation_mode == "Roku TV Design Review":
                                review_result = hub_reviewer.roku_design_review(
                                    uploaded_file,
                                    evaluation_criteria=roku_focus_areas if roku_focus_areas else [],
                                    model_provider=model_provider,
                                    model_name=model_name,
                                    assistant_id=assistant_id
                                )
                            else:
                                review_result = hub_reviewer.review_design(
                                    uploaded_file,
                                    review_type=review_type,
                                    detail_level=detail_level,
                                    include_suggestions=include_suggestions,
                                    model_provider=model_provider,
                                    model_name=model_name,
                                    assistant_id=assistant_id
                                )
                        
                        elif ai_source == "🆓 Free Cloud AI":
                            # Use cloud AI
                            from agents.cloud_reviewer import cloud_agent
                            if cloud_agent.is_available():
                                if uploaded_file.type.startswith('image'):
                                    # For images with cloud AI, we need a text description
                                    review_result = {
                                        'error': 'Image analysis requires OpenAI or AI Hub. Please provide a text description of the image instead.',
                                        'suggestion': 'Switch to "📝 Text Description" and describe your image in detail.'
                                    }
                                else:
                                    # For PDFs with cloud AI, extract text content
                                    review_result = {
                                        'error': 'PDF analysis requires OpenAI or AI Hub. Please extract the text content and use "📝 Text Description" instead.',
                                        'suggestion': 'Copy the text from your PDF and use the text description option.'
                                    }
                            else:
                                review_result = {
                                    'error': 'No cloud AI provider configured.',
                                    'setup_instructions': cloud_agent.get_setup_instructions()
                                }
                        
                        elif ai_source == "💻 Local AI (Ollama)":
                            # Use local Ollama
                            review_result = local_agent.review_design_with_local_ai(
                                uploaded_file,
                                review_type=review_type,
                                detail_level=detail_level,
                                include_suggestions=include_suggestions
                            )
                        
                        else:
                            # Use OpenAI agent
                            if evaluation_mode == "Roku TV Design Review":
                                # Use Roku-specific evaluation
                                review_result = agent.review_roku_design(
                                    uploaded_file,
                                    input_type="file",
                                    design_context=roku_context,
                                    focus_areas=roku_focus_areas if roku_focus_areas else None,
                                    include_grading=include_grading
                                )
                            else:
                                # Use standard evaluation
                                review_result = agent.review_design(
                                    uploaded_file,
                                    review_type=review_type,
                                    detail_level=detail_level,
                                    include_suggestions=include_suggestions
                                )
                        
                        # Display results
                        display_review_results(review_result, include_suggestions, evaluation_mode)
                        
                    except Exception as e:
                        st.error(f"Error analyzing design: {str(e)}")
        else:
            st.info("Upload a design file to get started!")


def show_figma_interface(ai_source, agent, evaluation_mode, review_type, detail_level, include_suggestions, roku_context, roku_focus_areas, include_grading, ai_hub_settings=None):
    """Simplified Figma interface."""
    if not settings.is_figma_configured():
        st.warning("⚠️ Figma integration requires configuration. Add your FIGMA_ACCESS_TOKEN to the .env file.")
        return
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Figma File")
        
        figma_input = st.text_input(
            "Figma URL or File Key",
            placeholder="https://www.figma.com/file/abc123/Design-File",
            help="Paste the full Figma URL or just the file key"
        )
        
        node_ids_input = st.text_input(
            "Specific Nodes (Optional)",
            placeholder="123:45, 456:78",
            help="Comma-separated node IDs to analyze specific components"
        )
        
        if figma_input:
            # Extract file key
            if "figma.com" in figma_input:
                file_key = document_loader_manager.extract_figma_file_key(figma_input)
            else:
                file_key = figma_input
            
            st.info(f"File Key: {file_key}")
    
    with col2:
        st.subheader("Analysis Results")
        
        if figma_input:
            if st.button("🔍 Analyze Figma Design", type="primary", key="figma_analyze"):
                with st.spinner("Loading and analyzing Figma design..."):
                    try:
                        node_ids = [nid.strip() for nid in node_ids_input.split(',') if nid.strip()] if node_ids_input else None
                        
                        if ai_source in ["🆓 Free Cloud AI", "💻 Local AI (Ollama)"]:
                            st.warning("Figma integration is only available with OpenAI or AI Hub. Please use file upload or export images from Figma.")
                            return
                        
                        if evaluation_mode == "Roku TV Design Review":
                            review_result = agent.review_roku_design(
                                file_key,
                                input_type="figma",
                                design_context=roku_context,
                                focus_areas=roku_focus_areas if roku_focus_areas else None,
                                include_grading=include_grading,
                                node_ids=node_ids
                            )
                        else:
                            review_result = agent.review_figma_file(
                                file_key,
                                review_type=review_type,
                                detail_level=detail_level,
                                include_suggestions=include_suggestions,
                                node_ids=node_ids
                            )
                        
                        display_review_results(review_result, include_suggestions, evaluation_mode)
                        
                    except Exception as e:
                        st.error(f"Error analyzing Figma file: {str(e)}")
        else:
            st.info("Enter a Figma URL or file key to get started!")


def show_confluence_interface(ai_source, agent, evaluation_mode, review_type, detail_level, include_suggestions, roku_context, roku_focus_areas, include_grading, ai_hub_settings=None):
    """Simplified Confluence interface."""
    if not settings.is_confluence_configured():
        st.warning("⚠️ Confluence integration requires configuration.")
        with st.expander("Setup Instructions"):
            st.code("""CONFLUENCE_URL=https://your-domain.atlassian.net
CONFLUENCE_USERNAME=your_email@domain.com
CONFLUENCE_API_KEY=your_api_key_here""")
        return
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Confluence Page")
        
        space_key = st.text_input(
            "Space Key",
            placeholder="e.g., DESIGN, PROJ",
            help="The key of the Confluence space to analyze"
        )
        
        page_ids_input = st.text_area(
            "Page IDs (Optional)",
            placeholder="Enter specific page IDs, one per line",
            help="Leave empty to analyze all pages in the space"
        )
        
        page_ids = [pid.strip() for pid in page_ids_input.split('\n') if pid.strip()] if page_ids_input else None
        
        if space_key and not page_ids:
            st.info(f"Will analyze all pages in space: {space_key}")
        elif space_key and page_ids:
            st.info(f"Will analyze {len(page_ids)} specific pages in space: {space_key}")
    
    with col2:
        st.subheader("Analysis Results")
        
        if space_key:
            if st.button("🔍 Analyze Confluence Pages", type="primary", key="confluence_analyze"):
                with st.spinner("Loading and analyzing Confluence pages..."):
                    try:
                        if ai_source in ["🆓 Free Cloud AI", "💻 Local AI (Ollama)"]:
                            st.warning("Confluence integration is only available with OpenAI or AI Hub. Please copy content manually.")
                            return
                        
                        if evaluation_mode == "Roku TV Design Review":
                            review_result = agent.review_roku_design(
                                space_key,
                                input_type="confluence",
                                design_context=roku_context,
                                focus_areas=roku_focus_areas if roku_focus_areas else None,
                                include_grading=include_grading,
                                page_ids=page_ids
                            )
                        else:
                            review_result = agent.review_confluence_pages(
                                space_key,
                                page_ids=page_ids,
                                review_type=review_type,
                                detail_level=detail_level,
                                include_suggestions=include_suggestions
                            )
                        
                        display_review_results(review_result, include_suggestions, evaluation_mode)
                        
                    except Exception as e:
                        st.error(f"Error analyzing Confluence pages: {str(e)}")
        else:
            st.info("Enter a Confluence space key to get started!")
    
    # VP Preferences & Learning Section
    st.markdown("---")
    st.header("⚙️ VP Preferences & Learning")
    st.caption("Customize evaluation criteria and track learning over time")
    
    # Sub-tabs for different preference areas
    pref_tab1, pref_tab2, pref_tab3, pref_tab4 = st.tabs([
        "📋 Custom Rules", 
        "👤 VP Profile", 
        "📊 Learning Insights", 
        "💬 Feedback"
    ])
    
    with pref_tab1:
            st.subheader("Custom Design Rules")
            st.write("Add your own design requirements that will be included in all evaluations.")
            
            # Add new custom rule form
            with st.expander("➕ Add New Custom Rule"):
                with st.form("add_custom_rule"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        rule_title = st.text_input("Rule Title", placeholder="e.g., 'Focus indicators must be 4px thick'")
                        rule_description = st.text_area("Description", placeholder="Detailed description of the requirement...")
                        rule_rationale = st.text_area("Rationale", placeholder="Why is this rule important? What problem does it solve?")
                    
                    with col2:
                        rule_priority = st.slider("Priority", 1, 5, 3, help="5 = Critical, 1 = Nice to have")
                        rule_category = st.selectbox("Category", [
                            "navigation", "visual design", "accessibility", 
                            "performance", "usability", "content", "branding"
                        ])
                    
                    rule_examples = st.text_area("Examples (one per line)", placeholder="Good example 1\nGood example 2")
                    rule_exceptions = st.text_area("Exceptions (one per line)", placeholder="Exception case 1\nException case 2")
                    
                    if st.form_submit_button("Add Custom Rule", type="primary"):
                        if rule_title and rule_description:
                            examples = [ex.strip() for ex in rule_examples.split('\n') if ex.strip()]
                            exceptions = [ex.strip() for ex in rule_exceptions.split('\n') if ex.strip()]
                            
                            rule_id = agent.add_custom_requirement(
                                title=rule_title,
                                description=rule_description,
                                rationale=rule_rationale,
                                priority=rule_priority,
                                category=rule_category,
                                examples=examples,
                                exceptions=exceptions
                            )
                            st.success(f"Custom rule added! ID: {rule_id}")
                            st.rerun()
                        else:
                            st.error("Please provide at least a title and description.")
            
            # Display existing custom rules
            st.subheader("Existing Custom Rules")
            custom_rules = vp_preference_manager.custom_rules
            
            if custom_rules:
                for rule in custom_rules:
                    with st.expander(f"🔧 {rule.title} (Priority {rule.priority})"):
                        st.write(f"**Category:** {rule.category}")
                        st.write(f"**Description:** {rule.description}")
                        if rule.rationale:
                            st.write(f"**Rationale:** {rule.rationale}")
                        if rule.examples:
                            st.write(f"**Examples:** {', '.join(rule.examples)}")
                        if rule.exceptions:
                            st.write(f"**Exceptions:** {', '.join(rule.exceptions)}")
                        st.caption(f"Created: {rule.created_date} | Modified: {rule.last_modified}")
            else:
                st.info("No custom rules yet. Add your first rule above!")
        
    with pref_tab2:
            st.subheader("VP Profile Settings")
            st.write("Configure your evaluation style and preferences.")
            
            # Get current profile
            current_profile = vp_preference_manager.vp_profile
            
            with st.form("vp_profile"):
                col1, col2 = st.columns(2)
                
                with col1:
                    vp_name = st.text_input("Name", value=current_profile.name if current_profile else "")
                    vp_role = st.text_input("Role", value=current_profile.role if current_profile else "")
                    
                    communication_style = st.selectbox(
                        "Communication Style",
                        ["detailed", "concise", "visual", "bullet_points"],
                        index=["detailed", "concise", "visual", "bullet_points"].index(
                            current_profile.communication_style if current_profile else "detailed"
                        )
                    )
                
                with col2:
                    focus_areas = st.multiselect(
                        "Primary Focus Areas",
                        ["usability", "accessibility", "visual design", "navigation", "performance", "content", "branding"],
                        default=current_profile.focus_areas if current_profile else []
                    )
                    
                    strict_areas = st.multiselect(
                        "Areas where you're particularly strict",
                        ["accessibility", "navigation", "visual hierarchy", "performance", "content clarity"],
                        default=current_profile.strict_areas if current_profile else []
                    )
                
                if st.form_submit_button("Update Profile", type="primary"):
                    vp_preference_manager.update_vp_profile(
                        name=vp_name,
                        role=vp_role,
                        focus_areas=focus_areas,
                        strict_areas=strict_areas,
                        communication_style=communication_style
                    )
                    st.success("VP Profile updated!")
                    st.rerun()
        
    with pref_tab3:
            st.subheader("Learning Insights")
            st.write("See what the system has learned from your feedback over time.")
            
            # Get learning insights
            if agent is not None:
                insights = agent.get_learning_summary()
            else:
                # Local AI doesn't have learning insights yet
                insights = {"total_evaluations": 0}
            
            if insights.get("total_evaluations", 0) > 0:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Total Evaluations", insights["total_evaluations"])
                
                with col2:
                    st.metric("Average Rating", f"{insights.get('average_vp_rating', 0):.1f}/5")
                
                with col3:
                    if insights.get("grade_distribution"):
                        most_common_grade = max(insights["grade_distribution"].items(), key=lambda x: x[1])[0]
                        st.metric("Most Common Grade", most_common_grade)
                
                # Most common issues
                if insights.get("most_common_issues"):
                    st.subheader("Most Frequently Found Issues")
                    for issue_type, count in insights["most_common_issues"]:
                        st.write(f"• **{issue_type}**: {count} times")
                
                # Recent feedback
                if insights.get("recent_feedback"):
                    st.subheader("Recent Feedback Themes")
                    for feedback in insights["recent_feedback"]:
                        st.write(f"• {feedback}")
                
                # Grade distribution chart
                if insights.get("grade_distribution"):
                    st.subheader("Grade Distribution")
                    grades = list(insights["grade_distribution"].keys())
                    counts = list(insights["grade_distribution"].values())
                    
                    import plotly.express as px
                    import pandas as pd
                    
                    df = pd.DataFrame({"Grade": grades, "Count": counts})
                    fig = px.bar(df, x="Grade", y="Count", title="Evaluation Grade Distribution")
                    st.plotly_chart(fig, use_container_width=True)
            
            else:
                st.info("No evaluation history yet. Start evaluating designs to see learning insights!")
        
    with pref_tab4:
            st.subheader("Provide Feedback on Evaluations")
            st.write("Rate the quality of recent evaluations to help the system learn your preferences.")
            
            # Show recent evaluations for feedback
            recent_evaluations = vp_preference_manager.evaluation_memory[-5:]  # Last 5
            
            if recent_evaluations:
                for eval_mem in reversed(recent_evaluations):  # Most recent first
                    with st.expander(f"📋 {eval_mem.design_id} - {eval_mem.context[:50]}..."):
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.write(f"**Date:** {eval_mem.evaluation_date}")
                            st.write(f"**Type:** {eval_mem.input_type}")
                            st.write(f"**Context:** {eval_mem.context}")
                            st.write(f"**Grade Given:** {eval_mem.grade_assigned}")
                            
                            if eval_mem.vp_feedback:
                                st.write(f"**Your Previous Feedback:** {eval_mem.vp_feedback}")
                                st.write(f"**Your Rating:** {eval_mem.vp_rating}/5")
                            else:
                                st.info("No feedback provided yet")
                        
                        with col2:
                            if not eval_mem.vp_feedback:
                                with st.form(f"feedback_{eval_mem.design_id}"):
                                    vp_rating = st.slider("Rate this evaluation", 1, 5, 3, 
                                                        help="1=Poor, 5=Excellent", 
                                                        key=f"rating_{eval_mem.design_id}")
                                    vp_feedback = st.text_area("Feedback", 
                                                              placeholder="What was good/bad about this evaluation?",
                                                              key=f"feedback_text_{eval_mem.design_id}")
                                    
                                    if st.form_submit_button("Submit Feedback"):
                                        if agent.provide_evaluation_feedback(eval_mem.design_id, vp_feedback, vp_rating):
                                            st.success("Feedback recorded!")
                                            st.rerun()
                                        else:
                                            st.error("Failed to record feedback")
            else:
                st.info("No evaluations to provide feedback on yet.")
    
    # Chat interface
    st.header("💬 Chat with Design Agent")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask questions about your design..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get agent response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = agent.chat(prompt)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()
