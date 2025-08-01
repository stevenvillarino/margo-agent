"""
Enhanced Multi-Agent Design Review System

This system integrates all specialized review agents with learning capabilities
and provides comprehensive design evaluation with continuous improvement.
"""

import asyncio
import json
import base64
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict

from agents.orchestrator import ReviewOrchestrator, ReviewResult, ReviewPhase
from agents.peer_review_agent import PeerDesignReviewAgent, create_peer_reviewer
from agents.vp_product_agent import VPProductReviewAgent
from agents.accessibility_agent import AccessibilityAgent
from agents.quality_evaluation_agent import QualityEvaluationAgent
from agents.learning_system import AgentLearningSystem

import asyncio
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

from agents.orchestrator import ReviewOrchestrator, OrchestratedReview
from agents.exa_search import ExaSearchAgent


class EnhancedDesignReviewSystem:
    """
    Complete multi-agent design review system with learning capabilities.
    """
    
    def __init__(self, 
                 openai_api_key: str,
                 exa_api_key: Optional[str] = None,
                 learning_enabled: bool = True,
                 company_context: Dict[str, Any] = None):
        """
        Initialize the enhanced design review system.
        
        Args:
            openai_api_key: OpenAI API key
            exa_api_key: Optional Exa API key for web research
            learning_enabled: Whether to enable learning system
            company_context: Company-specific context for VP agent
        """
        self.openai_api_key = openai_api_key
        self.exa_api_key = exa_api_key
        
        # Initialize orchestrator
        self.orchestrator = ReviewOrchestrator(
            openai_api_key=openai_api_key,
            exa_api_key=exa_api_key
        )
        
        # Initialize learning system
        self.learning_system = None
        if learning_enabled:
            self.learning_system = AgentLearningSystem()
        
        # Initialize specialized agents
        self._initialize_agents(company_context)
        
        # System configuration
        self.config = {
            "enable_parallel_reviews": True,
            "enable_learning": learning_enabled,
            "enable_adaptive_prompts": learning_enabled,
            "min_agents_for_review": 2,
            "confidence_threshold": 0.7
        }
        
        print("🚀 Enhanced Design Review System initialized")
        print(f"🤖 Total agents: {len(self.orchestrator.agents)}")
        print(f"🧠 Learning: {'enabled' if learning_enabled else 'disabled'}")
        print(f"🔍 Web research: {'enabled' if exa_api_key else 'disabled'}")
    
    def _initialize_agents(self, company_context: Dict[str, Any] = None):
        """Initialize and register all specialized agents."""
        
        # Create peer review agents
        ui_specialist = create_peer_reviewer("ui_specialist", self.openai_api_key, self.exa_api_key)
        ux_researcher = create_peer_reviewer("ux_researcher", self.openai_api_key, self.exa_api_key)
        creative_director = create_peer_reviewer("creative_director", self.openai_api_key, self.exa_api_key)
        
        # Create VP Product agent
        vp_context = company_context or {
            "industry": "Streaming/Entertainment",
            "company_stage": "Growth",
            "primary_metrics": ["User Engagement", "Content Discovery", "Revenue"],
            "target_audience": "TV viewers, families, cord-cutters",
            "competitive_position": "Premium streaming platform"
        }
        
        vp_priorities = [
            "Enhance user engagement and retention",
            "Improve content discovery experience", 
            "Optimize conversion funnel",
            "Strengthen competitive positioning",
            "Reduce customer acquisition costs"
        ]
        
        vp_agent = VPProductReviewAgent(
            openai_api_key=self.openai_api_key,
            company_context=vp_context,
            business_priorities=vp_priorities,
            exa_api_key=self.exa_api_key
        )
        
        # Create accessibility agent
        accessibility_agent = AccessibilityAgent(
            openai_api_key=self.openai_api_key,
            wcag_level="AA",
            target_disabilities=[
                "Visual impairments",
                "Hearing impairments",
                "Motor impairments", 
                "Cognitive impairments",
                "Age-related impairments"
            ],
            exa_api_key=self.exa_api_key
        )
        
        # Create quality evaluation agent
        confluence_config = {
            'url': getattr(self, 'confluence_url', None),
            'username': getattr(self, 'confluence_username', None),
            'api_key': getattr(self, 'confluence_api_key', None)
        } if hasattr(self, 'confluence_url') else None
        
        quality_agent = QualityEvaluationAgent(
            openai_api_key=self.openai_api_key,
            confluence_config=confluence_config,
            exa_api_key=self.exa_api_key,
            quality_standards={
                'minimum_compliance_score': 0.8,
                'critical_issue_threshold': 0,
                'high_issue_threshold': 2,
                'feature_guide_match_threshold': 0.7,
                'research_validation_threshold': 0.6,
                'pain_point_coverage_threshold': 0.8
            }
        )
        
        # Register all agents with orchestrator
        self.orchestrator.register_agent("ui_specialist", ui_specialist)
        self.orchestrator.register_agent("ux_researcher", ux_researcher)
        self.orchestrator.register_agent("creative_director", creative_director)
        self.orchestrator.register_agent("vp_product", vp_agent)
        self.orchestrator.register_agent("accessibility", accessibility_agent)
        self.orchestrator.register_agent("quality_evaluation", quality_agent)
        
        # Store agent references for direct access
        self.agents = {
            "ui_specialist": ui_specialist,
            "ux_researcher": ux_researcher,
            "creative_director": creative_director,
            "vp_product": vp_agent,
            "accessibility": accessibility_agent,
            "quality_evaluation": quality_agent
        }
    
    async def conduct_comprehensive_review(self, 
                                         image_data: str,
                                         design_type: str,
                                         context: Dict[str, Any] = None,
                                         selected_agents: List[str] = None) -> Dict[str, Any]:
        """
        Conduct a comprehensive multi-agent design review.
        
        Args:
            image_data: Base64 encoded image data
            design_type: Type of design being reviewed
            context: Additional context for the review
            selected_agents: Optional list of specific agents to use
            
        Returns:
            Complete review results with learning insights
        """
        print(f"🎯 Starting comprehensive review for {design_type}")
        
        # Apply learning enhancements if enabled
        if self.config["enable_adaptive_prompts"] and self.learning_system:
            await self._apply_learning_enhancements(design_type)
        
        # Filter agents if specified
        if selected_agents:
            # Temporarily store original agents
            original_agents = self.orchestrator.agents.copy()
            
            # Filter to selected agents
            filtered_agents = {
                agent_type: agent for agent_type, agent in original_agents.items()
                if agent_type in selected_agents
            }
            self.orchestrator.agents = filtered_agents
        
        try:
            # Conduct orchestrated review
            orchestrated_review = await self.orchestrator.conduct_review(
                image_data=image_data,
                design_type=design_type,
                context=context or {}
            )
            
            # Process with learning system
            learning_insights = []
            if self.learning_system:
                learning_insights = self.learning_system.process_review(orchestrated_review)
            
            # Compile comprehensive results
            results = {
                "review_id": orchestrated_review.review_id,
                "timestamp": orchestrated_review.timestamp,
                "design_type": orchestrated_review.design_type,
                "overall_score": orchestrated_review.overall_score,
                "overall_assessment": self._generate_overall_assessment(orchestrated_review),
                "phase_results": self._format_phase_results(orchestrated_review.phase_results),
                "synthesis": orchestrated_review.synthesis,
                "priority_actions": orchestrated_review.priority_actions,
                "agent_consensus": self._analyze_agent_consensus(orchestrated_review),
                "learning_insights": [
                    {
                        "type": insight.insight_type,
                        "description": insight.description,
                        "confidence": insight.confidence,
                        "impact": insight.impact_score
                    } for insight in learning_insights
                ],
                "system_recommendations": self._generate_system_recommendations(orchestrated_review, learning_insights),
                "confidence_score": self._calculate_overall_confidence(orchestrated_review),
                "review_quality_metrics": self._calculate_review_quality_metrics(orchestrated_review)
            }
            
            print(f"✅ Review completed: {results['overall_score']:.1f}/10 (Confidence: {results['confidence_score']:.2f})")
            
            return results
            
        finally:
            # Restore original agents if they were filtered
            if selected_agents:
                self.orchestrator.agents = original_agents
    
    async def _apply_learning_enhancements(self, design_type: str):
        """Apply learning-based enhancements to agents."""
        if not self.learning_system:
            return
        
        for agent_type, agent in self.agents.items():
            # Get adaptive enhancements for this agent
            enhancements = self.learning_system.get_adaptive_prompt_enhancements(agent_type, design_type)
            
            # Apply enhancements if the agent supports them
            if hasattr(agent, 'apply_learning_enhancements'):
                agent.apply_learning_enhancements(enhancements)
    
    def _generate_overall_assessment(self, orchestrated_review: OrchestratedReview) -> str:
        """Generate an overall assessment summary."""
        score = orchestrated_review.overall_score
        
        if score >= 9:
            assessment = "Exceptional design that meets or exceeds best practices across all evaluated dimensions."
        elif score >= 8:
            assessment = "Strong design with minor areas for improvement. Well-executed overall approach."
        elif score >= 7:
            assessment = "Good design foundation with several areas that could be enhanced for better user experience."
        elif score >= 6:
            assessment = "Adequate design with significant improvement opportunities identified by reviewers."
        elif score >= 5:
            assessment = "Below average design requiring substantial improvements before implementation."
        else:
            assessment = "Design needs major revisions across multiple areas to meet acceptable standards."
        
        # Add specific context from agents
        agent_count = sum(len(results) for results in orchestrated_review.phase_results.values())
        consensus_level = self._calculate_consensus_level(orchestrated_review)
        
        assessment += f" Based on {agent_count} specialized reviews with {consensus_level:.0%} consensus among agents."
        
        return assessment
    
    def _format_phase_results(self, phase_results: Dict[str, List]) -> Dict[str, Any]:
        """Format phase results for better presentation."""
        formatted = {}
        
        for phase, results in phase_results.items():
            formatted[phase] = []
            
            for result in results:
                formatted_result = {
                    "agent_name": result.agent_name,
                    "agent_type": result.agent_type,
                    "score": result.score,
                    "confidence": result.confidence,
                    "summary": result.feedback[:200] + "..." if len(result.feedback) > 200 else result.feedback,
                    "key_issues": result.specific_issues[:3],  # Top 3 issues
                    "key_recommendations": result.recommendations[:3],  # Top 3 recommendations
                    "review_time": result.review_time.isoformat(),
                    "metadata": result.metadata
                }
                formatted[phase].append(formatted_result)
        
        return formatted
    
    def _analyze_agent_consensus(self, orchestrated_review: OrchestratedReview) -> Dict[str, Any]:
        """Analyze consensus among agents."""
        all_results = []
        for results in orchestrated_review.phase_results.values():
            all_results.extend(results)
        
        if not all_results:
            return {"consensus_level": 0, "agreement_areas": [], "disagreement_areas": []}
        
        scores = [result.score for result in all_results]
        confidences = [result.confidence for result in all_results]
        
        # Calculate consensus metrics
        score_variance = np.var(scores) if len(scores) > 1 else 0
        avg_confidence = np.mean(confidences)
        consensus_level = max(0, 1 - (score_variance / 10))  # Normalize variance to consensus
        
        # Find common issues and recommendations
        all_issues = []
        all_recommendations = []
        
        for result in all_results:
            all_issues.extend(result.specific_issues)
            all_recommendations.extend(result.recommendations)
        
        # Count occurrences
        from collections import Counter
        issue_counts = Counter(all_issues)
        rec_counts = Counter(all_recommendations)
        
        # Find areas of agreement (mentioned by multiple agents)
        agreement_threshold = max(2, len(all_results) // 2)
        agreement_issues = [issue for issue, count in issue_counts.items() if count >= agreement_threshold]
        agreement_recs = [rec for rec, count in rec_counts.items() if count >= agreement_threshold]
        
        return {
            "consensus_level": consensus_level,
            "score_variance": score_variance,
            "average_confidence": avg_confidence,
            "agreement_areas": {
                "issues": agreement_issues[:5],
                "recommendations": agreement_recs[:5]
            },
            "agent_perspectives": {
                result.agent_type: {
                    "score": result.score,
                    "confidence": result.confidence,
                    "focus": result.metadata.get("specialization", "General") if result.metadata else "General"
                } for result in all_results
            }
        }
    
    def _generate_system_recommendations(self, orchestrated_review: OrchestratedReview, learning_insights: List) -> List[str]:
        """Generate system-level recommendations."""
        recommendations = []
        
        # Based on overall score
        if orchestrated_review.overall_score < 6:
            recommendations.append("Consider major design revisions before proceeding to development")
        elif orchestrated_review.overall_score < 7:
            recommendations.append("Address key issues identified by multiple agents before implementation")
        elif orchestrated_review.overall_score >= 8:
            recommendations.append("Design is ready for implementation with minor refinements")
        
        # Based on consensus
        consensus_level = self._calculate_consensus_level(orchestrated_review)
        if consensus_level < 0.7:
            recommendations.append("Low agent consensus suggests need for additional design exploration")
        
        # Based on learning insights
        high_impact_insights = [insight for insight in learning_insights if insight.impact_score > 0.7]
        if high_impact_insights:
            recommendations.append(f"Apply {len(high_impact_insights)} high-impact learning insights to improve future reviews")
        
        # Based on agent-specific feedback
        accessibility_results = []
        for results in orchestrated_review.phase_results.values():
            accessibility_results.extend([r for r in results if r.agent_type == "accessibility"])
        
        if accessibility_results and any(r.score < 7 for r in accessibility_results):
            recommendations.append("Prioritize accessibility improvements for inclusive design")
        
        return recommendations
    
    def _calculate_overall_confidence(self, orchestrated_review: OrchestratedReview) -> float:
        """Calculate overall confidence score."""
        all_results = []
        for results in orchestrated_review.phase_results.values():
            all_results.extend(results)
        
        if not all_results:
            return 0.0
        
        # Weighted confidence based on agent types
        weights = {
            "analysis": 1.0,
            "peer_review": 1.1,
            "vp_review": 1.2,
            "accessibility": 1.1,
            "synthesis": 1.3
        }
        
        weighted_confidences = []
        total_weight = 0
        
        for result in all_results:
            weight = weights.get(result.agent_type, 1.0)
            weighted_confidences.append(result.confidence * weight)
            total_weight += weight
        
        return sum(weighted_confidences) / total_weight if total_weight > 0 else 0.0
    
    def _calculate_consensus_level(self, orchestrated_review: OrchestratedReview) -> float:
        """Calculate consensus level among agents."""
        all_results = []
        for results in orchestrated_review.phase_results.values():
            all_results.extend(results)
        
        if len(all_results) < 2:
            return 1.0
        
        scores = [result.score for result in all_results]
        variance = np.var(scores)
        
        # Convert variance to consensus (lower variance = higher consensus)
        return max(0, 1 - (variance / 10))
    
    def _calculate_review_quality_metrics(self, orchestrated_review: OrchestratedReview) -> Dict[str, float]:
        """Calculate quality metrics for the review process."""
        all_results = []
        for results in orchestrated_review.phase_results.values():
            all_results.extend(results)
        
        if not all_results:
            return {}
        
        # Calculate various quality metrics
        avg_confidence = np.mean([r.confidence for r in all_results])
        score_consistency = 1 - (np.var([r.score for r in all_results]) / 10)
        
        # Coverage score (how many different agent types participated)
        unique_agent_types = len(set(r.agent_type for r in all_results))
        total_possible_agents = len(self.agents)
        coverage_score = unique_agent_types / total_possible_agents
        
        # Depth score (average number of issues and recommendations)
        avg_issues = np.mean([len(r.specific_issues) for r in all_results])
        avg_recommendations = np.mean([len(r.recommendations) for r in all_results])
        depth_score = min(1.0, (avg_issues + avg_recommendations) / 10)
        
        return {
            "confidence": round(avg_confidence, 3),
            "consistency": round(max(0, score_consistency), 3),
            "coverage": round(coverage_score, 3),
            "depth": round(depth_score, 3),
            "overall_quality": round((avg_confidence + max(0, score_consistency) + coverage_score + depth_score) / 4, 3)
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        # Agent status
        agent_status = {}
        for agent_type, agent in self.agents.items():
            if hasattr(agent, 'get_agent_stats'):
                agent_status[agent_type] = agent.get_agent_stats()
            else:
                agent_status[agent_type] = {"status": "active", "type": type(agent).__name__}
        
        # Learning system status
        learning_status = {}
        if self.learning_system:
            learning_status = self.learning_system.get_learning_summary()
        
        # Orchestrator status
        orchestrator_status = {
            "registered_agents": len(self.orchestrator.agents),
            "parallel_reviews": self.orchestrator.config["parallel_reviews"],
            "confidence_threshold": self.orchestrator.config["confidence_threshold"]
        }
        
        return {
            "system_config": self.config,
            "agent_status": agent_status,
            "learning_status": learning_status,
            "orchestrator_status": orchestrator_status,
            "capabilities": {
                "web_research": bool(self.exa_api_key),
                "learning_enabled": bool(self.learning_system),
                "parallel_processing": self.config["enable_parallel_reviews"],
                "adaptive_prompts": self.config["enable_adaptive_prompts"]
            }
        }
    
    def update_system_config(self, new_config: Dict[str, Any]):
        """Update system configuration."""
        self.config.update(new_config)
        
        # Update orchestrator config
        if "enable_parallel_reviews" in new_config:
            self.orchestrator.config["parallel_reviews"] = new_config["enable_parallel_reviews"]
        
        if "confidence_threshold" in new_config:
            self.orchestrator.config["confidence_threshold"] = new_config["confidence_threshold"]


# Example usage and demo
async def demo_enhanced_system():
    """Demo the enhanced design review system."""
    
    # Initialize system
    openai_key = os.getenv('OPENAI_API_KEY')
    exa_key = os.getenv('EXA_API_KEY')
    
    if not openai_key:
        print("❌ OPENAI_API_KEY required")
        return
    
    # Create enhanced system
    system = EnhancedDesignReviewSystem(
        openai_api_key=openai_key,
        exa_api_key=exa_key,
        learning_enabled=True
    )
    
    # Get system status
    status = system.get_system_status()
    print("\n📊 System Status:")
    print(f"  Agents: {status['orchestrator_status']['registered_agents']}")
    print(f"  Learning: {status['capabilities']['learning_enabled']}")
    print(f"  Web Research: {status['capabilities']['web_research']}")
    
    # Example review (would use real image data in practice)
    print("\n🎯 Example Review Process:")
    print("  1. Load design image")
    print("  2. Apply learning enhancements")
    print("  3. Conduct multi-agent review")
    print("  4. Synthesize results")
    print("  5. Extract learning insights")
    print("  6. Update agent knowledge")
    
    print("\n✅ Enhanced Design Review System ready for use!")


if __name__ == "__main__":
    import numpy as np
    asyncio.run(demo_enhanced_system())
