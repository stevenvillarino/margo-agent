"""
Agent Learning System

This system enables agents to learn from their review patterns, outcomes,
and feedback to improve their performance over time.
"""

import json
import pickle
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
import numpy as np
from pathlib import Path

from agents.orchestrator import ReviewResult, OrchestratedReview


@dataclass
class LearningInsight:
    """A learning insight extracted from review patterns."""
    insight_type: str
    description: str
    confidence: float
    evidence_count: int
    impact_score: float
    created_at: datetime
    agent_types: List[str]


@dataclass
class PerformanceMetric:
    """Performance metric for an agent."""
    metric_name: str
    current_value: float
    historical_values: List[float]
    trend: str  # "improving", "declining", "stable"
    target_value: Optional[float] = None


class AgentLearningSystem:
    """
    Learning system that helps agents improve their performance over time
    through pattern recognition, feedback analysis, and adaptive prompting.
    """
    
    def __init__(self, 
                 storage_path: str = "learning_data",
                 min_reviews_for_learning: int = 5,
                 confidence_threshold: float = 0.7):
        """
        Initialize the learning system.
        
        Args:
            storage_path: Path to store learning data
            min_reviews_for_learning: Minimum reviews needed before learning
            confidence_threshold: Minimum confidence for acting on insights
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        
        self.min_reviews_for_learning = min_reviews_for_learning
        self.confidence_threshold = confidence_threshold
        
        # Learning data storage
        self.review_patterns = defaultdict(list)
        self.agent_performance = defaultdict(dict)
        self.learning_insights = []
        self.feedback_correlations = {}
        
        # Pattern recognition
        self.issue_patterns = defaultdict(Counter)
        self.recommendation_patterns = defaultdict(Counter)
        self.score_patterns = defaultdict(list)
        
        # Load existing learning data
        self._load_learning_data()
        
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def process_review(self, orchestrated_review: OrchestratedReview) -> List[LearningInsight]:
        """
        Process a completed review to extract learning insights.
        
        Args:
            orchestrated_review: Completed orchestrated review
            
        Returns:
            List of new learning insights
        """
        insights = []
        
        # Store review data
        self._store_review_data(orchestrated_review)
        
        # Extract patterns
        self._update_patterns(orchestrated_review)
        
        # Generate insights if we have enough data
        if self._has_sufficient_data():
            # Analyze agent performance patterns
            performance_insights = self._analyze_agent_performance()
            insights.extend(performance_insights)
            
            # Analyze issue patterns
            issue_insights = self._analyze_issue_patterns()
            insights.extend(issue_insights)
            
            # Analyze consensus patterns
            consensus_insights = self._analyze_consensus_patterns()
            insights.extend(consensus_insights)
            
            # Analyze improvement opportunities
            improvement_insights = self._identify_improvement_opportunities()
            insights.extend(improvement_insights)
        
        # Store new insights
        self.learning_insights.extend(insights)
        
        # Save learning data
        self._save_learning_data()
        
        return insights
    
    def get_adaptive_prompt_enhancements(self, agent_type: str, design_type: str) -> Dict[str, Any]:
        """
        Get adaptive prompt enhancements based on learning insights.
        
        Args:
            agent_type: Type of agent requesting enhancements
            design_type: Type of design being reviewed
            
        Returns:
            Dictionary with prompt enhancements
        """
        enhancements = {
            "focus_areas": [],
            "warning_patterns": [],
            "success_patterns": [],
            "confidence_adjustments": {},
            "scoring_guidance": ""
        }
        
        # Get relevant insights for this agent type
        relevant_insights = [
            insight for insight in self.learning_insights
            if agent_type in insight.agent_types and insight.confidence >= self.confidence_threshold
        ]
        
        if not relevant_insights:
            return enhancements
        
        # Extract focus areas from high-impact insights
        for insight in relevant_insights:
            if insight.impact_score >= 0.7:
                if "focus" in insight.insight_type.lower():
                    enhancements["focus_areas"].append(insight.description)
                elif "warning" in insight.insight_type.lower():
                    enhancements["warning_patterns"].append(insight.description)
                elif "success" in insight.insight_type.lower():
                    enhancements["success_patterns"].append(insight.description)
        
        # Get agent-specific performance adjustments
        if agent_type in self.agent_performance:
            performance_data = self.agent_performance[agent_type]
            
            # Scoring guidance based on historical patterns
            avg_score = np.mean(performance_data.get("scores", [7.0]))
            score_variance = np.var(performance_data.get("scores", [7.0]))
            
            if score_variance > 2.0:  # High variance
                enhancements["scoring_guidance"] = (
                    "Previous reviews show inconsistent scoring. "
                    "Focus on specific, measurable criteria for more consistent evaluation."
                )
            elif avg_score < 6.0:  # Consistently low scores
                enhancements["scoring_guidance"] = (
                    "Previous reviews tend to be quite critical. "
                    "Consider balancing critique with recognition of positive elements."
                )
            elif avg_score > 8.5:  # Consistently high scores
                enhancements["scoring_guidance"] = (
                    "Previous reviews tend to be lenient. "
                    "Look more critically for areas that could be improved."
                )
        
        return enhancements
    
    def get_learning_summary(self) -> Dict[str, Any]:
        """Get comprehensive learning summary across all agents."""
        
        if not self.learning_insights:
            return {"message": "Insufficient data for learning analysis"}
        
        # Categorize insights
        insight_categories = defaultdict(list)
        for insight in self.learning_insights:
            insight_categories[insight.insight_type].append(insight)
        
        # Calculate learning metrics
        total_reviews = sum(len(patterns) for patterns in self.review_patterns.values())
        avg_confidence = np.mean([insight.confidence for insight in self.learning_insights])
        
        # Get top learning insights
        top_insights = sorted(
            self.learning_insights, 
            key=lambda x: x.impact_score * x.confidence, 
            reverse=True
        )[:10]
        
        # Agent performance summary
        agent_performance_summary = {}
        for agent_type, performance_data in self.agent_performance.items():
            scores = performance_data.get("scores", [])
            if scores:
                agent_performance_summary[agent_type] = {
                    "avg_score": round(np.mean(scores), 2),
                    "score_trend": self._calculate_trend(scores),
                    "total_reviews": len(scores),
                    "consistency": round(1 / (1 + np.var(scores)), 2)  # Higher is more consistent
                }
        
        return {
            "learning_status": "active" if total_reviews >= self.min_reviews_for_learning else "collecting_data",
            "total_reviews_processed": total_reviews,
            "total_insights_generated": len(self.learning_insights),
            "average_insight_confidence": round(avg_confidence, 2),
            "insight_categories": {cat: len(insights) for cat, insights in insight_categories.items()},
            "top_insights": [
                {
                    "type": insight.insight_type,
                    "description": insight.description,
                    "confidence": insight.confidence,
                    "impact": insight.impact_score
                } for insight in top_insights
            ],
            "agent_performance": agent_performance_summary,
            "learning_recommendations": self._generate_learning_recommendations()
        }
    
    def _store_review_data(self, orchestrated_review: OrchestratedReview):
        """Store review data for pattern analysis."""
        review_key = f"{orchestrated_review.design_type}_{orchestrated_review.timestamp.strftime('%Y%m%d')}"
        
        # Store review patterns
        self.review_patterns[review_key].append({
            "review_id": orchestrated_review.review_id,
            "overall_score": orchestrated_review.overall_score,
            "phase_results": {
                phase: [asdict(result) for result in results]
                for phase, results in orchestrated_review.phase_results.items()
            },
            "timestamp": orchestrated_review.timestamp.isoformat()
        })
    
    def _update_patterns(self, orchestrated_review: OrchestratedReview):
        """Update learning patterns from review data."""
        
        # Update agent performance tracking
        for phase, results in orchestrated_review.phase_results.items():
            for result in results:
                agent_type = result.agent_type
                
                # Initialize agent performance tracking
                if agent_type not in self.agent_performance:
                    self.agent_performance[agent_type] = {
                        "scores": [],
                        "confidences": [],
                        "issue_types": Counter(),
                        "recommendation_types": Counter()
                    }
                
                # Update performance data
                perf_data = self.agent_performance[agent_type]
                perf_data["scores"].append(result.score)
                perf_data["confidences"].append(result.confidence)
                
                # Track issue and recommendation patterns
                for issue in result.specific_issues:
                    # Extract key terms from issues
                    key_terms = self._extract_key_terms(issue)
                    for term in key_terms:
                        perf_data["issue_types"][term] += 1
                
                for rec in result.recommendations:
                    # Extract key terms from recommendations
                    key_terms = self._extract_key_terms(rec)
                    for term in key_terms:
                        perf_data["recommendation_types"][term] += 1
        
        # Update global patterns
        design_type = orchestrated_review.design_type
        self.score_patterns[design_type].append(orchestrated_review.overall_score)
    
    def _has_sufficient_data(self) -> bool:
        """Check if we have sufficient data for learning."""
        total_reviews = sum(len(patterns) for patterns in self.review_patterns.values())
        return total_reviews >= self.min_reviews_for_learning
    
    def _analyze_agent_performance(self) -> List[LearningInsight]:
        """Analyze agent performance patterns."""
        insights = []
        
        for agent_type, performance_data in self.agent_performance.items():
            scores = performance_data["scores"]
            confidences = performance_data["confidences"]
            
            if len(scores) < 3:  # Need at least 3 reviews
                continue
            
            # Performance trend analysis
            trend = self._calculate_trend(scores)
            
            if trend == "declining":
                insights.append(LearningInsight(
                    insight_type="performance_decline",
                    description=f"{agent_type} showing declining performance - may need prompt adjustments",
                    confidence=0.8,
                    evidence_count=len(scores),
                    impact_score=0.7,
                    created_at=datetime.now(),
                    agent_types=[agent_type]
                ))
            
            # Confidence-performance correlation
            if len(confidences) >= 5:
                correlation = np.corrcoef(scores, confidences)[0, 1]
                if correlation < 0.3:  # Low correlation between confidence and performance
                    insights.append(LearningInsight(
                        insight_type="confidence_calibration",
                        description=f"{agent_type} confidence levels not well-calibrated with performance",
                        confidence=0.6,
                        evidence_count=len(confidences),
                        impact_score=0.5,
                        created_at=datetime.now(),
                        agent_types=[agent_type]
                    ))
        
        return insights
    
    def _analyze_issue_patterns(self) -> List[LearningInsight]:
        """Analyze common issue patterns across agents."""
        insights = []
        
        # Find issues mentioned by multiple agents
        all_issue_terms = Counter()
        agent_issue_overlap = defaultdict(set)
        
        for agent_type, performance_data in self.agent_performance.items():
            issue_types = performance_data["issue_types"]
            for issue_term, count in issue_types.items():
                all_issue_terms[issue_term] += count
                agent_issue_overlap[issue_term].add(agent_type)
        
        # Find commonly identified issues
        common_issues = [
            (term, count) for term, count in all_issue_terms.items()
            if count >= 3 and len(agent_issue_overlap[term]) >= 2
        ]
        
        for issue_term, count in common_issues:
            agents_involved = list(agent_issue_overlap[issue_term])
            insights.append(LearningInsight(
                insight_type="common_issue_pattern",
                description=f"'{issue_term}' frequently identified across multiple agent types",
                confidence=min(0.9, count / 10),
                evidence_count=count,
                impact_score=0.6,
                created_at=datetime.now(),
                agent_types=agents_involved
            ))
        
        return insights
    
    def _analyze_consensus_patterns(self) -> List[LearningInsight]:
        """Analyze patterns in agent consensus."""
        insights = []
        
        # Analyze score variance across agents for similar review types
        design_type_scores = defaultdict(list)
        
        for review_data_list in self.review_patterns.values():
            for review_data in review_data_list:
                design_type = review_data.get("design_type", "unknown")
                overall_score = review_data.get("overall_score", 0)
                design_type_scores[design_type].append(overall_score)
        
        for design_type, scores in design_type_scores.items():
            if len(scores) >= 3:
                variance = np.var(scores)
                if variance > 3.0:  # High disagreement
                    insights.append(LearningInsight(
                        insight_type="high_disagreement",
                        description=f"High score variance for {design_type} designs - agents may need better alignment",
                        confidence=0.7,
                        evidence_count=len(scores),
                        impact_score=0.8,
                        created_at=datetime.now(),
                        agent_types=list(self.agent_performance.keys())
                    ))
        
        return insights
    
    def _identify_improvement_opportunities(self) -> List[LearningInsight]:
        """Identify specific improvement opportunities."""
        insights = []
        
        # Find agents with consistently low confidence
        for agent_type, performance_data in self.agent_performance.items():
            confidences = performance_data["confidences"]
            if len(confidences) >= 3:
                avg_confidence = np.mean(confidences)
                if avg_confidence < 0.6:
                    insights.append(LearningInsight(
                        insight_type="low_confidence",
                        description=f"{agent_type} shows consistently low confidence - may need domain-specific training",
                        confidence=0.8,
                        evidence_count=len(confidences),
                        impact_score=0.6,
                        created_at=datetime.now(),
                        agent_types=[agent_type]
                    ))
        
        # Find unused recommendation patterns
        all_recommendations = Counter()
        for agent_type, performance_data in self.agent_performance.items():
            rec_types = performance_data["recommendation_types"]
            all_recommendations.update(rec_types)
        
        # Identify potentially missing recommendation types
        expected_rec_types = [
            "accessibility", "usability", "visual_design", "consistency",
            "performance", "user_experience", "business_value"
        ]
        
        missing_types = []
        for expected_type in expected_rec_types:
            if not any(expected_type in rec for rec in all_recommendations.keys()):
                missing_types.append(expected_type)
        
        if missing_types:
            insights.append(LearningInsight(
                insight_type="coverage_gap",
                description=f"Potential coverage gaps in: {', '.join(missing_types)}",
                confidence=0.5,
                evidence_count=len(missing_types),
                impact_score=0.4,
                created_at=datetime.now(),
                agent_types=list(self.agent_performance.keys())
            ))
        
        return insights
    
    def _extract_key_terms(self, text: str) -> List[str]:
        """Extract key terms from text for pattern analysis."""
        # Simple keyword extraction (would use more sophisticated NLP in practice)
        import re
        
        # Clean and split text
        clean_text = re.sub(r'[^\w\s]', ' ', text.lower())
        words = clean_text.split()
        
        # Filter for meaningful terms
        stop_words = {"the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
        key_terms = [word for word in words if len(word) > 3 and word not in stop_words]
        
        return key_terms[:5]  # Return top 5 key terms
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend from a series of values."""
        if len(values) < 3:
            return "insufficient_data"
        
        # Simple linear trend
        x = np.arange(len(values))
        slope = np.polyfit(x, values, 1)[0]
        
        if slope > 0.1:
            return "improving"
        elif slope < -0.1:
            return "declining"
        else:
            return "stable"
    
    def _generate_learning_recommendations(self) -> List[str]:
        """Generate recommendations for improving the learning system."""
        recommendations = []
        
        total_reviews = sum(len(patterns) for patterns in self.review_patterns.values())
        
        if total_reviews < self.min_reviews_for_learning:
            recommendations.append(
                f"Collect {self.min_reviews_for_learning - total_reviews} more reviews to enable comprehensive learning"
            )
        
        # Check agent coverage
        agent_types = list(self.agent_performance.keys())
        if len(agent_types) < 3:
            recommendations.append("Add more specialized agents to improve review coverage")
        
        # Check for learning insights usage
        actionable_insights = [
            insight for insight in self.learning_insights
            if insight.confidence >= self.confidence_threshold
        ]
        
        if len(actionable_insights) < len(self.learning_insights) * 0.5:
            recommendations.append("Consider lowering confidence threshold to utilize more learning insights")
        
        return recommendations
    
    def _save_learning_data(self):
        """Save learning data to storage."""
        try:
            # Save patterns
            with open(self.storage_path / "review_patterns.json", "w") as f:
                # Convert defaultdict to regular dict for JSON serialization
                patterns_dict = {k: v for k, v in self.review_patterns.items()}
                json.dump(patterns_dict, f, indent=2, default=str)
            
            # Save agent performance
            with open(self.storage_path / "agent_performance.pickle", "wb") as f:
                pickle.dump(dict(self.agent_performance), f)
            
            # Save insights
            insights_data = [asdict(insight) for insight in self.learning_insights]
            with open(self.storage_path / "learning_insights.json", "w") as f:
                json.dump(insights_data, f, indent=2, default=str)
        
        except Exception as e:
            self.logger.error(f"Failed to save learning data: {e}")
    
    def _load_learning_data(self):
        """Load existing learning data from storage."""
        try:
            # Load patterns
            patterns_file = self.storage_path / "review_patterns.json"
            if patterns_file.exists():
                with open(patterns_file, "r") as f:
                    patterns_dict = json.load(f)
                    self.review_patterns = defaultdict(list, patterns_dict)
            
            # Load agent performance
            performance_file = self.storage_path / "agent_performance.pickle"
            if performance_file.exists():
                with open(performance_file, "rb") as f:
                    performance_dict = pickle.load(f)
                    self.agent_performance = defaultdict(dict, performance_dict)
            
            # Load insights
            insights_file = self.storage_path / "learning_insights.json"
            if insights_file.exists():
                with open(insights_file, "r") as f:
                    insights_data = json.load(f)
                    self.learning_insights = [
                        LearningInsight(
                            insight_type=data["insight_type"],
                            description=data["description"],
                            confidence=data["confidence"],
                            evidence_count=data["evidence_count"],
                            impact_score=data["impact_score"],
                            created_at=datetime.fromisoformat(data["created_at"]),
                            agent_types=data["agent_types"]
                        ) for data in insights_data
                    ]
        
        except Exception as e:
            self.logger.warning(f"Could not load existing learning data: {e}")


# Example usage
if __name__ == "__main__":
    # Initialize learning system
    learning_system = AgentLearningSystem()
    
    print("✅ Agent Learning System initialized")
    print(f"📁 Storage path: {learning_system.storage_path}")
    print(f"📊 Minimum reviews for learning: {learning_system.min_reviews_for_learning}")
    
    # Get learning summary
    summary = learning_system.get_learning_summary()
    print(f"\n📈 Learning Status: {summary.get('learning_status', 'unknown')}")
    print(f"📝 Total reviews processed: {summary.get('total_reviews_processed', 0)}")
    print(f"💡 Total insights generated: {summary.get('total_insights_generated', 0)}")
    
    if summary.get('learning_recommendations'):
        print("\n🎯 Learning Recommendations:")
        for rec in summary['learning_recommendations']:
            print(f"  - {rec}")
