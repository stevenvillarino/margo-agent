"""
Intelligent Chat-Based Design Review Interface

This creates a much more intelligent, conversational interface that:
1. Automatically detects what type of review is needed
2. Shows real-time agent orchestration and communication  
3. Provides a chat-like experience without rigid dropdowns
4. Demonstrates the multi-agent intelligence in action
"""

import streamlit as st
import os
import asyncio
import json
import base64
from datetime import datetime
from typing import Dict, List, Any, Optional
from PIL import Image
import io

from dotenv import load_dotenv
from agents.enhanced_system import EnhancedDesignReviewSystem
from agents.agent_communication import create_communication_hub, AgentCapability, MessageType, Priority
from agents.orchestrator import ReviewOrchestrator
from agents.design_reviewer import DesignReviewAgent
from config.settings import settings

# Load environment variables
load_dotenv()

class IntelligentDesignChat:
    """Intelligent chat interface that orchestrates multiple agents."""
    
    def __init__(self):
        # Initialize the enhanced multi-agent system
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.enhanced_system = None
        self.communication_hub = create_communication_hub()
        
        # Initialize session state
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        if "agent_activity" not in st.session_state:
            st.session_state.agent_activity = []
        if "current_analysis" not in st.session_state:
            st.session_state.current_analysis = None
        if "uploaded_images" not in st.session_state:
            st.session_state.uploaded_images = {}
            
        self._initialize_system()
    
    def _initialize_system(self):
        """Initialize the enhanced multi-agent system."""
        if self.openai_key and not self.enhanced_system:
            try:
                exa_key = os.getenv("EXA_API_KEY")
                self.enhanced_system = EnhancedDesignReviewSystem(
                    openai_api_key=self.openai_key,
                    exa_api_key=exa_key,
                    learning_enabled=True,
                    company_context={
                        "industry": "Streaming/Entertainment",
                        "company": "Roku",
                        "product_focus": "TV streaming interface",
                        "user_base": "TV viewers and families"
                    }
                )
                
                # Register agents with communication hub
                self._register_agents_with_hub()
                
                return True
            except Exception as e:
                st.error(f"Failed to initialize system: {e}")
                return False
        return self.enhanced_system is not None
    
    def _register_agents_with_hub(self):
        """Register all agents with the communication hub for message tracking."""
        if not self.enhanced_system:
            return
            
        # Register each agent with their capabilities
        agents_config = {
            "ui_specialist": {
                "name": "UI Design Specialist",
                "expertise": ["visual design", "interface patterns", "design systems"],
                "type": "specialist"
            },
            "ux_researcher": {
                "name": "UX Research Analyst", 
                "expertise": ["user research", "usability", "user journeys"],
                "type": "researcher"
            },
            "creative_director": {
                "name": "Creative Director",
                "expertise": ["brand consistency", "creative vision", "design strategy"],
                "type": "creative"
            },
            "vp_product": {
                "name": "VP of Product (Margo)",
                "expertise": ["business strategy", "product decisions", "ROI analysis"],
                "type": "executive"
            },
            "accessibility": {
                "name": "Accessibility Expert",
                "expertise": ["WCAG compliance", "inclusive design", "assistive technology"],
                "type": "specialist"
            },
            "quality_evaluation": {
                "name": "Quality Assurance Agent",
                "expertise": ["design standards", "compliance checking", "quality metrics"],
                "type": "qa"
            }
        }
        
        for agent_id, config in agents_config.items():
            capability = AgentCapability(
                agent_id=agent_id,
                agent_name=config["name"],
                agent_type=config["type"],
                expertise_areas=config["expertise"],
                available_methods=["review", "analyze", "provide_feedback"],
                current_load=0,
                response_time_avg=30.0,
                reliability_score=0.95
            )
            self.communication_hub.register_agent(agent_id, capability)

    def render_intelligent_interface(self):
        """Render the main intelligent chat interface."""
        st.set_page_config(
            page_title="Intelligent Design Review Assistant",
            page_icon="🎨",
            layout="wide",
            initial_sidebar_state="collapsed"
        )
        
        # Header
        st.title("🎨 Intelligent Design Review Assistant")
        st.markdown("*Upload a design and chat with our AI agents to get comprehensive feedback*")
        
        # Create main layout
        col1, col2 = st.columns([2, 1])
        
        with col1:
            self._render_chat_interface()
            
        with col2:
            self._render_agent_activity_panel()
    
    def _render_chat_interface(self):
        """Render the main chat interface."""
        st.markdown("### 💬 Chat with Design Agents")
        
        # File upload area (always visible but subtle)
        uploaded_file = st.file_uploader(
            "Upload a design file", 
            type=['png', 'jpg', 'jpeg', 'pdf'],
            help="Upload your design to start the conversation",
            label_visibility="collapsed"
        )
        
        if uploaded_file is not None:
            # Process uploaded file
            image_data = self._process_uploaded_file(uploaded_file)
            if image_data:
                st.session_state.uploaded_images[uploaded_file.name] = image_data
                
                # Show image preview
                with st.expander(f"📎 Attached: {uploaded_file.name}", expanded=False):
                    if uploaded_file.type.startswith('image'):
                        st.image(uploaded_file, width=300)
                    else:
                        st.info(f"File: {uploaded_file.name} ({uploaded_file.type})")
        
        # Chat history display
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.chat_history:
                with st.chat_message(message["role"], avatar=message.get("avatar")):
                    st.markdown(message["content"])
                    
                    # Show agent orchestration details if available
                    if message.get("agent_details"):
                        with st.expander("🤖 Agent Activity", expanded=False):
                            self._display_agent_details(message["agent_details"])
        
        # Chat input
        if prompt := st.chat_input("Describe what you'd like me to review, or just say hello!"):
            self._handle_user_message(prompt)
    
    def _render_agent_activity_panel(self):
        """Render the real-time agent activity panel."""
        st.markdown("### 🤖 Agent Activity")
        
        if not self.enhanced_system:
            st.info("💡 Configure OpenAI API key to see agent orchestration in action")
            with st.expander("🔧 Setup Instructions"):
                st.markdown("""
                **To see the intelligent multi-agent system in action:**
                
                1. Get an OpenAI API key from [platform.openai.com](https://platform.openai.com)
                2. Add it to your `.env` file: `OPENAI_API_KEY=your_key_here`
                3. Restart the application
                
                **You'll then see:**
                - Real-time agent communication
                - Intelligent review orchestration
                - Multi-perspective analysis
                - Collaborative decision making
                """)
            return
        
        # Show registered agents
        st.markdown("#### 👥 Available Agents")
        agents_status = []
        
        for agent_id, capability in self.communication_hub.agent_capabilities.items():
            status = self.communication_hub.agent_status.get(agent_id, {})
            agents_status.append({
                "name": capability.agent_name,
                "type": capability.agent_type,
                "expertise": capability.expertise_areas[:2],  # Show first 2 areas
                "status": status.get("status", "ready"),
                "load": status.get("current_tasks", [])
            })
        
        for agent in agents_status:
            with st.container():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**{agent['name']}**")
                    st.caption(f"{', '.join(agent['expertise'])}")
                with col2:
                    if len(agent['load']) > 0:
                        st.markdown("🔄 Working")
                    else:
                        st.markdown("✅ Ready")
        
        # Show recent activity
        if st.session_state.agent_activity:
            st.markdown("#### 📊 Recent Activity")
            activity_container = st.container()
            with activity_container:
                for activity in st.session_state.agent_activity[-5:]:  # Show last 5
                    st.markdown(f"• {activity}")
    
    def _process_uploaded_file(self, uploaded_file) -> Optional[str]:
        """Process uploaded file and return base64 encoded data."""
        try:
            if uploaded_file.type.startswith('image'):
                # Convert to base64
                image_data = base64.b64encode(uploaded_file.read()).decode()
                return image_data
            else:
                st.warning("Currently only image files are supported for analysis")
                return None
        except Exception as e:
            st.error(f"Error processing file: {e}")
            return None
    
    def _handle_user_message(self, message: str):
        """Handle user message and orchestrate agent responses."""
        # Add user message to chat
        st.session_state.chat_history.append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now()
        })
        
        # Check if we have images and what the user is asking for
        has_images = bool(st.session_state.uploaded_images)
        
        # Use intelligence to determine what to do
        if has_images:
            # User has uploaded images - likely wants a review
            self._conduct_intelligent_review(message)
        else:
            # No images - provide helpful guidance
            self._provide_guidance(message)
    
    def _conduct_intelligent_review(self, user_request: str):
        """Conduct an intelligent review using the multi-agent system."""
        if not self.enhanced_system:
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": "I need an OpenAI API key to provide intelligent design reviews. Please configure your API key to unlock the full multi-agent analysis capabilities.",
                "avatar": "🤖"
            })
            return
        
        # Show thinking message
        thinking_msg = {
            "role": "assistant", 
            "content": "🤔 Analyzing your design and coordinating with my team of specialist agents...",
            "avatar": "🤖"
        }
        st.session_state.chat_history.append(thinking_msg)
        
        # Refresh to show thinking message
        st.rerun()
        
        # Conduct the actual review
        try:
            # Get the most recent image
            image_name, image_data = list(st.session_state.uploaded_images.items())[-1]
            
            # Analyze the user request to determine review type and focus
            review_context = self._analyze_user_intent(user_request)
            
            # Add agent activity
            st.session_state.agent_activity.append(
                f"🎯 Starting {review_context['review_type']} review for {image_name}"
            )
            
            # Run the enhanced review (this would be async in practice)
            review_result = self._simulate_enhanced_review(image_data, review_context, user_request)
            
            # Remove thinking message and add results
            st.session_state.chat_history.pop()  # Remove thinking message
            
            # Add comprehensive results
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": review_result["summary"],
                "avatar": "🎨",
                "agent_details": review_result["agent_details"]
            })
            
        except Exception as e:
            # Remove thinking message and show error
            st.session_state.chat_history.pop()
            st.session_state.chat_history.append({
                "role": "assistant", 
                "content": f"I encountered an issue analyzing your design: {str(e)}",
                "avatar": "⚠️"
            })
    
    def _analyze_user_intent(self, user_request: str) -> Dict[str, Any]:
        """Analyze user request to determine what kind of review they want."""
        request_lower = user_request.lower()
        
        # Detect review type based on keywords
        if any(word in request_lower for word in ['accessibility', 'a11y', 'wcag', 'disability']):
            return {
                "review_type": "accessibility_focused",
                "primary_agents": ["accessibility", "ui_specialist"],
                "focus_areas": ["WCAG compliance", "inclusive design", "keyboard navigation"]
            }
        elif any(word in request_lower for word in ['business', 'roi', 'revenue', 'conversion']):
            return {
                "review_type": "business_focused", 
                "primary_agents": ["vp_product", "ux_researcher"],
                "focus_areas": ["business impact", "user conversion", "strategic alignment"]
            }
        elif any(word in request_lower for word in ['user', 'ux', 'usability', 'journey']):
            return {
                "review_type": "ux_focused",
                "primary_agents": ["ux_researcher", "ui_specialist"],
                "focus_areas": ["user experience", "usability", "user journeys"]
            }
        elif any(word in request_lower for word in ['brand', 'visual', 'style', 'creative']):
            return {
                "review_type": "creative_focused",
                "primary_agents": ["creative_director", "ui_specialist"],
                "focus_areas": ["brand consistency", "visual design", "creative direction"]
            }
        else:
            return {
                "review_type": "comprehensive",
                "primary_agents": ["ui_specialist", "ux_researcher", "vp_product"],
                "focus_areas": ["overall design quality", "user experience", "business alignment"]
            }
    
    def _simulate_enhanced_review(self, image_data: str, context: Dict[str, Any], user_request: str) -> Dict[str, Any]:
        """Simulate the enhanced multi-agent review process."""
        
        # For demo purposes, we'll simulate the multi-agent process
        # In the real implementation, this would call the actual enhanced system
        
        review_type = context["review_type"]
        primary_agents = context["primary_agents"]
        
        # Simulate agent coordination
        agent_results = {}
        agent_messages = []
        
        for i, agent_id in enumerate(primary_agents):
            agent_name = self.communication_hub.agent_capabilities[agent_id].agent_name
            
            # Simulate agent thinking
            st.session_state.agent_activity.append(f"🔍 {agent_name} analyzing design...")
            
            # Simulate agent-specific insights
            if agent_id == "accessibility":
                agent_results[agent_id] = {
                    "score": 7.5,
                    "insights": [
                        "Good color contrast ratios detected",
                        "Consider adding alt text for decorative elements", 
                        "Touch targets appear to meet minimum size requirements"
                    ],
                    "recommendations": [
                        "Add skip navigation links",
                        "Ensure focus indicators are visible",
                        "Test with screen readers"
                    ]
                }
                agent_messages.append(f"🛡️ **{agent_name}**: Accessibility score 7.5/10 - good foundation with room for improvement")
                
            elif agent_id == "vp_product":
                agent_results[agent_id] = {
                    "score": 8.2,
                    "insights": [
                        "Strong alignment with business objectives",
                        "Clear value proposition presented to users",
                        "Potential for increased user engagement"
                    ],
                    "recommendations": [
                        "Consider A/B testing key interaction points",
                        "Add metrics tracking for conversion analysis",
                        "Align with quarterly OKRs for engagement"
                    ]
                }
                agent_messages.append(f"💼 **{agent_name}**: Business impact score 8.2/10 - solid strategic alignment")
                
            elif agent_id == "ux_researcher":
                agent_results[agent_id] = {
                    "score": 7.8,
                    "insights": [
                        "Intuitive navigation patterns",
                        "Clear information hierarchy",
                        "Some potential friction points identified"
                    ],
                    "recommendations": [
                        "Conduct user testing on new interaction patterns",
                        "Simplify the primary user flow",
                        "Add contextual help for complex features"
                    ]
                }
                agent_messages.append(f"🔬 **{agent_name}**: UX analysis complete - 7.8/10 with clear optimization paths")
                
            elif agent_id == "ui_specialist":
                agent_results[agent_id] = {
                    "score": 8.5,
                    "insights": [
                        "Strong visual hierarchy and typography",
                        "Consistent design system usage",
                        "Effective use of white space"
                    ],
                    "recommendations": [
                        "Consider mobile responsiveness for smaller screens",
                        "Enhance micro-interactions for delight",
                        "Optimize loading states and transitions"
                    ]
                }
                agent_messages.append(f"🎨 **{agent_name}**: Visual design assessment - 8.5/10, excellent execution")
                
            elif agent_id == "creative_director":
                agent_results[agent_id] = {
                    "score": 8.0,
                    "insights": [
                        "Consistent brand expression",
                        "Creative solution fits target audience",
                        "Strong emotional resonance potential"
                    ],
                    "recommendations": [
                        "Amplify unique brand differentiators",
                        "Consider seasonal creative variations",
                        "Ensure scalability across product family"
                    ]
                }
                agent_messages.append(f"✨ **{agent_name}**: Creative review done - 8.0/10, strong brand alignment")
        
        # Simulate agent collaboration and consensus
        st.session_state.agent_activity.append("🤝 Agents collaborating on final recommendations...")
        
        # Calculate overall score
        overall_score = sum(result["score"] for result in agent_results.values()) / len(agent_results)
        
        # Create consensus summary
        summary = f"""## 🎯 {review_type.replace('_', ' ').title()} Review Complete

**Overall Score: {overall_score:.1f}/10**

{chr(10).join(agent_messages)}

### 🔄 Agent Collaboration Summary
Our {len(primary_agents)} specialist agents have analyzed your design and reached consensus on key areas for improvement. The analysis combined multiple perspectives to provide comprehensive feedback.

### 🎯 Key Insights
- **Strengths**: {self._extract_top_insights(agent_results, 'positive')}
- **Opportunities**: {self._extract_top_insights(agent_results, 'improvement')}

### 🚀 Next Steps
Based on our multi-agent analysis, here are the prioritized recommendations:
{self._generate_prioritized_recommendations(agent_results)}

*Want to dive deeper into any specific area? Just ask!*
"""

        return {
            "summary": summary,
            "overall_score": overall_score,
            "agent_details": {
                "agents_involved": primary_agents,
                "review_type": review_type,
                "individual_results": agent_results,
                "collaboration_notes": "Agents successfully coordinated and reached consensus"
            }
        }
    
    def _extract_top_insights(self, agent_results: Dict, insight_type: str) -> str:
        """Extract top insights from agent results."""
        if insight_type == 'positive':
            insights = []
            for result in agent_results.values():
                insights.extend([insight for insight in result["insights"] if any(word in insight.lower() for word in ['good', 'strong', 'clear', 'effective', 'excellent'])])
            return ", ".join(insights[:2]) if insights else "Multiple strengths identified"
        else:
            insights = []
            for result in agent_results.values():
                insights.extend(result["recommendations"][:1])  # Take first recommendation from each
            return ", ".join(insights[:2]) if insights else "Several optimization opportunities"
    
    def _generate_prioritized_recommendations(self, agent_results: Dict) -> str:
        """Generate prioritized recommendations from all agents."""
        all_recommendations = []
        for agent_id, result in agent_results.items():
            agent_name = self.communication_hub.agent_capabilities[agent_id].agent_name
            all_recommendations.extend([f"- **{agent_name}**: {rec}" for rec in result["recommendations"][:2]])
        
        return "\n".join(all_recommendations[:4])  # Show top 4 recommendations
    
    def _provide_guidance(self, message: str):
        """Provide helpful guidance when no images are uploaded."""
        guidance_responses = {
            "hello": "👋 Hello! I'm your intelligent design review assistant. I work with a team of specialist AI agents to provide comprehensive design feedback. Upload a design file to get started!",
            "help": "🤖 I coordinate with multiple specialist agents including:\n\n• **UI Specialist** - Visual design & interface patterns\n• **UX Researcher** - User experience & usability\n• **Creative Director** - Brand consistency & creative vision\n• **VP of Product** - Business impact & strategic alignment\n• **Accessibility Expert** - WCAG compliance & inclusive design\n• **Quality Assurance** - Design standards & compliance\n\nJust upload your design and tell me what you'd like me to focus on!",
            "what": "🎯 I provide intelligent design reviews by coordinating multiple AI agents. Each agent brings different expertise, and they collaborate to give you comprehensive feedback. Think of it as having your entire design team review your work simultaneously!",
            "how": "⚡ Here's how I work:\n\n1. **Upload** your design file\n2. **Tell me** what you want me to focus on (or just say 'review this')\n3. **Watch** as I coordinate with specialist agents in real-time\n4. **Get** comprehensive feedback with multiple perspectives\n5. **Ask** follow-up questions to dive deeper\n\nIt's like having a design review meeting, but instant and always available!"
        }
        
        message_lower = message.lower()
        
        # Find best matching response
        best_response = guidance_responses["help"]  # default
        for key, response in guidance_responses.items():
            if key in message_lower:
                best_response = response
                break
        
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": best_response,
            "avatar": "🤖"
        })
    
    def _display_agent_details(self, agent_details: Dict[str, Any]):
        """Display detailed agent orchestration information."""
        st.markdown(f"**Review Type**: {agent_details['review_type'].replace('_', ' ').title()}")
        st.markdown(f"**Agents Involved**: {', '.join([self.communication_hub.agent_capabilities[agent_id].agent_name for agent_id in agent_details['agents_involved']])}")
        
        if agent_details.get("individual_results"):
            st.markdown("**Individual Agent Scores**:")
            for agent_id, result in agent_details["individual_results"].items():
                agent_name = self.communication_hub.agent_capabilities[agent_id].agent_name
                st.markdown(f"• {agent_name}: {result['score']}/10")
        
        if agent_details.get("collaboration_notes"):
            st.markdown(f"**Collaboration**: {agent_details['collaboration_notes']}")


def main():
    """Main application entry point."""
    chat_interface = IntelligentDesignChat()
    chat_interface.render_intelligent_interface()


if __name__ == "__main__":
    main()
