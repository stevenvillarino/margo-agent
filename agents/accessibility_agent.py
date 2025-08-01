"""
Accessibility Review Agent

This agent specializes in accessibility evaluation, WCAG compliance,
and inclusive design principles for comprehensive accessibility auditing.
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
class AccessibilityIssue:
    """Structured accessibility issue."""
    severity: str  # Critical, High, Medium, Low
    wcag_criterion: str
    description: str
    impact: str
    solution: str
    affected_users: List[str]


class AccessibilityReviewAgent:
    """
    Accessibility review agent that evaluates designs for WCAG compliance
    and inclusive design principles.
    """
    
    def __init__(self, 
                 openai_api_key: str,
                 wcag_level: str = "AA",
                 target_disabilities: List[str] = None,
                 exa_api_key: Optional[str] = None):
        """
        Initialize the accessibility review agent.
        
        Args:
            openai_api_key: OpenAI API key
            wcag_level: WCAG compliance level (A, AA, AAA)
            target_disabilities: Specific disabilities to focus on
            exa_api_key: Optional Exa API key for accessibility research
        """
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.1,  # Very low for consistent accessibility evaluation
            max_tokens=2000
        )
        
        self.wcag_level = wcag_level
        self.target_disabilities = target_disabilities or [
            "Visual impairments",
            "Hearing impairments", 
            "Motor impairments",
            "Cognitive impairments",
            "Neurological conditions"
        ]
        
        # Memory for accessibility learning
        self.memory = ConversationBufferMemory(return_messages=True)
        self.review_history = []
        self.accessibility_patterns = {}
        
        # Research capability for accessibility guidelines
        self.exa_agent = None
        if exa_api_key:
            try:
                self.exa_agent = ExaSearchAgent(exa_api_key)
            except Exception as e:
                print(f"Warning: Could not initialize accessibility research: {e}")
        
        # WCAG 2.1 Success Criteria mapping
        self.wcag_criteria = {
            "1.1.1": {"name": "Non-text Content", "level": "A", "category": "Perceivable"},
            "1.2.1": {"name": "Audio-only and Video-only", "level": "A", "category": "Perceivable"},
            "1.2.2": {"name": "Captions", "level": "A", "category": "Perceivable"},
            "1.2.3": {"name": "Audio Description or Media Alternative", "level": "A", "category": "Perceivable"},
            "1.3.1": {"name": "Info and Relationships", "level": "A", "category": "Perceivable"},
            "1.3.2": {"name": "Meaningful Sequence", "level": "A", "category": "Perceivable"},
            "1.3.3": {"name": "Sensory Characteristics", "level": "A", "category": "Perceivable"},
            "1.4.1": {"name": "Use of Color", "level": "A", "category": "Perceivable"},
            "1.4.2": {"name": "Audio Control", "level": "A", "category": "Perceivable"},
            "1.4.3": {"name": "Contrast (Minimum)", "level": "AA", "category": "Perceivable"},
            "1.4.4": {"name": "Resize text", "level": "AA", "category": "Perceivable"},
            "1.4.5": {"name": "Images of Text", "level": "AA", "category": "Perceivable"},
            "1.4.6": {"name": "Contrast (Enhanced)", "level": "AAA", "category": "Perceivable"},
            "1.4.10": {"name": "Reflow", "level": "AA", "category": "Perceivable"},
            "1.4.11": {"name": "Non-text Contrast", "level": "AA", "category": "Perceivable"},
            "1.4.12": {"name": "Text Spacing", "level": "AA", "category": "Perceivable"},
            "1.4.13": {"name": "Content on Hover or Focus", "level": "AA", "category": "Perceivable"},
            "2.1.1": {"name": "Keyboard", "level": "A", "category": "Operable"},
            "2.1.2": {"name": "No Keyboard Trap", "level": "A", "category": "Operable"},
            "2.1.4": {"name": "Character Key Shortcuts", "level": "A", "category": "Operable"},
            "2.2.1": {"name": "Timing Adjustable", "level": "A", "category": "Operable"},
            "2.2.2": {"name": "Pause, Stop, Hide", "level": "A", "category": "Operable"},
            "2.3.1": {"name": "Three Flashes or Below Threshold", "level": "A", "category": "Operable"},
            "2.4.1": {"name": "Bypass Blocks", "level": "A", "category": "Operable"},
            "2.4.2": {"name": "Page Titled", "level": "A", "category": "Operable"},
            "2.4.3": {"name": "Focus Order", "level": "A", "category": "Operable"},
            "2.4.4": {"name": "Link Purpose (In Context)", "level": "A", "category": "Operable"},
            "2.4.5": {"name": "Multiple Ways", "level": "AA", "category": "Operable"},
            "2.4.6": {"name": "Headings and Labels", "level": "AA", "category": "Operable"},
            "2.4.7": {"name": "Focus Visible", "level": "AA", "category": "Operable"},
            "2.5.1": {"name": "Pointer Gestures", "level": "A", "category": "Operable"},
            "2.5.2": {"name": "Pointer Cancellation", "level": "A", "category": "Operable"},
            "2.5.3": {"name": "Label in Name", "level": "A", "category": "Operable"},
            "2.5.4": {"name": "Motion Actuation", "level": "A", "category": "Operable"},
            "3.1.1": {"name": "Language of Page", "level": "A", "category": "Understandable"},
            "3.1.2": {"name": "Language of Parts", "level": "AA", "category": "Understandable"},
            "3.2.1": {"name": "On Focus", "level": "A", "category": "Understandable"},
            "3.2.2": {"name": "On Input", "level": "A", "category": "Understandable"},
            "3.2.3": {"name": "Consistent Navigation", "level": "AA", "category": "Understandable"},
            "3.2.4": {"name": "Consistent Identification", "level": "AA", "category": "Understandable"},
            "3.3.1": {"name": "Error Identification", "level": "A", "category": "Understandable"},
            "3.3.2": {"name": "Labels or Instructions", "level": "A", "category": "Understandable"},
            "3.3.3": {"name": "Error Suggestion", "level": "AA", "category": "Understandable"},
            "3.3.4": {"name": "Error Prevention (Legal, Financial, Data)", "level": "AA", "category": "Understandable"},
            "4.1.1": {"name": "Parsing", "level": "A", "category": "Robust"},
            "4.1.2": {"name": "Name, Role, Value", "level": "A", "category": "Robust"},
            "4.1.3": {"name": "Status Messages", "level": "AA", "category": "Robust"}
        }
        
        # TV/Streaming specific accessibility considerations
        self.tv_accessibility_focus = [
            "Remote control navigation",
            "Screen reader compatibility",
            "High contrast modes",
            "Text size and readability",
            "Audio descriptions",
            "Closed captions",
            "Motion sensitivity",
            "Cognitive load management"
        ]
        
        # Performance tracking
        self.accessibility_metrics = {
            "wcag_violations_found": [],
            "severity_distribution": {"Critical": 0, "High": 0, "Medium": 0, "Low": 0},
            "improvement_trends": []
        }
    
    async def async_review(self, 
                          image_data: str,
                          design_type: str,
                          context: Dict[str, Any],
                          analysis_results: List[ReviewResult]) -> List[ReviewResult]:
        """
        Conduct async accessibility review.
        
        Args:
            image_data: Base64 encoded image
            design_type: Type of design being reviewed
            context: Additional context
            analysis_results: Results from initial analysis
            
        Returns:
            List of accessibility review results
        """
        # Get accessibility research context
        research_context = await self._get_accessibility_research(design_type)
        
        # Analyze accessibility implications from other reviews
        accessibility_context = self._extract_accessibility_context(analysis_results)
        
        # Create accessibility review prompt
        prompt = self._create_accessibility_prompt(
            design_type, research_context, accessibility_context, context
        )
        
        try:
            messages = [
                SystemMessage(content=prompt),
                HumanMessage(content=[
                    {"type": "text", "text": "Please conduct a comprehensive accessibility review of this design."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
                ])
            ]
            
            response = await self.llm.ainvoke(messages)
            
            # Parse the response into structured accessibility feedback
            review_result = self._parse_accessibility_response(response.content, design_type)
            
            # Store for accessibility learning
            self.review_history.append(review_result)
            self._update_accessibility_patterns(review_result)
            
            return [review_result]
            
        except Exception as e:
            print(f"Accessibility review failed: {e}")
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
    
    async def _get_accessibility_research(self, design_type: str) -> str:
        """Get accessibility research and guidelines."""
        if not self.exa_agent:
            return ""
        
        try:
            # Search for accessibility guidelines and best practices
            research_queries = [
                f"{design_type} accessibility WCAG guidelines",
                f"TV interface accessibility best practices",
                f"streaming platform accessibility requirements"
            ]
            
            all_context = []
            for query in research_queries:
                results = self.exa_agent.search_accessibility_guidelines(query, 2)
                if results:
                    for doc in results:
                        title = doc.metadata.get('title', 'Unknown')
                        content_preview = doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
                        all_context.append(f"♿ {title}: {content_preview}")
            
            return "\n".join(all_context) if all_context else ""
            
        except Exception as e:
            print(f"Accessibility research failed: {e}")
            return ""
    
    def _extract_accessibility_context(self, analysis_results: List[ReviewResult]) -> str:
        """Extract accessibility-relevant context from other reviews."""
        if not analysis_results:
            return ""
        
        accessibility_keywords = [
            "contrast", "color", "text", "font", "readable", "visible",
            "navigation", "focus", "keyboard", "screen reader", "aria",
            "accessibility", "a11y", "inclusive", "usability"
        ]
        
        relevant_feedback = []
        for result in analysis_results:
            # Find accessibility-relevant content
            for line in result.feedback.split('.'):
                if any(keyword in line.lower() for keyword in accessibility_keywords):
                    relevant_feedback.append(f"{result.agent_name}: {line.strip()}")
        
        return "\n".join(relevant_feedback[:5]) if relevant_feedback else ""
    
    def _create_accessibility_prompt(self, 
                                   design_type: str,
                                   research_context: str,
                                   accessibility_context: str,
                                   context: Dict[str, Any]) -> str:
        """Create the accessibility review prompt."""
        
        # Get relevant WCAG criteria for the target level
        relevant_criteria = []
        for criterion_id, criterion_info in self.wcag_criteria.items():
            if (criterion_info["level"] == "A" or 
                (self.wcag_level == "AA" and criterion_info["level"] in ["A", "AA"]) or
                (self.wcag_level == "AAA")):
                relevant_criteria.append(f"• {criterion_id}: {criterion_info['name']} ({criterion_info['level']})")
        
        criteria_context = "\n".join(relevant_criteria[:15])  # Limit for prompt length
        
        # TV-specific considerations
        tv_considerations = "\n".join([f"• {consideration}" for consideration in self.tv_accessibility_focus])
        
        prompt = f"""
You are an Accessibility Expert conducting a comprehensive WCAG {self.wcag_level} compliance review of a {design_type}.

Your Expertise:
- WCAG 2.1 Guidelines specialist
- Assistive technology expert
- Inclusive design advocate
- TV/streaming platform accessibility specialist

Target User Groups:
{chr(10).join([f"• {disability}" for disability in self.target_disabilities])}

WCAG {self.wcag_level} Success Criteria to Evaluate:
{criteria_context}

TV/Streaming Platform Specific Considerations:
{tv_considerations}

Current Accessibility Research:
{research_context}

Context from Other Reviews:
{accessibility_context}

Evaluation Framework:

1. **Visual Accessibility**
   - Color contrast ratios (4.5:1 for normal text, 3:1 for large text)
   - Color dependency for information
   - Text readability and sizing
   - Visual focus indicators

2. **Navigation Accessibility**
   - Keyboard/remote control navigation
   - Focus order and management
   - Skip links and shortcuts
   - Consistent navigation patterns

3. **Content Accessibility**
   - Alternative text for images
   - Proper heading structure
   - Clear language and instructions
   - Error handling and feedback

4. **Interactive Accessibility**
   - Form labels and instructions
   - Button and link clarity
   - Touch target sizes (minimum 44px)
   - Pointer gesture alternatives

5. **Media Accessibility**
   - Captions and transcripts
   - Audio descriptions
   - Auto-play controls
   - Motion controls and preferences

For each issue found, provide:
- **Severity**: Critical/High/Medium/Low
- **WCAG Criterion**: Specific WCAG reference
- **Impact**: Who is affected and how
- **Solution**: Specific remediation steps
- **Priority**: Implementation priority

Rate overall accessibility 1-10 and provide confidence level.
Focus on actionable, specific recommendations with clear implementation guidance.
Consider the TV viewing context and remote control interaction patterns.
"""
        
        return prompt
    
    def _parse_accessibility_response(self, response_content: str, design_type: str) -> ReviewResult:
        """Parse the accessibility review response into structured format."""
        
        # Extract accessibility score
        score = self._extract_accessibility_score(response_content)
        
        # Extract confidence
        confidence = self._extract_confidence(response_content)
        
        # Extract structured accessibility issues
        issues = self._extract_accessibility_issues(response_content)
        
        # Extract specific recommendations
        recommendations = self._extract_accessibility_recommendations(response_content)
        
        # Calculate WCAG compliance level
        wcag_compliance = self._assess_wcag_compliance(issues)
        
        return ReviewResult(
            agent_type="accessibility",
            agent_name="Accessibility Expert",
            score=score,
            feedback=response_content,
            specific_issues=[issue.description for issue in issues],
            recommendations=recommendations,
            confidence=confidence,
            review_time=datetime.now(),
            metadata={
                "wcag_level": self.wcag_level,
                "wcag_compliance": wcag_compliance,
                "accessibility_issues": [
                    {
                        "severity": issue.severity,
                        "wcag_criterion": issue.wcag_criterion,
                        "description": issue.description,
                        "impact": issue.impact,
                        "solution": issue.solution,
                        "affected_users": issue.affected_users
                    } for issue in issues
                ],
                "target_disabilities": self.target_disabilities,
                "design_type": design_type,
                "tv_specific_review": "TV" in design_type or "streaming" in design_type.lower()
            }
        )
    
    def _extract_accessibility_score(self, response_content: str) -> float:
        """Extract accessibility score from response."""
        # Look for numerical scores
        score_patterns = [
            r'accessibility.*?(\d+(?:\.\d+)?)/10',
            r'score.*?(\d+(?:\.\d+)?)/10',
            r'rating.*?(\d+(?:\.\d+)?)'
        ]
        
        for pattern in score_patterns:
            match = re.search(pattern, response_content.lower())
            if match:
                try:
                    score = float(match.group(1))
                    if 1 <= score <= 10:
                        return score
                except:
                    pass
        
        # Fallback: assess based on severity of issues found
        severity_indicators = {
            "critical": -3.0,
            "high": -1.5,
            "medium": -0.5,
            "low": -0.2
        }
        
        base_score = 8.0
        for severity, penalty in severity_indicators.items():
            count = response_content.lower().count(severity)
            base_score += count * penalty
        
        return max(1.0, min(10.0, base_score))
    
    def _extract_confidence(self, response_content: str) -> float:
        """Extract confidence level from response."""
        confidence_match = re.search(r'confidence.*?(\d+(?:\.\d+)?)', response_content.lower())
        if confidence_match:
            try:
                confidence = float(confidence_match.group(1))
                return confidence / 100 if confidence > 1 else confidence
            except:
                pass
        
        # Calculate based on response thoroughness
        accessibility_terms = [
            "wcag", "aria", "contrast", "keyboard", "screen reader",
            "accessibility", "inclusive", "usability", "navigation"
        ]
        
        term_count = sum(1 for term in accessibility_terms if term in response_content.lower())
        word_count = len(response_content.split())
        
        # Higher confidence for more thorough responses
        thoroughness = min(1.0, term_count / 5)
        depth = min(1.0, word_count / 800)
        
        return (thoroughness + depth) / 2
    
    def _extract_accessibility_issues(self, response_content: str) -> List[AccessibilityIssue]:
        """Extract structured accessibility issues from response."""
        issues = []
        
        # Parse structured issues (simplified implementation)
        lines = response_content.split('\n')
        current_issue = {}
        
        for line in lines:
            line = line.strip()
            
            # Look for severity indicators
            if any(severity in line.lower() for severity in ["critical", "high", "medium", "low"]):
                if current_issue:
                    issues.append(self._create_accessibility_issue(current_issue))
                    current_issue = {}
                
                # Extract severity
                for severity in ["critical", "high", "medium", "low"]:
                    if severity in line.lower():
                        current_issue["severity"] = severity.title()
                        break
                
                current_issue["description"] = line
            
            # Look for WCAG criterion
            elif re.search(r'\d+\.\d+\.\d+', line):
                wcag_match = re.search(r'(\d+\.\d+\.\d+)', line)
                if wcag_match:
                    current_issue["wcag_criterion"] = wcag_match.group(1)
            
            # Extract other components
            elif "impact:" in line.lower():
                current_issue["impact"] = line.split(":", 1)[1].strip()
            elif "solution:" in line.lower():
                current_issue["solution"] = line.split(":", 1)[1].strip()
        
        # Add final issue
        if current_issue:
            issues.append(self._create_accessibility_issue(current_issue))
        
        return issues[:10]  # Limit to prevent overwhelming output
    
    def _create_accessibility_issue(self, issue_data: Dict[str, str]) -> AccessibilityIssue:
        """Create AccessibilityIssue object from parsed data."""
        return AccessibilityIssue(
            severity=issue_data.get("severity", "Medium"),
            wcag_criterion=issue_data.get("wcag_criterion", "General"),
            description=issue_data.get("description", "Accessibility issue identified"),
            impact=issue_data.get("impact", "May affect user experience"),
            solution=issue_data.get("solution", "Review and implement accessibility best practices"),
            affected_users=self._determine_affected_users(issue_data.get("description", ""))
        )
    
    def _determine_affected_users(self, description: str) -> List[str]:
        """Determine which user groups are affected by an issue."""
        affected = []
        
        user_indicators = {
            "Visual impairments": ["contrast", "color", "visual", "text", "font", "visibility"],
            "Hearing impairments": ["audio", "caption", "sound", "transcript"],
            "Motor impairments": ["keyboard", "mouse", "click", "navigation", "gesture"],
            "Cognitive impairments": ["complex", "confusing", "language", "instruction", "clarity"],
            "Screen reader users": ["aria", "label", "alt", "semantic", "structure"]
        }
        
        description_lower = description.lower()
        for user_group, indicators in user_indicators.items():
            if any(indicator in description_lower for indicator in indicators):
                affected.append(user_group)
        
        return affected if affected else ["General users"]
    
    def _extract_accessibility_recommendations(self, response_content: str) -> List[str]:
        """Extract accessibility recommendations from response."""
        recommendations = []
        
        recommendation_keywords = [
            "recommend", "should", "implement", "add", "improve",
            "ensure", "provide", "include", "consider", "use"
        ]
        
        lines = response_content.split('\n')
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in recommendation_keywords):
                # Clean up the line
                clean_line = re.sub(r'^[-•*]\s*|\d+\.\s*', '', line)
                if clean_line and len(clean_line) > 20:
                    recommendations.append(clean_line)
        
        return recommendations[:8]  # Limit to top recommendations
    
    def _assess_wcag_compliance(self, issues: List[AccessibilityIssue]) -> Dict[str, Any]:
        """Assess overall WCAG compliance based on issues found."""
        compliance_assessment = {
            "level": "Non-compliant",
            "critical_violations": 0,
            "high_violations": 0,
            "medium_violations": 0,
            "low_violations": 0,
            "total_violations": len(issues)
        }
        
        for issue in issues:
            severity_key = f"{issue.severity.lower()}_violations"
            if severity_key in compliance_assessment:
                compliance_assessment[severity_key] += 1
        
        # Determine compliance level
        if compliance_assessment["critical_violations"] == 0 and compliance_assessment["high_violations"] == 0:
            if compliance_assessment["medium_violations"] <= 2:
                compliance_assessment["level"] = f"WCAG {self.wcag_level} Compliant"
            else:
                compliance_assessment["level"] = "Partially Compliant"
        elif compliance_assessment["critical_violations"] == 0 and compliance_assessment["high_violations"] <= 1:
            compliance_assessment["level"] = "Partially Compliant"
        
        return compliance_assessment
    
    def _update_accessibility_patterns(self, review_result: ReviewResult):
        """Update accessibility patterns for learning."""
        # Track common accessibility issues
        for issue_description in review_result.specific_issues:
            # Simple pattern recognition (would be more sophisticated in practice)
            key_words = [word.lower() for word in issue_description.split() if len(word) > 3]
            for word in key_words[:3]:  # Track top 3 keywords
                self.accessibility_patterns[word] = self.accessibility_patterns.get(word, 0) + 1
        
        # Update metrics
        severity_dist = review_result.metadata.get("accessibility_issues", [])
        for issue in severity_dist:
            severity = issue.get("severity", "Medium")
            if severity in self.accessibility_metrics["severity_distribution"]:
                self.accessibility_metrics["severity_distribution"][severity] += 1
    
    def get_accessibility_summary(self) -> Dict[str, Any]:
        """Get accessibility summary and insights."""
        if not self.review_history:
            return {"message": "No accessibility review history available."}
        
        scores = [r.score for r in self.review_history]
        total_issues = sum(len(r.specific_issues) for r in self.review_history)
        
        # Common accessibility patterns
        top_patterns = sorted(self.accessibility_patterns.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "total_reviews": len(self.review_history),
            "average_accessibility_score": round(sum(scores) / len(scores), 2),
            "total_issues_identified": total_issues,
            "wcag_level": self.wcag_level,
            "severity_distribution": self.accessibility_metrics["severity_distribution"],
            "common_issue_patterns": [pattern for pattern, count in top_patterns],
            "target_disabilities": self.target_disabilities,
            "accessibility_trend": "improving" if len(scores) >= 3 and scores[-1] > scores[-3] else "stable"
        }


# Example usage
if __name__ == "__main__":
    import os
    
    openai_key = os.getenv('OPENAI_API_KEY')
    exa_key = os.getenv('EXA_API_KEY')
    
    if openai_key:
        # Create accessibility review agent
        accessibility_agent = AccessibilityReviewAgent(
            openai_api_key=openai_key,
            wcag_level="AA",
            target_disabilities=[
                "Visual impairments",
                "Hearing impairments", 
                "Motor impairments",
                "Cognitive impairments",
                "Age-related impairments"
            ],
            exa_api_key=exa_key
        )
        
        print("✅ Accessibility Review Agent created successfully")
        print(f"♿ WCAG Level: {accessibility_agent.wcag_level}")
        print(f"🎯 Target Disabilities: {len(accessibility_agent.target_disabilities)} categories")
        print(f"📋 WCAG Criteria: {len(accessibility_agent.wcag_criteria)} success criteria")
        print(f"🔍 Research capability: {'enabled' if exa_key else 'disabled'}")
        
        # Show focus areas
        print("\n📺 TV-Specific Accessibility Focus:")
        for focus_area in accessibility_agent.tv_accessibility_focus:
            print(f"  - {focus_area}")
    else:
        print("❌ OPENAI_API_KEY required")
