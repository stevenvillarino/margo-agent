"""
Peer Design Review Agent

This agent simulates a peer designer's perspective, focusing on design
craft, usability, and creative feedback from a practitioner's viewpoint.
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.memory import ConversationBufferMemory
from dataclasses import dataclass

from agents.orchestrator import ReviewResult
from agents.exa_search import ExaSearchAgent


class PeerDesignReviewAgent:
    """
    Peer design review agent that provides feedback from a fellow designer's perspective.
    Focuses on design craft, usability, and creative solutions.
    """
    
    def __init__(self, 
                 openai_api_key: str,
                 agent_name: str = "Senior Designer Peer",
                 specialization: str = "UI/UX Design",
                 experience_level: str = "Senior",
                 exa_api_key: Optional[str] = None):
        """
        Initialize the peer design review agent.
        
        Args:
            openai_api_key: OpenAI API key
            agent_name: Name of the peer reviewer
            specialization: Design specialization area
            experience_level: Experience level (Junior, Mid, Senior, Lead)
            exa_api_key: Optional Exa API key for research
        """
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.4,  # Slightly more creative than analysis
            max_tokens=1500
        )
        
        self.agent_name = agent_name
        self.specialization = specialization
        self.experience_level = experience_level
        
        # Memory for learning from past reviews
        self.memory = ConversationBufferMemory(return_messages=True)
        self.review_history = []
        
        # Research capability
        self.exa_agent = None
        if exa_api_key:
            try:
                self.exa_agent = ExaSearchAgent(exa_api_key)
            except Exception as e:
                print(f"Warning: Could not initialize research capability: {e}")
        
        # Peer reviewer personality and focus areas
        self.focus_areas = [
            "Design consistency and patterns",
            "User experience flow",
            "Visual hierarchy and typography",
            "Color and contrast choices",
            "Interactive element design",
            "Creative problem solving",
            "Design system adherence",
            "Responsive design considerations"
        ]
        
        # Learning weights - areas to focus on based on past feedback
        self.learning_weights = {
            "visual_design": 1.0,
            "usability": 1.0,
            "consistency": 1.0,
            "innovation": 1.0,
            "accessibility": 0.8,  # Not primary focus but considered
            "technical_feasibility": 0.7
        }
    
    async def async_review(self, 
                          image_data: str,
                          design_type: str,
                          context: Dict[str, Any],
                          analysis_results: List[ReviewResult]) -> List[ReviewResult]:
        """
        Conduct async peer design review.
        
        Args:
            image_data: Base64 encoded image
            design_type: Type of design being reviewed
            context: Additional context
            analysis_results: Results from initial analysis
            
        Returns:
            List of review results from peer perspective
        """
        # Get research context if available
        research_context = await self._get_research_context(design_type)
        
        # Get insights from analysis results
        analysis_insights = self._extract_analysis_insights(analysis_results)
        
        # Create peer review prompt
        prompt = self._create_peer_review_prompt(
            design_type, research_context, analysis_insights, context
        )
        
        try:
            messages = [
                SystemMessage(content=prompt),
                HumanMessage(content=[
                    {"type": "text", "text": "Please provide your peer design review of this interface."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
                ])
            ]
            
            response = await self.llm.ainvoke(messages)
            
            # Parse the response into structured feedback
            review_result = self._parse_peer_response(response.content, design_type)
            
            # Store for learning
            self.review_history.append(review_result)
            self._update_learning_weights(review_result)
            
            return [review_result]
            
        except Exception as e:
            print(f"Peer review failed: {e}")
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
    
    async def _get_research_context(self, design_type: str) -> str:
        """Get research context for the design type."""
        if not self.exa_agent:
            return ""
        
        try:
            # Search for current design trends and best practices
            research_queries = [
                f"{design_type} design trends 2024",
                f"{design_type} usability best practices",
                f"creative {design_type} examples"
            ]
            
            all_context = []
            for query in research_queries:
                results = self.exa_agent.search_design_examples(query, 2)
                if results:
                    for doc in results:
                        all_context.append(f"- {doc.metadata.get('title', 'Unknown')}: {doc.page_content[:100]}...")
            
            return "\n".join(all_context) if all_context else ""
            
        except Exception as e:
            print(f"Research context failed: {e}")
            return ""
    
    def _extract_analysis_insights(self, analysis_results: List[ReviewResult]) -> str:
        """Extract key insights from analysis results."""
        if not analysis_results:
            return ""
        
        insights = []
        for result in analysis_results:
            insights.append(f"- {result.agent_name} (Score: {result.score}/10): {result.feedback[:100]}...")
            if result.specific_issues:
                insights.append(f"  Issues: {', '.join(result.specific_issues[:3])}")
        
        return "\n".join(insights)
    
    def _create_peer_review_prompt(self, 
                                 design_type: str,
                                 research_context: str,
                                 analysis_insights: str,
                                 context: Dict[str, Any]) -> str:
        """Create the peer review prompt."""
        
        # Adjust prompt based on learning weights
        focus_priorities = sorted(self.learning_weights.items(), key=lambda x: x[1], reverse=True)
        top_focus_areas = [area.replace('_', ' ').title() for area, _ in focus_priorities[:4]]
        
        prompt = f"""
You are {self.agent_name}, a {self.experience_level} {self.specialization} providing peer feedback on a {design_type}.

Your Personality & Approach:
- Collaborative and constructive
- Focus on practical, actionable feedback
- Balance critique with encouragement
- Draw from real-world design experience
- Consider both user needs and design craft

Primary Focus Areas (based on your expertise):
{', '.join(top_focus_areas)}

Current Design Trends & Research:
{research_context}

Initial Analysis Context:
{analysis_insights}

Review Guidelines:
1. **Visual Design Craft**: Evaluate typography, spacing, color, visual hierarchy
2. **User Experience**: Consider user flow, cognitive load, interaction patterns
3. **Design Consistency**: Check for pattern consistency and design system usage
4. **Creative Solutions**: Assess innovation and creative problem-solving
5. **Practical Considerations**: Think about implementation and edge cases

Provide feedback in this structure:
- Overall impression and standout elements
- Specific design strengths
- Areas for improvement with concrete suggestions
- Creative opportunities or alternative approaches
- Design system and consistency observations

Rate the design 1-10 and include your confidence level (0-1).
Be specific, actionable, and encouraging while maintaining professional standards.
"""
        
        return prompt
    
    def _parse_peer_response(self, response_content: str, design_type: str) -> ReviewResult:
        """Parse the peer review response into structured format."""
        
        # Extract score and confidence (simplified parsing)
        score = 7.0  # Default
        confidence = 0.8  # Default
        
        # Look for score in response
        import re
        score_match = re.search(r'(?:score|rating|rate).*?(\d+(?:\.\d+)?)/10', response_content.lower())
        if score_match:
            try:
                score = float(score_match.group(1))
            except:
                pass
        
        confidence_match = re.search(r'confidence.*?(\d+(?:\.\d+)?)', response_content.lower())
        if confidence_match:
            try:
                confidence = float(confidence_match.group(1))
                if confidence > 1:  # If given as percentage
                    confidence = confidence / 100
            except:
                pass
        
        # Extract issues and recommendations (simplified)
        issues = []
        recommendations = []
        
        # Look for bullet points or numbered lists
        lines = response_content.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in ['issue', 'problem', 'concern', 'improvement']):
                current_section = 'issues'
            elif any(keyword in line.lower() for keyword in ['recommend', 'suggest', 'consider', 'try']):
                current_section = 'recommendations'
            elif line.startswith(('-', '•', '*')) or re.match(r'^\d+\.', line):
                content = re.sub(r'^[-•*]\s*|\d+\.\s*', '', line)
                if current_section == 'issues' and content:
                    issues.append(content)
                elif current_section == 'recommendations' and content:
                    recommendations.append(content)
        
        # Create review result
        return ReviewResult(
            agent_type="peer_review",
            agent_name=self.agent_name,
            score=score,
            feedback=response_content,
            specific_issues=issues[:5],  # Limit to top 5
            recommendations=recommendations[:5],  # Limit to top 5
            confidence=confidence,
            review_time=datetime.now(),
            metadata={
                "specialization": self.specialization,
                "experience_level": self.experience_level,
                "focus_areas": self.focus_areas,
                "design_type": design_type
            }
        )
    
    def _update_learning_weights(self, review_result: ReviewResult):
        """Update learning weights based on review outcomes."""
        # Simple learning mechanism - would be more sophisticated in practice
        
        # If low score, increase weight on areas that might need more focus
        if review_result.score < 6:
            self.learning_weights["consistency"] = min(1.5, self.learning_weights["consistency"] * 1.1)
            self.learning_weights["usability"] = min(1.5, self.learning_weights["usability"] * 1.1)
        
        # If high score, maintain current balance
        elif review_result.score > 8:
            # Slightly reduce weights to maintain balance
            for key in self.learning_weights:
                self.learning_weights[key] = max(0.5, self.learning_weights[key] * 0.95)
    
    def get_agent_stats(self) -> Dict[str, Any]:
        """Get statistics about this agent's performance."""
        if not self.review_history:
            return {"message": "No review history available"}
        
        scores = [r.score for r in self.review_history]
        confidences = [r.confidence for r in self.review_history]
        
        return {
            "agent_name": self.agent_name,
            "specialization": self.specialization,
            "total_reviews": len(self.review_history),
            "average_score_given": round(sum(scores) / len(scores), 2),
            "average_confidence": round(sum(confidences) / len(confidences), 2),
            "learning_weights": self.learning_weights,
            "recent_trend": "improving" if len(scores) >= 3 and scores[-1] > scores[-3] else "stable"
        }
    
    def customize_focus(self, new_focus_areas: List[str], new_weights: Dict[str, float] = None):
        """Customize the agent's focus areas and learning weights."""
        self.focus_areas = new_focus_areas
        
        if new_weights:
            for key, value in new_weights.items():
                if key in self.learning_weights:
                    self.learning_weights[key] = value


# Factory function to create different types of peer reviewers
def create_peer_reviewer(reviewer_type: str, openai_api_key: str, exa_api_key: str = None) -> PeerDesignReviewAgent:
    """
    Factory function to create different specialized peer reviewers.
    
    Args:
        reviewer_type: Type of peer reviewer to create
        openai_api_key: OpenAI API key
        exa_api_key: Optional Exa API key
        
    Returns:
        Configured PeerDesignReviewAgent
    """
    
    reviewer_configs = {
        "ui_specialist": {
            "agent_name": "UI Design Specialist",
            "specialization": "User Interface Design",
            "experience_level": "Senior",
            "focus_areas": [
                "Visual hierarchy and layout",
                "Component design and consistency",
                "Design system implementation",
                "Micro-interactions",
                "Responsive design patterns"
            ],
            "learning_weights": {
                "visual_design": 1.4,
                "consistency": 1.3,
                "usability": 1.0,
                "innovation": 0.9,
                "accessibility": 0.8,
                "technical_feasibility": 1.1
            }
        },
        
        "ux_researcher": {
            "agent_name": "UX Research-Informed Designer",
            "specialization": "User Experience Research",
            "experience_level": "Senior",
            "focus_areas": [
                "User flow and task completion",
                "Cognitive load assessment",
                "Usability patterns",
                "Information architecture",
                "User journey optimization"
            ],
            "learning_weights": {
                "visual_design": 0.9,
                "consistency": 1.1,
                "usability": 1.5,
                "innovation": 1.0,
                "accessibility": 1.2,
                "technical_feasibility": 0.8
            }
        },
        
        "creative_director": {
            "agent_name": "Creative Director",
            "specialization": "Creative Direction",
            "experience_level": "Lead",
            "focus_areas": [
                "Brand expression and personality",
                "Creative concept execution",
                "Visual impact and memorability",
                "Market differentiation",
                "Trend awareness and innovation"
            ],
            "learning_weights": {
                "visual_design": 1.3,
                "consistency": 1.0,
                "usability": 0.9,
                "innovation": 1.5,
                "accessibility": 0.7,
                "technical_feasibility": 0.6
            }
        },
        
        "frontend_designer": {
            "agent_name": "Frontend Design Engineer",
            "specialization": "Frontend Development",
            "experience_level": "Senior",
            "focus_areas": [
                "Implementation feasibility",
                "Performance considerations",
                "Responsive design patterns",
                "Browser compatibility",
                "Component architecture"
            ],
            "learning_weights": {
                "visual_design": 1.0,
                "consistency": 1.2,
                "usability": 1.1,
                "innovation": 0.8,
                "accessibility": 1.1,
                "technical_feasibility": 1.4
            }
        }
    }
    
    config = reviewer_configs.get(reviewer_type, reviewer_configs["ui_specialist"])
    
    agent = PeerDesignReviewAgent(
        openai_api_key=openai_api_key,
        agent_name=config["agent_name"],
        specialization=config["specialization"],
        experience_level=config["experience_level"],
        exa_api_key=exa_api_key
    )
    
    # Customize the agent
    agent.customize_focus(config["focus_areas"], config["learning_weights"])
    
    return agent


# Example usage
if __name__ == "__main__":
    import os
    
    openai_key = os.getenv('OPENAI_API_KEY')
    exa_key = os.getenv('EXA_API_KEY')
    
    if openai_key:
        # Create different types of peer reviewers
        ui_specialist = create_peer_reviewer("ui_specialist", openai_key, exa_key)
        ux_researcher = create_peer_reviewer("ux_researcher", openai_key, exa_key)
        creative_director = create_peer_reviewer("creative_director", openai_key, exa_key)
        
        print("✅ Peer Design Review Agents created:")
        print(f"  - {ui_specialist.agent_name}")
        print(f"  - {ux_researcher.agent_name}")
        print(f"  - {creative_director.agent_name}")
        
        print(f"\n🔍 Research capability: {'enabled' if exa_key else 'disabled'}")
    else:
        print("❌ OPENAI_API_KEY required")
