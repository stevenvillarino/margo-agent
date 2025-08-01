"""
Demo Script for Enhanced Multi-Agent Design Review System

This script demonstrates the complete functionality of the enhanced
design review system with all agents and learning capabilities.
"""

import asyncio
import base64
import os
from datetime import datetime
from pathlib import Path

from agents.enhanced_system import EnhancedDesignReviewSystem


async def demo_complete_system():
    """Complete demonstration of the enhanced design review system."""
    
    print("=" * 80)
    print("🚀 ENHANCED MULTI-AGENT DESIGN REVIEW SYSTEM DEMO")
    print("=" * 80)
    
    # Check API keys
    openai_key = os.getenv('OPENAI_API_KEY')
    exa_key = os.getenv('EXA_API_KEY')
    
    if not openai_key:
        print("❌ Error: OPENAI_API_KEY environment variable not set")
        print("   Please set your OpenAI API key to use the system")
        return
    
    print("✅ OpenAI API key found")
    print(f"🔍 Exa API key: {'found' if exa_key else 'not found (web search disabled)'}")
    
    # Initialize the enhanced system
    print("\n📋 Initializing Enhanced Design Review System...")
    
    try:
        system = EnhancedDesignReviewSystem(
            openai_api_key=openai_key,
            exa_api_key=exa_key,
            learning_enabled=True,
            company_context={
                "industry": "Streaming/Entertainment",
                "company_stage": "Growth",
                "primary_metrics": ["User Engagement", "Content Discovery", "Revenue Per User"],
                "target_audience": "TV viewers, families, cord-cutters",
                "competitive_position": "Premium streaming platform with focus on user experience"
            }
        )
        
        print("✅ System initialized successfully!")
        
    except Exception as e:
        print(f"❌ Error initializing system: {e}")
        return
    
    # Display system status
    print("\n📊 SYSTEM STATUS")
    print("-" * 40)
    
    status = system.get_system_status()
    
    print(f"🤖 Registered Agents: {status['orchestrator_status']['registered_agents']}")
    print(f"🧠 Learning System: {'Active' if status['capabilities']['learning_enabled'] else 'Disabled'}")
    print(f"🔍 Web Research: {'Enabled' if status['capabilities']['web_research'] else 'Disabled'}")
    print(f"⚡ Parallel Processing: {'Enabled' if status['capabilities']['parallel_processing'] else 'Disabled'}")
    print(f"🎯 Adaptive Prompts: {'Enabled' if status['capabilities']['adaptive_prompts'] else 'Disabled'}")
    
    # Show available agents
    print("\n🤖 AVAILABLE AGENTS")
    print("-" * 40)
    
    for agent_type, agent_info in status['agent_status'].items():
        agent_name = agent_info.get('agent_name', agent_type)
        specialization = agent_info.get('specialization', 'General')
        print(f"  • {agent_name} ({agent_type})")
        print(f"    Specialization: {specialization}")
    
    # Demonstrate different review scenarios
    print("\n🎯 DEMONSTRATION SCENARIOS")
    print("-" * 40)
    
    scenarios = [
        {
            "name": "Roku TV Interface Navigation",
            "design_type": "TV interface navigation",
            "context": {
                "platform": "Roku TV",
                "target_users": "General TV audience",
                "key_requirements": ["Remote control navigation", "Accessibility", "Fast discovery"]
            },
            "selected_agents": ["ui_specialist", "accessibility", "vp_product"]
        },
        {
            "name": "Streaming App Homepage",
            "design_type": "streaming app homepage",
            "context": {
                "platform": "Mobile/Web",
                "target_users": "Streaming subscribers",
                "key_requirements": ["Content discovery", "Personalization", "Quick access"]
            },
            "selected_agents": ["ux_researcher", "creative_director", "vp_product"]
        },
        {
            "name": "Channel Store Interface",
            "design_type": "app store interface",
            "context": {
                "platform": "Roku Channel Store",
                "target_users": "Roku device owners",
                "key_requirements": ["Easy browsing", "Clear categorization", "Install flow"]
            },
            "selected_agents": ["ui_specialist", "ux_researcher", "accessibility"]
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{i}. {scenario['name']}")
        print(f"   Design Type: {scenario['design_type']}")
        print(f"   Platform: {scenario['context']['platform']}")
        print(f"   Selected Agents: {', '.join(scenario['selected_agents'])}")
        
        # Simulate review process (without actual image)
        print(f"   📋 Simulating review process...")
        
        # In a real scenario, you would have actual image data
        # For demo purposes, we'll show what the process would look like
        print(f"   🔍 Step 1: Loading design image and context")
        print(f"   🧠 Step 2: Applying learning enhancements")
        print(f"   🤖 Step 3: Conducting multi-agent review")
        print(f"   📝 Step 4: Synthesizing agent feedback")
        print(f"   💡 Step 5: Extracting learning insights")
        print(f"   ✅ Step 6: Generating final recommendations")
        
        # Show what the results would contain
        print(f"   📊 Expected Output:")
        print(f"      - Overall score (1-10)")
        print(f"      - Agent-specific feedback")
        print(f"      - Consensus analysis")
        print(f"      - Priority action items")
        print(f"      - Learning insights")
        print(f"      - Implementation recommendations")
    
    # Demonstrate learning capabilities
    print("\n🧠 LEARNING SYSTEM CAPABILITIES")
    print("-" * 40)
    
    learning_status = status.get('learning_status', {})
    
    if learning_status.get('learning_status') == 'active':
        print("✅ Learning system is active and processing review patterns")
        print(f"📊 Total reviews processed: {learning_status.get('total_reviews_processed', 0)}")
        print(f"💡 Insights generated: {learning_status.get('total_insights_generated', 0)}")
        print(f"🎯 Average confidence: {learning_status.get('average_insight_confidence', 0):.2f}")
    else:
        print("📚 Learning system is collecting data for pattern analysis")
        print("   Need more reviews to generate insights and improvements")
    
    # Show learning capabilities
    print("\n🔧 Learning Features:")
    print("  • Pattern recognition across reviews")
    print("  • Agent performance tracking")
    print("  • Adaptive prompt enhancement")
    print("  • Consensus analysis")
    print("  • Issue trend identification")
    print("  • Recommendation effectiveness tracking")
    
    # Demonstrate configuration options
    print("\n⚙️ SYSTEM CONFIGURATION")
    print("-" * 40)
    
    current_config = status['system_config']
    print("Current Configuration:")
    for key, value in current_config.items():
        print(f"  • {key}: {value}")
    
    print("\nAvailable Configuration Options:")
    print("  • enable_parallel_reviews: Speed vs. resource usage")
    print("  • enable_learning: Adaptive improvement over time")
    print("  • enable_adaptive_prompts: Use learning insights")
    print("  • min_agents_for_review: Quality vs. speed trade-off")
    print("  • confidence_threshold: Learning insight filtering")
    
    # Show example API usage
    print("\n💻 EXAMPLE API USAGE")
    print("-" * 40)
    
    print("""
# Basic usage example:
system = EnhancedDesignReviewSystem(
    openai_api_key="your_key",
    exa_api_key="your_exa_key",  # Optional
    learning_enabled=True
)

# Conduct comprehensive review:
results = await system.conduct_comprehensive_review(
    image_data=base64_encoded_image,
    design_type="TV interface",
    context={
        "platform": "Roku TV",
        "requirements": ["accessibility", "usability"]
    },
    selected_agents=["ui_specialist", "accessibility", "vp_product"]
)

# Access results:
overall_score = results['overall_score']
priority_actions = results['priority_actions']
learning_insights = results['learning_insights']
agent_consensus = results['agent_consensus']
""")
    
    # Performance and capabilities summary
    print("\n🎯 SYSTEM CAPABILITIES SUMMARY")
    print("-" * 40)
    
    print("✅ Multi-Agent Architecture:")
    print("  • UI/UX Specialist - Design craft and usability")
    print("  • UX Researcher - User-centered analysis")
    print("  • Creative Director - Innovation and brand alignment")
    print("  • VP of Product - Business and strategic perspective")
    print("  • Accessibility Expert - WCAG compliance and inclusion")
    
    print("\n✅ Advanced Features:")
    print("  • Web research integration (Exa AI)")
    print("  • Learning and adaptation over time")
    print("  • Parallel processing for speed")
    print("  • Consensus analysis and conflict resolution")
    print("  • Structured feedback with actionable insights")
    
    print("\n✅ Quality Assurance:")
    print("  • Confidence scoring for reliability")
    print("  • Agent performance tracking")
    print("  • Review quality metrics")
    print("  • Pattern recognition for consistency")
    
    # Next steps
    print("\n🚀 NEXT STEPS TO GET STARTED")
    print("-" * 40)
    
    print("1. Set up environment variables:")
    print("   export OPENAI_API_KEY='your_openai_key'")
    print("   export EXA_API_KEY='your_exa_key'  # Optional but recommended")
    
    print("\n2. Install dependencies:")
    print("   pip install -r requirements.txt")
    
    print("\n3. Initialize the system:")
    print("   from agents.enhanced_system import EnhancedDesignReviewSystem")
    print("   system = EnhancedDesignReviewSystem(openai_api_key, exa_api_key)")
    
    print("\n4. Conduct your first review:")
    print("   results = await system.conduct_comprehensive_review(image_data, design_type)")
    
    print("\n5. Iterate and improve:")
    print("   • Review learning insights")
    print("   • Adjust agent configurations")
    print("   • Customize for your specific needs")
    
    print("\n" + "=" * 80)
    print("🎉 DEMO COMPLETE - SYSTEM READY FOR PRODUCTION USE!")
    print("=" * 80)


def create_sample_image_data():
    """Create sample base64 image data for testing."""
    # In a real scenario, you would load an actual image file
    # For demo purposes, we'll create a placeholder
    sample_text = "Sample image data for demo purposes"
    return base64.b64encode(sample_text.encode()).decode()


if __name__ == "__main__":
    # Run the demo
    asyncio.run(demo_complete_system())
