"""
Multi-Agent Design Review Orchestrator

This orchestrator coordinates multiple specialized design review agents,
manages their interactions, and provides comprehensive feedback through
a coordinated approach.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.memory import ConversationBufferMemory
from agents.exa_search import ExaSearchAgent


class ReviewPhase(Enum):
    """Phases of the design review process."""
    ANALYSIS = "analysis"
    PEER_REVIEW = "peer_review"
    VP_REVIEW = "vp_review"
    ACCESSIBILITY = "accessibility"
    SYNTHESIS = "synthesis"
    LEARNING = "learning"


@dataclass
class ReviewResult:
    """Structured result from an agent review."""
    agent_type: str
    agent_name: str
    score: float  # 1-10 rating
    feedback: str
    specific_issues: List[str]
    recommendations: List[str]
    confidence: float  # 0-1 confidence level
    review_time: datetime
    metadata: Dict[str, Any] = None


@dataclass
class OrchestratedReview:
    """Complete orchestrated review result."""
    overall_score: float
    phase_results: Dict[str, List[ReviewResult]]
    synthesis: str
    priority_actions: List[str]
    learning_insights: List[str]
    review_id: str
    timestamp: datetime
    design_type: str


class ReviewOrchestrator:
    """
    Orchestrates multiple design review agents for comprehensive feedback.
    """
    
    def __init__(self, 
                 openai_api_key: str,
                 exa_api_key: Optional[str] = None,
                 model_name: str = "gpt-4-turbo"):
        """
        Initialize the review orchestrator.
        
        Args:
            openai_api_key: OpenAI API key
            exa_api_key: Optional Exa API key for web research
            model_name: OpenAI model to use
        """
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=0.2,
            max_tokens=2000
        )
        
        # Initialize web research capability
        self.exa_agent = None
        if exa_api_key:
            try:
                self.exa_agent = ExaSearchAgent(exa_api_key)
            except Exception as e:
                logging.warning(f"Could not initialize Exa search: {e}")
        
        # Agent registry - will be populated by specialized agents
        self.agents = {}
        
        # Learning system
        self.learning_memory = ConversationBufferMemory(return_messages=True)
        self.review_history = []
        
        # Configuration
        self.config = {
            "parallel_reviews": True,
            "enable_learning": True,
            "confidence_threshold": 0.7,
            "consensus_threshold": 0.8
        }
        
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def register_agent(self, agent_type: str, agent_instance):
        """Register a specialized agent with the orchestrator."""
        self.agents[agent_type] = agent_instance
        self.logger.info(f"Registered agent: {agent_type}")
    
    async def conduct_review(self, 
                           image_data: str,
                           design_type: str,
                           context: Dict[str, Any] = None) -> OrchestratedReview:
        """
        Conduct a comprehensive multi-agent design review.
        
        Args:
            image_data: Base64 encoded image data
            design_type: Type of design being reviewed
            context: Additional context for the review
            
        Returns:
            Comprehensive orchestrated review result
        """
        review_id = f"review_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.logger.info(f"Starting orchestrated review {review_id}")
        
        # Phase 1: Initial Analysis
        analysis_results = await self._conduct_analysis_phase(image_data, design_type, context)
        
        # Phase 2: Parallel Specialized Reviews
        if self.config["parallel_reviews"]:
            specialized_results = await self._conduct_parallel_reviews(image_data, design_type, context, analysis_results)
        else:
            specialized_results = await self._conduct_sequential_reviews(image_data, design_type, context, analysis_results)
        
        # Phase 3: Synthesis and Consensus
        synthesis_result = await self._conduct_synthesis_phase(analysis_results, specialized_results, design_type)
        
        # Phase 4: Learning Phase
        learning_insights = []
        if self.config["enable_learning"]:
            learning_insights = await self._conduct_learning_phase(analysis_results, specialized_results, synthesis_result)
        
        # Compile final result
        all_results = {
            ReviewPhase.ANALYSIS.value: analysis_results,
            **specialized_results,
            ReviewPhase.SYNTHESIS.value: [synthesis_result] if synthesis_result else []
        }
        
        orchestrated_review = OrchestratedReview(
            overall_score=self._calculate_overall_score(all_results),
            phase_results=all_results,
            synthesis=synthesis_result.feedback if synthesis_result else "",
            priority_actions=self._extract_priority_actions(all_results),
            learning_insights=learning_insights,
            review_id=review_id,
            timestamp=datetime.now(),
            design_type=design_type
        )
        
        # Store for learning
        self.review_history.append(orchestrated_review)
        
        return orchestrated_review
    
    async def _conduct_analysis_phase(self, 
                                    image_data: str,
                                    design_type: str,
                                    context: Dict[str, Any]) -> List[ReviewResult]:
        """Conduct initial analysis phase."""
        results = []
        
        # Get web research context if available
        web_context = ""
        if self.exa_agent:
            try:
                research_results = self.exa_agent.comprehensive_design_research(f"{design_type} design")
                web_context = self._format_research_context(research_results)
            except Exception as e:
                self.logger.warning(f"Web research failed: {e}")
        
        # Initial analysis prompt
        analysis_prompt = f"""
        You are conducting an initial analysis of a {design_type} design.
        
        Web Research Context:
        {web_context}
        
        Provide a comprehensive initial analysis focusing on:
        1. Overall design quality and approach
        2. Key strengths and weaknesses
        3. Areas that need specialized review
        4. Initial recommendations
        
        Rate the design on a scale of 1-10 and provide your confidence level (0-1).
        """
        
        try:
            messages = [
                SystemMessage(content=analysis_prompt),
                HumanMessage(content=[
                    {"type": "text", "text": "Please analyze this design image."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
                ])
            ]
            
            response = await self.llm.ainvoke(messages)
            
            # Parse response (simplified - would use more sophisticated parsing)
            result = ReviewResult(
                agent_type="analysis",
                agent_name="Initial Analyzer",
                score=7.5,  # Would parse from response
                feedback=response.content,
                specific_issues=[],  # Would extract from response
                recommendations=[],  # Would extract from response
                confidence=0.8,  # Would parse from response
                review_time=datetime.now()
            )
            
            results.append(result)
            
        except Exception as e:
            self.logger.error(f"Analysis phase failed: {e}")
        
        return results
    
    async def _conduct_parallel_reviews(self, 
                                      image_data: str,
                                      design_type: str,
                                      context: Dict[str, Any],
                                      analysis_results: List[ReviewResult]) -> Dict[str, List[ReviewResult]]:
        """Conduct specialized reviews in parallel."""
        tasks = []
        
        # Create tasks for each registered agent
        for agent_type, agent in self.agents.items():
            if hasattr(agent, 'async_review'):
                task = agent.async_review(image_data, design_type, context, analysis_results)
                tasks.append((agent_type, task))
        
        # Execute all tasks in parallel
        results = {}
        if tasks:
            completed_tasks = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)
            
            for (agent_type, _), result in zip(tasks, completed_tasks):
                if isinstance(result, Exception):
                    self.logger.error(f"Agent {agent_type} failed: {result}")
                    results[agent_type] = []
                else:
                    results[agent_type] = result if isinstance(result, list) else [result]
        
        return results
    
    async def _conduct_sequential_reviews(self, 
                                        image_data: str,
                                        design_type: str,
                                        context: Dict[str, Any],
                                        analysis_results: List[ReviewResult]) -> Dict[str, List[ReviewResult]]:
        """Conduct specialized reviews sequentially."""
        results = {}
        
        for agent_type, agent in self.agents.items():
            try:
                if hasattr(agent, 'async_review'):
                    result = await agent.async_review(image_data, design_type, context, analysis_results)
                elif hasattr(agent, 'review'):
                    result = agent.review(image_data, design_type, context, analysis_results)
                else:
                    continue
                
                results[agent_type] = result if isinstance(result, list) else [result]
                
            except Exception as e:
                self.logger.error(f"Agent {agent_type} failed: {e}")
                results[agent_type] = []
        
        return results
    
    async def _conduct_synthesis_phase(self, 
                                     analysis_results: List[ReviewResult],
                                     specialized_results: Dict[str, List[ReviewResult]],
                                     design_type: str) -> Optional[ReviewResult]:
        """Synthesize all review results into comprehensive feedback."""
        
        # Compile all results
        all_results = analysis_results.copy()
        for results_list in specialized_results.values():
            all_results.extend(results_list)
        
        if not all_results:
            return None
        
        # Create synthesis prompt
        results_summary = self._format_results_for_synthesis(all_results)
        
        synthesis_prompt = f"""
        You are synthesizing multiple expert design reviews into a comprehensive final assessment.
        
        Review Results Summary:
        {results_summary}
        
        Provide a synthesized review that:
        1. Identifies consensus points among reviewers
        2. Addresses conflicting opinions
        3. Prioritizes the most critical issues
        4. Provides a unified set of recommendations
        5. Assigns an overall quality score (1-10)
        
        Focus on actionable insights and clear priorities.
        """
        
        try:
            messages = [SystemMessage(content=synthesis_prompt)]
            response = await self.llm.ainvoke(messages)
            
            synthesis_result = ReviewResult(
                agent_type="synthesis",
                agent_name="Review Synthesizer",
                score=self._calculate_overall_score({"all": all_results}),
                feedback=response.content,
                specific_issues=self._extract_consensus_issues(all_results),
                recommendations=self._extract_consensus_recommendations(all_results),
                confidence=self._calculate_consensus_confidence(all_results),
                review_time=datetime.now()
            )
            
            return synthesis_result
            
        except Exception as e:
            self.logger.error(f"Synthesis phase failed: {e}")
            return None
    
    async def _conduct_learning_phase(self, 
                                    analysis_results: List[ReviewResult],
                                    specialized_results: Dict[str, List[ReviewResult]],
                                    synthesis_result: Optional[ReviewResult]) -> List[str]:
        """Extract learning insights from the review process."""
        insights = []
        
        # Analyze patterns in reviews
        all_results = analysis_results.copy()
        for results_list in specialized_results.values():
            all_results.extend(results_list)
        
        if len(self.review_history) > 5:  # Need some history to learn from
            # Compare with historical reviews
            similar_reviews = self._find_similar_reviews(all_results[-1] if all_results else None)
            
            if similar_reviews:
                learning_prompt = f"""
                Analyze the patterns in these design reviews to extract learning insights:
                
                Current Review Summary: {self._format_results_for_synthesis(all_results)}
                
                Similar Historical Reviews: {len(similar_reviews)} reviews found
                
                Identify:
                1. Recurring issues across similar designs
                2. Effective recommendations that appear frequently
                3. Agent performance patterns
                4. Areas where review quality could be improved
                
                Provide 3-5 key learning insights for improving future reviews.
                """
                
                try:
                    messages = [SystemMessage(content=learning_prompt)]
                    response = await self.llm.ainvoke(messages)
                    
                    # Parse insights from response
                    insights = [line.strip() for line in response.content.split('\n') 
                              if line.strip() and any(char.isalpha() for char in line)]
                    
                except Exception as e:
                    self.logger.error(f"Learning phase failed: {e}")
        
        return insights[:5]  # Limit to top 5 insights
    
    def _calculate_overall_score(self, results: Dict[str, List[ReviewResult]]) -> float:
        """Calculate overall score from all review results."""
        all_scores = []
        total_weight = 0
        
        weights = {
            "analysis": 1.0,
            "peer_review": 1.2,
            "vp_review": 1.5,
            "accessibility": 1.3,
            "synthesis": 1.1
        }
        
        for phase, phase_results in results.items():
            weight = weights.get(phase, 1.0)
            for result in phase_results:
                all_scores.append(result.score * weight * result.confidence)
                total_weight += weight * result.confidence
        
        if total_weight == 0:
            return 0.0
        
        return sum(all_scores) / total_weight
    
    def _extract_priority_actions(self, results: Dict[str, List[ReviewResult]]) -> List[str]:
        """Extract priority actions from all review results."""
        actions = []
        
        # Collect all recommendations
        all_recommendations = []
        for phase_results in results.values():
            for result in phase_results:
                all_recommendations.extend(result.recommendations)
        
        # Use LLM to prioritize (simplified implementation)
        if all_recommendations:
            # For now, return top recommendations
            # In practice, would use LLM to analyze and prioritize
            actions = list(set(all_recommendations))[:5]
        
        return actions
    
    def _format_research_context(self, research_results: Dict[str, List]) -> str:
        """Format web research results for prompt context."""
        context_parts = []
        
        for category, documents in research_results.items():
            if documents:
                context_parts.append(f"\n{category.replace('_', ' ').title()}:")
                for doc in documents[:2]:  # Limit to top 2 per category
                    if hasattr(doc, 'metadata'):
                        context_parts.append(f"- {doc.metadata.get('title', 'Unknown')}")
                        if hasattr(doc, 'page_content') and doc.page_content:
                            preview = doc.page_content[:150] + "..." if len(doc.page_content) > 150 else doc.page_content
                            context_parts.append(f"  {preview}")
        
        return "\n".join(context_parts)
    
    def _format_results_for_synthesis(self, results: List[ReviewResult]) -> str:
        """Format review results for synthesis prompt."""
        formatted = []
        
        for result in results:
            formatted.append(f"""
Agent: {result.agent_name} ({result.agent_type})
Score: {result.score}/10 (Confidence: {result.confidence:.2f})
Issues: {', '.join(result.specific_issues[:3])}
Top Recommendations: {', '.join(result.recommendations[:2])}
""")
        
        return "\n".join(formatted)
    
    def _extract_consensus_issues(self, results: List[ReviewResult]) -> List[str]:
        """Extract issues that multiple agents agree on."""
        issue_counts = {}
        
        for result in results:
            for issue in result.specific_issues:
                issue_counts[issue] = issue_counts.get(issue, 0) + 1
        
        # Return issues mentioned by multiple agents
        consensus_threshold = max(2, len(results) // 2)
        return [issue for issue, count in issue_counts.items() if count >= consensus_threshold]
    
    def _extract_consensus_recommendations(self, results: List[ReviewResult]) -> List[str]:
        """Extract recommendations that multiple agents agree on."""
        rec_counts = {}
        
        for result in results:
            for rec in result.recommendations:
                rec_counts[rec] = rec_counts.get(rec, 0) + 1
        
        # Return recommendations mentioned by multiple agents
        consensus_threshold = max(2, len(results) // 2)
        return [rec for rec, count in rec_counts.items() if count >= consensus_threshold]
    
    def _calculate_consensus_confidence(self, results: List[ReviewResult]) -> float:
        """Calculate confidence based on consensus among agents."""
        if not results:
            return 0.0
        
        # Calculate variance in scores as inverse confidence indicator
        scores = [r.score for r in results]
        if len(scores) <= 1:
            return results[0].confidence if results else 0.0
        
        mean_score = sum(scores) / len(scores)
        variance = sum((s - mean_score) ** 2 for s in scores) / len(scores)
        
        # Lower variance = higher confidence
        consensus_factor = max(0, 1 - (variance / 10))  # Normalize variance
        avg_confidence = sum(r.confidence for r in results) / len(results)
        
        return (consensus_factor + avg_confidence) / 2
    
    def _find_similar_reviews(self, current_result: Optional[ReviewResult]) -> List[OrchestratedReview]:
        """Find similar reviews from history for learning."""
        if not current_result or not self.review_history:
            return []
        
        # Simple similarity based on design type and score range
        similar = []
        score_threshold = 1.5
        
        for historical_review in self.review_history[-10:]:  # Check last 10 reviews
            if (historical_review.design_type == current_result.agent_type and
                abs(historical_review.overall_score - current_result.score) <= score_threshold):
                similar.append(historical_review)
        
        return similar
    
    def get_learning_summary(self) -> Dict[str, Any]:
        """Get a summary of learning insights across all reviews."""
        if not self.review_history:
            return {"message": "No review history available for learning analysis."}
        
        total_reviews = len(self.review_history)
        avg_score = sum(r.overall_score for r in self.review_history) / total_reviews
        
        # Collect all learning insights
        all_insights = []
        for review in self.review_history:
            all_insights.extend(review.learning_insights)
        
        # Count most common insights
        insight_counts = {}
        for insight in all_insights:
            insight_counts[insight] = insight_counts.get(insight, 0) + 1
        
        top_insights = sorted(insight_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "total_reviews": total_reviews,
            "average_score": round(avg_score, 2),
            "top_learning_insights": [insight for insight, count in top_insights],
            "recent_trend": "improving" if len(self.review_history) >= 3 and 
                           self.review_history[-1].overall_score > self.review_history[-3].overall_score else "stable"
        }


# Example usage and testing
if __name__ == "__main__":
    import os
    
    # Initialize orchestrator
    openai_key = os.getenv('OPENAI_API_KEY')
    exa_key = os.getenv('EXA_API_KEY')
    
    if openai_key:
        orchestrator = ReviewOrchestrator(openai_key, exa_key)
        print("✅ Review Orchestrator initialized successfully")
        print(f"🔍 Web research: {'enabled' if exa_key else 'disabled'}")
        print(f"🤖 Registered agents: {len(orchestrator.agents)}")
    else:
        print("❌ OPENAI_API_KEY required to initialize orchestrator")
