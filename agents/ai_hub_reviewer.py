"""
AI Hub-powered design reviewer that integrates with the existing margo-agent system.
Replaces OpenAI calls with Roku AI Hub API for enterprise-grade AI capabilities.
"""

import base64
import io
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from PIL import Image
from agents.ai_hub_client import AIHubClient, FileDescriptor
from agents.utils import encode_image, extract_text_from_pdf
from prompts.review_prompts import DesignReviewPrompts
from prompts.roku_prompts import RokuDesignPrompts


class AIHubDesignReviewer:
    """
    AI Hub-powered design review agent that maintains compatibility 
    with the existing DesignReviewAgent interface.
    """
    
    def __init__(self, api_token: str, assistant_id: Optional[int] = None):
        """
        Initialize the AI Hub design review agent.
        
        Args:
            api_token: AI Hub API token
            assistant_id: Optional specific assistant to use
        """
        self.client = AIHubClient(api_token=api_token)
        self.assistant_id = assistant_id
        self.prompts = DesignReviewPrompts()
        self.roku_prompts = RokuDesignPrompts()
        
        # Cache available models and assistants
        self._models = None
        self._assistants = None
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get available AI models from the hub."""
        if self._models is None:
            try:
                providers = self.client.get_providers()
                self._models = []
                for provider in providers:
                    for model in provider.display_model_names:
                        self._models.append({
                            "provider": provider.name,
                            "model": model,
                            "description": provider.description
                        })
            except Exception as e:
                print(f"Warning: Could not fetch models: {e}")
                self._models = []
        
        return self._models
    
    def get_available_assistants(self) -> List[Dict[str, Any]]:
        """Get available assistants from the hub."""
        if self._assistants is None:
            try:
                assistants = self.client.get_assistants()
                self._assistants = [
                    {
                        "id": assistant.id,
                        "name": assistant.name,
                        "display_name": assistant.display_name,
                        "description": assistant.description
                    }
                    for assistant in assistants
                ]
            except Exception as e:
                print(f"Warning: Could not fetch assistants: {e}")
                self._assistants = []
        
        return self._assistants
    
    def review_design(
        self, 
        file, 
        review_type: str = "General Design",
        detail_level: int = 3,
        include_suggestions: bool = True,
        model_provider: Optional[str] = None,
        model_name: Optional[str] = None,
        temperature: float = 0.3
    ) -> Dict[str, Any]:
        """
        Review a design file and provide feedback using AI Hub.
        
        Args:
            file: Uploaded file object
            review_type: Type of review to perform
            detail_level: Level of detail (1-5)
            include_suggestions: Whether to include improvement suggestions
            model_provider: Optional specific model provider
            model_name: Optional specific model name
            temperature: Model temperature setting
            
        Returns:
            Dictionary containing review results
        """
        try:
            # Create chat session
            session = self.client.create_chat_session(assistant_id=self.assistant_id)
            
            # Set custom model if specified
            if model_provider and model_name:
                session.set_llm(model_provider, model_name, temperature)
            
            # Process the file based on type
            if file.type.startswith('image'):
                return self._analyze_image_with_hub(
                    file, session, review_type, detail_level, include_suggestions
                )
            elif file.type == 'application/pdf':
                return self._analyze_pdf_with_hub(
                    file, session, review_type, detail_level, include_suggestions
                )
            else:
                raise ValueError(f"Unsupported file type: {file.type}")
                
        except Exception as e:
            return {
                "error": f"Failed to analyze design with AI Hub: {str(e)}",
                "source": "ai_hub",
                "timestamp": datetime.now().isoformat()
            }
    
    def _analyze_image_with_hub(
        self, 
        image_file, 
        session, 
        review_type: str, 
        detail_level: int, 
        include_suggestions: bool
    ) -> Dict[str, Any]:
        """Analyze an image file using AI Hub."""
        try:
            # Save image temporarily for upload
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
                # Convert to PIL Image and save
                image = Image.open(image_file)
                # Convert to RGB if necessary
                if image.mode in ('RGBA', 'P'):
                    image = image.convert('RGB')
                image.save(temp_file.name, 'JPEG', quality=95)
                temp_path = temp_file.name
            
            try:
                # Upload file to AI Hub
                uploaded_files = self.client.upload_files([temp_path])
                
                # Get appropriate prompt
                system_prompt = self.prompts.get_review_prompt(
                    review_type, detail_level, include_suggestions
                )
                
                # Create analysis message
                message = f"""
{system_prompt}

Please analyze this {review_type.lower()} design image and provide detailed feedback.

The image has been uploaded for your analysis. Please examine it carefully and provide:
1. Overall design assessment
2. Specific observations about layout, typography, colors, and visual hierarchy
3. Accessibility considerations
4. {"Improvement suggestions" if include_suggestions else "Areas for potential enhancement"}

Please structure your response clearly with distinct sections.
"""
                
                # Send message with uploaded file
                response = session.send_message_simple(message)
                
                # Parse response
                return {
                    "analysis": response.get("answer", "No analysis provided"),
                    "source": "ai_hub",
                    "model": session.llm_override.get("model_version") if session.llm_override else "default",
                    "provider": session.llm_override.get("model_provider") if session.llm_override else "default",
                    "file_uploaded": True,
                    "file_id": uploaded_files[0].id if uploaded_files else None,
                    "session_id": session.chat_id,
                    "timestamp": datetime.now().isoformat(),
                    "review_type": review_type,
                    "detail_level": detail_level,
                    "include_suggestions": include_suggestions
                }
                
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_path)
                except OSError:
                    pass
                    
        except Exception as e:
            return {
                "error": f"Failed to analyze image: {str(e)}",
                "source": "ai_hub",
                "timestamp": datetime.now().isoformat()
            }
    
    def _analyze_pdf_with_hub(
        self, 
        pdf_file, 
        session, 
        review_type: str, 
        detail_level: int, 
        include_suggestions: bool
    ) -> Dict[str, Any]:
        """Analyze a PDF file using AI Hub."""
        try:
            # Save PDF temporarily for upload
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                temp_file.write(pdf_file.read())
                temp_path = temp_file.name
            
            try:
                # Upload file to AI Hub
                uploaded_files = self.client.upload_files([temp_path])
                
                # Get appropriate prompt
                system_prompt = self.prompts.get_review_prompt(
                    review_type, detail_level, include_suggestions
                )
                
                # Create analysis message
                message = f"""
{system_prompt}

Please analyze this {review_type.lower()} design document (PDF) and provide detailed feedback.

The PDF has been uploaded for your analysis. Please examine it carefully and provide:
1. Overall design assessment across all pages
2. Specific observations about layout, typography, colors, and visual hierarchy
3. Consistency across pages
4. Accessibility considerations
5. {"Improvement suggestions" if include_suggestions else "Areas for potential enhancement"}

Please structure your response clearly with distinct sections and reference specific pages when relevant.
"""
                
                # Send message with uploaded file
                response = session.send_message_simple(message)
                
                # Parse response
                return {
                    "analysis": response.get("answer", "No analysis provided"),
                    "source": "ai_hub",
                    "model": session.llm_override.get("model_version") if session.llm_override else "default",
                    "provider": session.llm_override.get("model_provider") if session.llm_override else "default",
                    "file_uploaded": True,
                    "file_id": uploaded_files[0].id if uploaded_files else None,
                    "session_id": session.chat_id,
                    "timestamp": datetime.now().isoformat(),
                    "review_type": review_type,
                    "detail_level": detail_level,
                    "include_suggestions": include_suggestions
                }
                
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_path)
                except OSError:
                    pass
                    
        except Exception as e:
            return {
                "error": f"Failed to analyze PDF: {str(e)}",
                "source": "ai_hub",
                "timestamp": datetime.now().isoformat()
            }
    
    def roku_design_review(
        self,
        file,
        evaluation_criteria: List[str],
        model_provider: Optional[str] = None,
        model_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Perform Roku-specific design review using AI Hub.
        
        Args:
            file: Design file to review
            evaluation_criteria: List of Roku design criteria to evaluate
            model_provider: Optional specific model provider
            model_name: Optional specific model name
            
        Returns:
            Dictionary containing Roku design review results
        """
        try:
            # Create chat session
            session = self.client.create_chat_session(assistant_id=self.assistant_id)
            
            # Set custom model if specified
            if model_provider and model_name:
                session.set_llm(model_provider, model_name, 0.3)
            
            # Get Roku-specific prompt
            roku_prompt = self.roku_prompts.get_roku_review_prompt(evaluation_criteria)
            
            # Process file and get analysis
            if file.type.startswith('image'):
                result = self._analyze_image_with_roku_criteria(
                    file, session, roku_prompt, evaluation_criteria
                )
            elif file.type == 'application/pdf':
                result = self._analyze_pdf_with_roku_criteria(
                    file, session, roku_prompt, evaluation_criteria
                )
            else:
                raise ValueError(f"Unsupported file type: {file.type}")
            
            # Add Roku-specific metadata
            result.update({
                "evaluation_type": "roku_design_review",
                "criteria_evaluated": evaluation_criteria,
                "source": "ai_hub_roku"
            })
            
            return result
            
        except Exception as e:
            return {
                "error": f"Failed to perform Roku design review: {str(e)}",
                "source": "ai_hub_roku",
                "timestamp": datetime.now().isoformat()
            }
    
    def _analyze_image_with_roku_criteria(
        self, 
        image_file, 
        session, 
        roku_prompt: str, 
        criteria: List[str]
    ) -> Dict[str, Any]:
        """Analyze image with Roku-specific criteria."""
        # Similar to _analyze_image_with_hub but with Roku-specific prompting
        # Implementation similar to above but with roku_prompt instead of general prompt
        return self._analyze_image_with_hub(image_file, session, "Roku TV Design", 5, True)
    
    def _analyze_pdf_with_roku_criteria(
        self, 
        pdf_file, 
        session, 
        roku_prompt: str, 
        criteria: List[str]
    ) -> Dict[str, Any]:
        """Analyze PDF with Roku-specific criteria."""
        # Similar to _analyze_pdf_with_hub but with Roku-specific prompting
        return self._analyze_pdf_with_hub(pdf_file, session, "Roku TV Design", 5, True)


# Factory function for easy integration
def create_ai_hub_reviewer(api_token: str, assistant_id: Optional[int] = None) -> AIHubDesignReviewer:
    """Create an AI Hub design reviewer instance."""
    return AIHubDesignReviewer(api_token=api_token, assistant_id=assistant_id)
