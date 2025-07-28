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
    
    rubric_text = "# Roku Design Evaluation Grading Rubric\n\n"
    
    for grade, details in rubric.items():
        rubric_text += f"## Grade {grade}: {details['description']}\n"
        rubric_text += f"{details['criteria']}\n\n"
    
    return rubric_text

def get_all_principles_summary() -> str:
    """Get a summary of all Roku design principles."""
    principles = roku_knowledge_base.get_all_principles()
    
    summary = "# Roku TV Design Principles\n\n"
    
    for key, principle in principles.items():
        summary += f"## {principle.name}: {principle.description}\n"
        summary += f"**Key Focus:** {', '.join(principle.key_aspects[:2])}\n\n"
    
    return summary
