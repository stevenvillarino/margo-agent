"""
Workflow Orchestrator for Design Review Automation

This orchestrator manages complex design workflows including:
- Agent knowledge gap handling and escalation
- JIRA ticket creation for design issues
- QA/Design spec cross-validation with Playwright
- Research study creation and management
- Inter-agent communication and coordination
- Margo agent (senior review) gate keeping

Key Features:
- Knowledge gap detection and escalation
- Automated issue tracking
- Cross-validation workflows
- Research automation
- Pre-Margo filtering system
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union, TYPE_CHECKING
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

from agents.exa_search import ExaSearchAgent

if TYPE_CHECKING:
    from agents.enhanced_system import EnhancedDesignReviewSystem


class WorkflowType(Enum):
    """Types of design workflows."""
    DESIGN_REVIEW = "design_review"
    KNOWLEDGE_GAP = "knowledge_gap" 
    ISSUE_ESCALATION = "issue_escalation"
    QA_VALIDATION = "qa_validation"
    RESEARCH_STUDY = "research_study"
    MARGO_PREPARATION = "margo_preparation"


class Priority(Enum):
    """Issue priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class WorkflowStatus(Enum):
    """Workflow execution status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ESCALATED = "escalated"
    FAILED = "failed"


@dataclass
class KnowledgeGap:
    """Represents a knowledge gap identified by an agent."""
    gap_id: str
    agent_name: str
    topic: str
    question: str
    context: Dict[str, Any]
    severity: Priority
    timestamp: datetime
    suggested_next_steps: List[str]


@dataclass
class JIRATicket:
    """JIRA ticket creation request."""
    ticket_id: str
    title: str
    description: str
    issue_type: str  # "Bug", "Task", "Story", etc.
    priority: Priority
    assignee: Optional[str]
    labels: List[str]
    design_file_url: Optional[str]
    related_workflow_id: str


@dataclass
class QAValidationRequest:
    """QA validation workflow request."""
    validation_id: str
    qa_link: str
    design_spec_url: str
    playwright_test_config: Dict[str, Any]
    stakeholders: List[str]
    expected_elements: List[str]
    accessibility_checks: bool = True


@dataclass
class ResearchStudy:
    """Research study definition and management."""
    study_id: str
    title: str
    research_type: str  # "User Interview", "Survey", "A/B Test", etc.
    objectives: List[str]
    target_participants: Dict[str, Any]
    timeline: Dict[str, datetime]
    deliverables: List[str]
    status: WorkflowStatus
    findings: Optional[Dict[str, Any]] = None


@dataclass
class WorkflowExecution:
    """Complete workflow execution tracking."""
    workflow_id: str
    workflow_type: WorkflowType
    status: WorkflowStatus
    created_at: datetime
    updated_at: datetime
    triggered_by: str
    context: Dict[str, Any]
    results: Dict[str, Any]
    next_steps: List[str]
    stakeholders: List[str]


class WorkflowOrchestrator:
    """
    Advanced workflow orchestrator for design review automation.
    """
    
    def __init__(self, 
                 enhanced_system: 'EnhancedDesignReviewSystem',
                 exa_api_key: Optional[str] = None,
                 jira_config: Optional[Dict[str, str]] = None,
                 playwright_config: Optional[Dict[str, Any]] = None):
        """
        Initialize the workflow orchestrator.
        
        Args:
            enhanced_system: The enhanced design review system to orchestrate
            exa_api_key: Exa API key for research
            jira_config: JIRA integration configuration
            playwright_config: Playwright testing configuration
        """
        self.enhanced_system = enhanced_system
        
        self.jira_config = jira_config
        self.playwright_config = playwright_config
        
        # Initialize research agent
        self.research_agent = ExaSearchAgent(exa_api_key) if exa_api_key else None
        
        # Workflow tracking
        self.active_workflows: Dict[str, WorkflowExecution] = {}
        self.knowledge_gaps: Dict[str, KnowledgeGap] = {}
        self.pending_tickets: Dict[str, JIRATicket] = {}
        self.research_studies: Dict[str, ResearchStudy] = {}
        
        # Margo agent threshold settings
        self.margo_threshold = {
            "min_agent_consensus": 0.8,
            "critical_issues_max": 2,
            "overall_score_min": 7.0,
            "accessibility_score_min": 8.0
        }
        
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        print("🔄 Workflow Orchestrator initialized")
        print(f"🎫 JIRA integration: {'enabled' if jira_config else 'disabled'}")
        print(f"🧪 Playwright testing: {'enabled' if playwright_config else 'disabled'}")
    
    async def process_design_submission(self, 
                                      design_data: Dict[str, Any],
                                      designer_info: Dict[str, str]) -> Dict[str, Any]:
        """
        Process a design submission through the complete workflow.
        
        Args:
            design_data: Design files and metadata
            designer_info: Designer information and context
            
        Returns:
            Complete workflow results
        """
        workflow_id = f"design_review_{uuid.uuid4().hex[:8]}"
        
        self.logger.info(f"Processing design submission: {workflow_id}")
        
        # Phase 1: Pre-Margo Agent Screening
        screening_result = await self._pre_margo_screening(design_data, designer_info, workflow_id)
        
        if screening_result["requires_margo"]:
            # Phase 2: Margo Agent Review (Full Review)
            margo_result = await self._conduct_margo_review(design_data, screening_result, workflow_id)
            final_result = margo_result
        else:
            # Handle through automated agents only
            final_result = screening_result
        
        # Phase 3: Post-Review Actions
        await self._execute_post_review_actions(final_result, workflow_id)
        
        return {
            "workflow_id": workflow_id,
            "status": "completed",
            "results": final_result,
            "next_steps": final_result.get("next_steps", []),
            "escalations": final_result.get("escalations", [])
        }
    
    async def _pre_margo_screening(self, 
                                 design_data: Dict[str, Any],
                                 designer_info: Dict[str, str],
                                 workflow_id: str) -> Dict[str, Any]:
        """
        Pre-Margo screening to filter common issues and validate readiness.
        """
        self.logger.info(f"Starting pre-Margo screening for {workflow_id}")
        
        # 1. Feature Guide Validation
        feature_validation = await self._validate_feature_guide_alignment(design_data)
        
        # 2. Research History Check
        research_status = await self._check_research_history(design_data, designer_info)
        
        # 3. Basic Design Review
        basic_review = await self.enhanced_system.conduct_comprehensive_review(
            image_data=design_data.get("image_data"),
            design_type=design_data.get("type", "ui_design"),
            context={"phase": "pre_screening", "workflow_id": workflow_id}
        )
        
        # 4. Knowledge Gap Detection
        knowledge_gaps = await self._detect_knowledge_gaps(basic_review, design_data)
        
        # 5. Issue Analysis
        critical_issues = self._analyze_critical_issues(basic_review)
        
        # 6. Decision Logic
        requires_margo = self._should_escalate_to_margo(
            basic_review, critical_issues, feature_validation, research_status
        )
        
        screening_result = {
            "workflow_id": workflow_id,
            "requires_margo": requires_margo,
            "basic_review": basic_review,
            "feature_validation": feature_validation,
            "research_status": research_status,
            "knowledge_gaps": knowledge_gaps,
            "critical_issues": critical_issues,
            "readiness_score": self._calculate_readiness_score(basic_review, feature_validation, research_status),
            "recommendations": self._generate_pre_margo_recommendations(
                requires_margo, critical_issues, knowledge_gaps, research_status
            )
        }
        
        # Log knowledge gaps for follow-up
        for gap in knowledge_gaps:
            await self._log_knowledge_gap(gap, workflow_id)
        
        return screening_result
    
    async def _validate_feature_guide_alignment(self, design_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate design alignment with feature guides."""
        
        # Check if feature guide is provided
        feature_guide = design_data.get("feature_guide")
        if not feature_guide:
            return {
                "status": "missing",
                "issues": ["No feature guide provided"],
                "alignment_score": 0.0,
                "action": "request_feature_guide"
            }
        
        # Cross-reference design with feature guide
        validation_prompt = f"""
        Analyze this design against the provided feature guide and determine alignment:
        
        Feature Guide: {feature_guide}
        Design Context: {design_data.get('description', 'No description provided')}
        
        Evaluate:
        1. Feature completeness - Are all required features present?
        2. User flow alignment - Does the design follow the specified user journey?
        3. Requirements compliance - Are all technical requirements addressed?
        4. Success metrics - Can the design achieve the defined success metrics?
        
        Provide a structured assessment with specific gaps identified.
        """
        
        # This would call your LLM for analysis
        # For now, returning a structured response
        return {
            "status": "analyzed",
            "alignment_score": 8.5,  # Would be calculated
            "compliant_features": [],
            "missing_features": [],
            "alignment_issues": [],
            "recommendations": []
        }
    
    async def _check_research_history(self, 
                                    design_data: Dict[str, Any],
                                    designer_info: Dict[str, str]) -> Dict[str, Any]:
        """Check if relevant research exists for this design area."""
        
        design_area = design_data.get("area", "general")
        feature_type = design_data.get("feature_type", "unknown")
        
        # Search for existing research using EXA
        if self.research_agent:
            research_query = f"user research {design_area} {feature_type} usability testing"
            existing_research = await self._search_existing_research(research_query)
            
            if existing_research:
                return {
                    "status": "research_found",
                    "research_count": len(existing_research),
                    "research_summary": existing_research,
                    "research_gaps": self._identify_research_gaps(existing_research, design_data),
                    "action": "review_existing_research"
                }
        
        # No research found - determine if needed
        research_needed = self._assess_research_need(design_data)
        
        if research_needed["required"]:
            # Create research study
            study = await self._create_research_study(design_data, research_needed)
            return {
                "status": "research_required",
                "study_created": study,
                "action": "conduct_research_first"
            }
        
        return {
            "status": "no_research_needed",
            "action": "proceed_without_research"
        }
    
    async def _detect_knowledge_gaps(self, 
                                   review_result: Any,
                                   design_data: Dict[str, Any]) -> List[KnowledgeGap]:
        """Detect knowledge gaps from agent responses."""
        
        gaps = []
        
        # Analyze agent responses for uncertainty indicators
        if hasattr(review_result, 'phase_results'):
            for phase, results in review_result.phase_results.items():
                for result in results:
                    # Look for uncertainty indicators in feedback
                    uncertainty_indicators = [
                        "unclear", "uncertain", "need more information",
                        "would require", "depends on", "not specified",
                        "unclear requirements", "missing context"
                    ]
                    
                    feedback_lower = result.feedback.lower()
                    for indicator in uncertainty_indicators:
                        if indicator in feedback_lower:
                            gap = KnowledgeGap(
                                gap_id=uuid.uuid4().hex[:8],
                                agent_name=result.agent_name,
                                topic=self._extract_topic_from_feedback(result.feedback, indicator),
                                question=self._formulate_question(result.feedback, indicator),
                                context={"design_data": design_data, "agent_result": asdict(result)},
                                severity=self._assess_gap_severity(result.feedback, indicator),
                                timestamp=datetime.now(),
                                suggested_next_steps=self._suggest_gap_resolution(indicator, result.agent_type)
                            )
                            gaps.append(gap)
        
        return gaps
    
    async def _log_knowledge_gap(self, gap: KnowledgeGap, workflow_id: str):
        """Log knowledge gap for appropriate agent intervention."""
        
        self.knowledge_gaps[gap.gap_id] = gap
        
        # Create intervention workflow
        intervention_workflow = WorkflowExecution(
            workflow_id=f"intervention_{gap.gap_id}",
            workflow_type=WorkflowType.KNOWLEDGE_GAP,
            status=WorkflowStatus.PENDING,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            triggered_by=workflow_id,
            context={"gap": asdict(gap)},
            results={},
            next_steps=gap.suggested_next_steps,
            stakeholders=self._identify_gap_stakeholders(gap)
        )
        
        self.active_workflows[intervention_workflow.workflow_id] = intervention_workflow
        
        # Notify appropriate stakeholders
        await self._notify_stakeholders(intervention_workflow)
    
    async def _create_jira_ticket(self, 
                                issue_data: Dict[str, Any],
                                workflow_id: str) -> str:
        """Create JIRA ticket for design issues."""
        
        ticket = JIRATicket(
            ticket_id=f"DESIGN-{uuid.uuid4().hex[:6].upper()}",
            title=issue_data["title"],
            description=issue_data["description"],
            issue_type=issue_data.get("type", "Task"),
            priority=Priority(issue_data.get("priority", "medium")),
            assignee=issue_data.get("assignee"),
            labels=issue_data.get("labels", ["design-review", "automated"]),
            design_file_url=issue_data.get("design_file"),
            related_workflow_id=workflow_id
        )
        
        self.pending_tickets[ticket.ticket_id] = ticket
        
        # In real implementation, would use JIRA API
        self.logger.info(f"JIRA ticket created: {ticket.ticket_id}")
        
        return ticket.ticket_id
    
    async def _validate_qa_against_design(self, 
                                        qa_link: str,
                                        design_spec: str,
                                        workflow_id: str) -> Dict[str, Any]:
        """Use Playwright to validate QA implementation against design spec."""
        
        validation_id = f"qa_val_{uuid.uuid4().hex[:8]}"
        
        validation_request = QAValidationRequest(
            validation_id=validation_id,
            qa_link=qa_link,
            design_spec_url=design_spec,
            playwright_test_config=self.playwright_config or {},
            stakeholders=["qa_team", "design_team", "dev_team"],
            expected_elements=[]  # Would be extracted from design spec
        )
        
        # Playwright validation logic would go here
        # For now, returning mock results
        discrepancies = [
            {
                "element": "primary_button",
                "expected": "Blue #007AFF, 44px height",
                "actual": "Blue #0066CC, 40px height",
                "severity": "medium",
                "screenshot": "path/to/screenshot.png"
            }
        ]
        
        if discrepancies:
            # Create tickets for discrepancies
            for discrepancy in discrepancies:
                await self._create_jira_ticket({
                    "title": f"Design Implementation Discrepancy: {discrepancy['element']}",
                    "description": f"Expected: {discrepancy['expected']}\nActual: {discrepancy['actual']}",
                    "type": "Bug",
                    "priority": discrepancy["severity"],
                    "labels": ["design-discrepancy", "qa-validation"]
                }, workflow_id)
        
        return {
            "validation_id": validation_id,
            "discrepancies_found": len(discrepancies),
            "discrepancies": discrepancies,
            "tickets_created": len(discrepancies),
            "status": "completed"
        }
    
    def _should_escalate_to_margo(self, 
                                review_result: Any,
                                critical_issues: List[Dict],
                                feature_validation: Dict,
                                research_status: Dict) -> bool:
        """Determine if design should be escalated to Margo agent."""
        
        # Check against thresholds
        if len(critical_issues) > self.margo_threshold["critical_issues_max"]:
            return True
        
        if hasattr(review_result, 'overall_score'):
            if review_result.overall_score < self.margo_threshold["overall_score_min"]:
                return True
        
        # Check feature guide alignment
        if feature_validation.get("alignment_score", 0) < 7.0:
            return True
        
        # Check research requirements
        if research_status.get("status") == "research_required":
            return False  # Don't escalate until research is done
        
        # Check for complex strategic decisions
        complex_indicators = [
            "strategic alignment", "business impact", "competitive analysis",
            "market positioning", "roi analysis", "user acquisition"
        ]
        
        if hasattr(review_result, 'phase_results'):
            for phase, results in review_result.phase_results.items():
                for result in results:
                    feedback_lower = result.feedback.lower()
                    if any(indicator in feedback_lower for indicator in complex_indicators):
                        return True
        
        return False
    
    async def _conduct_margo_review(self, 
                                  design_data: Dict[str, Any],
                                  screening_result: Dict[str, Any],
                                  workflow_id: str) -> Dict[str, Any]:
        """Conduct full Margo agent review for complex/strategic decisions."""
        
        self.logger.info(f"Escalating to Margo agent: {workflow_id}")
        
        # Prepare enhanced context for Margo
        margo_context = {
            "pre_screening_result": screening_result,
            "escalation_reason": self._determine_escalation_reason(screening_result),
            "strategic_focus": True,
            "workflow_id": workflow_id
        }
        
        # Conduct enhanced review with full agent suite
        margo_review = await self.enhanced_system.conduct_comprehensive_review(
            image_data=design_data.get("image_data"),
            design_type=design_data.get("type", "ui_design"),
            context=margo_context
        )
        
        return {
            "margo_review": margo_review,
            "strategic_assessment": await self._conduct_strategic_assessment(margo_review, design_data),
            "final_recommendation": self._generate_margo_recommendation(margo_review),
            "meeting_prep": self._prepare_meeting_materials(margo_review, screening_result)
        }
    
    async def _execute_post_review_actions(self, 
                                         review_result: Dict[str, Any],
                                         workflow_id: str):
        """Execute post-review actions based on results."""
        
        actions = []
        
        # Create JIRA tickets for issues
        if "critical_issues" in review_result:
            for issue in review_result["critical_issues"]:
                ticket_id = await self._create_jira_ticket({
                    "title": f"Design Issue: {issue['title']}",
                    "description": issue["description"],
                    "type": "Task",
                    "priority": issue.get("priority", "medium")
                }, workflow_id)
                actions.append(f"Created JIRA ticket: {ticket_id}")
        
        # Schedule research if needed
        if review_result.get("research_status", {}).get("study_created"):
            study = review_result["research_status"]["study_created"]
            actions.append(f"Research study scheduled: {study.study_id}")
        
        # Notify stakeholders
        stakeholders = self._identify_result_stakeholders(review_result)
        await self._notify_stakeholders_of_results(review_result, stakeholders)
        actions.append(f"Notified {len(stakeholders)} stakeholders")
        
        return actions
    
    # Utility methods
    def _analyze_critical_issues(self, review_result: Any) -> List[Dict]:
        """Analyze review results for critical issues."""
        critical_issues = []
        
        if hasattr(review_result, 'phase_results'):
            for phase, results in review_result.phase_results.items():
                for result in results:
                    if hasattr(result, 'score') and result.score < 5.0:
                        critical_issues.append({
                            "title": f"Low score in {result.agent_name}",
                            "description": result.feedback[:200] + "...",
                            "score": result.score,
                            "agent": result.agent_name,
                            "priority": "high" if result.score < 3.0 else "medium"
                        })
        
        return critical_issues
    
    def _calculate_readiness_score(self, 
                                 review_result: Any,
                                 feature_validation: Dict,
                                 research_status: Dict) -> float:
        """Calculate overall readiness score for Margo review."""
        
        base_score = getattr(review_result, 'overall_score', 5.0)
        feature_score = feature_validation.get("alignment_score", 5.0)
        research_score = 10.0 if research_status.get("status") != "research_required" else 5.0
        
        return (base_score + feature_score + research_score) / 3
    
    def _extract_topic_from_feedback(self, feedback: str, indicator: str) -> str:
        """Extract topic from feedback containing uncertainty."""
        # Simple extraction - would be more sophisticated in practice
        sentences = feedback.split('.')
        for sentence in sentences:
            if indicator in sentence.lower():
                return sentence.strip()[:50]
        return "General uncertainty"
    
    def _formulate_question(self, feedback: str, indicator: str) -> str:
        """Formulate specific question from uncertain feedback."""
        # Would use NLP to extract proper questions
        return f"Question about: {indicator} in context of {feedback[:100]}..."
    
    def _assess_gap_severity(self, feedback: str, indicator: str) -> Priority:
        """Assess severity of knowledge gap."""
        critical_indicators = ["critical", "essential", "required", "must"]
        if any(word in feedback.lower() for word in critical_indicators):
            return Priority.HIGH
        return Priority.MEDIUM
    
    def _suggest_gap_resolution(self, indicator: str, agent_type: str) -> List[str]:
        """Suggest resolution steps for knowledge gap."""
        return [
            f"Consult with {agent_type} specialist",
            "Gather additional requirements",
            "Schedule stakeholder meeting",
            "Research industry best practices"
        ]
    
    def _identify_gap_stakeholders(self, gap: KnowledgeGap) -> List[str]:
        """Identify stakeholders who can resolve knowledge gap."""
        stakeholder_map = {
            "ui_specialist": ["design_lead", "ux_team"],
            "ux_researcher": ["research_team", "product_manager"],
            "accessibility": ["accessibility_lead", "qa_team"],
            "vp_product": ["product_leadership", "strategy_team"]
        }
        
        agent_type = gap.context.get("agent_result", {}).get("agent_type", "general")
        return stakeholder_map.get(agent_type, ["design_team"])
    
    async def _notify_stakeholders(self, workflow: WorkflowExecution):
        """Notify stakeholders of workflow status."""
        # Would integrate with notification systems (Slack, email, etc.)
        self.logger.info(f"Notifying stakeholders for workflow: {workflow.workflow_id}")
    
    async def _notify_stakeholders_of_results(self, results: Dict, stakeholders: List[str]):
        """Notify stakeholders of review results."""
        self.logger.info(f"Notifying {len(stakeholders)} stakeholders of results")
    
    def _identify_result_stakeholders(self, results: Dict) -> List[str]:
        """Identify stakeholders based on review results."""
        return ["design_team", "product_team", "qa_team"]  # Would be more sophisticated
    
    async def _search_existing_research(self, query: str) -> List[Dict]:
        """Search for existing research using EXA."""
        if not self.research_agent:
            return []
        
        try:
            results = self.research_agent.search_design_best_practices(query, num_results=5)
            return [{"title": doc.metadata.get("title", ""), "content": doc.page_content[:200]} for doc in results]
        except:
            return []
    
    def _identify_research_gaps(self, existing_research: List[Dict], design_data: Dict) -> List[str]:
        """Identify gaps in existing research."""
        # Would analyze research coverage vs. design requirements
        return ["User onboarding flow", "Mobile accessibility patterns"]
    
    def _assess_research_need(self, design_data: Dict) -> Dict[str, Any]:
        """Assess if research is needed for this design."""
        # Complex logic to determine research requirements
        high_impact_areas = ["user_onboarding", "payment_flow", "core_navigation"]
        
        if design_data.get("area") in high_impact_areas:
            return {
                "required": True,
                "type": "User Interview",
                "urgency": "high",
                "participants": 8
            }
        
        return {"required": False}
    
    async def _create_research_study(self, design_data: Dict, research_need: Dict) -> ResearchStudy:
        """Create and schedule research study."""
        study = ResearchStudy(
            study_id=f"study_{uuid.uuid4().hex[:8]}",
            title=f"Research for {design_data.get('title', 'Design Feature')}",
            research_type=research_need["type"],
            objectives=[
                "Validate user flow assumptions",
                "Identify usability issues",
                "Gather user feedback"
            ],
            target_participants={
                "count": research_need.get("participants", 5),
                "criteria": "Regular platform users"
            },
            timeline={
                "start": datetime.now() + timedelta(days=3),
                "end": datetime.now() + timedelta(days=14)
            },
            deliverables=[
                "Research findings report",
                "Usability recommendations", 
                "Design iteration suggestions"
            ],
            status=WorkflowStatus.PENDING
        )
        
        self.research_studies[study.study_id] = study
        return study
    
    def _generate_pre_margo_recommendations(self, 
                                          requires_margo: bool,
                                          critical_issues: List,
                                          knowledge_gaps: List,
                                          research_status: Dict) -> List[str]:
        """Generate recommendations for pre-Margo phase."""
        recommendations = []
        
        if not requires_margo:
            recommendations.append("✅ Design ready for implementation - no Margo review needed")
        else:
            recommendations.append("⚠️ Design requires Margo review before proceeding")
        
        if critical_issues:
            recommendations.append(f"🚨 Address {len(critical_issues)} critical issues first")
        
        if knowledge_gaps:
            recommendations.append(f"❓ Resolve {len(knowledge_gaps)} knowledge gaps")
        
        if research_status.get("status") == "research_required":
            recommendations.append("🔬 Complete research study before final review")
        
        return recommendations
    
    def _determine_escalation_reason(self, screening_result: Dict) -> str:
        """Determine why escalation to Margo is needed."""
        if screening_result["readiness_score"] < 7.0:
            return "Low readiness score"
        if len(screening_result["critical_issues"]) > 2:
            return "Multiple critical issues"
        return "Strategic complexity"
    
    async def _conduct_strategic_assessment(self, review: Any, design_data: Dict) -> Dict:
        """Conduct strategic assessment for Margo review."""
        return {
            "business_impact": "High",
            "competitive_advantage": "Medium", 
            "risk_assessment": "Low",
            "roi_projection": "Positive"
        }
    
    def _generate_margo_recommendation(self, review: Any) -> Dict:
        """Generate final recommendation from Margo review."""
        return {
            "decision": "Approve with conditions",
            "conditions": ["Address accessibility concerns", "Update feature guide"],
            "timeline": "2 week implementation window"
        }
    
    def _prepare_meeting_materials(self, review: Any, screening: Dict) -> Dict:
        """Prepare materials for face-to-face Margo meeting."""
        return {
            "agenda": ["Strategic alignment", "Risk assessment", "Implementation plan"],
            "key_decisions": ["Feature scope", "Launch timeline", "Success metrics"],
            "supporting_docs": ["Design specs", "Research findings", "Technical requirements"]
        }


# Factory function for easy integration
def create_workflow_orchestrator(
    openai_api_key: str,
    exa_api_key: Optional[str] = None,
    jira_config: Optional[Dict[str, str]] = None,
    playwright_config: Optional[Dict[str, Any]] = None
) -> WorkflowOrchestrator:
    """Create a workflow orchestrator instance."""
    return WorkflowOrchestrator(
        openai_api_key=openai_api_key,
        exa_api_key=exa_api_key,
        jira_config=jira_config,
        playwright_config=playwright_config
    )


# Example usage
if __name__ == "__main__":
    import os
    
    # Initialize orchestrator
    orchestrator = create_workflow_orchestrator(
        openai_api_key=os.getenv('OPENAI_API_KEY'),
        exa_api_key=os.getenv('EXA_API_KEY'),
        jira_config={
            "url": "https://your-company.atlassian.net",
            "username": os.getenv('JIRA_USERNAME'),
            "api_token": os.getenv('JIRA_API_TOKEN')
        },
        playwright_config={
            "browser": "chromium",
            "headless": True,
            "viewport": {"width": 1920, "height": 1080}
        }
    )
    
    print("✅ Workflow Orchestrator ready for design automation")
