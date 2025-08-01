"""
Exa AI Search Integration for Design Review Agent

This module provides functionality to search for design-related content,
best practices, and reference materials using the Exa AI search API.
"""

import os
from typing import List, Dict, Optional, Any
from exa_py import Exa
from langchain.schema import Document


class ExaSearchAgent:
    """
    Exa AI search agent for finding design-related content and best practices.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Exa search agent.
        
        Args:
            api_key: Exa API key. If not provided, will look for EXA_API_KEY environment variable.
        """
        self.api_key = api_key or os.getenv('EXA_API_KEY')
        if not self.api_key:
            raise ValueError("Exa API key is required. Set EXA_API_KEY environment variable or pass api_key parameter.")
        
        self.exa = Exa(api_key=self.api_key)
    
    def search_design_best_practices(self, query: str, num_results: int = 5) -> List[Document]:
        """
        Search for design best practices and guidelines.
        
        Args:
            query: Search query related to design
            num_results: Number of results to return
            
        Returns:
            List of LangChain Documents with search results
        """
        enhanced_query = f"design best practices UI UX guidelines {query}"
        
        try:
            results = self.exa.search(
                query=enhanced_query,
                num_results=num_results,
                include_domains=["nngroup.com", "smashingmagazine.com", "uxplanet.org", "medium.com", "designsystem.digital.gov"],
                type="neural"
            )
            
            documents = []
            for result in results.results:
                doc = Document(
                    page_content=result.title + "\n" + (result.text or ""),
                    metadata={
                        "source": result.url,
                        "title": result.title,
                        "score": result.score,
                        "search_type": "design_best_practices"
                    }
                )
                documents.append(doc)
            
            return documents
            
        except Exception as e:
            print(f"Error searching for design best practices: {e}")
            return []
    
    def search_roku_specific_content(self, query: str, num_results: int = 3) -> List[Document]:
        """
        Search for Roku-specific design content and guidelines.
        
        Args:
            query: Search query related to Roku design
            num_results: Number of results to return
            
        Returns:
            List of LangChain Documents with search results
        """
        enhanced_query = f"Roku TV interface design guidelines {query}"
        
        try:
            results = self.exa.search(
                query=enhanced_query,
                num_results=num_results,
                include_domains=["developer.roku.com", "docs.roku.com"],
                type="neural"
            )
            
            documents = []
            for result in results.results:
                doc = Document(
                    page_content=result.title + "\n" + (result.text or ""),
                    metadata={
                        "source": result.url,
                        "title": result.title,
                        "score": result.score,
                        "search_type": "roku_specific"
                    }
                )
                documents.append(doc)
            
            return documents
            
        except Exception as e:
            print(f"Error searching for Roku-specific content: {e}")
            return []
    
    def search_accessibility_guidelines(self, query: str, num_results: int = 3) -> List[Document]:
        """
        Search for accessibility guidelines and best practices.
        
        Args:
            query: Search query related to accessibility
            num_results: Number of results to return
            
        Returns:
            List of LangChain Documents with search results
        """
        enhanced_query = f"accessibility guidelines WCAG {query}"
        
        try:
            results = self.exa.search(
                query=enhanced_query,
                num_results=num_results,
                include_domains=["webaim.org", "w3.org", "a11y.org", "accessibility.digital.gov"],
                type="neural"
            )
            
            documents = []
            for result in results.results:
                doc = Document(
                    page_content=result.title + "\n" + (result.text or ""),
                    metadata={
                        "source": result.url,
                        "title": result.title,
                        "score": result.score,
                        "search_type": "accessibility"
                    }
                )
                documents.append(doc)
            
            return documents
            
        except Exception as e:
            print(f"Error searching for accessibility guidelines: {e}")
            return []
    
    def search_design_examples(self, design_type: str, num_results: int = 5) -> List[Document]:
        """
        Search for design examples and inspiration.
        
        Args:
            design_type: Type of design to search for (e.g., "TV interface", "navigation menu")
            num_results: Number of results to return
            
        Returns:
            List of LangChain Documents with search results
        """
        enhanced_query = f"{design_type} design examples inspiration showcase"
        
        try:
            results = self.exa.search(
                query=enhanced_query,
                num_results=num_results,
                include_domains=["dribbble.com", "behance.net", "uxplanet.org", "designsystem.digital.gov"],
                type="neural"
            )
            
            documents = []
            for result in results.results:
                doc = Document(
                    page_content=result.title + "\n" + (result.text or ""),
                    metadata={
                        "source": result.url,
                        "title": result.title,
                        "score": result.score,
                        "search_type": "design_examples"
                    }
                )
                documents.append(doc)
            
            return documents
            
        except Exception as e:
            print(f"Error searching for design examples: {e}")
            return []
    
    def comprehensive_design_research(self, query: str) -> Dict[str, List[Document]]:
        """
        Perform comprehensive design research using multiple search strategies.
        
        Args:
            query: Main search query
            
        Returns:
            Dictionary with different types of search results
        """
        results = {
            "best_practices": self.search_design_best_practices(query, 3),
            "roku_specific": self.search_roku_specific_content(query, 2),
            "accessibility": self.search_accessibility_guidelines(query, 2),
            "examples": self.search_design_examples(query, 3)
        }
        
        return results


def get_exa_enhanced_context(query: str, api_key: Optional[str] = None) -> str:
    """
    Get enhanced context for design reviews using Exa search.
    
    Args:
        query: Search query
        api_key: Optional Exa API key
        
    Returns:
        Formatted string with search results for use in prompts
    """
    try:
        exa_agent = ExaSearchAgent(api_key)
        results = exa_agent.comprehensive_design_research(query)
        
        context_parts = []
        
        for category, documents in results.items():
            if documents:
                context_parts.append(f"\n## {category.replace('_', ' ').title()}")
                for doc in documents:
                    context_parts.append(f"- **{doc.metadata['title']}** ({doc.metadata['source']})")
                    if doc.page_content:
                        # Take first 200 chars of content
                        content_preview = doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
                        context_parts.append(f"  {content_preview}")
        
        return "\n".join(context_parts)
        
    except Exception as e:
        return f"Unable to fetch enhanced context: {e}"


# Example usage
if __name__ == "__main__":
    # This is just for testing - you would use this in your main application
    api_key = os.getenv('EXA_API_KEY')
    if api_key:
        exa_agent = ExaSearchAgent(api_key)
        
        # Example: Search for TV interface design best practices
        results = exa_agent.search_design_best_practices("TV interface navigation")
        print(f"Found {len(results)} results for design best practices")
        
        for doc in results:
            print(f"- {doc.metadata['title']}")
            print(f"  {doc.metadata['source']}")
    else:
        print("EXA_API_KEY not set. Please set your Exa API key in environment variables.")
