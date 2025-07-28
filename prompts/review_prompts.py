from typing import Dict

class DesignReviewPrompts:
    """
    Collection of prompt templates for design review tasks.
    """
    
    def __init__(self):
        self.base_prompt = """You are an expert design reviewer with extensive experience in UI/UX design, 
        visual design principles, accessibility, and brand consistency. Your role is to provide constructive, 
        actionable feedback on design work."""
        
        self.review_criteria = {
            "General Design": [
                "Visual hierarchy and layout",
                "Color scheme and contrast",
                "Typography and readability",
                "Spacing and alignment",
                "Overall aesthetic appeal",
                "User experience flow"
            ],
            "UI/UX": [
                "User interface usability",
                "Navigation clarity",
                "Interactive element design",
                "Information architecture",
                "User journey optimization",
                "Mobile responsiveness considerations"
            ],
            "Accessibility": [
                "Color contrast ratios",
                "Text readability",
                "Alternative text considerations",
                "Keyboard navigation support",
                "Screen reader compatibility",
                "WCAG compliance"
            ],
            "Brand Consistency": [
                "Brand guideline adherence",
                "Logo usage and placement",
                "Color palette consistency",
                "Typography consistency",
                "Visual style alignment",
                "Brand voice representation"
            ]
        }
    
    def get_review_prompt(
        self, 
        review_type: str, 
        detail_level: int, 
        include_suggestions: bool
    ) -> str:
        """
        Generate a review prompt based on parameters.
        
        Args:
            review_type: Type of review to perform
            detail_level: Level of detail (1-5)
            include_suggestions: Whether to include suggestions
            
        Returns:
            Formatted prompt string
        """
        criteria = self.review_criteria.get(review_type, self.review_criteria["General Design"])
        
        detail_instruction = {
            1: "Provide a brief overview",
            2: "Give a concise analysis",
            3: "Provide a balanced review",
            4: "Give a detailed analysis",
            5: "Provide a comprehensive, in-depth review"
        }[detail_level]
        
        prompt = f"""{self.base_prompt}

**Review Type**: {review_type}
**Detail Level**: {detail_instruction}

**Focus Areas for This Review**:
{chr(10).join(f"- {criterion}" for criterion in criteria)}

**Instructions**:
1. Analyze the design carefully against the focus areas listed above
2. {detail_instruction} with specific observations
3. Provide a design score from 1-10 (where 10 is excellent)
4. Be constructive and professional in your feedback
5. Point out both strengths and areas for improvement"""

        if include_suggestions:
            prompt += """
6. Provide 3-5 specific, actionable suggestions for improvement

**Format your response as follows**:
- Start with an overall assessment and score
- Discuss key strengths
- Identify areas for improvement
- End with specific suggestions (if requested)"""
        
        return prompt
    
    def get_chat_prompt(self) -> str:
        """Get prompt for chat interactions."""
        return f"""{self.base_prompt}

You are now in chat mode. The user may ask questions about design principles, 
seek advice on specific design challenges, or want to discuss design-related topics.

**Guidelines**:
- Be helpful and educational
- Provide practical advice
- Reference design best practices
- Ask clarifying questions when needed
- Keep responses concise but informative
- Maintain a friendly, professional tone"""
    
    def get_scoring_criteria(self, review_type: str) -> Dict[str, str]:
        """Get scoring criteria for a specific review type."""
        criteria = {
            "General Design": {
                "9-10": "Exceptional design with excellent visual hierarchy, perfect color harmony, outstanding typography, and flawless execution",
                "7-8": "Strong design with good visual principles, effective color use, clear typography, and professional execution",
                "5-6": "Adequate design with basic visual principles, acceptable color choices, readable typography, and competent execution",
                "3-4": "Below average design with weak visual hierarchy, poor color choices, unclear typography, or execution issues",
                "1-2": "Poor design with major visual problems, inappropriate colors, unreadable text, or significant execution flaws"
            },
            "UI/UX": {
                "9-10": "Intuitive interface with excellent usability, clear navigation, perfect information architecture, and optimal user flow",
                "7-8": "Good interface with solid usability, effective navigation, good information structure, and smooth user experience",
                "5-6": "Functional interface with basic usability, adequate navigation, acceptable information organization, and decent user flow",
                "3-4": "Problematic interface with usability issues, confusing navigation, poor information structure, or awkward user flow",
                "1-2": "Broken interface with major usability problems, unclear navigation, chaotic information architecture, or frustrated user experience"
            },
            "Accessibility": {
                "9-10": "Fully accessible with excellent contrast, perfect readability, comprehensive alt text, keyboard support, and WCAG AAA compliance",
                "7-8": "Highly accessible with good contrast, clear readability, appropriate alt text, keyboard navigation, and WCAG AA compliance",
                "5-6": "Moderately accessible with acceptable contrast, readable text, basic alt text considerations, and partial keyboard support",
                "3-4": "Limited accessibility with poor contrast, readability issues, missing alt text, or inadequate keyboard support",
                "1-2": "Inaccessible with major contrast problems, unreadable text, no accessibility considerations, or complete keyboard navigation failure"
            },
            "Brand Consistency": {
                "9-10": "Perfect brand alignment with flawless guideline adherence, consistent visual elements, and strong brand identity representation",
                "7-8": "Strong brand consistency with good guideline following, mostly consistent elements, and clear brand identity",
                "5-6": "Adequate brand consistency with basic guideline adherence, some consistent elements, and recognizable brand identity",
                "3-4": "Weak brand consistency with poor guideline following, inconsistent elements, or unclear brand identity",
                "1-2": "No brand consistency with complete guideline violations, conflicting elements, or unrecognizable brand identity"
            }
        }
        
        return criteria.get(review_type, criteria["General Design"])
