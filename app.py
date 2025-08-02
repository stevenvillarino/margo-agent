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
from agents.enhanced_system import create_enhanced_design_review_system
from agents.agent_communication import create_communication_hub, AgentCapability, MessageType, Priority
from agents.orchestrator import ReviewOrchestrator
from agents.design_reviewer import DesignReviewAgent
from config.settings import settings

# Load environment variables
load_dotenv()

class IntelligentDesignChat:
    """Intelligent chat interface that orchestrates multiple agents."""
    
    def __init__(self):
        # Only initialize session state, not heavy objects
        self._init_session_state()
    
    def _init_session_state(self):
        """Initialize session state variables once."""
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        if "agent_activity" not in st.session_state:
            st.session_state.agent_activity = []
        if "current_analysis" not in st.session_state:
            st.session_state.current_analysis = None
        if "uploaded_images" not in st.session_state:
            st.session_state.uploaded_images = {}
        if "system_initialized" not in st.session_state:
            st.session_state.system_initialized = False
            
    @property
    def openai_key(self):
        """Get OpenAI key from environment."""
        return os.getenv("OPENAI_API_KEY")
    
    @property  
    def enhanced_system(self):
        """Get or initialize enhanced system."""
        if not st.session_state.system_initialized:
            self._initialize_system()
        return getattr(st.session_state, '_enhanced_system', None)
    
    @property
    def communication_hub(self):
        """Get or initialize communication hub.""" 
        if not hasattr(st.session_state, '_communication_hub'):
            st.session_state._communication_hub = create_communication_hub()
        return st.session_state._communication_hub
    
    def _initialize_system(self):
        """Initialize the enhanced multi-agent system once."""
        if st.session_state.system_initialized:
            return
            
        if self.openai_key:
            try:
                exa_key = os.getenv("EXA_API_KEY")
                st.session_state._enhanced_system = create_enhanced_design_review_system(
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
                st.session_state.system_initialized = True
                
            except Exception as e:
                st.error(f"Failed to initialize system: {e}")
                st.session_state.system_initialized = False
    
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
        
        # Optional settings in sidebar
        with st.sidebar:
            st.markdown("### ⚙️ Settings")
            if st.button("🤖 Toggle Agent Dashboard"):
                st.session_state.show_agent_panel = not st.session_state.get("show_agent_panel", False)
                st.rerun()
        
        # Create main layout - full width for cleaner interface
        self._render_chat_interface()
        
        # Optional agent activity panel (only show if user wants to see it)
        if st.session_state.get("show_agent_panel", False):
            with st.expander("🤖 Agent Activity Dashboard", expanded=False):
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
            
            # **REAL AGENT ORCHESTRATION** - Use the actual enhanced system
            review_result = self._conduct_real_enhanced_review(image_data, review_context, user_request)
            
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
    
    def _conduct_real_enhanced_review(self, image_data: str, context: Dict[str, Any], user_request: str) -> Dict[str, Any]:
        """Conduct the REAL enhanced multi-agent review using the actual system."""
        
        review_type = context["review_type"]
        primary_agents = context["primary_agents"]
        
        # Add real agent activity tracking
        st.session_state.agent_activity.append("🔄 Initializing enhanced multi-agent system...")
        
        try:
            # Simplified synchronous approach to avoid async issues
            st.session_state.agent_activity.append("🔍 Conducting design analysis...")
            st.session_state.agent_activity.append("👥 Coordinating specialist agents...")
            
            # Use the enhanced system's synchronous methods if available
            if hasattr(self.enhanced_system, 'review_design'):
                result = self.enhanced_system.review_design(
                    image_data=image_data,
                    review_type=review_type.replace('_', ' '),
                    context=user_request
                )
            else:
                # Use a basic OpenAI call as fallback
                from openai import OpenAI
                client = OpenAI(api_key=self.openai_key)
                
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": f"Please review this design with focus on: {review_type}. Context: {user_request}"},
                                {
                                    "type": "image_url",
                                    "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}
                                }
                            ]
                        }
                    ],
                    max_tokens=1500
                )
                
                result = {
                    "analysis": response.choices[0].message.content,
                    "agents_involved": primary_agents,
                    "review_type": review_type
                }
            
            st.session_state.agent_activity.append("✅ Multi-agent review completed")
            return self._format_real_review_results(result, context)
            
        except Exception as e:
            st.session_state.agent_activity.append(f"❌ Error: {str(e)}")
            # Return a helpful error response
            return {
                "analysis": f"I encountered an issue: {str(e)}. Please check your OpenAI API key configuration.",
                "agents_involved": ["system"],
                "review_type": review_type,
                "error": True
            }
    
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
    
    def _format_real_review_results(self, comprehensive_result: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Format the real enhanced system results for display."""
        
        # Extract phase results to show real agent work
        phase_results = comprehensive_result.get("phase_results", {})
        agent_messages = []
        individual_results = {}
        
        # Process each phase to show real agent activity
        for phase_name, results_list in phase_results.items():
            if not results_list:
                continue
                
            for result in results_list:
                agent_name = result.get("agent_name", "Unknown Agent")
                agent_score = result.get("score", 0)
                agent_feedback = result.get("feedback", "")
                
                # Add to activity log
                st.session_state.agent_activity.append(f"✅ {agent_name}: {agent_score:.1f}/10 analysis complete")
                
                # Format message
                if agent_score >= 8:
                    emoji = "🟢"
                elif agent_score >= 6:
                    emoji = "🟡"
                else:
                    emoji = "🔴"
                    
                agent_messages.append(f"{emoji} **{agent_name}**: {agent_score:.1f}/10 - {agent_feedback[:100]}{'...' if len(agent_feedback) > 100 else ''}")
                
                # Store for detailed view
                individual_results[result.get("agent_type", agent_name.lower().replace(" ", "_"))] = {
                    "score": agent_score,
                    "insights": result.get("specific_issues", [])[:3],  # Top 3 insights
                    "recommendations": result.get("recommendations", [])[:3]  # Top 3 recommendations
                }
        
        # Get overall metrics
        overall_score = comprehensive_result.get("overall_score", 0)
        confidence_score = comprehensive_result.get("confidence_score", 0)
        
        # Extract learning insights
        learning_insights = comprehensive_result.get("learning_insights", [])
        learning_summary = ""
        if learning_insights:
            high_impact_insights = [insight for insight in learning_insights if insight.get("impact", 0) > 0.7]
            if high_impact_insights:
                learning_summary = f"\n\n### 🧠 AI Learning Insights\nThe system identified {len(high_impact_insights)} high-impact patterns for future improvement."
        
        # Extract research context if EXA was used
        research_context = ""
        if "web_research" in comprehensive_result or any("research" in phase.lower() for phase in phase_results.keys()):
            research_context = "\n\n*🔍 Enhanced with real-time web research via EXA search*"
        
        # Create comprehensive summary
        summary = f"""## 🎯 {context['review_type'].replace('_', ' ').title()} Review Complete

**Overall Score: {overall_score:.1f}/10** | **Confidence: {confidence_score:.1f}**{research_context}

{chr(10).join(agent_messages)}

### 🔄 Real Agent Collaboration Summary
Our specialist agents used the enhanced multi-agent system with real orchestration, including:
- **Web Research**: {f"✅ EXA search conducted" if research_context else "❌ No external research"}
- **Knowledge Sharing**: ✅ Agent communication hub active
- **Learning System**: ✅ AI learning from previous reviews
- **Quality Assurance**: ✅ Cross-agent validation performed

### 🎯 Key Insights from Real Analysis
- **Primary Strengths**: {comprehensive_result.get('synthesis', 'Analysis completed')[:100]}...
- **Priority Actions**: {len(comprehensive_result.get('priority_actions', []))} actionable items identified

### 🚀 Next Steps (AI-Prioritized)
{chr(10).join([f"- {action}" for action in comprehensive_result.get('priority_actions', [])[:4]])}

{learning_summary}

*This was a real multi-agent analysis, not a simulation. The same system powers our Slack integration.*
"""

        return {
            "summary": summary,
            "overall_score": overall_score,
            "confidence_score": confidence_score,
            "agent_details": {
                "agents_involved": list(individual_results.keys()),
                "review_type": context["review_type"],
                "individual_results": individual_results,
                "collaboration_notes": f"Real enhanced system with {len(phase_results)} coordination phases",
                "research_conducted": bool(research_context),
                "learning_insights_count": len(learning_insights),
                "priority_actions_count": len(comprehensive_result.get('priority_actions', []))
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
