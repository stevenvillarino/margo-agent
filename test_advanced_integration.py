"""
Advanced Workflow System Integration Test

This script validates that all components of the advanced workflow system
are properly integrated and working together.
"""

import asyncio
import os
import sys
import json
from datetime import datetime
from typing import Dict, Any, List


class AdvancedWorkflowIntegrationTest:
    """Integration test suite for the advanced workflow system."""
    
    def __init__(self):
        """Initialize the integration test."""
        self.test_results: List[Dict[str, Any]] = []
        self.openai_key = os.getenv('OPENAI_API_KEY')
        self.exa_key = os.getenv('EXA_API_KEY')
        
        # Track test status
        self.tests_passed = 0
        self.tests_failed = 0
        self.tests_skipped = 0
    
    async def run_all_tests(self):
        """Run complete integration test suite."""
        
        print("🧪 ADVANCED WORKFLOW SYSTEM - INTEGRATION TESTS")
        print("=" * 60)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Test environment setup
        await self._test_environment_setup()
        
        # Test imports
        await self._test_imports()
        
        # Test agent communication hub
        await self._test_agent_communication()
        
        # Test workflow orchestrator
        await self._test_workflow_orchestrator()
        
        # Test JIRA integration
        await self._test_jira_integration()
        
        # Test Playwright validator
        await self._test_playwright_validator()
        
        # Test EXA research agent
        await self._test_exa_research()
        
        # Test complete workflow system
        await self._test_complete_workflow_system()
        
        # Display results
        self._display_test_results()
    
    async def _test_environment_setup(self):
        """Test environment configuration."""
        
        print("🔧 Testing Environment Setup...")
        
        # Test required environment variables
        required_vars = {
            'OPENAI_API_KEY': 'OpenAI API integration'
        }
        
        for var, description in required_vars.items():
            value = os.getenv(var)
            if value:
                self._record_test_result("Environment", f"{var} configured", True, description)
            else:
                self._record_test_result("Environment", f"{var} missing", False, f"Required for {description}")
        
        # Test optional environment variables
        optional_vars = {
            'EXA_API_KEY': 'Web research capabilities',
            'JIRA_URL': 'JIRA issue tracking',
            'JIRA_USERNAME': 'JIRA authentication',
            'JIRA_API_TOKEN': 'JIRA API access'
        }
        
        for var, description in optional_vars.items():
            value = os.getenv(var)
            if value:
                self._record_test_result("Environment", f"{var} configured", True, f"Enables {description}")
            else:
                self._record_test_result("Environment", f"{var} not configured", None, f"Optional - {description} will be disabled")
    
    async def _test_imports(self):
        """Test that all required modules can be imported."""
        
        print("📦 Testing Module Imports...")
        
        # Core imports
        core_imports = [
            ('langchain', 'LangChain framework'),
            ('langchain_openai', 'OpenAI integration'),
            ('agents.enhanced_system', 'Enhanced design system'),
            ('agents.workflow_orchestrator', 'Workflow orchestrator'),
            ('agents.agent_communication', 'Agent communication hub'),
            ('agents.jira_integration', 'JIRA integration'),
        ]
        
        for module_name, description in core_imports:
            try:
                __import__(module_name)
                self._record_test_result("Imports", f"{module_name}", True, description)
            except ImportError as e:
                self._record_test_result("Imports", f"{module_name}", False, f"Import failed: {e}")
        
        # Optional imports
        optional_imports = [
            ('playwright.async_api', 'Playwright QA validation'),
            ('exa_py', 'EXA web research'),
            ('slack_bolt', 'Slack bot integration'),
            ('jira', 'JIRA Python client')
        ]
        
        for module_name, description in optional_imports:
            try:
                __import__(module_name)
                self._record_test_result("Imports", f"{module_name}", True, f"Optional - {description}")
            except ImportError:
                self._record_test_result("Imports", f"{module_name}", None, f"Optional - {description} not available")
    
    async def _test_agent_communication(self):
        """Test agent communication hub functionality."""
        
        print("💬 Testing Agent Communication Hub...")
        
        try:
            from agents.agent_communication import create_communication_hub, AgentCapability, MessageType, Priority
            
            # Create communication hub
            hub = create_communication_hub()
            self._record_test_result("Communication", "Hub creation", True, "Communication hub initialized")
            
            # Register test agents
            test_capability = AgentCapability(
                agent_id="test_agent",
                agent_name="Test Agent",
                agent_type="test",
                expertise_areas=["testing"],
                available_methods=["test"],
                current_load=0,
                response_time_avg=60.0,
                reliability_score=1.0
            )
            
            hub.register_agent("test_agent", test_capability)
            self._record_test_result("Communication", "Agent registration", True, "Test agent registered successfully")
            
            # Test message sending
            message_id = await hub.send_message(
                sender="test_agent",
                recipient="test_agent",
                message_type=MessageType.NOTIFICATION,
                subject="Test message",
                content={"test": True},
                priority=Priority.LOW
            )
            
            if message_id:
                self._record_test_result("Communication", "Message sending", True, "Messages can be sent between agents")
            else:
                self._record_test_result("Communication", "Message sending", False, "Message sending failed")
            
        except Exception as e:
            self._record_test_result("Communication", "Hub functionality", False, f"Error: {e}")
    
    async def _test_workflow_orchestrator(self):
        """Test workflow orchestrator functionality."""
        
        print("🔄 Testing Workflow Orchestrator...")
        
        if not self.openai_key:
            self._record_test_result("Orchestrator", "Initialization", None, "Skipped - no OpenAI key")
            return
        
        try:
            from agents.workflow_orchestrator import create_workflow_orchestrator
            
            # Create orchestrator
            orchestrator = create_workflow_orchestrator(
                openai_api_key=self.openai_key,
                exa_api_key=self.exa_key
            )
            
            self._record_test_result("Orchestrator", "Initialization", True, "Workflow orchestrator created successfully")
            
            # Test enhanced system integration
            if hasattr(orchestrator, 'enhanced_system'):
                self._record_test_result("Orchestrator", "Enhanced system integration", True, "Enhanced design system integrated")
            else:
                self._record_test_result("Orchestrator", "Enhanced system integration", False, "Enhanced system not integrated")
            
        except Exception as e:
            self._record_test_result("Orchestrator", "Functionality", False, f"Error: {e}")
    
    async def _test_jira_integration(self):
        """Test JIRA integration functionality."""
        
        print("🎫 Testing JIRA Integration...")
        
        jira_url = os.getenv('JIRA_URL')
        jira_username = os.getenv('JIRA_USERNAME')
        jira_token = os.getenv('JIRA_API_TOKEN')
        
        if not all([jira_url, jira_username, jira_token]):
            self._record_test_result("JIRA", "Configuration", None, "Skipped - JIRA credentials not configured")
            return
        
        try:
            from agents.jira_integration import create_jira_integration
            
            # Create JIRA integration
            jira = create_jira_integration(
                jira_url=jira_url,
                username=jira_username,
                api_token=jira_token
            )
            
            if jira:
                self._record_test_result("JIRA", "Connection", True, "JIRA connection established")
                
                # Test issue creation (dry run)
                try:
                    # Note: This would create an actual ticket, so we just test the method exists
                    if hasattr(jira, 'create_design_issue'):
                        self._record_test_result("JIRA", "Issue creation capability", True, "Can create design issues")
                    else:
                        self._record_test_result("JIRA", "Issue creation capability", False, "create_design_issue method missing")
                except Exception as e:
                    self._record_test_result("JIRA", "Issue creation test", False, f"Error: {e}")
            else:
                self._record_test_result("JIRA", "Connection", False, "Failed to establish JIRA connection")
                
        except Exception as e:
            self._record_test_result("JIRA", "Integration", False, f"Error: {e}")
    
    async def _test_playwright_validator(self):
        """Test Playwright QA validator functionality."""
        
        print("🧪 Testing Playwright QA Validator...")
        
        try:
            from agents.playwright_validator import create_playwright_validator
            
            # Create validator
            validator = create_playwright_validator()
            
            if validator:
                self._record_test_result("Playwright", "Initialization", True, "Playwright validator created successfully")
                
                # Test design tokens loading
                if hasattr(validator, 'design_tokens'):
                    self._record_test_result("Playwright", "Design tokens", True, "Design tokens loaded")
                else:
                    self._record_test_result("Playwright", "Design tokens", False, "Design tokens not loaded")
                    
            else:
                self._record_test_result("Playwright", "Initialization", None, "Playwright not available")
                
        except Exception as e:
            self._record_test_result("Playwright", "Validator", False, f"Error: {e}")
    
    async def _test_exa_research(self):
        """Test EXA research agent functionality."""
        
        print("🔍 Testing EXA Research Agent...")
        
        if not self.exa_key:
            self._record_test_result("EXA", "Configuration", None, "Skipped - no EXA API key")
            return
        
        try:
            from agents.exa_search import ExaSearchAgent
            
            # Create EXA agent
            exa_agent = ExaSearchAgent(self.exa_key)
            self._record_test_result("EXA", "Initialization", True, "EXA research agent created")
            
            # Test search capability
            try:
                # Small test search
                results = exa_agent.search_design_best_practices("button design", num_results=1)
                if results:
                    self._record_test_result("EXA", "Search capability", True, f"Found {len(results)} research results")
                else:
                    self._record_test_result("EXA", "Search capability", False, "No search results returned")
            except Exception as e:
                self._record_test_result("EXA", "Search capability", False, f"Search failed: {e}")
                
        except Exception as e:
            self._record_test_result("EXA", "Research agent", False, f"Error: {e}")
    
    async def _test_complete_workflow_system(self):
        """Test the complete advanced workflow system."""
        
        print("🚀 Testing Complete Workflow System...")
        
        if not self.openai_key:
            self._record_test_result("Complete System", "Initialization", None, "Skipped - no OpenAI key")
            return
        
        try:
            from agents.advanced_workflow_system import create_advanced_workflow_system
            
            # Create complete system
            system = create_advanced_workflow_system(
                openai_api_key=self.openai_key,
                exa_api_key=self.exa_key,
                enable_playwright=True
            )
            
            self._record_test_result("Complete System", "Initialization", True, "Advanced workflow system created")
            
            # Test component integration
            components = [
                ('workflow_orchestrator', 'Workflow orchestrator'),
                ('design_system', 'Enhanced design system'),
                ('communication_hub', 'Agent communication hub')
            ]
            
            for component, description in components:
                if hasattr(system, component):
                    self._record_test_result("Complete System", f"{description} integration", True, f"{description} properly integrated")
                else:
                    self._record_test_result("Complete System", f"{description} integration", False, f"{description} not integrated")
            
            # Test agent registration
            agent_count = len(system.communication_hub.agent_capabilities)
            if agent_count > 0:
                self._record_test_result("Complete System", "Agent registration", True, f"{agent_count} agents registered")
            else:
                self._record_test_result("Complete System", "Agent registration", False, "No agents registered")
                
        except Exception as e:
            self._record_test_result("Complete System", "System integration", False, f"Error: {e}")
    
    def _record_test_result(self, category: str, test_name: str, passed: bool, description: str):
        """Record a test result."""
        
        result = {
            "category": category,
            "test_name": test_name,
            "passed": passed,
            "description": description,
            "timestamp": datetime.now()
        }
        
        self.test_results.append(result)
        
        # Update counters
        if passed is True:
            self.tests_passed += 1
            status = "✅"
        elif passed is False:
            self.tests_failed += 1
            status = "❌"
        else:
            self.tests_skipped += 1
            status = "⚠️"
        
        print(f"   {status} {test_name}: {description}")
    
    def _display_test_results(self):
        """Display comprehensive test results."""
        
        print("\n" + "=" * 60)
        print("🧪 INTEGRATION TEST RESULTS")
        print("=" * 60)
        
        # Summary
        total_tests = self.tests_passed + self.tests_failed + self.tests_skipped
        print(f"📊 Test Summary:")
        print(f"   Total Tests: {total_tests}")
        print(f"   ✅ Passed: {self.tests_passed}")
        print(f"   ❌ Failed: {self.tests_failed}")
        print(f"   ⚠️  Skipped: {self.tests_skipped}")
        
        if self.tests_failed == 0:
            print("\n🎉 ALL TESTS PASSED!")
            print("✅ System is ready for production use")
        else:
            print(f"\n⚠️  {self.tests_failed} test(s) failed")
            print("❌ System requires attention before production use")
        
        # Category breakdown
        print(f"\n📋 Test Results by Category:")
        categories = {}
        for result in self.test_results:
            category = result["category"]
            if category not in categories:
                categories[category] = {"passed": 0, "failed": 0, "skipped": 0}
            
            if result["passed"] is True:
                categories[category]["passed"] += 1
            elif result["passed"] is False:
                categories[category]["failed"] += 1
            else:
                categories[category]["skipped"] += 1
        
        for category, counts in categories.items():
            total = counts["passed"] + counts["failed"] + counts["skipped"]
            print(f"   {category}: {counts['passed']}/{total} passed, {counts['failed']} failed, {counts['skipped']} skipped")
        
        # Failed tests detail
        if self.tests_failed > 0:
            print(f"\n❌ Failed Tests Detail:")
            for result in self.test_results:
                if result["passed"] is False:
                    print(f"   • {result['category']} - {result['test_name']}: {result['description']}")
        
        # Configuration recommendations
        print(f"\n🔧 Configuration Recommendations:")
        
        if not os.getenv('OPENAI_API_KEY'):
            print("   • Set OPENAI_API_KEY for core functionality")
        
        if not os.getenv('EXA_API_KEY'):
            print("   • Set EXA_API_KEY for web research capabilities")
        
        if not os.getenv('JIRA_URL'):
            print("   • Configure JIRA credentials for issue tracking")
        
        jira_vars = ['JIRA_URL', 'JIRA_USERNAME', 'JIRA_API_TOKEN']
        jira_configured = all(os.getenv(var) for var in jira_vars)
        if not jira_configured:
            print("   • Complete JIRA configuration for automated ticket creation")
        
        print(f"\n📝 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Save results to file
        self._save_test_results()
    
    def _save_test_results(self):
        """Save test results to file."""
        
        try:
            # Create results directory
            os.makedirs("test_results", exist_ok=True)
            
            # Save detailed results
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"test_results/integration_test_{timestamp}.json"
            
            results_data = {
                "test_run": {
                    "timestamp": datetime.now().isoformat(),
                    "total_tests": len(self.test_results),
                    "passed": self.tests_passed,
                    "failed": self.tests_failed,
                    "skipped": self.tests_skipped
                },
                "environment": {
                    "openai_configured": bool(os.getenv('OPENAI_API_KEY')),
                    "exa_configured": bool(os.getenv('EXA_API_KEY')),
                    "jira_configured": bool(os.getenv('JIRA_URL')),
                    "python_version": sys.version
                },
                "results": [
                    {
                        **result,
                        "timestamp": result["timestamp"].isoformat()
                    } for result in self.test_results
                ]
            }
            
            with open(filename, 'w') as f:
                json.dump(results_data, f, indent=2)
            
            print(f"📁 Test results saved to: {filename}")
            
        except Exception as e:
            print(f"⚠️ Failed to save test results: {e}")


async def main():
    """Run the integration test suite."""
    
    print("🎯 MARGO AGENT - ADVANCED WORKFLOW INTEGRATION TEST")
    print("=" * 60)
    print("This test validates all components of the advanced workflow system")
    print("=" * 60)
    
    test_suite = AdvancedWorkflowIntegrationTest()
    await test_suite.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
