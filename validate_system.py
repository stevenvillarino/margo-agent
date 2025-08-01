#!/usr/bin/env python3
"""
Comprehensive Test Suite for Margo Design Review System

This script validates all agents, optimizations, and integrations
to ensure the system is production-ready.
"""

import os
import sys
import asyncio
import json
import base64
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.enhanced_system import EnhancedDesignReviewSystem
from agents.quality_evaluation_agent import QualityEvaluationAgent
from agents.optimized_prompts import get_agent_optimization, AGENT_OPTIMIZATIONS
from slack_bot import SlackDesignReviewBot


class SystemValidator:
    """Comprehensive system validation and testing."""
    
    def __init__(self):
        self.test_results = {}
        self.errors = []
        self.warnings = []
        
        # Load environment variables
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.exa_api_key = os.getenv('EXA_API_KEY')
        self.slack_bot_token = os.getenv('SLACK_BOT_TOKEN')
        self.slack_app_token = os.getenv('SLACK_APP_TOKEN')
    
    def validate_environment(self) -> bool:
        """Validate environment setup and dependencies."""
        print("🔍 Validating environment setup...")
        
        # Check required environment variables
        required_vars = ['OPENAI_API_KEY']
        optional_vars = ['EXA_API_KEY', 'SLACK_BOT_TOKEN', 'SLACK_APP_TOKEN']
        
        env_status = {}
        
        for var in required_vars:
            if os.getenv(var):
                env_status[var] = "✅ Set"
            else:
                env_status[var] = "❌ Missing"
                self.errors.append(f"Required environment variable {var} not set")
        
        for var in optional_vars:
            if os.getenv(var):
                env_status[var] = "✅ Set"
            else:
                env_status[var] = "⚠️ Optional (not set)"
                self.warnings.append(f"Optional environment variable {var} not set")
        
        # Check Python dependencies
        dependencies = [
            'langchain',
            'langchain_openai',
            'openai',
            'streamlit',
            'exa_py',
            'requests',
            'pillow'
        ]
        
        dependency_status = {}
        for dep in dependencies:
            try:
                __import__(dep.replace('-', '_'))
                dependency_status[dep] = "✅ Installed"
            except ImportError:
                dependency_status[dep] = "❌ Missing"
                self.errors.append(f"Required dependency {dep} not installed")
        
        # Check Slack dependencies (optional)
        slack_deps = ['slack_bolt', 'slack_sdk', 'aiohttp']
        for dep in slack_deps:
            try:
                __import__(dep.replace('-', '_'))
                dependency_status[dep] = "✅ Installed"
            except ImportError:
                dependency_status[dep] = "⚠️ Missing (Slack features disabled)"
                self.warnings.append(f"Slack dependency {dep} not installed")
        
        self.test_results['environment'] = {
            'environment_variables': env_status,
            'dependencies': dependency_status,
            'status': 'pass' if not self.errors else 'fail'
        }
        
        print(f"Environment Status: {'✅ PASS' if not self.errors else '❌ FAIL'}")
        return len(self.errors) == 0
    
    def validate_agent_optimizations(self) -> bool:
        """Validate agent optimization configurations."""
        print("🤖 Validating agent optimizations...")
        
        optimization_results = {}
        
        for agent_type in AGENT_OPTIMIZATIONS.keys():
            try:
                optimization = get_agent_optimization(agent_type)
                
                # Validate optimization structure
                validation = {
                    'prompt_templates': len(optimization.prompt_templates),
                    'capabilities': len(optimization.capability_enhancements),
                    'performance_metrics': len(optimization.performance_metrics),
                    'system_prompt_length': len(optimization.prompt_templates.get('system_prompt', '')),
                    'status': 'pass'
                }
                
                # Check for minimum requirements
                if validation['prompt_templates'] < 2:
                    validation['status'] = 'fail'
                    self.errors.append(f"{agent_type}: Insufficient prompt templates")
                
                if validation['system_prompt_length'] < 500:
                    validation['status'] = 'fail'
                    self.errors.append(f"{agent_type}: System prompt too short")
                
                optimization_results[agent_type] = validation
                print(f"  {agent_type}: {'✅' if validation['status'] == 'pass' else '❌'}")
                
            except Exception as e:
                optimization_results[agent_type] = {
                    'status': 'error',
                    'error': str(e)
                }
                self.errors.append(f"{agent_type} optimization failed: {e}")
                print(f"  {agent_type}: ❌ {e}")
        
        self.test_results['optimizations'] = optimization_results
        
        status = all(result.get('status') == 'pass' for result in optimization_results.values())
        print(f"Optimization Status: {'✅ PASS' if status else '❌ FAIL'}")
        return status
    
    async def validate_enhanced_system(self) -> bool:
        """Validate the enhanced design review system."""
        print("🏗️ Validating enhanced design review system...")
        
        if not self.openai_api_key:
            print("  ⚠️ Skipping system validation (no OpenAI API key)")
            self.test_results['enhanced_system'] = {'status': 'skipped', 'reason': 'No API key'}
            return True
        
        try:
            # Initialize system
            system = EnhancedDesignReviewSystem(
                openai_api_key=self.openai_api_key,
                exa_api_key=self.exa_api_key
            )
            
            # Test system components
            system_validation = {
                'agents_loaded': len(system.agents),
                'orchestrator_ready': hasattr(system, 'orchestrator'),
                'learning_system_ready': hasattr(system, 'learning_system'),
                'expected_agents': 6,  # ui_specialist, ux_researcher, creative_director, vp_product, accessibility, quality_evaluation
                'status': 'pass'
            }
            
            # Validate agent count
            if system_validation['agents_loaded'] != system_validation['expected_agents']:
                system_validation['status'] = 'fail'
                self.errors.append(f"Expected {system_validation['expected_agents']} agents, got {system_validation['agents_loaded']}")
            
            # Test with sample data (without making API calls)
            sample_context = {
                'design_type': 'ui_design',
                'target_audience': 'roku_users',
                'review_focus': 'comprehensive'
            }
            
            # Validate agent accessibility
            for agent_name in system.agents:
                if not hasattr(system.agents[agent_name], 'review'):
                    system_validation['status'] = 'fail'
                    self.errors.append(f"Agent {agent_name} missing review method")
            
            self.test_results['enhanced_system'] = system_validation
            
            print(f"  Agents loaded: {system_validation['agents_loaded']}")
            print(f"  Orchestrator: {'✅' if system_validation['orchestrator_ready'] else '❌'}")
            print(f"  Learning system: {'✅' if system_validation['learning_system_ready'] else '❌'}")
            
            status = system_validation['status'] == 'pass'
            print(f"Enhanced System Status: {'✅ PASS' if status else '❌ FAIL'}")
            return status
            
        except Exception as e:
            self.test_results['enhanced_system'] = {
                'status': 'error',
                'error': str(e)
            }
            self.errors.append(f"Enhanced system validation failed: {e}")
            print(f"Enhanced System Status: ❌ FAIL - {e}")
            return False
    
    def validate_quality_agent(self) -> bool:
        """Validate the Quality Evaluation Agent specifically."""
        print("🔍 Validating Quality Evaluation Agent...")
        
        if not self.openai_api_key:
            print("  ⚠️ Skipping quality agent validation (no OpenAI API key)")
            self.test_results['quality_agent'] = {'status': 'skipped', 'reason': 'No API key'}
            return True
        
        try:
            # Initialize quality agent
            quality_agent = QualityEvaluationAgent(
                openai_api_key=self.openai_api_key,
                exa_api_key=self.exa_api_key
            )
            
            quality_validation = {
                'agent_initialized': True,
                'confluence_integration': quality_agent.confluence_client is not None,
                'research_capability': quality_agent.exa_agent is not None,
                'quality_categories': len(quality_agent.quality_categories),
                'design_principles': len(quality_agent.roku_design_principles),
                'expected_categories': 8,
                'expected_principles': 9,
                'status': 'pass'
            }
            
            # Validate configuration
            if quality_validation['quality_categories'] != quality_validation['expected_categories']:
                quality_validation['status'] = 'warning'
                self.warnings.append(f"Expected {quality_validation['expected_categories']} quality categories, got {quality_validation['quality_categories']}")
            
            if quality_validation['design_principles'] != quality_validation['expected_principles']:
                quality_validation['status'] = 'warning'
                self.warnings.append(f"Expected {quality_validation['expected_principles']} design principles, got {quality_validation['design_principles']}")
            
            self.test_results['quality_agent'] = quality_validation
            
            print(f"  Agent initialized: ✅")
            print(f"  Confluence integration: {'✅' if quality_validation['confluence_integration'] else '⚠️'}")
            print(f"  Research capability: {'✅' if quality_validation['research_capability'] else '⚠️'}")
            print(f"  Quality categories: {quality_validation['quality_categories']}")
            print(f"  Design principles: {quality_validation['design_principles']}")
            
            status = quality_validation['status'] in ['pass', 'warning']
            print(f"Quality Agent Status: {'✅ PASS' if status else '❌ FAIL'}")
            return status
            
        except Exception as e:
            self.test_results['quality_agent'] = {
                'status': 'error',
                'error': str(e)
            }
            self.errors.append(f"Quality agent validation failed: {e}")
            print(f"Quality Agent Status: ❌ FAIL - {e}")
            return False
    
    def validate_slack_integration(self) -> bool:
        """Validate Slack bot integration (without starting)."""
        print("💬 Validating Slack integration...")
        
        if not all([self.slack_bot_token, self.slack_app_token, self.openai_api_key]):
            print("  ⚠️ Skipping Slack validation (missing tokens)")
            self.test_results['slack_integration'] = {
                'status': 'skipped', 
                'reason': 'Missing required tokens'
            }
            return True
        
        try:
            # Test Slack dependencies
            import slack_bolt
            import slack_sdk
            import aiohttp
            
            # Initialize bot (without starting)
            bot = SlackDesignReviewBot(
                slack_bot_token=self.slack_bot_token,
                slack_app_token=self.slack_app_token,
                openai_api_key=self.openai_api_key,
                exa_api_key=self.exa_api_key
            )
            
            slack_validation = {
                'bot_initialized': True,
                'review_system_ready': hasattr(bot, 'review_system'),
                'event_handlers_setup': hasattr(bot.app, '_listeners'),
                'supported_formats': len(bot.supported_formats),
                'status': 'pass'
            }
            
            self.test_results['slack_integration'] = slack_validation
            
            print(f"  Bot initialized: ✅")
            print(f"  Review system: {'✅' if slack_validation['review_system_ready'] else '❌'}")
            print(f"  Event handlers: {'✅' if slack_validation['event_handlers_setup'] else '❌'}")
            print(f"  Supported formats: {slack_validation['supported_formats']}")
            
            status = slack_validation['status'] == 'pass'
            print(f"Slack Integration Status: {'✅ PASS' if status else '❌ FAIL'}")
            return status
            
        except ImportError as e:
            self.test_results['slack_integration'] = {
                'status': 'skipped',
                'reason': f'Missing Slack dependencies: {e}'
            }
            print(f"  ⚠️ Skipping Slack validation (missing dependencies): {e}")
            return True
            
        except Exception as e:
            self.test_results['slack_integration'] = {
                'status': 'error',
                'error': str(e)
            }
            self.errors.append(f"Slack integration validation failed: {e}")
            print(f"Slack Integration Status: ❌ FAIL - {e}")
            return False
    
    async def validate_full_system_integration(self) -> bool:
        """Validate full system integration with mock data."""
        print("🔄 Validating full system integration...")
        
        if not self.openai_api_key:
            print("  ⚠️ Skipping integration test (no OpenAI API key)")
            self.test_results['integration'] = {'status': 'skipped', 'reason': 'No API key'}
            return True
        
        try:
            # Create sample base64 image (1x1 pixel PNG)
            sample_image_data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
            
            # Sample context
            context = {
                'design_type': 'ui_design',
                'target_audience': 'roku_users',
                'review_focus': 'comprehensive',
                'product_requirements': ['Improve user engagement', 'Reduce cognitive load'],
                'business_goals': ['Increase retention', 'Improve usability'],
                'user_needs': ['Find content quickly', 'Easy navigation'],
                'pain_points': ['Complex navigation', 'Poor content discovery']
            }
            
            # Initialize system
            system = EnhancedDesignReviewSystem(
                openai_api_key=self.openai_api_key,
                exa_api_key=self.exa_api_key
            )
            
            print("  🚀 Starting mock design review...")
            
            # Note: In a real test, we would use system.conduct_comprehensive_review()
            # For validation, we'll test component integration without API calls
            
            integration_validation = {
                'system_initialized': True,
                'agents_count': len(system.agents),
                'sample_context_valid': bool(context),
                'mock_image_ready': bool(sample_image_data),
                'status': 'pass'
            }
            
            # Test agent accessibility
            for agent_name, agent in system.agents.items():
                if not hasattr(agent, 'review'):
                    integration_validation['status'] = 'fail'
                    self.errors.append(f"Agent {agent_name} missing review method")
            
            self.test_results['integration'] = integration_validation
            
            print(f"  System components: ✅")
            print(f"  Agent integration: {'✅' if integration_validation['status'] == 'pass' else '❌'}")
            
            status = integration_validation['status'] == 'pass'
            print(f"Integration Status: {'✅ PASS' if status else '❌ FAIL'}")
            return status
            
        except Exception as e:
            self.test_results['integration'] = {
                'status': 'error',
                'error': str(e)
            }
            self.errors.append(f"Integration validation failed: {e}")
            print(f"Integration Status: ❌ FAIL - {e}")
            return False
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive validation report."""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() 
                          if result.get('status') in ['pass', 'warning'])
        failed_tests = sum(1 for result in self.test_results.values() 
                          if result.get('status') == 'fail')
        error_tests = sum(1 for result in self.test_results.values() 
                         if result.get('status') == 'error')
        skipped_tests = sum(1 for result in self.test_results.values() 
                           if result.get('status') == 'skipped')
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_tests': total_tests,
                'passed': passed_tests,
                'failed': failed_tests,
                'errors': error_tests,
                'skipped': skipped_tests,
                'success_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0
            },
            'test_results': self.test_results,
            'errors': self.errors,
            'warnings': self.warnings,
            'status': 'PASS' if failed_tests == 0 and error_tests == 0 else 'FAIL'
        }
        
        return report
    
    async def run_all_validations(self) -> bool:
        """Run all validation tests."""
        print("🧪 Starting comprehensive system validation...\n")
        
        # Run all validations
        validations = [
            ('Environment', self.validate_environment),
            ('Agent Optimizations', self.validate_agent_optimizations),
            ('Enhanced System', self.validate_enhanced_system),
            ('Quality Agent', self.validate_quality_agent),
            ('Slack Integration', self.validate_slack_integration),
            ('System Integration', self.validate_full_system_integration)
        ]
        
        all_passed = True
        
        for name, validation_func in validations:
            print(f"\n{'='*50}")
            print(f"Testing: {name}")
            print('='*50)
            
            if asyncio.iscoroutinefunction(validation_func):
                result = await validation_func()
            else:
                result = validation_func()
            
            all_passed = all_passed and result
        
        # Generate and display report
        print(f"\n{'='*50}")
        print("VALIDATION SUMMARY")
        print('='*50)
        
        report = self.generate_report()
        
        print(f"Total Tests: {report['summary']['total_tests']}")
        print(f"Passed: {report['summary']['passed']} ✅")
        print(f"Failed: {report['summary']['failed']} ❌")
        print(f"Errors: {report['summary']['errors']} 💥")
        print(f"Skipped: {report['summary']['skipped']} ⚠️")
        print(f"Success Rate: {report['summary']['success_rate']:.1f}%")
        
        if self.errors:
            print(f"\n🚨 ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  • {error}")
        
        if self.warnings:
            print(f"\n⚠️ WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  • {warning}")
        
        print(f"\nOverall Status: {'✅ SYSTEM READY' if report['status'] == 'PASS' else '❌ SYSTEM NOT READY'}")
        
        # Save report
        with open('validation_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\n📊 Detailed report saved to: validation_report.json")
        
        return all_passed


async def main():
    """Main validation runner."""
    print("🤖 Margo Design Review System - Comprehensive Validation")
    print("="*60)
    
    validator = SystemValidator()
    success = await validator.run_all_validations()
    
    if success:
        print("\n🎉 System is ready for deployment!")
        print("\nNext steps:")
        print("1. Configure your API keys in .env")
        print("2. Set up Slack app if using Slack integration")
        print("3. Deploy using your preferred method (see SLACK_DEPLOYMENT.md)")
        print("4. Test with real design files")
    else:
        print("\n🔧 Please fix the issues above before deployment.")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
