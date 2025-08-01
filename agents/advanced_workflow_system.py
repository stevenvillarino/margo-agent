"""
Advanced Workflow Automation System

This is the complete integration of all workflow automation features including:
- Multi-agent design review with Margo gate-keeping
- Knowledge gap detection and escalation  
- JIRA integration for issue tracking
- QA validation with Playwright
- Research study automation
- Inter-agent communication
- EXA web research integration

This system serves as the central orchestrator for the entire design workflow.
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
import uuid

# Import all the components we've built
from agents.workflow_orchestrator import WorkflowOrchestrator, WorkflowType, Priority, WorkflowStatus
from agents.jira_integration import JIRAIntegration, create_jira_integration
from agents.playwright_validator import PlaywrightQAValidator, create_playwright_validator
from agents.agent_communication import AgentCommunicationHub, create_communication_hub, MessageType, AgentCapability
from agents.enhanced_system import EnhancedDesignReviewSystem
from agents.exa_search import ExaSearchAgent


@dataclass
class AdvancedWorkflowConfig:
    """Configuration for the advanced workflow system."""
    openai_api_key: str
    exa_api_key: Optional[str] = None
    jira_url: Optional[str] = None
    jira_username: Optional[str] = None
    jira_api_token: Optional[str] = None
    jira_project_key: str = "DESIGN"
    playwright_enabled: bool = True
    playwright_browser: str = "chromium"
    screenshots_dir: str = "screenshots"
    notifications_enabled: bool = True
    slack_webhook_url: Optional[str] = None
    margo_threshold_config: Dict[str, Any] = None


class AdvancedWorkflowSystem:
    """
    Complete advanced workflow automation system for design reviews.
    """
    
    def __init__(self, config: AdvancedWorkflowConfig):
        """
        Initialize the advanced workflow system.
        
        Args:
            config: System configuration
        """
        self.config = config
        
        # Initialize core components
        self.workflow_orchestrator = WorkflowOrchestrator(
            openai_api_key=config.openai_api_key,
            exa_api_key=config.exa_api_key,
            jira_config={
                "url": config.jira_url,
                "username": config.jira_username,
                "api_token": config.jira_api_token
            } if config.jira_url else None,
            playwright_config={
                "browser": config.playwright_browser,
                "headless": True,
                "viewport": {"width": 1920, "height": 1080}
            } if config.playwright_enabled else None
        )
        
        # Initialize enhanced design review system
        self.design_system = EnhancedDesignReviewSystem(
            openai_api_key=config.openai_api_key,
            exa_api_key=config.exa_api_key,
            learning_enabled=True
        )
        
        # Initialize JIRA integration
        self.jira = create_jira_integration(
            jira_url=config.jira_url,
            username=config.jira_username,
            api_token=config.jira_api_token,
            project_key=config.jira_project_key
        ) if config.jira_url else None
        
        # Initialize Playwright validator
        self.playwright_validator = create_playwright_validator(
            headless=True,
            browser_type=config.playwright_browser,
            screenshots_dir=config.screenshots_dir
        ) if config.playwright_enabled else None
        
        # Initialize communication hub
        self.communication_hub = create_communication_hub()
        
        # Initialize EXA search
        self.exa_agent = ExaSearchAgent(config.exa_api_key) if config.exa_api_key else None
        
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Initialize agent registry
        self._register_all_agents()
        
        # Workflow tracking
        self.active_workflows: Dict[str, Dict[str, Any]] = {}
        self.completed_workflows: List[Dict[str, Any]] = []
        
        print("🚀 Advanced Workflow System initialized")
        print(f"🤖 JIRA integration: {'✅' if self.jira else '❌'}")
        print(f"🧪 Playwright validation: {'✅' if self.playwright_validator else '❌'}")
        print(f"🔍 EXA research: {'✅' if self.exa_agent else '❌'}")
        print(f"💬 Agent communication: {'✅'}")
        print(f"🎯 Total agents: {len(self.communication_hub.agent_capabilities)}")
    
    def _register_all_agents(self):
        """Register all agents with the communication hub."""
        
        # Register core design review agents
        agents_to_register = [
            {
                "agent_id": "ui_specialist",
                "capability": AgentCapability(
                    agent_id="ui_specialist",
                    agent_name="UI Design Specialist",
                    agent_type="peer_reviewer",
                    expertise_areas=["ui_design", "visual_design", "design_systems", "interaction_design"],
                    available_methods=["review", "critique", "recommend", "collaborate"],
                    current_load=0,
                    response_time_avg=60.0,
                    reliability_score=0.9
                )
            },
            {
                "agent_id": "ux_researcher",
                "capability": AgentCapability(
                    agent_id="ux_researcher",
                    agent_name="UX Researcher",
                    agent_type="peer_reviewer",
                    expertise_areas=["user_research", "usability", "user_testing", "behavioral_analysis"],
                    available_methods=["research", "analyze", "test", "recommend"],
                    current_load=0,
                    response_time_avg=120.0,
                    reliability_score=0.95
                )
            },
            {
                "agent_id": "creative_director",
                "capability": AgentCapability(
                    agent_id="creative_director",
                    agent_name="Creative Director",
                    agent_type="peer_reviewer",
                    expertise_areas=["creative_direction", "brand_alignment", "innovation", "visual_strategy"],
                    available_methods=["strategic_review", "brand_audit", "innovation_assessment"],
                    current_load=0,
                    response_time_avg=90.0,
                    reliability_score=0.88
                )
            },
            {
                "agent_id": "vp_product",
                "capability": AgentCapability(
                    agent_id="vp_product",
                    agent_name="VP of Product",
                    agent_type="strategic_reviewer",
                    expertise_areas=["product_strategy", "business_alignment", "market_analysis", "roi_analysis"],
                    available_methods=["strategic_assessment", "business_validation", "market_analysis"],
                    current_load=0,
                    response_time_avg=180.0,
                    reliability_score=0.92
                )
            },
            {
                "agent_id": "accessibility_expert",
                "capability": AgentCapability(
                    agent_id="accessibility_expert",
                    agent_name="Accessibility Expert",
                    agent_type="specialist_reviewer",
                    expertise_areas=["accessibility", "wcag_compliance", "inclusive_design", "assistive_technology"],
                    available_methods=["accessibility_audit", "wcag_validation", "inclusion_assessment"],
                    current_load=0,
                    response_time_avg=75.0,
                    reliability_score=0.96
                )
            },
            {
                "agent_id": "quality_evaluator",
                "capability": AgentCapability(
                    agent_id="quality_evaluator",
                    agent_name="Quality Evaluation Agent",
                    agent_type="quality_assurance",
                    expertise_areas=["quality_assurance", "feature_validation", "cross_reference", "compliance"],
                    available_methods=["feature_validation", "cross_reference", "compliance_check"],
                    current_load=0,
                    response_time_avg=100.0,
                    reliability_score=0.93
                )
            },
            {
                "agent_id": "margo_agent",
                "capability": AgentCapability(
                    agent_id="margo_agent",
                    agent_name="Margo Senior Review Agent",
                    agent_type="senior_gatekeeper",
                    expertise_areas=["strategic_oversight", "senior_review", "final_approval", "complex_decisions"],
                    available_methods=["comprehensive_review", "final_assessment", "strategic_guidance"],
                    current_load=0,
                    response_time_avg=300.0,
                    reliability_score=0.98
                )
            },
            {
                "agent_id": "web_researcher",
                "capability": AgentCapability(
                    agent_id="web_researcher",
                    agent_name="Web Research Agent",
                    agent_type="research_specialist",
                    expertise_areas=["web_research", "industry_analysis", "best_practices", "trend_analysis"],
                    available_methods=["web_search", "trend_analysis", "best_practice_research"],
                    current_load=0,
                    response_time_avg=45.0,
                    reliability_score=0.85
                )
            }
        ]
        
        # Register all agents
        for agent_info in agents_to_register:
            self.communication_hub.register_agent(
                agent_id=agent_info["agent_id"],
                capability=agent_info["capability"]
            )
        
        self.logger.info(f"Registered {len(agents_to_register)} agents with communication hub")
    
    async def process_complete_design_workflow(self, 
                                             submission: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a complete design workflow from submission to completion.
        
        Args:
            submission: Design submission with all relevant data
            
        Returns:
            Complete workflow results
        """
        
        workflow_id = f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:4]}"
        
        self.logger.info(f"🚀 Starting complete design workflow: {workflow_id}")
        
        # Track workflow
        self.active_workflows[workflow_id] = {
            "workflow_id": workflow_id,
            "submission": submission,
            "status": "processing",
            "started_at": datetime.now(),
            "phases": {},
            "results": {},
            "notifications": []
        }
        
        try:
            # Phase 1: Designer Pre-Check and Research Validation
            self.logger.info(f"📋 Phase 1: Pre-check and research validation")
            precheck_result = await self._phase_1_precheck_and_research(submission, workflow_id)
            self.active_workflows[workflow_id]["phases"]["precheck"] = precheck_result
            
            # Phase 2: Multi-Agent Design Review
            self.logger.info(f"🤖 Phase 2: Multi-agent design review")
            design_review_result = await self._phase_2_design_review(submission, precheck_result, workflow_id)
            self.active_workflows[workflow_id]["phases"]["design_review"] = design_review_result
            
            # Phase 3: Knowledge Gap Resolution
            self.logger.info(f"🧠 Phase 3: Knowledge gap resolution")
            knowledge_gap_result = await self._phase_3_knowledge_gaps(design_review_result, workflow_id)
            self.active_workflows[workflow_id]["phases"]["knowledge_gaps"] = knowledge_gap_result
            
            # Phase 4: Issue Detection and JIRA Creation
            self.logger.info(f"🎫 Phase 4: Issue tracking and JIRA creation")
            issue_tracking_result = await self._phase_4_issue_tracking(design_review_result, workflow_id)
            self.active_workflows[workflow_id]["phases"]["issue_tracking"] = issue_tracking_result
            
            # Phase 5: Margo Gate Decision
            self.logger.info(f"🛡️ Phase 5: Margo gate decision")
            margo_decision = await self._phase_5_margo_gate(design_review_result, workflow_id)
            self.active_workflows[workflow_id]["phases"]["margo_gate"] = margo_decision
            
            # Phase 6: QA Validation (if QA link provided)
            qa_validation_result = None
            if submission.get("qa_link"):
                self.logger.info(f"🧪 Phase 6: QA validation")
                qa_validation_result = await self._phase_6_qa_validation(submission, workflow_id)
                self.active_workflows[workflow_id]["phases"]["qa_validation"] = qa_validation_result
            
            # Phase 7: Final Notifications and Next Steps
            self.logger.info(f"📢 Phase 7: Final notifications")
            notification_result = await self._phase_7_notifications(workflow_id)
            self.active_workflows[workflow_id]["phases"]["notifications"] = notification_result
            
            # Compile final results
            final_result = self._compile_final_workflow_result(workflow_id)
            
            # Move to completed workflows
            self.completed_workflows.append(self.active_workflows[workflow_id])
            del self.active_workflows[workflow_id]
            
            self.logger.info(f"✅ Workflow completed: {workflow_id}")
            
            return final_result
            
        except Exception as e:
            self.logger.error(f"❌ Workflow failed: {workflow_id} - {e}")
            self.active_workflows[workflow_id]["status"] = "failed"
            self.active_workflows[workflow_id]["error"] = str(e)
            
            return {
                "workflow_id": workflow_id,
                "status": "failed",
                "error": str(e),
                "partial_results": self.active_workflows[workflow_id].get("phases", {})
            }
    
    async def _phase_1_precheck_and_research(self, 
                                           submission: Dict[str, Any],
                                           workflow_id: str) -> Dict[str, Any]:
        """Phase 1: Designer pre-check and research validation."""
        
        # Check if feature guide is provided
        feature_guide_status = "provided" if submission.get("feature_guide") else "missing"
        
        # Check research history using EXA
        research_status = await self._check_research_history(submission)
        
        # If no research and high-impact feature, create research study
        research_study = None
        if research_status["needs_research"] and submission.get("impact_level", "medium") == "high":
            research_study = await self._create_research_study(submission, workflow_id)
            
            # Create JIRA ticket for research
            if self.jira:
                research_ticket = self.jira.create_research_request_issue(
                    research_type=research_study["type"],
                    objectives=research_study["objectives"],
                    target_users=research_study["target_users"],
                    timeline=research_study["timeline"],
                    deliverables=research_study["deliverables"],
                    workflow_id=workflow_id
                )
                research_study["jira_ticket"] = research_ticket
        
        # Designer guidance based on readiness
        designer_guidance = self._generate_designer_guidance(feature_guide_status, research_status)
        
        return {
            "feature_guide_status": feature_guide_status,
            "research_status": research_status,
            "research_study": research_study,
            "designer_guidance": designer_guidance,
            "ready_for_review": feature_guide_status == "provided" and not research_status["needs_research"]
        }
    
    async def _phase_2_design_review(self, 
                                   submission: Dict[str, Any],
                                   precheck_result: Dict[str, Any],
                                   workflow_id: str) -> Dict[str, Any]:
        """Phase 2: Multi-agent design review."""
        
        # Conduct comprehensive review using enhanced system
        review_result = await self.design_system.conduct_comprehensive_review(
            image_data=submission.get("image_data"),
            design_type=submission.get("design_type", "ui_design"),
            context={
                "workflow_id": workflow_id,
                "precheck_result": precheck_result,
                "submission_context": submission.get("context", {})
            }
        )
        
        # Analyze for critical issues
        critical_issues = self._extract_critical_issues(review_result)
        
        # Calculate consensus score
        consensus_score = self._calculate_agent_consensus(review_result)
        
        return {
            "review_result": review_result,
            "critical_issues": critical_issues,
            "consensus_score": consensus_score,
            "agent_count": len(review_result.phase_results) if hasattr(review_result, 'phase_results') else 0,
            "overall_score": getattr(review_result, 'overall_score', 0)
        }
    
    async def _phase_3_knowledge_gaps(self, 
                                    design_review_result: Dict[str, Any],
                                    workflow_id: str) -> Dict[str, Any]:
        """Phase 3: Knowledge gap detection and resolution."""
        
        gaps_detected = []
        gap_resolutions = []
        
        # Extract knowledge gaps from review
        review_result = design_review_result["review_result"]
        if hasattr(review_result, 'phase_results'):
            for phase, results in review_result.phase_results.items():
                for result in results:
                    gaps = self._detect_agent_knowledge_gaps(result)
                    gaps_detected.extend(gaps)
        
        # For each gap, request knowledge from appropriate agents
        for gap in gaps_detected:
            try:
                # Request knowledge through communication hub
                request_id = await self.communication_hub.request_knowledge(
                    requester=gap["source_agent"],
                    topic=gap["topic"],
                    specific_question=gap["question"],
                    context={"workflow_id": workflow_id, "gap_details": gap},
                    urgency=Priority.MEDIUM
                )
                
                gap_resolutions.append({
                    "gap": gap,
                    "request_id": request_id,
                    "status": "requested"
                })
                
            except Exception as e:
                self.logger.warning(f"Failed to request knowledge for gap: {e}")
                gap_resolutions.append({
                    "gap": gap,
                    "status": "failed",
                    "error": str(e)
                })
        
        return {
            "gaps_detected": gaps_detected,
            "gap_resolutions": gap_resolutions,
            "total_gaps": len(gaps_detected),
            "resolution_rate": len([r for r in gap_resolutions if r["status"] == "requested"]) / max(1, len(gaps_detected))
        }
    
    async def _phase_4_issue_tracking(self, 
                                    design_review_result: Dict[str, Any],
                                    workflow_id: str) -> Dict[str, Any]:
        """Phase 4: Issue detection and JIRA ticket creation."""
        
        if not self.jira:
            return {"status": "skipped", "reason": "JIRA not configured"}
        
        created_tickets = []
        
        # Extract issues from review results
        critical_issues = design_review_result.get("critical_issues", [])
        
        # Create JIRA tickets for critical issues
        for issue in critical_issues:
            try:
                ticket_id = self.jira.create_design_issue(
                    title=issue.get("title", "Design Issue"),
                    description=issue.get("description", ""),
                    issue_type="Task",
                    priority=issue.get("severity", "Medium"),
                    labels=["design-review", "automated", f"workflow-{workflow_id}"],
                    workflow_id=workflow_id
                )
                
                created_tickets.append({
                    "ticket_id": ticket_id,
                    "issue": issue,
                    "status": "created"
                })
                
            except Exception as e:
                self.logger.error(f"Failed to create JIRA ticket: {e}")
                created_tickets.append({
                    "issue": issue,
                    "status": "failed",
                    "error": str(e)
                })
        
        # Create accessibility tickets if needed
        review_result = design_review_result["review_result"]
        accessibility_issues = self._extract_accessibility_issues(review_result)
        
        for a11y_issue in accessibility_issues:
            try:
                ticket_id = self.jira.create_accessibility_issue(
                    violation_type=a11y_issue["type"],
                    wcag_guideline=a11y_issue["guideline"],
                    description=a11y_issue["description"],
                    severity=a11y_issue["severity"],
                    workflow_id=workflow_id
                )
                
                created_tickets.append({
                    "ticket_id": ticket_id,
                    "issue": a11y_issue,
                    "type": "accessibility",
                    "status": "created"
                })
                
            except Exception as e:
                self.logger.error(f"Failed to create accessibility ticket: {e}")
        
        return {
            "tickets_created": len(created_tickets),
            "tickets": created_tickets,
            "issues_tracked": len(critical_issues) + len(accessibility_issues)
        }
    
    async def _phase_5_margo_gate(self, 
                                design_review_result: Dict[str, Any],
                                workflow_id: str) -> Dict[str, Any]:
        """Phase 5: Margo gate decision process."""
        
        # Evaluate against Margo thresholds
        overall_score = design_review_result.get("overall_score", 0)
        consensus_score = design_review_result.get("consensus_score", 0)
        critical_issues_count = len(design_review_result.get("critical_issues", []))
        
        # Default thresholds (can be configured)
        margo_thresholds = self.config.margo_threshold_config or {
            "min_overall_score": 7.0,
            "min_consensus_score": 0.8,
            "max_critical_issues": 2
        }
        
        # Decision logic
        requires_margo = (
            overall_score < margo_thresholds["min_overall_score"] or
            consensus_score < margo_thresholds["min_consensus_score"] or
            critical_issues_count > margo_thresholds["max_critical_issues"]
        )
        
        if requires_margo:
            # Escalate to Margo agent through communication hub
            escalation_id = await self.communication_hub.escalate_issue(
                escalator="workflow_orchestrator",
                issue={
                    "title": "Design requires senior review",
                    "type": "strategic_review",
                    "severity": "high",
                    "details": {
                        "overall_score": overall_score,
                        "consensus_score": consensus_score,
                        "critical_issues": critical_issues_count,
                        "review_summary": "Complex design requiring senior strategic oversight"
                    }
                },
                escalation_reason="Failed to meet automated review thresholds",
                suggested_actions=[
                    "Conduct comprehensive strategic review",
                    "Assess business alignment and risk",
                    "Provide implementation guidance"
                ],
                workflow_id=workflow_id
            )
            
            margo_status = "escalated"
            margo_action = "Senior review required - meeting recommended"
        else:
            margo_status = "approved"
            margo_action = "Design approved for implementation"
            escalation_id = None
        
        return {
            "requires_margo": requires_margo,
            "margo_status": margo_status,
            "margo_action": margo_action,
            "escalation_id": escalation_id,
            "threshold_analysis": {
                "overall_score": {"value": overall_score, "threshold": margo_thresholds["min_overall_score"], "passed": overall_score >= margo_thresholds["min_overall_score"]},
                "consensus_score": {"value": consensus_score, "threshold": margo_thresholds["min_consensus_score"], "passed": consensus_score >= margo_thresholds["min_consensus_score"]},
                "critical_issues": {"value": critical_issues_count, "threshold": margo_thresholds["max_critical_issues"], "passed": critical_issues_count <= margo_thresholds["max_critical_issues"]}
            }
        }
    
    async def _phase_6_qa_validation(self, 
                                   submission: Dict[str, Any],
                                   workflow_id: str) -> Dict[str, Any]:
        """Phase 6: QA validation using Playwright."""
        
        if not self.playwright_validator:
            return {"status": "skipped", "reason": "Playwright not configured"}
        
        qa_link = submission.get("qa_link")
        design_spec_url = submission.get("design_spec_url", "")
        
        # Prepare design specification for validation
        design_spec = {
            "spec_url": design_spec_url,
            "elements": submission.get("expected_elements", [])
        }
        
        try:
            # Run Playwright validation
            validation_result = await self.playwright_validator.validate_qa_against_design(
                qa_url=qa_link,
                design_spec=design_spec,
                validation_config={"include_mobile": True}
            )
            
            # Create JIRA tickets for discrepancies
            discrepancy_tickets = []
            if self.jira and validation_result.visual_discrepancies:
                for discrepancy in validation_result.visual_discrepancies:
                    if discrepancy.severity in ["high", "critical"]:
                        ticket_id = self.jira.create_qa_discrepancy_issue(
                            element_name=discrepancy.element_name,
                            expected_behavior=f"{discrepancy.expected_property}: {discrepancy.expected_value}",
                            actual_behavior=f"{discrepancy.expected_property}: {discrepancy.actual_value}",
                            qa_url=qa_link,
                            design_spec_url=design_spec_url,
                            severity=discrepancy.severity,
                            workflow_id=workflow_id
                        )
                        discrepancy_tickets.append(ticket_id)
            
            return {
                "validation_result": validation_result,
                "discrepancy_tickets": discrepancy_tickets,
                "status": "completed",
                "overall_score": validation_result.overall_score,
                "discrepancies_found": len(validation_result.visual_discrepancies),
                "accessibility_issues": len(validation_result.accessibility_issues)
            }
            
        except Exception as e:
            self.logger.error(f"QA validation failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    async def _phase_7_notifications(self, workflow_id: str) -> Dict[str, Any]:
        """Phase 7: Final notifications and stakeholder communication."""
        
        workflow_data = self.active_workflows[workflow_id]
        
        # Compile notification summary
        summary = {
            "workflow_id": workflow_id,
            "completion_time": datetime.now(),
            "total_phases": len(workflow_data["phases"]),
            "status": "completed",
            "key_findings": []
        }
        
        # Extract key findings from each phase
        if "design_review" in workflow_data["phases"]:
            design_phase = workflow_data["phases"]["design_review"]
            summary["key_findings"].append(f"Overall design score: {design_phase.get('overall_score', 0):.1f}/10")
            summary["key_findings"].append(f"Agent consensus: {design_phase.get('consensus_score', 0):.1%}")
        
        if "issue_tracking" in workflow_data["phases"]:
            issue_phase = workflow_data["phases"]["issue_tracking"]
            tickets_created = issue_phase.get("tickets_created", 0)
            if tickets_created > 0:
                summary["key_findings"].append(f"Created {tickets_created} JIRA tickets for issues")
        
        if "margo_gate" in workflow_data["phases"]:
            margo_phase = workflow_data["phases"]["margo_gate"]
            summary["key_findings"].append(f"Margo gate: {margo_phase.get('margo_status', 'unknown')}")
        
        if "qa_validation" in workflow_data["phases"]:
            qa_phase = workflow_data["phases"]["qa_validation"]
            if qa_phase.get("status") == "completed":
                summary["key_findings"].append(f"QA validation score: {qa_phase.get('overall_score', 0):.1f}/10")
        
        # Send notifications (would integrate with Slack, email, etc.)
        notification_targets = self._identify_notification_targets(workflow_data)
        notifications_sent = []
        
        for target in notification_targets:
            # In practice, would send actual notifications
            notifications_sent.append({
                "target": target,
                "type": "workflow_complete",
                "status": "sent",
                "summary": summary
            })
        
        return {
            "summary": summary,
            "notifications_sent": len(notifications_sent),
            "notification_targets": notification_targets
        }
    
    # Utility methods
    
    async def _check_research_history(self, submission: Dict[str, Any]) -> Dict[str, Any]:
        """Check if relevant research exists."""
        
        if not self.exa_agent:
            return {"needs_research": False, "reason": "Research capability not available"}
        
        design_area = submission.get("design_area", "general")
        feature_type = submission.get("feature_type", "unknown")
        
        # Search for existing research
        try:
            research_query = f"user research {design_area} {feature_type} usability testing"
            existing_research = self.exa_agent.search_design_best_practices(research_query, num_results=3)
            
            if len(existing_research) >= 2:
                return {
                    "needs_research": False,
                    "existing_research": len(existing_research),
                    "research_summary": [{"title": doc.metadata.get("title", ""), "content": doc.page_content[:100]} for doc in existing_research]
                }
            else:
                return {
                    "needs_research": True,
                    "reason": "Insufficient existing research found",
                    "recommended_research_type": "User Interview"
                }
        except Exception as e:
            self.logger.warning(f"Research check failed: {e}")
            return {"needs_research": False, "reason": "Research check failed"}
    
    async def _create_research_study(self, submission: Dict[str, Any], workflow_id: str) -> Dict[str, Any]:
        """Create a research study based on submission."""
        
        return {
            "study_id": f"study_{uuid.uuid4().hex[:8]}",
            "type": "User Interview",
            "objectives": [
                f"Validate {submission.get('design_area', 'design')} assumptions",
                "Identify usability issues",
                "Gather user feedback on proposed solution"
            ],
            "target_users": "Primary user segment",
            "timeline": "2 weeks",
            "deliverables": [
                "Research findings report",
                "Usability recommendations",
                "Design iteration suggestions"
            ],
            "workflow_id": workflow_id
        }
    
    def _generate_designer_guidance(self, feature_guide_status: str, research_status: Dict[str, Any]) -> List[str]:
        """Generate guidance for designers."""
        
        guidance = []
        
        if feature_guide_status == "missing":
            guidance.append("📋 Please provide feature guide before proceeding with review")
        
        if research_status.get("needs_research"):
            guidance.append("🔬 Research study recommended before final implementation")
            guidance.append(f"📝 Suggested research: {research_status.get('recommended_research_type', 'User Research')}")
        
        if feature_guide_status == "provided" and not research_status.get("needs_research"):
            guidance.append("✅ Ready for comprehensive design review")
        
        return guidance
    
    def _extract_critical_issues(self, review_result: Any) -> List[Dict[str, Any]]:
        """Extract critical issues from review results."""
        
        critical_issues = []
        
        if hasattr(review_result, 'phase_results'):
            for phase, results in review_result.phase_results.items():
                for result in results:
                    if hasattr(result, 'score') and result.score < 5.0:
                        critical_issues.append({
                            "title": f"Low score in {result.agent_name}",
                            "description": result.feedback[:200] + "...",
                            "severity": "High" if result.score < 3.0 else "Medium",
                            "agent": result.agent_name,
                            "score": result.score
                        })
        
        return critical_issues
    
    def _calculate_agent_consensus(self, review_result: Any) -> float:
        """Calculate consensus score among agents."""
        
        if not hasattr(review_result, 'phase_results'):
            return 0.0
        
        scores = []
        for phase, results in review_result.phase_results.items():
            for result in results:
                if hasattr(result, 'score'):
                    scores.append(result.score)
        
        if not scores:
            return 0.0
        
        # Calculate consensus as inverse of score variance
        mean_score = sum(scores) / len(scores)
        variance = sum((s - mean_score) ** 2 for s in scores) / len(scores)
        consensus = max(0.0, 1.0 - (variance / 25.0))  # Normalize variance
        
        return consensus
    
    def _detect_agent_knowledge_gaps(self, agent_result: Any) -> List[Dict[str, Any]]:
        """Detect knowledge gaps in agent responses."""
        
        gaps = []
        
        if hasattr(agent_result, 'feedback'):
            feedback = agent_result.feedback.lower()
            
            # Look for uncertainty indicators
            uncertainty_patterns = [
                ("unclear", "Clarification needed"),
                ("uncertain", "Additional information required"),
                ("depends on", "Context-dependent decision"),
                ("would need", "Missing requirements"),
                ("not specified", "Specification incomplete")
            ]
            
            for pattern, gap_type in uncertainty_patterns:
                if pattern in feedback:
                    gaps.append({
                        "source_agent": agent_result.agent_name,
                        "topic": gap_type,
                        "question": f"Agent {agent_result.agent_name} needs clarification on: {pattern}",
                        "context": feedback[:100] + "...",
                        "severity": "medium"
                    })
        
        return gaps
    
    def _extract_accessibility_issues(self, review_result: Any) -> List[Dict[str, Any]]:
        """Extract accessibility issues from review results."""
        
        accessibility_issues = []
        
        if hasattr(review_result, 'phase_results'):
            for phase, results in review_result.phase_results.items():
                for result in results:
                    if result.agent_name == "Accessibility Expert" and hasattr(result, 'specific_issues'):
                        for issue in result.specific_issues:
                            accessibility_issues.append({
                                "type": "WCAG Violation",
                                "guideline": "WCAG 2.1 AA",  # Would be more specific
                                "description": issue,
                                "severity": "Medium"  # Would be assessed
                            })
        
        return accessibility_issues
    
    def _identify_notification_targets(self, workflow_data: Dict[str, Any]) -> List[str]:
        """Identify who should be notified of workflow completion."""
        
        targets = ["designer", "design_lead"]
        
        # Add stakeholders based on workflow results
        if workflow_data.get("phases", {}).get("margo_gate", {}).get("requires_margo"):
            targets.append("vp_product")
        
        if workflow_data.get("phases", {}).get("issue_tracking", {}).get("tickets_created", 0) > 0:
            targets.extend(["qa_team", "engineering_lead"])
        
        if workflow_data.get("phases", {}).get("qa_validation", {}).get("discrepancies_found", 0) > 0:
            targets.extend(["qa_team", "engineering_team"])
        
        return list(set(targets))  # Remove duplicates
    
    def _compile_final_workflow_result(self, workflow_id: str) -> Dict[str, Any]:
        """Compile final workflow results."""
        
        workflow_data = self.active_workflows[workflow_id]
        
        return {
            "workflow_id": workflow_id,
            "status": "completed",
            "started_at": workflow_data["started_at"],
            "completed_at": datetime.now(),
            "phases_completed": len(workflow_data["phases"]),
            "phase_results": workflow_data["phases"],
            "summary": {
                "overall_score": workflow_data.get("phases", {}).get("design_review", {}).get("overall_score", 0),
                "issues_created": workflow_data.get("phases", {}).get("issue_tracking", {}).get("tickets_created", 0),
                "margo_required": workflow_data.get("phases", {}).get("margo_gate", {}).get("requires_margo", False),
                "qa_validation_score": workflow_data.get("phases", {}).get("qa_validation", {}).get("overall_score", 0)
            },
            "next_steps": self._generate_next_steps(workflow_data),
            "stakeholder_notifications": workflow_data.get("phases", {}).get("notifications", {}).get("notifications_sent", 0)
        }
    
    def _generate_next_steps(self, workflow_data: Dict[str, Any]) -> List[str]:
        """Generate next steps based on workflow results."""
        
        next_steps = []
        phases = workflow_data.get("phases", {})
        
        # Design review next steps
        if phases.get("design_review", {}).get("overall_score", 0) < 7.0:
            next_steps.append("Address design review feedback before implementation")
        
        # JIRA next steps
        if phases.get("issue_tracking", {}).get("tickets_created", 0) > 0:
            next_steps.append("Resolve JIRA tickets before proceeding")
        
        # Margo next steps
        if phases.get("margo_gate", {}).get("requires_margo"):
            next_steps.append("Schedule Margo review meeting for strategic approval")
        
        # QA next steps
        if phases.get("qa_validation", {}).get("discrepancies_found", 0) > 0:
            next_steps.append("Fix QA discrepancies and re-validate")
        
        # Research next steps
        if phases.get("precheck", {}).get("research_study"):
            next_steps.append("Complete user research study before final implementation")
        
        if not next_steps:
            next_steps.append("Design approved - ready for implementation")
        
        return next_steps


# Factory function for easy setup
def create_advanced_workflow_system(
    openai_api_key: str,
    exa_api_key: Optional[str] = None,
    jira_url: Optional[str] = None,
    jira_username: Optional[str] = None,
    jira_api_token: Optional[str] = None,
    enable_playwright: bool = True,
    **kwargs
) -> AdvancedWorkflowSystem:
    """
    Create an advanced workflow system with all integrations.
    
    Args:
        openai_api_key: OpenAI API key
        exa_api_key: EXA API key for research
        jira_url: JIRA instance URL
        jira_username: JIRA username
        jira_api_token: JIRA API token
        enable_playwright: Enable Playwright QA validation
        **kwargs: Additional configuration options
        
    Returns:
        AdvancedWorkflowSystem instance
    """
    
    config = AdvancedWorkflowConfig(
        openai_api_key=openai_api_key,
        exa_api_key=exa_api_key,
        jira_url=jira_url,
        jira_username=jira_username,
        jira_api_token=jira_api_token,
        playwright_enabled=enable_playwright,
        **kwargs
    )
    
    return AdvancedWorkflowSystem(config)


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def main():
        # Create system from environment variables
        system = create_advanced_workflow_system(
            openai_api_key=os.getenv('OPENAI_API_KEY'),
            exa_api_key=os.getenv('EXA_API_KEY'),
            jira_url=os.getenv('JIRA_URL'),
            jira_username=os.getenv('JIRA_USERNAME'),
            jira_api_token=os.getenv('JIRA_API_TOKEN'),
            enable_playwright=True
        )
        
        print("🚀 Advanced Workflow System ready")
        
        # Example workflow submission
        example_submission = {
            "design_type": "ui_design",
            "design_area": "checkout_flow",
            "feature_type": "payment_integration",
            "impact_level": "high",
            "image_data": "base64_encoded_image_data_here",
            "feature_guide": "Feature guide content here",
            "qa_link": "https://qa.yourapp.com/checkout",
            "design_spec_url": "https://figma.com/file/example",
            "context": {
                "designer": "John Doe",
                "feature_deadline": "2024-02-15",
                "stakeholders": ["product_team", "engineering_team"]
            }
        }
        
        # Process complete workflow
        # result = await system.process_complete_design_workflow(example_submission)
        # print(f"✅ Workflow completed: {result['workflow_id']}")
        # print(f"📊 Summary: {result['summary']}")
    
    if os.getenv('OPENAI_API_KEY'):
        asyncio.run(main())
    else:
        print("❌ OPENAI_API_KEY required to run example")
