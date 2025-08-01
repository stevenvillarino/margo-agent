"""
Margo - VP of Design Review Agent

This agent represents Margo, the VP of Design, who provides final strategic 
design approval and ensures alignment with Roku's design vision and business goals.
Serves as the senior "tollgate" for all design decisions.
"""

import asyncio
import json
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.memory import ConversationBufferMemory
from dataclasses import dataclass

from agents.orchestrator import ReviewResult
from agents.exa_search import ExaSearchAgent


@dataclass
class DesignCriteria:
    """Design criteria for evaluating designs from Margo's perspective."""
    criteria_name: str
    weight: float
    description: str
    target_range: Tuple[float, float]  # (min, max) acceptable values


class MargoVPDesignAgent:
    """
    Margo - VP of Design agent that provides final strategic design approval.
    Focuses on design vision, brand consistency, user experience excellence, 
    and strategic business alignment from a design leadership perspective.
    """
    
    def __init__(self, 
                 openai_api_key: str,
                 design_vision: Dict[str, Any] = None,
                 design_priorities: List[str] = None,
                 exa_api_key: Optional[str] = None):
        """
        Initialize Margo, the VP of Design review agent.
        
        Args:
            openai_api_key: OpenAI API key
            design_vision: Roku's design vision and strategic goals
            design_priorities: Current design priorities and initiatives
            exa_api_key: Optional Exa API key for design trend research
        """
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.2,  # More conservative, business-focused
            max_tokens=2000
        )
        
        # Design leadership context
        self.design_vision = design_vision or {
            "industry": "Streaming/Entertainment",
            "design_philosophy": "Human-centered, accessible, delightful",
            "key_principles": ["Simplicity", "Accessibility", "Brand Consistency"],
            "target_users": "TV viewers across all demographics",
            "design_position": "Premium, intuitive streaming experience"
        }
        
        self.design_priorities = design_priorities or [
            "Enhance user experience consistency",
            "Improve accessibility across all features",
            "Strengthen Roku brand identity",
            "Optimize for TV/remote interaction",
            "Drive design system adoption"
        ]
        
        # Also store as business_priorities for backward compatibility
        self.business_priorities = self.design_priorities
        
        # Memory for design leadership insights
        self.memory = ConversationBufferMemory(return_messages=True)
        self.review_history = []
        self.design_insights = []
        
        # Research capability for design trends and best practices
        self.exa_agent = None
        if exa_api_key:
            try:
                self.exa_agent = ExaSearchAgent(exa_api_key)
            except Exception as e:
                print(f"Warning: Could not initialize design research: {e}")
        
        # Design evaluation criteria from Margo's perspective
        self.design_criteria = [
            DesignCriteria("User Experience Excellence", 1.5, "Quality of user interaction and flow", (8.0, 10.0)),
            DesignCriteria("Brand Consistency", 1.4, "Alignment with Roku design system", (8.0, 10.0)),
            DesignCriteria("Accessibility Compliance", 1.3, "Inclusive design for all users", (7.0, 10.0)),
            DesignCriteria("Design Innovation", 1.2, "Creative and forward-thinking approach", (6.0, 10.0)),
            DesignCriteria("Technical Feasibility", 1.1, "Realistic implementation on Roku platform", (7.0, 10.0)),
            DesignCriteria("Business Value", 1.3, "Contribution to business objectives", (7.0, 10.0)),
            DesignCriteria("User Research Foundation", 1.2, "Grounded in user insights and data", (6.0, 10.0))
        ]
        
        # Performance tracking
        self.business_impact_tracking = {
            "engagement_predictions": [],
            "strategic_alignments": [],
            "competitive_insights": []
        }
    
    async def async_review(self, 
                          image_data: str,
                          design_type: str,
                          context: Dict[str, Any],
                          analysis_results: List[ReviewResult]) -> List[ReviewResult]:
        """
        Conduct async VP Product review with business focus.
        
        Args:
            image_data: Base64 encoded image
            design_type: Type of design being reviewed
            context: Additional context including business requirements
            analysis_results: Results from initial analysis
            
        Returns:
            List of review results from VP perspective
        """
        # Get competitive research
        competitive_context = await self._get_competitive_research(design_type)
        
        # Analyze business implications from other reviews
        business_implications = self._analyze_business_implications(analysis_results)
        
        # Create strategic review prompt
        prompt = self._create_vp_review_prompt(
            design_type, competitive_context, business_implications, context
        )
        
        try:
            messages = [
                SystemMessage(content=prompt),
                HumanMessage(content=[
                    {"type": "text", "text": "Please provide your strategic product review of this design."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
                ])
            ]
            
            response = await self.llm.ainvoke(messages)
            
            # Parse the response into structured business feedback
            review_result = self._parse_vp_response(response.content, design_type, context)
            
            # Store for strategic learning
            self.review_history.append(review_result)
            self._update_strategic_insights(review_result)
            
            return [review_result]
            
        except Exception as e:
            print(f"VP Product review failed: {e}")
            return []
    
    def review(self, 
               image_data: str,
               design_type: str,
               context: Dict[str, Any],
               analysis_results: List[ReviewResult]) -> List[ReviewResult]:
        """
        Synchronous version of review method.
        """
        return asyncio.run(self.async_review(image_data, design_type, context, analysis_results))
    
    async def _get_competitive_research(self, design_type: str) -> str:
        """Get competitive research and market context."""
        if not self.exa_agent:
            return ""
        
        try:
            # Search for competitive analysis and market trends
            research_queries = [
                f"{design_type} competitive analysis streaming platforms",
                f"best practices {design_type} streaming TV",
                f"user engagement {design_type} video platforms"
            ]
            
            all_context = []
            for query in research_queries:
                results = self.exa_agent.search_design_best_practices(query, 2)
                if results:
                    for doc in results:
                        title = doc.metadata.get('title', 'Unknown')
                        content_preview = doc.page_content[:150] + "..." if len(doc.page_content) > 150 else doc.page_content
                        all_context.append(f"📊 {title}: {content_preview}")
            
            # Add Roku-specific competitive context
            roku_results = self.exa_agent.search_roku_specific_content(f"{design_type} competitive features", 1)
            if roku_results:
                for doc in roku_results:
                    title = doc.metadata.get('title', 'Unknown')
                    content_preview = doc.page_content[:150] + "..." if len(doc.page_content) > 150 else doc.page_content
                    all_context.append(f"🏢 Roku Context - {title}: {content_preview}")
            
            return "\n".join(all_context) if all_context else ""
            
        except Exception as e:
            print(f"Competitive research failed: {e}")
            return ""
    
    def _analyze_business_implications(self, analysis_results: List[ReviewResult]) -> str:
        """Analyze business implications from other review results."""
        if not analysis_results:
            return ""
        
        implications = []
        
        for result in analysis_results:
            # Extract business-relevant insights
            business_keywords = [
                "user", "engagement", "conversion", "retention", "churn",
                "revenue", "adoption", "satisfaction", "usability", "accessibility"
            ]
            
            # Find business-relevant feedback
            business_feedback = []
            for line in result.feedback.split('.'):
                if any(keyword in line.lower() for keyword in business_keywords):
                    business_feedback.append(line.strip())
            
            if business_feedback:
                implications.append(f"From {result.agent_name}: {' '.join(business_feedback[:2])}")
        
        return "\n".join(implications) if implications else ""
    
    def _create_vp_review_prompt(self, 
                               design_type: str,
                               competitive_context: str,
                               business_implications: str,
                               context: Dict[str, Any]) -> str:
        """Create the VP Product review prompt."""
        
        # Get current business priorities as context
        priorities_context = "\n".join([f"• {priority}" for priority in self.business_priorities])
        
        # Company context
        company_info = "\n".join([f"• {key}: {value}" for key, value in self.company_context.items()])
        
        prompt = f"""
You are a VP of Product conducting a strategic review of a {design_type} design.

Your Role & Perspective:
- Strategic business leader responsible for product success
- Focus on business outcomes, user value, and competitive positioning
- Balance user needs with business objectives and constraints
- Think about long-term product strategy and market positioning

Company Context:
{company_info}

Current Business Priorities:
{priorities_context}

Competitive Intelligence:
{competitive_context}

Business Implications from Technical Reviews:
{business_implications}

Evaluation Framework - Rate each area (1-10):

1. **Business Goal Alignment** (Weight: 1.5x)
   - How well does this design advance our strategic objectives?
   - Does it support key business metrics and KPIs?

2. **User Value Proposition** (Weight: 1.4x)
   - What clear value does this provide to users?
   - How does it solve real user problems or needs?

3. **Competitive Differentiation** (Weight: 1.2x)
   - How does this compare to competitive offerings?
   - What unique advantages does it provide?

4. **Implementation ROI** (Weight: 1.3x)
   - What's the effort-to-impact ratio?
   - Are there simpler solutions that achieve similar goals?

5. **Risk Assessment** (Weight: 1.1x, lower scores are better)
   - What are potential negative impacts on business metrics?
   - User confusion, increased support burden, technical risks?

6. **Strategic Vision Alignment** (Weight: 1.2x)
   - How does this fit our 12-18 month product roadmap?
   - Does it position us well for future opportunities?

Provide your review in this structure:
1. **Executive Summary**: 2-3 sentences on overall strategic assessment
2. **Business Impact Analysis**: Specific impact on key metrics and goals
3. **Competitive Positioning**: How this affects our market position
4. **Strategic Recommendations**: 3-4 prioritized actions for maximum business impact
5. **Risk Mitigation**: Key risks and how to address them
6. **Success Metrics**: How to measure the business impact of this design

Be decisive, business-focused, and provide clear strategic direction.
Include an overall business recommendation (Approve/Approve with Changes/Reject/Needs More Research).
"""
        
        return prompt
    
    def _parse_vp_response(self, response_content: str, design_type: str, context: Dict[str, Any]) -> ReviewResult:
        """Parse the VP review response into structured business format."""
        
        # Extract business recommendation
        recommendation = "Approve with Changes"  # Default
        if "approve" in response_content.lower():
            if "reject" in response_content.lower():
                recommendation = "Reject"
            elif "changes" in response_content.lower() or "modification" in response_content.lower():
                recommendation = "Approve with Changes"
            else:
                recommendation = "Approve"
        elif "reject" in response_content.lower():
            recommendation = "Reject"
        elif "research" in response_content.lower():
            recommendation = "Needs More Research"
        
        # Calculate business score based on criteria
        business_score = self._calculate_business_score(response_content)
        
        # Extract strategic issues and recommendations
        issues = self._extract_business_issues(response_content)
        recommendations = self._extract_strategic_recommendations(response_content)
        
        # Calculate confidence based on competitive context and strategic clarity
        confidence = self._calculate_strategic_confidence(response_content, context)
        
        return ReviewResult(
            agent_type="vp_review",
            agent_name="VP of Product",
            score=business_score,
            feedback=response_content,
            specific_issues=issues,
            recommendations=recommendations,
            confidence=confidence,
            review_time=datetime.now(),
            metadata={
                "business_recommendation": recommendation,
                "company_context": self.company_context,
                "business_priorities": self.business_priorities,
                "competitive_research_available": bool(self.exa_agent),
                "design_type": design_type,
                "strategic_focus": "business_outcomes"
            }
        )
    
    def _calculate_business_score(self, response_content: str) -> float:
        """Calculate business score based on multiple criteria."""
        scores = []
        
        # Look for numerical scores in response
        import re
        score_patterns = [
            r'(\d+(?:\.\d+)?)/10',
            r'score.*?(\d+(?:\.\d+)?)',
            r'rating.*?(\d+(?:\.\d+)?)'
        ]
        
        found_scores = []
        for pattern in score_patterns:
            matches = re.findall(pattern, response_content.lower())
            for match in matches:
                try:
                    score = float(match)
                    if 1 <= score <= 10:
                        found_scores.append(score)
                except:
                    pass
        
        if found_scores:
            return sum(found_scores) / len(found_scores)
        
        # Fallback: analyze sentiment and business keywords
        positive_indicators = [
            "strong business case", "clear value", "competitive advantage",
            "aligns with strategy", "high impact", "excellent roi"
        ]
        
        negative_indicators = [
            "business risk", "unclear value", "low impact", "poor roi",
            "competitive disadvantage", "strategic misalignment"
        ]
        
        positive_count = sum(1 for indicator in positive_indicators if indicator in response_content.lower())
        negative_count = sum(1 for indicator in negative_indicators if indicator in response_content.lower())
        
        # Base score with adjustments
        base_score = 7.0
        adjustment = (positive_count - negative_count) * 0.5
        
        return max(1.0, min(10.0, base_score + adjustment))
    
    def _extract_business_issues(self, response_content: str) -> List[str]:
        """Extract business-focused issues from response."""
        issues = []
        
        business_issue_keywords = [
            "business risk", "competitive threat", "user confusion",
            "low engagement", "poor conversion", "strategic misalignment",
            "unclear value", "implementation cost", "technical debt"
        ]
        
        lines = response_content.split('\n')
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in business_issue_keywords):
                # Clean up the line
                clean_line = re.sub(r'^[-•*]\s*|\d+\.\s*', '', line)
                if clean_line and len(clean_line) > 10:
                    issues.append(clean_line)
        
        return issues[:5]  # Limit to top 5 business issues
    
    def _extract_strategic_recommendations(self, response_content: str) -> List[str]:
        """Extract strategic recommendations from response."""
        recommendations = []
        
        strategic_keywords = [
            "recommend", "suggest", "should", "consider", "prioritize",
            "focus on", "optimize", "improve", "enhance", "implement"
        ]
        
        lines = response_content.split('\n')
        in_recommendations_section = False
        
        for line in lines:
            line = line.strip()
            
            # Check if we're in recommendations section
            if any(keyword in line.lower() for keyword in ["recommendation", "action", "next step"]):
                in_recommendations_section = True
                continue
            
            # Extract recommendations
            if (in_recommendations_section or 
                any(keyword in line.lower() for keyword in strategic_keywords)):
                
                # Clean up the line
                clean_line = re.sub(r'^[-•*]\s*|\d+\.\s*', '', line)
                if clean_line and len(clean_line) > 15:
                    recommendations.append(clean_line)
        
        return recommendations[:5]  # Limit to top 5 strategic recommendations
    
    def _calculate_strategic_confidence(self, response_content: str, context: Dict[str, Any]) -> float:
        """Calculate confidence based on strategic analysis depth."""
        
        confidence_factors = []
        
        # Check for business metrics mention
        business_metrics = ["engagement", "conversion", "retention", "revenue", "roi", "kpi"]
        metrics_mentioned = sum(1 for metric in business_metrics if metric in response_content.lower())
        confidence_factors.append(min(1.0, metrics_mentioned / 3))  # Normalize to 0-1
        
        # Check for competitive analysis
        competitive_terms = ["competitor", "competitive", "market", "industry", "benchmark"]
        competitive_analysis = sum(1 for term in competitive_terms if term in response_content.lower())
        confidence_factors.append(min(1.0, competitive_analysis / 2))
        
        # Check for strategic thinking
        strategic_terms = ["strategy", "vision", "roadmap", "long-term", "strategic"]
        strategic_thinking = sum(1 for term in strategic_terms if term in response_content.lower())
        confidence_factors.append(min(1.0, strategic_thinking / 2))
        
        # Check response length and depth
        word_count = len(response_content.split())
        depth_factor = min(1.0, word_count / 500)  # Assume 500+ words indicates thorough analysis
        confidence_factors.append(depth_factor)
        
        return sum(confidence_factors) / len(confidence_factors)
    
    def _update_strategic_insights(self, review_result: ReviewResult):
        """Update strategic insights based on review outcomes."""
        
        # Extract key strategic learnings
        insights = {
            "timestamp": review_result.review_time,
            "design_type": review_result.metadata.get("design_type"),
            "business_recommendation": review_result.metadata.get("business_recommendation"),
            "score": review_result.score,
            "key_issues": review_result.specific_issues[:3],
            "strategic_recommendations": review_result.recommendations[:3]
        }
        
        self.strategic_insights.append(insights)
        
        # Keep only recent insights (last 20 reviews)
        if len(self.strategic_insights) > 20:
            self.strategic_insights = self.strategic_insights[-20:]
    
    def get_strategic_summary(self) -> Dict[str, Any]:
        """Get strategic summary and insights from all reviews."""
        if not self.review_history:
            return {"message": "No review history available for strategic analysis."}
        
        # Calculate strategic metrics
        scores = [r.score for r in self.review_history]
        recommendations = [r.metadata.get("business_recommendation", "Unknown") for r in self.review_history]
        
        # Count recommendation types
        recommendation_counts = {}
        for rec in recommendations:
            recommendation_counts[rec] = recommendation_counts.get(rec, 0) + 1
        
        # Extract common strategic themes
        all_issues = []
        all_recommendations = []
        for review in self.review_history:
            all_issues.extend(review.specific_issues)
            all_recommendations.extend(review.recommendations)
        
        # Find most common issues and recommendations
        issue_counts = {}
        rec_counts = {}
        
        for issue in all_issues:
            issue_counts[issue] = issue_counts.get(issue, 0) + 1
        
        for rec in all_recommendations:
            rec_counts[rec] = rec_counts.get(rec, 0) + 1
        
        top_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        top_recommendations = sorted(rec_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        return {
            "total_reviews": len(self.review_history),
            "average_business_score": round(sum(scores) / len(scores), 2),
            "recommendation_distribution": recommendation_counts,
            "top_strategic_issues": [issue for issue, count in top_issues],
            "top_strategic_recommendations": [rec for rec, count in top_recommendations],
            "business_priorities": self.business_priorities,
            "strategic_trend": "positive" if len(scores) >= 3 and scores[-1] > scores[-3] else "stable",
            "competitive_research_enabled": bool(self.exa_agent)
        }
    
    def update_business_context(self, new_context: Dict[str, Any]):
        """Update business context and priorities."""
        self.company_context.update(new_context)
    
    def update_business_priorities(self, new_priorities: List[str]):
        """Update current business priorities."""
        self.business_priorities = new_priorities


# Example usage
if __name__ == "__main__":
    import os
    
    openai_key = os.getenv('OPENAI_API_KEY')
    exa_key = os.getenv('EXA_API_KEY')
    
    if openai_key:
        # Create VP Product review agent with Roku-specific context
        roku_context = {
            "industry": "Streaming/Entertainment",
            "company_stage": "Mature",
            "primary_metrics": ["User Engagement", "Content Discovery", "Ad Revenue"],
            "target_audience": "TV viewers, families, cord-cutters",
            "competitive_position": "Platform leader in streaming TV"
        }
        
        roku_priorities = [
            "Enhance content discovery experience",
            "Increase user engagement with personalization",
            "Improve advertising effectiveness",
            "Reduce user acquisition costs",
            "Strengthen platform ecosystem"
        ]
        
        vp_agent = VPProductReviewAgent(
            openai_api_key=openai_key,
            company_context=roku_context,
            business_priorities=roku_priorities,
            exa_api_key=exa_key
        )
        
        print("✅ VP of Product Review Agent created successfully")
        print(f"🏢 Company Context: {vp_agent.company_context['industry']}")
        print(f"🎯 Business Priorities: {len(vp_agent.business_priorities)} priorities set")
        print(f"🔍 Competitive Research: {'enabled' if exa_key else 'disabled'}")
        
        # Show business criteria
        print("\n📊 Business Evaluation Criteria:")
        for criteria in vp_agent.business_criteria:
            print(f"  - {criteria.metric_name} (Weight: {criteria.weight}x)")
    else:
        print("❌ OPENAI_API_KEY required")
