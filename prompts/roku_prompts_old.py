"""
Roku TV Design Review Prompts

This module provides specialized prompts for evaluating Roku TV interface designs
using the VP's comprehensive evaluation criteria from the knowledge base.
"""

from typing import List, Optional
from knowledge.roku_criteria import roku_knowledge_base

def get_roku_evaluation_prompt(
    design_context: str = "",
    focus_areas: Optional[List[str]] = None,
    include_grading: bool = True
) -> str:
    """
    Generate a comprehensive Roku TV design evaluation prompt.
    
    Args:
        design_context: Context about the specific design being evaluated
        focus_areas: Specific areas to focus evaluation on
        include_grading: Whether to include letter grading
        
    Returns:
        Formatted evaluation prompt
    """
    
    # Get the base evaluation prompt from knowledge base
    base_prompt = roku_knowledge_base.get_evaluation_prompt(focus_areas)
    
    # Add context-specific information
    context_section = ""
    if design_context:
        context_section = f"""
## DESIGN CONTEXT
{design_context}

Please evaluate this specific design context against the Roku principles below.
"""
    
    # Combine all sections
    full_prompt = f"""{context_section}

{base_prompt}

## ADDITIONAL INSTRUCTIONS

- Focus on practical, actionable feedback
- Consider the VP's perspective: "Can this design actually be seen and analyzed from embedded images?"
- Prioritize issues that impact core user journeys
- Provide specific recommendations, not just criticism
- Consider both immediate usability and long-term user satisfaction

Remember: This evaluation helps solve the VP's problem of not being able to see images in ai.roku.com - you CAN see the actual design files!
"""
    
    return full_prompt

def get_principle_explanation(principle_name: str) -> str:
    """Get detailed explanation of a specific Roku design principle."""
    principle = roku_knowledge_base.get_principle_details(principle_name)
    
    if not principle:
        return f"Principle '{principle_name}' not found."
    
    explanation = f"""
# {principle.name.upper()}: {principle.description}

## Key Aspects:
{chr(10).join(f"• {aspect}" for aspect in principle.key_aspects)}

## Evaluation Questions:
{chr(10).join(f"• {question}" for question in principle.evaluation_questions)}

## Success Indicators:
{chr(10).join(f"✅ {indicator}" for indicator in principle.success_indicators)}

## Common Failures:
{chr(10).join(f"❌ {failure}" for failure in principle.common_failures)}
"""
    
    return explanation

def get_grading_rubric() -> str:
    """Get the Roku design grading rubric."""
    rubric = roku_knowledge_base.get_grading_criteria()
    
    rubric_text = "# Roku Design Evaluation Grading Rubric

"
    
    for grade, details in rubric.items():
        rubric_text += f"## Grade {grade}: {details['description']}
"
        rubric_text += f"{details['criteria']}

"
    
    return rubric_text

def get_all_principles_summary() -> str:
    """Get a summary of all Roku design principles."""
    principles = roku_knowledge_base.get_all_principles()
    
    summary = "# Roku TV Design Principles

"
    
    for key, principle in principles.items():
        summary += f"## {principle.name}: {principle.description}
"
        summary += f"**Key Focus:** {', '.join(principle.key_aspects[:2])}

"
    
    return summary

class RokuDesignPrompts:
    """
    Roku-specific design evaluation prompts and criteria.
    """
    
    def __init__(self):
        self.key_principles = {
            "easy": """
1. Easy to use with minimal effort to achieve user's goal (typically "watching something great")
- Clear primary purpose per screen with visually prominent important actions
- Helpful and efficient features with most useful options prominent
- Minimize clicks, provide simple choices, use plain concise language
- Clear content entitlement indicators (free vs. paid)
- All UI accessible with standard remote buttons (HOME, BACK, UP, DOWN, LEFT, RIGHT, OK, STAR, PLAY/PAUSE)
- Adhere to accessibility standards (WCAG) with high contrast, scalable fonts, clear focus indicators
- Present manageable options (5-7 per screen), group logically with clear visual hierarchy
- Intuitive consistent navigation with clear position indicators
            """,
            
            "just_works": """
2. Snappy, reliable experience free of crashes and errors
- Show progress for transitions exceeding 2 seconds
- Minimize likelihood of user errors with clear, actionable error messages
- Design for accessibility including screen reader support
- Design for global audience with space for translation
- Provide immediate feedback for user actions
            """,
            
            "looks_simple": """
3. Clear visual communication of location and available actions
- Minimal, sufficient-sized text with good contrast
- Clean, focused layout using whitespace and alignment
- Minimize competing elements and different kinds of actions
- Optimize element sizing for easy viewing without overwhelming
- Consistent UI for similar use cases
- Minimize distractions, use predictable subtle animations
- Respect Reduce Motion accessibility setting
            """,
            
            "trustworthy": """
4. Meet user expectations with straightforward communication
- Screen purpose matches user expectations
- Accurate labels and actions representing actual functionality
- Clear indication of content costs (free, subscription, additional charges)
- Transparent data usage explanations
- Prioritize user needs over aggressive upselling
- Mark recommended choices clearly
            """,
            
            "delightful": """
5. Deliver unexpected smiles through:
- Unexpectedly simple tasks
- Unexpectedly helpful features
- Pleasant images or animations
- Smooth animations, personalized recommendations, celebratory messages
            """,
            
            "outcome_focused": """
6. Meet user needs while supporting business goals
- Optimize for critical user journey completion
- Align features with business goals while enhancing user experience
- Balance monetization with user trust through upfront cost communication
            """
        }
        
        self.critical_user_journeys = [
            "Continue watching unfinished content",
            "Search for specific show/movie",
            "Find content from existing subscriptions",
            "Browse by genre or type",
            "Find free content with commercials",
            "Discover popular or new content",
            "Track content for later viewing",
            "Get personalized recommendations",
            "Watch live broadcasts",
            "Manage TV spending",
            "Set up new Roku device",
            "Learn Roku capabilities"
        ]
        
        self.technical_constraints = """
TV Interface Constraints:
- Designs displayed on TV screen controlled by Roku remote
- Remote buttons: BACK, HOME, UP, DOWN, LEFT, RIGHT, OK, STAR, REPLAY, PLAY/PAUSE, REWIND, FAST FORWARD, VOICE
- No direct clicking - must navigate with directional buttons then press OK
- Badges on content tiles ($ or "New Episode") are display-only, not clickable
- Ignore "Roku Preview" text in mockups
        """
        
        self.specific_rules = """
Specific Pattern Rules:
- $ indicator: Lower left corner for paid content
- Metadata: Show streaming service icons below content tiles
- Interactive HUD: For interactive elements
- MiniHUD: Brief status changes, max 60 characters
- Countdown Timers: Alert users of upcoming changes, disabled for screen readers
- Autoplay: Video yes, sound no (user must enable sound)
        """
    
    def get_roku_evaluation_prompt(
        self, 
        design_context: str = "", 
        focus_areas: list = None,
        include_grading: bool = True
    ) -> str:
        """
        Generate comprehensive Roku design evaluation prompt.
        
        Args:
            design_context: Additional context about the design being evaluated
            focus_areas: Specific areas to focus on (if None, evaluates all)
            include_grading: Whether to include letter grading
            
        Returns:
            Complete evaluation prompt
        """
        
        focus_instruction = ""
        if focus_areas:
            focus_instruction = f"\nFocus particularly on these areas: {', '.join(focus_areas)}"
        
        prompt = f"""You are an expert UX designer for TV interfaces. Evaluate the provided DESIGN PAGE to ensure all Roku UX designs and specifications are easy-to-learn, easy-to-use, and align with Roku's core tenets of simplicity and delight, while maintaining transparency and trust with the user.

{design_context}

EVALUATION CRITERIA:
Evaluate with regards to usability, learnability, information architecture and findability, visual design and aesthetics, accessibility, localization, layout, and emotional impact and delight.

Focus on functionality, clarity of information, visual cues, overall ease of understanding the system's functionality, intuitiveness of the navigation structure, use of color and contrast, typography, and imagery, overall layout, microinteractions, animations, specific words and tone of language.{focus_instruction}

KEY PRINCIPLES TO EVALUATE AGAINST:

{self.key_principles['easy']}

{self.key_principles['just_works']}

{self.key_principles['looks_simple']}

{self.key_principles['trustworthy']}

{self.key_principles['delightful']}

{self.key_principles['outcome_focused']}

CRITICAL USER JOURNEYS TO CONSIDER:
{chr(10).join([f"- {journey}" for journey in self.critical_user_journeys])}

{self.technical_constraints}

{self.specific_rules}

OUTPUT FORMAT:

1. **Known Issues Section** (if applicable):
   - List any current issues identified in the design (e.g., missing icons, "U.S. only" or "English only" limitations)
   - Do NOT mention these issues elsewhere in the evaluation

2. **Priority Issues Table**:
   Create a table with columns: Number | Priority | Type of Issue | Description | Recommendation
   - Number each row sequentially
   - Order by priority (highest to lowest)
   - Type includes: navigation, visual design, accessibility, information architecture, etc.
   - Include ALL identified issues (including missing items)
   - Focus on the specific feature being evaluated, not the entire system

3. **Purpose and Value Questions**:
   - List key questions about unclear feature purpose or value
   - Provide recommendations for how to answer each question

4. **Critical User Journey Impact**:
   - Identify which journeys will be MORE successful with this design
   - Identify which journeys might be made WORSE by this design

5. **Design Variation Selection** (if multiple options provided):
   - Identify which variation should be selected and why

{"6. **Letter Grade**: Assign a letter grade (A, B, C, D, F with + and - allowed) based on overall quality against the criteria" if include_grading else ""}

7. **Scope Expansion Suggestions**:
   - Describe improvements that would benefit users and business
   - Explain why these improvements would be valuable

EVALUATION GUIDELINES:
- Be specific and actionable in recommendations
- Consider both user experience and business objectives
- Maintain focus on TV interface constraints and remote control navigation
- Ensure recommendations align with Roku's design principles
- Consider accessibility and global audience needs"""

        return prompt
    
    def get_confluence_extraction_prompt(self) -> str:
        """Get prompt for extracting design information from Confluence pages."""
        return """Extract all design-related information from this Confluence page, including:

1. **Design Specifications**: Any mentioned features, layouts, or UI elements
2. **Images and Mockups**: Describe any embedded images, screenshots, or design mockups in detail
3. **User Stories or Requirements**: Any mentioned user needs or business requirements
4. **Current Issues**: Any acknowledged problems or limitations
5. **Design Variations**: Multiple options or iterations if present
6. **Context**: Background information about the feature or page purpose

Format the extracted information clearly with headers and bullet points for easy analysis."""
    
    def get_figma_analysis_prompt(self) -> str:
        """Get prompt for analyzing Figma designs with Roku criteria."""
        return """Analyze this Figma design file for TV interface compliance with Roku design standards.

Pay special attention to:
- Remote control navigation patterns
- TV screen layout and proportions  
- Content tile arrangements and entitlement indicators
- Text sizing and contrast for TV viewing
- Focus states and highlight indicators
- Information hierarchy and visual prominence

Extract all design elements, interactions, and layout decisions for comprehensive evaluation."""
