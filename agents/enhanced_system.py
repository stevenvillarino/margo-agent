"""
Enhanced Multi-Agent Design Review System

This system integrates all specialized review agents with learning capabilities
and provides comprehensive design evaluation with continuous improvement.
"""

import asyncio
import json
import base64
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict

from agents.orchestrator import ReviewOrchestrator, ReviewResult, ReviewPhase, OrchestratedReview
from agents.peer_review_agent import PeerDesignReviewAgent, create_peer_reviewer
from agents.vp_product_agent import MargoVPDesignAgent
from agents.accessibility_agent import AccessibilityReviewAgent
from agents.quality_evaluation_agent import QualityEvaluationAgent
from agents.learning_system import AgentLearningSystem
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
            openai_api_key: OpenAI API key for LLM interactions
            exa_api_key: Optional Exa API key for web research
            learning_enabled: Whether to enable the learning system
            company_context: Optional company context for customization
        """
        self.openai_api_key = openai_api_key
        self.exa_api_key = exa_api_key
        self.learning_enabled = learning_enabled
        
        # Initialize orchestrator with API keys
        self.orchestrator = ReviewOrchestrator(
            openai_api_key=openai_api_key,
            exa_api_key=exa_api_key
        )
        
        # Initialize optional components
        self.exa_agent = None
        if exa_api_key:
            try:
                self.exa_agent = ExaSearchAgent(exa_api_key)
            except Exception as e:
                print(f"Warning: Could not initialize Exa search: {e}")
        
        self.learning_system = None
        if learning_enabled:
            try:
                self.learning_system = AgentLearningSystem()
            except Exception as e:
                print(f"Warning: Could not initialize learning system: {e}")
        
        # Initialize workflow orchestrator (will be set after this instance is created)
        self.workflow_orchestrator = None
        
        # System configuration
        self.config = {
            "enable_parallel_reviews": True,
            "enable_learning": learning_enabled,
            "enable_adaptive_prompts": learning_enabled,
            "min_agents_for_review": 2,
            "confidence_threshold": 0.7
        }
        
        # Initialize agents
        self._initialize_agents(company_context)
        
        print("🎯 Enhanced Design Review System initialized")
        print(f"📊 Agents registered: {len(self.orchestrator.agents)}")
        print(f"🧠 Learning system: {'enabled' if self.learning_system else 'disabled'}")
        print(f"🔍 Web research: {'enabled' if self.exa_agent else 'disabled'}")
    
    def set_workflow_orchestrator(self, workflow_orchestrator):
        """Set the workflow orchestrator after initialization to avoid circular imports."""
        self.workflow_orchestrator = workflow_orchestrator
    
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
        
        vp_agent = MargoVPDesignAgent(
            openai_api_key=self.openai_api_key,
            design_vision=vp_context,  # Fixed parameter name
            design_priorities=vp_priorities,  # Fixed parameter name
            exa_api_key=self.exa_api_key
        )
        
        # Create accessibility agent
        accessibility_agent = AccessibilityReviewAgent(
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
                
                # Learn from this design review for future improvements
                await self._learn_from_design_review(orchestrated_review, design_type, context)
            
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

    async def handle_knowledge_question(self, question: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Handle knowledge questions using the workflow orchestrator."""
        try:
            # Use the workflow orchestrator to detect and handle knowledge gaps
            result = await self.workflow_orchestrator.handle_knowledge_question(question, user_id)
            
            # Log the interaction for learning and knowledge evolution
            if hasattr(self.learning_system, 'log_interaction'):
                await self.learning_system.log_interaction(
                    question=question,
                    response=result.get('answer', ''),
                    confidence=result.get('confidence', 0.0),
                    user_id=user_id
                )
            
            # Learn from this knowledge interaction
            await self._learn_from_knowledge_interaction(question, result, user_id)
            
            return result
            
        except Exception as e:
            print(f"Error handling knowledge question: {e}")
            # Even errors are learning opportunities
            if self.learning_system:
                await self.learning_system.log_knowledge_gap(question, "system_error", user_id)
            
            return {
                'answer': 'I apologize, but I encountered an error processing your question.',
                'confidence': 0.0,
                'error': str(e)
            }

    async def _learn_from_knowledge_interaction(self, question: str, result: Dict[str, Any], user_id: Optional[str] = None):
        """Learn from knowledge interactions to improve future responses."""
        if not self.learning_system:
            return
            
        try:
            # Categorize the question type for learning
            question_category = self._categorize_question(question)
            
            # Track question patterns
            await self.learning_system.track_question_pattern(
                question=question,
                category=question_category,
                confidence=result.get('confidence', 0.0),
                user_id=user_id,
                timestamp=datetime.now()
            )
            
            # If confidence is low, this is a learning opportunity
            if result.get('confidence', 0.0) < 0.7:
                await self.learning_system.identify_knowledge_gap(
                    question=question,
                    category=question_category,
                    current_knowledge=result.get('answer', ''),
                    suggested_improvements=self._suggest_knowledge_improvements(question, result)
                )
                
            # Learn from successful knowledge provision
            elif result.get('confidence', 0.0) > 0.8:
                await self.learning_system.reinforce_knowledge_pattern(
                    question=question,
                    category=question_category,
                    successful_response=result.get('answer', '')
                )
                
        except Exception as e:
            print(f"Error in knowledge learning: {e}")

    def _categorize_question(self, question: str) -> str:
        """Categorize questions to help the system learn patterns."""
        question_lower = question.lower()
        
        # Brand and guidelines
        if any(keyword in question_lower for keyword in ['brand', 'guideline', 'standard', 'style', 'color', 'font', 'logo']):
            return 'brand_guidelines'
        
        # Accessibility
        elif any(keyword in question_lower for keyword in ['accessibility', 'a11y', 'wcag', 'screen reader', 'contrast']):
            return 'accessibility'
        
        # User experience
        elif any(keyword in question_lower for keyword in ['user', 'experience', 'usability', 'journey', 'flow']):
            return 'user_experience'
        
        # Technical implementation
        elif any(keyword in question_lower for keyword in ['implement', 'code', 'technical', 'development', 'css', 'react']):
            return 'technical_implementation'
        
        # Design patterns
        elif any(keyword in question_lower for keyword in ['pattern', 'component', 'layout', 'grid', 'navigation']):
            return 'design_patterns'
        
        # Performance
        elif any(keyword in question_lower for keyword in ['performance', 'speed', 'optimization', 'loading']):
            return 'performance'
        
        # Business/product
        elif any(keyword in question_lower for keyword in ['business', 'kpi', 'metric', 'conversion', 'engagement']):
            return 'business_product'
        
        else:
            return 'general_design'

    def _suggest_knowledge_improvements(self, question: str, result: Dict[str, Any]) -> List[str]:
        """Suggest how to improve knowledge for similar future questions."""
        suggestions = []
        category = self._categorize_question(question)
        
        if category == 'brand_guidelines':
            suggestions.extend([
                "Add more detailed brand documentation",
                "Include visual examples of brand application",
                "Create brand decision trees for common scenarios",
                "Connect to official brand asset libraries"
            ])
        elif category == 'accessibility':
            suggestions.extend([
                "Expand WCAG guidelines database",
                "Add more accessibility testing tools",
                "Include real user feedback on accessibility",
                "Create accessibility pattern library"
            ])
        elif category == 'design_patterns':
            suggestions.extend([
                "Build comprehensive design pattern library",
                "Document when to use each pattern",
                "Include anti-patterns to avoid",
                "Add pattern performance implications"
            ])
        else:
            suggestions.extend([
                f"Expand knowledge base for {category} questions",
                "Connect to more external knowledge sources",
                "Gather expert input for this domain",
                "Create decision frameworks for this area"
            ])
            
        return suggestions

    async def enhanced_review_with_knowledge_integration(self, image_data: str, design_type: str, user_question: str = None, user_id: str = None) -> Dict[str, Any]:
        """Enhanced review that integrates knowledge gap detection and learning."""
        try:
            # Check if this is primarily a knowledge question
            if user_question and any(keyword in user_question.lower() for keyword in ['brand', 'guideline', 'standard', 'policy', 'requirement']):
                knowledge_result = await self.handle_knowledge_question(user_question, user_id)
                
                # If we have good knowledge, combine it with the design review
                if knowledge_result.get('confidence', 0) > 0.7:
                    review_result = await self.conduct_comprehensive_review(
                        image_data=image_data,
                        design_type=design_type,
                        context={'user_question': user_question}
                    )
                    
                    # Merge knowledge and review results
                    return {
                        'review': review_result,
                        'knowledge': knowledge_result,
                        'type': 'integrated_review',
                        'timestamp': datetime.now().isoformat()
                    }
            
            # Standard comprehensive review
            return await self.conduct_comprehensive_review(
                image_data=image_data,
                design_type=design_type,
                context={'user_question': user_question} if user_question else None
            )
            
        except Exception as e:
            print(f"Error in enhanced review with knowledge integration: {e}")
            return await self.conduct_comprehensive_review(
                image_data=image_data,
                design_type=design_type,
                context={'user_question': user_question} if user_question else None
            )

    async def _learn_from_design_review(self, orchestrated_review: OrchestratedReview, design_type: str, context: Dict[str, Any] = None):
        """Learn from design reviews to improve future analysis and knowledge."""
        if not self.learning_system:
            return
            
        try:
            # Extract learning patterns from the review
            score = orchestrated_review.overall_score
            consensus_level = self._calculate_consensus_level(orchestrated_review)
            
            # Learn from high-quality reviews (good score + high consensus)
            if score >= 8.0 and consensus_level >= 0.8:
                await self._learn_from_successful_design(orchestrated_review, design_type, context)
            
            # Learn from problematic reviews (low score or low consensus)
            elif score < 6.0 or consensus_level < 0.6:
                await self._learn_from_problematic_design(orchestrated_review, design_type, context)
            
            # Learn from agent disagreements
            if consensus_level < 0.7:
                await self._learn_from_agent_disagreement(orchestrated_review)
                
            # Learn from user context patterns
            if context and context.get('user_question'):
                await self._learn_from_user_context(context['user_question'], orchestrated_review)
                
        except Exception as e:
            print(f"Error learning from design review: {e}")

    async def _learn_from_successful_design(self, review: OrchestratedReview, design_type: str, context: Dict[str, Any] = None):
        """Learn patterns from highly successful designs."""
        if not self.learning_system:
            return
            
        # Extract success patterns
        successful_elements = []
        
        for phase_results in review.phase_results.values():
            for result in phase_results:
                if result.score >= 8.0:
                    # Extract what this agent found successful
                    successful_elements.extend([
                        rec for rec in result.recommendations 
                        if any(positive in rec.lower() for positive in ['excellent', 'great', 'strong', 'effective'])
                    ])
        
        # Learn the pattern
        await self.learning_system.record_success_pattern(
            design_type=design_type,
            elements=successful_elements,
            score=review.overall_score,
            context=context or {}
        )

    async def _learn_from_problematic_design(self, review: OrchestratedReview, design_type: str, context: Dict[str, Any] = None):
        """Learn from designs that had issues."""
        if not self.learning_system:
            return
            
        # Extract problem patterns
        common_issues = []
        
        for phase_results in review.phase_results.values():
            for result in phase_results:
                if result.score < 6.0:
                    common_issues.extend(result.specific_issues)
        
        # Find the most common issues
        from collections import Counter
        issue_frequency = Counter(common_issues)
        top_issues = [issue for issue, count in issue_frequency.most_common(5)]
        
        # Learn to watch for these patterns
        await self.learning_system.record_failure_pattern(
            design_type=design_type,
            common_issues=top_issues,
            score=review.overall_score,
            context=context or {}
        )

    async def _learn_from_agent_disagreement(self, review: OrchestratedReview):
        """Learn from cases where agents disagree significantly."""
        if not self.learning_system:
            return
            
        # Find areas of disagreement
        all_results = []
        for results in review.phase_results.values():
            all_results.extend(results)
        
        if len(all_results) < 2:
            return
            
        # Group by agent type and compare
        agent_scores = {}
        agent_issues = {}
        
        for result in all_results:
            agent_scores[result.agent_type] = result.score
            agent_issues[result.agent_type] = result.specific_issues
        
        # Find disagreement patterns
        score_variance = np.var(list(agent_scores.values()))
        
        if score_variance > 4.0:  # High disagreement
            # Learn about what causes disagreement
            await self.learning_system.record_disagreement_pattern(
                agent_scores=agent_scores,
                agent_issues=agent_issues,
                variance=score_variance,
                review_context={"design_type": review.design_type}
            )

    async def _learn_from_user_context(self, user_question: str, review: OrchestratedReview):
        """Learn from what users ask about in relation to reviews."""
        if not self.learning_system:
            return
            
        question_category = self._categorize_question(user_question)
        
        # Learn about user intent vs. review outcomes
        await self.learning_system.correlate_user_intent_with_outcomes(
            question=user_question,
            category=question_category,
            review_score=review.overall_score,
            agent_findings=self._extract_key_findings(review)
        )

    def _extract_key_findings(self, review: OrchestratedReview) -> Dict[str, List[str]]:
        """Extract key findings from a review for learning purposes."""
        findings = {
            'strengths': [],
            'issues': [],
            'recommendations': []
        }
        
        for phase_results in review.phase_results.values():
            for result in phase_results:
                # Extract positive findings
                positive_feedback = [
                    item for item in result.recommendations 
                    if any(positive in item.lower() for positive in ['good', 'strong', 'effective', 'excellent'])
                ]
                findings['strengths'].extend(positive_feedback[:2])  # Top 2
                
                # Extract issues
                findings['issues'].extend(result.specific_issues[:2])  # Top 2
                
                # Extract actionable recommendations
                actionable_recs = [
                    item for item in result.recommendations 
                    if any(action in item.lower() for action in ['should', 'consider', 'improve', 'add', 'remove'])
                ]
                findings['recommendations'].extend(actionable_recs[:2])  # Top 2
        
        return findings
    
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


def create_enhanced_design_review_system(
    openai_api_key: str,
    exa_api_key: Optional[str] = None,
    learning_enabled: bool = True,
    company_context: Dict[str, Any] = None,
    jira_config: Optional[Dict[str, str]] = None,
    playwright_config: Optional[Dict[str, Any]] = None
) -> 'EnhancedDesignReviewSystem':
    """
    Factory function to create an enhanced design review system with workflow orchestrator.
    
    This function handles the circular import issue by creating the enhanced system first,
    then creating the workflow orchestrator with the enhanced system as a dependency.
    
    Args:
        openai_api_key: OpenAI API key
        exa_api_key: Optional Exa API key for research
        learning_enabled: Whether to enable learning capabilities
        company_context: Optional company context for customization
        jira_config: Optional JIRA configuration for issue tracking
        playwright_config: Optional Playwright configuration for testing
        
    Returns:
        Fully configured EnhancedDesignReviewSystem with workflow orchestrator
    """
    # Create the enhanced system first
    system = EnhancedDesignReviewSystem(
        openai_api_key=openai_api_key,
        exa_api_key=exa_api_key,
        learning_enabled=learning_enabled,
        company_context=company_context
    )
    
    # Import and create workflow orchestrator here to avoid circular import
    try:
        from agents.workflow_orchestrator import WorkflowOrchestrator
        workflow_orchestrator = WorkflowOrchestrator(
            enhanced_system=system,
            exa_api_key=exa_api_key,
            jira_config=jira_config,
            playwright_config=playwright_config
        )
        system.set_workflow_orchestrator(workflow_orchestrator)
        print("🔄 Workflow orchestrator initialized and connected")
    except ImportError as e:
        print(f"Warning: Could not initialize workflow orchestrator: {e}")
    
    return system


# Example usage and demo
async def demo_enhanced_system():
    """Demo the enhanced design review system."""
    
    # Initialize system
    openai_key = os.getenv('OPENAI_API_KEY')
    exa_key = os.getenv('EXA_API_KEY')
    
    if not openai_key:
        print("❌ OPENAI_API_KEY required")
        return
    
    # Create enhanced system using the factory function
    system = create_enhanced_design_review_system(
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
