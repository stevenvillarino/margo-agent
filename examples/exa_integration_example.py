"""
Example integration of Exa search into the design review process.

This demonstrates how to enhance design reviews with real-time web research
using the Exa AI search API.
"""

from typing import List, Dict, Optional
from agents.exa_search import ExaSearchAgent, get_exa_enhanced_context
from agents.design_reviewer import DesignReviewer
from langchain.schema import Document


class EnhancedDesignReviewer(DesignReviewer):
    """
    Enhanced Design Reviewer that uses Exa search to provide more comprehensive reviews.
    """
    
    def __init__(self, openai_api_key: str, exa_api_key: Optional[str] = None):
        """
        Initialize the enhanced design reviewer.
        
        Args:
            openai_api_key: OpenAI API key
            exa_api_key: Exa API key for web search
        """
        super().__init__(openai_api_key)
        
        self.exa_agent = None
        if exa_api_key:
            try:
                self.exa_agent = ExaSearchAgent(exa_api_key)
            except Exception as e:
                print(f"Warning: Could not initialize Exa search: {e}")
    
    def get_enhanced_context_for_review(self, design_type: str, specific_concerns: List[str] = None) -> str:
        """
        Get enhanced context for design review using Exa search.
        
        Args:
            design_type: Type of design being reviewed (e.g., "TV interface", "mobile app")
            specific_concerns: List of specific design concerns to research
            
        Returns:
            Enhanced context string for use in review prompts
        """
        if not self.exa_agent:
            return ""
        
        context_parts = []
        
        # Search for general best practices
        general_query = f"{design_type} design best practices"
        general_context = get_exa_enhanced_context(general_query, self.exa_agent.api_key)
        if general_context:
            context_parts.append("## Web Research - Design Best Practices")
            context_parts.append(general_context)
        
        # Search for specific concerns if provided
        if specific_concerns:
            for concern in specific_concerns:
                concern_query = f"{design_type} {concern}"
                concern_context = get_exa_enhanced_context(concern_query, self.exa_agent.api_key)
                if concern_context:
                    context_parts.append(f"## Web Research - {concern.title()}")
                    context_parts.append(concern_context)
        
        return "\n\n".join(context_parts)
    
    def review_with_web_research(self, 
                                image_data: str, 
                                design_type: str = "interface",
                                specific_concerns: List[str] = None,
                                include_roku_research: bool = True) -> Dict:
        """
        Perform design review enhanced with web research.
        
        Args:
            image_data: Base64 encoded image data
            design_type: Type of design being reviewed
            specific_concerns: Specific areas to research and focus on
            include_roku_research: Whether to include Roku-specific research
            
        Returns:
            Enhanced review results
        """
        # Get enhanced context from web research
        enhanced_context = ""
        
        if self.exa_agent:
            # General design research
            enhanced_context = self.get_enhanced_context_for_review(design_type, specific_concerns)
            
            # Roku-specific research if requested
            if include_roku_research and "roku" in design_type.lower() or "tv" in design_type.lower():
                roku_context = get_exa_enhanced_context(f"Roku {design_type}", self.exa_agent.api_key)
                if roku_context:
                    enhanced_context += f"\n\n## Roku-Specific Research\n{roku_context}"
        
        # Create enhanced prompt with web research
        enhanced_prompt = f"""
        You are conducting a design review. Use the following web research to inform your analysis:

        {enhanced_context}

        Based on this research and your expertise, provide a comprehensive design review that:
        1. References current best practices from the research
        2. Compares the design to industry standards
        3. Provides specific, actionable recommendations
        4. Highlights both strengths and areas for improvement

        Please analyze the provided design image.
        """
        
        # Perform the actual review (you would integrate this with your existing review method)
        # For now, returning a structured response
        return {
            "enhanced_context": enhanced_context,
            "design_type": design_type,
            "specific_concerns": specific_concerns or [],
            "research_available": bool(enhanced_context),
            "prompt_used": enhanced_prompt
        }


def demo_exa_integration():
    """
    Demonstration of how to use Exa search for design reviews.
    """
    import os
    
    # Check for API keys
    openai_key = os.getenv('OPENAI_API_KEY')
    exa_key = os.getenv('EXA_API_KEY')
    
    if not openai_key:
        print("OPENAI_API_KEY not found in environment variables")
        return
    
    if not exa_key:
        print("EXA_API_KEY not found - web search features will be disabled")
        print("To enable web search, get an API key from https://exa.ai and set EXA_API_KEY")
    
    # Create enhanced reviewer
    reviewer = EnhancedDesignReviewer(openai_key, exa_key)
    
    # Example review scenarios
    scenarios = [
        {
            "design_type": "TV interface navigation",
            "concerns": ["accessibility", "remote control navigation", "visual hierarchy"]
        },
        {
            "design_type": "Roku channel homepage",
            "concerns": ["content discovery", "visual design", "user engagement"]
        },
        {
            "design_type": "streaming app interface",
            "concerns": ["search functionality", "content organization"]
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n=== Scenario {i}: {scenario['design_type']} ===")
        
        if reviewer.exa_agent:
            # Get enhanced context for this scenario
            context = reviewer.get_enhanced_context_for_review(
                scenario['design_type'], 
                scenario['concerns']
            )
            
            if context:
                print("✅ Web research available")
                print(f"Context length: {len(context)} characters")
                
                # Show a preview of the research
                lines = context.split('\n')
                preview_lines = lines[:10]  # First 10 lines
                print("Research preview:")
                for line in preview_lines:
                    if line.strip():
                        print(f"  {line}")
                
                if len(lines) > 10:
                    print(f"  ... and {len(lines) - 10} more lines")
            else:
                print("❌ No web research results found")
        else:
            print("❌ Exa search not available")


if __name__ == "__main__":
    demo_exa_integration()
