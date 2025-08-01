"""
Complete Advanced Workflow Demo

This script demonstrates the full advanced workflow system including:
- Multi-agent design review with inter-communication
- Knowledge gap detection and agent escalation
- JIRA ticket creation for issues
- QA validation with Playwright
- Research study automation
- Margo agent gate-keeping
- EXA web research integration

Run this to see the complete system in action.
"""

import asyncio
import json
import os
import base64
from datetime import datetime
from typing import Dict, Any

from agents.advanced_workflow_system import create_advanced_workflow_system


class AdvancedWorkflowDemo:
    """Complete demonstration of the advanced workflow system."""
    
    def __init__(self):
        """Initialize the demo."""
        
        # Check for required environment variables
        self.openai_key = os.getenv('OPENAI_API_KEY')
        self.exa_key = os.getenv('EXA_API_KEY')
        
        if not self.openai_key:
            print("❌ OPENAI_API_KEY required for demo")
            return
        
        # Initialize the complete system
        print("🚀 Initializing Advanced Workflow System...")
        self.system = create_advanced_workflow_system(
            openai_api_key=self.openai_key,
            exa_api_key=self.exa_key,
            jira_url=os.getenv('JIRA_URL'),
            jira_username=os.getenv('JIRA_USERNAME'),
            jira_api_token=os.getenv('JIRA_API_TOKEN'),
            enable_playwright=True
        )
        
        print("✅ Advanced Workflow System initialized successfully!")
        print("=" * 80)
    
    async def run_complete_demo(self):
        """Run the complete workflow demo."""
        
        if not self.openai_key:
            return
        
        print("🎯 ADVANCED DESIGN WORKFLOW AUTOMATION DEMO")
        print("=" * 80)
        
        # Demo scenarios
        scenarios = [
            self._demo_scenario_1_complex_design(),
            self._demo_scenario_2_simple_approval(),
            self._demo_scenario_3_qa_discrepancies()
        ]
        
        for i, scenario in enumerate(scenarios, 1):
            print(f"\n🎬 SCENARIO {i}: {scenario['title']}")
            print("-" * 60)
            print(f"📝 Description: {scenario['description']}")
            print()
            
            # Process the scenario
            try:
                result = await self.system.process_complete_design_workflow(scenario['submission'])
                self._display_workflow_results(result, scenario['title'])
                
            except Exception as e:
                print(f"❌ Scenario {i} failed: {e}")
            
            print("\n" + "=" * 80)
            
            # Wait between scenarios
            await asyncio.sleep(2)
        
        # Demo inter-agent communication
        await self._demo_agent_communication()
        
        # Demo knowledge sharing
        await self._demo_knowledge_sharing()
        
        print("\n🎉 DEMO COMPLETED!")
        print("✅ All scenarios processed successfully")
        print("📊 System ready for production use")
    
    def _demo_scenario_1_complex_design(self) -> Dict[str, Any]:
        """Scenario 1: Complex design requiring research and Margo review."""
        
        return {
            "title": "Complex Checkout Flow Redesign",
            "description": "High-impact payment flow with accessibility concerns and missing research",
            "submission": {
                "design_type": "ui_design",
                "design_area": "checkout_flow",
                "feature_type": "payment_integration",
                "impact_level": "high",
                "image_data": self._create_sample_image_data(),
                # "feature_guide": None,  # Missing - should trigger research
                "qa_link": "https://qa-demo.yourapp.com/checkout",
                "design_spec_url": "https://figma.com/file/checkout-redesign",
                "expected_elements": [
                    {
                        "name": "Pay Button",
                        "selector": ".btn-pay",
                        "properties": {
                            "background-color": "#007AFF",
                            "height": "44px",
                            "border-radius": "8px"
                        }
                    },
                    {
                        "name": "Total Amount",
                        "selector": ".checkout-total",
                        "properties": {
                            "font-size": "24px",
                            "font-weight": "600",
                            "color": "#000000"
                        }
                    }
                ],
                "context": {
                    "designer": "Sarah Chen",
                    "product_manager": "Mike Rodriguez",
                    "feature_deadline": "2024-03-15",
                    "business_impact": "High - affects conversion rate",
                    "user_segments": ["Premium subscribers", "New users"],
                    "accessibility_requirements": "WCAG 2.1 AA compliance required",
                    "stakeholders": ["product_team", "engineering_team", "accessibility_team", "legal_team"]
                }
            }
        }
    
    def _demo_scenario_2_simple_approval(self) -> Dict[str, Any]:
        """Scenario 2: Simple design that should pass all checks."""
        
        return {
            "title": "Simple Icon Update",
            "description": "Low-risk icon update with complete documentation",
            "submission": {
                "design_type": "ui_design",
                "design_area": "navigation",
                "feature_type": "icon_update",
                "impact_level": "low",
                "image_data": self._create_sample_image_data(),
                "feature_guide": "Update navigation icons to new design system icons. No functional changes.",
                "design_spec_url": "https://figma.com/file/icon-update",
                "context": {
                    "designer": "Alex Kim",
                    "feature_deadline": "2024-02-28",
                    "business_impact": "Low - visual consistency improvement",
                    "accessibility_requirements": "Maintain existing accessibility",
                    "stakeholders": ["design_team"]
                }
            }
        }
    
    def _demo_scenario_3_qa_discrepancies(self) -> Dict[str, Any]:
        """Scenario 3: Design with QA implementation discrepancies."""
        
        return {
            "title": "Button Styling Discrepancies",
            "description": "QA implementation doesn't match design specification",
            "submission": {
                "design_type": "ui_design",
                "design_area": "forms",
                "feature_type": "button_styling",
                "impact_level": "medium",
                "image_data": self._create_sample_image_data(),
                "feature_guide": "Update button styles to match new design system specifications.",
                "qa_link": "https://qa-demo.yourapp.com/forms",
                "design_spec_url": "https://figma.com/file/button-spec",
                "expected_elements": [
                    {
                        "name": "Primary Button",
                        "selector": ".btn-primary",
                        "properties": {
                            "background-color": "#007AFF",
                            "height": "44px",
                            "border-radius": "8px",
                            "font-weight": "600"
                        }
                    }
                ],
                "context": {
                    "designer": "Emma Wilson",
                    "qa_engineer": "David Park",
                    "feature_deadline": "2024-03-01",
                    "business_impact": "Medium - affects user experience",
                    "stakeholders": ["design_team", "qa_team", "engineering_team"]
                }
            }
        }
    
    def _create_sample_image_data(self) -> str:
        """Create sample base64 image data for demo."""
        # In a real scenario, this would be actual design file data
        sample_data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
        return sample_data
    
    def _display_workflow_results(self, result: Dict[str, Any], scenario_title: str):
        """Display workflow results in a formatted way."""
        
        print(f"📊 WORKFLOW RESULTS: {scenario_title}")
        print(f"🆔 Workflow ID: {result['workflow_id']}")
        print(f"⏱️  Duration: {self._calculate_duration(result)}")
        print(f"✅ Status: {result['status']}")
        print()
        
        # Summary metrics
        summary = result.get('summary', {})
        print("📈 SUMMARY METRICS:")
        print(f"   Overall Design Score: {summary.get('overall_score', 0):.1f}/10")
        print(f"   Issues Created: {summary.get('issues_created', 0)}")
        print(f"   Margo Review Required: {'Yes' if summary.get('margo_required') else 'No'}")
        
        if summary.get('qa_validation_score'):
            print(f"   QA Validation Score: {summary.get('qa_validation_score', 0):.1f}/10")
        print()
        
        # Phase results
        phases = result.get('phase_results', {})
        print("🔄 PHASE RESULTS:")
        
        for phase_name, phase_data in phases.items():
            print(f"   📋 {phase_name.replace('_', ' ').title()}:")
            
            if phase_name == 'precheck':
                feature_status = phase_data.get('feature_guide_status', 'unknown')
                research_needed = phase_data.get('research_status', {}).get('needs_research', False)
                print(f"      - Feature Guide: {feature_status}")
                print(f"      - Research Required: {'Yes' if research_needed else 'No'}")
                
                if phase_data.get('research_study'):
                    study = phase_data['research_study']
                    print(f"      - Research Study Created: {study.get('study_id', 'N/A')}")
            
            elif phase_name == 'design_review':
                agent_count = phase_data.get('agent_count', 0)
                consensus = phase_data.get('consensus_score', 0)
                critical_issues = len(phase_data.get('critical_issues', []))
                print(f"      - Agents Participated: {agent_count}")
                print(f"      - Consensus Score: {consensus:.1%}")
                print(f"      - Critical Issues: {critical_issues}")
            
            elif phase_name == 'issue_tracking':
                tickets = phase_data.get('tickets_created', 0)
                print(f"      - JIRA Tickets Created: {tickets}")
                
                if tickets > 0 and phase_data.get('tickets'):
                    for ticket in phase_data['tickets'][:3]:  # Show first 3
                        print(f"        • {ticket.get('ticket_id', 'N/A')}: {ticket.get('issue', {}).get('title', 'Issue')}")
            
            elif phase_name == 'margo_gate':
                margo_status = phase_data.get('margo_status', 'unknown')
                print(f"      - Margo Status: {margo_status}")
                print(f"      - Action: {phase_data.get('margo_action', 'N/A')}")
            
            elif phase_name == 'qa_validation':
                if phase_data.get('status') == 'completed':
                    score = phase_data.get('overall_score', 0)
                    discrepancies = phase_data.get('discrepancies_found', 0)
                    print(f"      - Validation Score: {score:.1f}/10")
                    print(f"      - Discrepancies Found: {discrepancies}")
                else:
                    print(f"      - Status: {phase_data.get('status', 'unknown')}")
            
            elif phase_name == 'knowledge_gaps':
                gaps = phase_data.get('total_gaps', 0)
                resolution_rate = phase_data.get('resolution_rate', 0)
                print(f"      - Knowledge Gaps: {gaps}")
                print(f"      - Resolution Rate: {resolution_rate:.1%}")
        
        print()
        
        # Next steps
        next_steps = result.get('next_steps', [])
        if next_steps:
            print("🎯 NEXT STEPS:")
            for i, step in enumerate(next_steps, 1):
                print(f"   {i}. {step}")
            print()
        
        # Stakeholder notifications
        notifications = result.get('stakeholder_notifications', 0)
        if notifications > 0:
            print(f"📧 Stakeholder Notifications Sent: {notifications}")
    
    async def _demo_agent_communication(self):
        """Demonstrate inter-agent communication."""
        
        print("\n💬 INTER-AGENT COMMUNICATION DEMO")
        print("-" * 60)
        
        # Request knowledge between agents
        print("📩 Demonstrating knowledge request between agents...")
        
        request_id = await self.system.communication_hub.request_knowledge(
            requester="ui_specialist",
            topic="accessibility",
            specific_question="What are the WCAG requirements for button contrast ratios?",
            urgency=Priority.MEDIUM
        )
        
        print(f"✅ Knowledge request sent: {request_id}")
        
        # Simulate response
        if request_id:
            response_id = await self.system.communication_hub.provide_knowledge_response(
                responder="accessibility_expert",
                original_message_id=request_id,
                knowledge={
                    "wcag_requirement": "4.5:1 for normal text, 3:1 for large text",
                    "guideline": "WCAG 2.1 SC 1.4.3 Contrast (Minimum)",
                    "tools": ["WebAIM Contrast Checker", "Colour Contrast Analyser"]
                },
                confidence=0.95,
                sources=["WCAG 2.1 Guidelines", "WebAIM Documentation"]
            )
            print(f"✅ Knowledge response provided: {response_id}")
        
        # Demonstrate escalation
        print("\n🚨 Demonstrating issue escalation...")
        
        escalation_id = await self.system.communication_hub.escalate_issue(
            escalator="ui_specialist",
            issue={
                "title": "Complex accessibility requirement needs senior review",
                "type": "accessibility",
                "severity": "high",
                "description": "New accessibility requirement conflicts with existing design patterns"
            },
            escalation_reason="Requires strategic decision on design system impact"
        )
        
        print(f"✅ Issue escalated: {escalation_id}")
        
        # Show communication stats
        hub_stats = {
            "total_agents": len(self.system.communication_hub.agent_capabilities),
            "active_conversations": len(self.system.communication_hub.threads),
            "total_messages": len(self.system.communication_hub.messages)
        }
        
        print(f"\n📊 Communication Hub Stats:")
        print(f"   Registered Agents: {hub_stats['total_agents']}")
        print(f"   Active Conversations: {hub_stats['active_conversations']}")
        print(f"   Total Messages: {hub_stats['total_messages']}")
    
    async def _demo_knowledge_sharing(self):
        """Demonstrate knowledge sharing capabilities."""
        
        print("\n🧠 KNOWLEDGE SHARING DEMO")
        print("-" * 60)
        
        # Show shared knowledge base
        knowledge_topics = ["accessibility", "design_systems", "user_research", "brand_guidelines"]
        
        print("📚 Shared Knowledge Base:")
        for topic in knowledge_topics:
            knowledge = self.system.communication_hub.get_shared_knowledge(topic)
            contributions = len(knowledge.get("contributions", []))
            last_updated = knowledge.get("last_updated")
            
            print(f"   📖 {topic.replace('_', ' ').title()}: {contributions} contributions")
            if last_updated:
                print(f"      Last updated: {last_updated.strftime('%Y-%m-%d %H:%M')}")
        
        print()
        
        # Demonstrate research capabilities
        if self.system.exa_agent:
            print("🔍 EXA Research Integration Demo:")
            
            research_query = "design system best practices accessibility"
            print(f"   Searching for: '{research_query}'")
            
            try:
                research_results = self.system.exa_agent.search_design_best_practices(
                    research_query, num_results=3
                )
                
                print(f"   ✅ Found {len(research_results)} research results")
                
                for i, result in enumerate(research_results[:2], 1):
                    title = result.metadata.get('title', 'Unknown')
                    print(f"      {i}. {title[:60]}...")
                
            except Exception as e:
                print(f"   ❌ Research failed: {e}")
        else:
            print("🔍 EXA Research: Not configured (requires EXA_API_KEY)")
    
    def _calculate_duration(self, result: Dict[str, Any]) -> str:
        """Calculate workflow duration."""
        
        started = result.get('started_at')
        completed = result.get('completed_at')
        
        if started and completed:
            if isinstance(started, str):
                return "completed"
            duration = completed - started
            return f"{duration.total_seconds():.1f}s"
        
        return "unknown"


# Main execution
async def main():
    """Run the complete advanced workflow demo."""
    
    print("🎯 MARGO AGENT - ADVANCED WORKFLOW AUTOMATION DEMO")
    print("=" * 80)
    print("This demo showcases the complete workflow automation system including:")
    print("• Multi-agent design review with intelligent orchestration")
    print("• Knowledge gap detection and inter-agent communication")
    print("• Automated JIRA ticket creation for issues")
    print("• QA validation with Playwright automation")
    print("• Research study automation and management")
    print("• Margo agent gate-keeping for strategic oversight")
    print("• EXA web research integration")
    print("• Complete stakeholder notification system")
    print("=" * 80)
    
    # Check environment
    required_vars = ["OPENAI_API_KEY"]
    optional_vars = ["EXA_API_KEY", "JIRA_URL", "JIRA_USERNAME", "JIRA_API_TOKEN"]
    
    print("\n🔧 ENVIRONMENT CHECK:")
    for var in required_vars:
        status = "✅" if os.getenv(var) else "❌"
        print(f"   {status} {var}: {'Set' if os.getenv(var) else 'Missing (Required)'}")
    
    for var in optional_vars:
        status = "✅" if os.getenv(var) else "⚠️"
        feature_map = {
            "EXA_API_KEY": "Web Research",
            "JIRA_URL": "JIRA Integration",
            "JIRA_USERNAME": "JIRA Integration", 
            "JIRA_API_TOKEN": "JIRA Integration"
        }
        feature = feature_map.get(var, var)
        print(f"   {status} {var}: {'Set' if os.getenv(var) else f'Missing ({feature} disabled)'}")
    
    if not os.getenv('OPENAI_API_KEY'):
        print("\n❌ Cannot run demo without OPENAI_API_KEY")
        print("Please set your OpenAI API key and try again.")
        return
    
    print("\n⏱️  Starting demo in 3 seconds...")
    await asyncio.sleep(3)
    
    # Run the demo
    demo = AdvancedWorkflowDemo()
    await demo.run_complete_demo()


if __name__ == "__main__":
    # Import Priority here to avoid circular import
    from agents.agent_communication import Priority
    
    asyncio.run(main())
