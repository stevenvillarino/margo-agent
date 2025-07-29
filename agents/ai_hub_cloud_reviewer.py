"""
AI Hub Cloud Reviewer - Enterprise AI-powered design analysis using Roku's AI Hub.
Replaces the existing cloud_reviewer.py with AI Hub integration.
"""

import os
from typing import Dict, List, Any, Optional
from agents.ai_hub_reviewer import AIHubDesignReviewer
from config.settings import settings


class AIHubCloudReviewer:
    """
    Cloud-based design reviewer using Roku's AI Hub infrastructure.
    Provides enterprise-grade AI capabilities with multiple model options.
    """
    
    def __init__(self):
        """Initialize the AI Hub cloud reviewer."""
        self.api_token = settings.ai_hub_token
        self.base_url = settings.ai_hub_url
        self.enabled = settings.ai_hub_enabled
        
        if not self.enabled:
            raise ValueError(
                "AI Hub is not configured. Please set AI_HUB_TOKEN environment variable."
            )
        
        self.reviewer = AIHubDesignReviewer(api_token=self.api_token)
        
        # Cache for models and assistants
        self._available_models = None
        self._available_assistants = None
    
    def is_available(self) -> bool:
        """Check if AI Hub service is available."""
        return self.enabled and bool(self.api_token)
    
    def get_status(self) -> Dict[str, Any]:
        """Get the status of the AI Hub connection."""
        if not self.enabled:
            return {
                "available": False,
                "error": "AI Hub token not configured",
                "setup_required": True
            }
        
        try:
            # Test connection by fetching assistants
            assistants = self.reviewer.get_available_assistants()
            models = self.reviewer.get_available_models()
            
            return {
                "available": True,
                "assistants_count": len(assistants),
                "models_count": len(models),
                "base_url": self.base_url,
                "token_configured": True
            }
        except Exception as e:
            return {
                "available": False,
                "error": f"AI Hub connection failed: {str(e)}",
                "base_url": self.base_url,
                "token_configured": True
            }
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available AI models."""
        if self._available_models is None:
            self._available_models = self.reviewer.get_available_models()
        return self._available_models
    
    def get_available_assistants(self) -> List[Dict[str, Any]]:
        """Get list of available AI assistants."""
        if self._available_assistants is None:
            self._available_assistants = self.reviewer.get_available_assistants()
        return self._available_assistants
    
    def review_design(
        self,
        file,
        review_type: str = "General Design",
        detail_level: int = 3,
        include_suggestions: bool = True,
        model_provider: Optional[str] = None,
        model_name: Optional[str] = None,
        assistant_id: Optional[int] = None,
        temperature: float = 0.3
    ) -> Dict[str, Any]:
        """
        Review a design file using AI Hub.
        
        Args:
            file: Uploaded file object
            review_type: Type of review to perform
            detail_level: Level of detail (1-5)
            include_suggestions: Whether to include improvement suggestions
            model_provider: Optional specific model provider
            model_name: Optional specific model name
            assistant_id: Optional specific assistant to use
            temperature: Model temperature setting
            
        Returns:
            Dictionary containing review results
        """
        if not self.is_available():
            return {
                "error": "AI Hub is not available",
                "source": "ai_hub",
                "setup_required": True
            }
        
        try:
            # Use specific assistant if provided
            if assistant_id:
                reviewer = AIHubDesignReviewer(
                    api_token=self.api_token, 
                    assistant_id=assistant_id
                )
            else:
                reviewer = self.reviewer
            
            # Perform the review
            result = reviewer.review_design(
                file=file,
                review_type=review_type,
                detail_level=detail_level,
                include_suggestions=include_suggestions,
                model_provider=model_provider,
                model_name=model_name,
                temperature=temperature
            )
            
            # Add metadata
            result.update({
                "source": "ai_hub",
                "enterprise": True,
                "model_provider": model_provider or "default",
                "model_name": model_name or "default",
                "assistant_id": assistant_id
            })
            
            return result
            
        except Exception as e:
            return {
                "error": f"AI Hub review failed: {str(e)}",
                "source": "ai_hub",
                "timestamp": None
            }
    
    def roku_design_review(
        self,
        file,
        evaluation_criteria: List[str],
        model_provider: Optional[str] = None,
        model_name: Optional[str] = None,
        assistant_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Perform Roku-specific design review using AI Hub.
        
        Args:
            file: Design file to review
            evaluation_criteria: List of Roku design criteria to evaluate
            model_provider: Optional specific model provider
            model_name: Optional specific model name
            assistant_id: Optional specific assistant to use
            
        Returns:
            Dictionary containing Roku design review results
        """
        if not self.is_available():
            return {
                "error": "AI Hub is not available for Roku design review",
                "source": "ai_hub_roku",
                "setup_required": True
            }
        
        try:
            # Use specific assistant if provided
            if assistant_id:
                reviewer = AIHubDesignReviewer(
                    api_token=self.api_token, 
                    assistant_id=assistant_id
                )
            else:
                reviewer = self.reviewer
            
            # Perform Roku-specific review
            result = reviewer.roku_design_review(
                file=file,
                evaluation_criteria=evaluation_criteria,
                model_provider=model_provider,
                model_name=model_name
            )
            
            # Add metadata
            result.update({
                "source": "ai_hub_roku",
                "enterprise": True,
                "roku_specific": True,
                "model_provider": model_provider or "default",
                "model_name": model_name or "default",
                "assistant_id": assistant_id
            })
            
            return result
            
        except Exception as e:
            return {
                "error": f"AI Hub Roku review failed: {str(e)}",
                "source": "ai_hub_roku",
                "timestamp": None
            }
    
    def get_model_info(self, provider: str, model: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific model."""
        models = self.get_available_models()
        for model_info in models:
            if (model_info.get("provider") == provider and 
                model_info.get("model") == model):
                return model_info
        return None
    
    def get_assistant_info(self, assistant_id: int) -> Optional[Dict[str, Any]]:
        """Get information about a specific assistant."""
        assistants = self.get_available_assistants()
        for assistant in assistants:
            if assistant.get("id") == assistant_id:
                return assistant
        return None


# Global instance
ai_hub_reviewer = None

def get_ai_hub_reviewer() -> AIHubCloudReviewer:
    """Get or create the global AI Hub reviewer instance."""
    global ai_hub_reviewer
    if ai_hub_reviewer is None:
        ai_hub_reviewer = AIHubCloudReviewer()
    return ai_hub_reviewer

def is_ai_hub_available() -> bool:
    """Check if AI Hub is available for use."""
    try:
        reviewer = get_ai_hub_reviewer()
        return reviewer.is_available()
    except Exception:
        return False
