"""
Roku TV Design Evaluation Criteria - Knowledge Base

This module contains the comprehensive design evaluation criteria for Roku TV interfaces,
based on the VP's established standards and principles.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class DesignPrinciple:
    """Represents a core design principle with evaluation criteria."""
    name: str
    description: str
    key_aspects: List[str]
    evaluation_questions: List[str]
    success_indicators: List[str]
    common_failures: List[str]

class RokuDesignKnowledgeBase:
    """
    Knowledge base containing Roku TV design evaluation criteria.
    
    This serves as the single source of truth for design evaluation standards,
    making the criteria modular and easy to update.
    """
    
    def __init__(self):
        self.principles = self._load_core_principles()
        self.critical_user_journeys = self._load_critical_journeys()
        self.technical_constraints = self._load_technical_constraints()
        self.grading_rubric = self._load_grading_rubric()
    
    def _load_core_principles(self) -> Dict[str, DesignPrinciple]:
        """Load the 6 core Roku design principles."""
        return {
            "easy": DesignPrinciple(
                name="Easy",
                description="Users can achieve their goals with minimal effort and the primary purpose is clear",
                key_aspects=[
                    "Clear primary purpose",
                    "Minimal cognitive load",
                    "Intuitive navigation flow",
                    "Reduced steps to completion"
                ],
                evaluation_questions=[
                    "What is the primary purpose of this screen/feature?",
                    "How many steps does it take to complete the main task?",
                    "Are there any unnecessary complexity or friction points?",
                    "Would a first-time user understand what to do immediately?"
                ],
                success_indicators=[
                    "Single, clear call-to-action",
                    "Logical information hierarchy",
                    "Minimal scrolling required",
                    "Obvious next steps"
                ],
                common_failures=[
                    "Multiple competing CTAs",
                    "Unclear primary action",
                    "Too many options presented at once",
                    "Hidden or buried primary functions"
                ]
            ),
            
            "just_works": DesignPrinciple(
                name="Just Works",
                description="Snappy, reliable, and error-free experience that performs as expected",
                key_aspects=[
                    "Performance optimization",
                    "Error prevention and handling",
                    "System reliability",
                    "Responsive interactions"
                ],
                evaluation_questions=[
                    "Are loading states and feedback provided?",
                    "How are errors handled and communicated?",
                    "Does the interface respond immediately to user input?",
                    "Are there any potential failure points?"
                ],
                success_indicators=[
                    "Immediate visual feedback",
                    "Clear loading indicators",
                    "Graceful error recovery",
                    "Consistent performance"
                ],
                common_failures=[
                    "Long loading times without feedback",
                    "Unclear error messages",
                    "System crashes or freezes",
                    "Inconsistent response times"
                ]
            ),
            
            "looks_simple": DesignPrinciple(
                name="Looks Simple",
                description="Clear visual communication with minimal clutter and obvious functionality",
                key_aspects=[
                    "Visual hierarchy",
                    "Clean layout design",
                    "Purposeful use of space",
                    "Clear information architecture"
                ],
                evaluation_questions=[
                    "Is the visual hierarchy clear and logical?",
                    "Are there any unnecessary visual elements?",
                    "Does the layout support the primary user goal?",
                    "Is the information organized in a scannable way?"
                ],
                success_indicators=[
                    "Clean, uncluttered layout",
                    "Clear visual hierarchy",
                    "Purposeful whitespace usage",
                    "Consistent design patterns"
                ],
                common_failures=[
                    "Visual clutter and noise",
                    "Poor contrast and readability",
                    "Inconsistent styling",
                    "Overwhelming amount of information"
                ]
            ),
            
            "trustworthy": DesignPrinciple(
                name="Trustworthy",
                description="Meets user expectations through straightforward communication and reliable behavior",
                key_aspects=[
                    "Predictable behavior",
                    "Clear communication",
                    "Transparent information",
                    "Consistent patterns"
                ],
                evaluation_questions=[
                    "Does the interface behave as users would expect?",
                    "Is information presented clearly and honestly?",
                    "Are there any misleading elements?",
                    "Does it follow established conventions?"
                ],
                success_indicators=[
                    "Predictable navigation patterns",
                    "Clear, honest messaging",
                    "Transparent pricing/terms",
                    "Consistent interaction patterns"
                ],
                common_failures=[
                    "Misleading buttons or links",
                    "Hidden costs or terms",
                    "Inconsistent behavior",
                    "Confusing navigation patterns"
                ]
            ),
            
            "delightful": DesignPrinciple(
                name="Delightful",
                description="Provides unexpected smiles and helpful features that enhance the user experience",
                key_aspects=[
                    "Moments of surprise",
                    "Helpful micro-interactions",
                    "Thoughtful details",
                    "Emotional connection"
                ],
                evaluation_questions=[
                    "Are there any delightful moments or surprises?",
                    "Do micro-interactions feel polished?",
                    "Are there helpful features that go beyond basic needs?",
                    "Does the experience create positive emotions?"
                ],
                success_indicators=[
                    "Smooth, polished animations",
                    "Helpful contextual features",
                    "Pleasant visual details",
                    "Personalized touches"
                ],
                common_failures=[
                    "Generic, soulless interface",
                    "Jarring or missing animations",
                    "Lack of personality",
                    "No consideration for emotional experience"
                ]
            ),
            
            "outcome_focused": DesignPrinciple(
                name="Outcome-Focused",
                description="Successfully meets user needs while supporting business goals",
                key_aspects=[
                    "User goal achievement",
                    "Business objective alignment",
                    "Measurable success metrics",
                    "Value proposition clarity"
                ],
                evaluation_questions=[
                    "Does this help users achieve their primary goal?",
                    "How does this support business objectives?",
                    "What metrics would indicate success?",
                    "Is the value proposition clear to users?"
                ],
                success_indicators=[
                    "Clear path to user goal completion",
                    "Aligned business and user objectives",
                    "Measurable success criteria",
                    "Obvious value proposition"
                ],
                common_failures=[
                    "Features that don't serve user needs",
                    "Business goals that conflict with user goals",
                    "Unclear value proposition",
                    "No clear success metrics"
                ]
            )
        }
    
    def _load_critical_journeys(self) -> Dict[str, List[str]]:
        """Load critical user journeys for TV interface evaluation."""
        return {
            "content_discovery": [
                "Finding something to watch quickly",
                "Browsing by genre or mood",
                "Searching for specific content",
                "Discovering new content recommendations"
            ],
            "content_consumption": [
                "Starting playback smoothly",
                "Controlling playback (pause, seek, volume)",
                "Switching between audio/subtitle options",
                "Exiting to browse for something else"
            ],
            "account_management": [
                "Signing up for new service",
                "Managing subscription settings",
                "Setting up parental controls",
                "Managing multiple user profiles"
            ],
            "system_navigation": [
                "Moving between apps/channels",
                "Accessing system settings",
                "Managing installed channels",
                "Using voice search effectively"
            ]
        }
    
    def _load_technical_constraints(self) -> Dict[str, List[str]]:
        """Load TV-specific technical constraints and considerations."""
        return {
            "remote_control": [
                "Directional pad (D-pad) navigation only",
                "Limited number of buttons available",
                "Voice remote capabilities",
                "Focus states must be clearly visible"
            ],
            "display_considerations": [
                "10-foot viewing distance",
                "Variable screen sizes (32\" to 75\"+)",
                "Different aspect ratios and resolutions",
                "Potential for overscan issues"
            ],
            "performance_constraints": [
                "Limited processing power",
                "Memory usage optimization",
                "Network connectivity variations",
                "Battery life for remote control"
            ],
            "accessibility": [
                "Screen reader compatibility",
                "High contrast mode support",
                "Audio description capabilities",
                "Closed captioning requirements"
            ]
        }
    
    def _load_grading_rubric(self) -> Dict[str, Dict[str, str]]:
        """Load the grading rubric for Roku design evaluation."""
        return {
            "A": {
                "description": "Exemplary - Exceeds Roku standards",
                "criteria": "Demonstrates mastery of all 6 principles with innovative solutions"
            },
            "B": {
                "description": "Proficient - Meets Roku standards", 
                "criteria": "Successfully implements 4-6 principles with minor areas for improvement"
            },
            "C": {
                "description": "Developing - Approaching standards",
                "criteria": "Implements 2-3 principles but needs significant improvements"
            },
            "D": {
                "description": "Beginning - Below standards",
                "criteria": "Shows understanding of 1-2 principles but major issues present"
            },
            "F": {
                "description": "Inadequate - Does not meet standards",
                "criteria": "Fails to demonstrate understanding of core principles"
            }
        }
    
    def get_evaluation_prompt(self, focus_areas: Optional[List[str]] = None) -> str:
        """Generate a comprehensive evaluation prompt based on the knowledge base."""
        prompt = """You are an expert Roku TV interface design evaluator. Use these comprehensive criteria to evaluate the design:

## CORE DESIGN PRINCIPLES

"""
        
        # Add all principles or just focused ones
        principles_to_include = self.principles.keys()
        if focus_areas:
            # Map focus areas to principles
            focus_mapping = {
                "usability": ["easy", "just_works"],
                "visual design": ["looks_simple"],
                "reliability": ["trustworthy", "just_works"],
                "experience": ["delightful"],
                "effectiveness": ["outcome_focused"],
                "navigation": ["easy", "trustworthy"],
                "accessibility": ["easy", "trustworthy"],
                "performance": ["just_works"]
            }
            
            mapped_principles = set()
            for area in focus_areas:
                if area in focus_mapping:
                    mapped_principles.update(focus_mapping[area])
            
            if mapped_principles:
                principles_to_include = mapped_principles
        
        for principle_key in principles_to_include:
            if principle_key in self.principles:
                principle = self.principles[principle_key]
                prompt += f"\n### {principle.name.upper()}: {principle.description}\n"
                prompt += f"**Key Aspects:** {', '.join(principle.key_aspects)}\n"
                prompt += f"**Evaluation Questions:**\n"
                for question in principle.evaluation_questions:
                    prompt += f"- {question}\n"
                prompt += "\n"
        
        prompt += """
## TV-SPECIFIC CONSIDERATIONS

**Remote Control Navigation:**
- All interactions must work with D-pad navigation
- Focus states must be clearly visible from 10 feet
- Limited button inputs available

**Display Optimization:**
- Designed for 10-foot viewing distance
- Text must be readable on smallest supported screen size
- High contrast for various lighting conditions

**Performance Requirements:**
- Fast loading and responsive interactions
- Optimized for limited processing power
- Graceful handling of network issues

## EVALUATION FORMAT

Provide your evaluation in this format:

**OVERALL GRADE:** [A/B/C/D/F]

**PRIORITIZED ISSUES TABLE:**
| Priority | Issue | Principle Violated | Recommendation |
|----------|-------|-------------------|----------------|
| High     | [Specific issue] | [Principle] | [Actionable fix] |
| Medium   | [Specific issue] | [Principle] | [Actionable fix] |
| Low      | [Specific issue] | [Principle] | [Actionable fix] |

**DETAILED ANALYSIS:**
[Comprehensive review addressing each relevant principle with specific examples and recommendations]

**CRITICAL USER JOURNEY IMPACT:**
[How identified issues affect key user journeys like content discovery, playback control, etc.]
"""
        
        return prompt
    
    def get_principle_details(self, principle_name: str) -> Optional[DesignPrinciple]:
        """Get detailed information about a specific principle."""
        return self.principles.get(principle_name.lower().replace(" ", "_"))
    
    def get_all_principles(self) -> Dict[str, DesignPrinciple]:
        """Get all design principles."""
        return self.principles
    
    def get_grading_criteria(self) -> Dict[str, Dict[str, str]]:
        """Get the grading rubric."""
        return self.grading_rubric

# Global knowledge base instance
roku_knowledge_base = RokuDesignKnowledgeBase()
