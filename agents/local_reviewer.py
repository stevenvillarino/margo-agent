"""
Local Design Review Agent using Ollama (Free)
"""

import requests
import json
from typing import Dict, Any, List, Optional
from PIL import Image
import base64
import io

class LocalDesignReviewAgent:
    """
    Design review agent using local Ollama models (completely free).
    """
    
    def __init__(self, model_name: str = "llama3.1:8b"):
        self.model_name = model_name
        self.ollama_url = "http://localhost:11434"
        
    def _check_ollama_running(self) -> bool:
        """Check if Ollama is running locally."""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def _encode_image(self, image: Image.Image) -> str:
        """Encode PIL Image to base64."""
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return img_str
    
    def review_design_local(
        self, 
        image: Optional[Image.Image] = None,
        text_content: Optional[str] = None,
        review_type: str = "General Design",
        detail_level: int = 3
    ) -> Dict[str, Any]:
        """
        Review design using local Ollama model.
        
        Args:
            image: PIL Image object (optional)
            text_content: Text content to review (optional)
            review_type: Type of review to perform
            detail_level: Level of detail (1-5)
            
        Returns:
            Dictionary containing review results
        """
        if not self._check_ollama_running():
            return {
                'error': 'Ollama is not running. Please install and start Ollama first.',
                'setup_instructions': self._get_setup_instructions()
            }
        
        # Build the prompt
        prompt = self._build_review_prompt(review_type, detail_level)
        
        if text_content:
            prompt += f"\n\nContent to review:\n{text_content}"
        
        # Prepare request data
        data = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,
                "num_predict": 1000
            }
        }
        
        # Add image if provided (for vision models)
        if image and "vision" in self.model_name.lower():
            data["images"] = [self._encode_image(image)]
        
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'review': result.get('response', 'No response generated'),
                    'model': self.model_name,
                    'source': 'local_ollama',
                    'success': True
                }
            else:
                return {
                    'error': f'Ollama API error: {response.status_code}',
                    'details': response.text
                }
                
        except requests.exceptions.RequestException as e:
            return {
                'error': f'Failed to connect to Ollama: {str(e)}',
                'setup_instructions': self._get_setup_instructions()
            }
    
    def _build_review_prompt(self, review_type: str, detail_level: int) -> str:
        """Build the review prompt based on type and detail level."""
        base_prompt = f"""You are an expert {review_type.lower()} reviewer. 
Analyze the provided content and provide detailed feedback.

Detail Level: {detail_level}/5

Please provide:
1. Overall Assessment
2. Strengths identified
3. Areas for improvement
4. Specific recommendations
5. Priority actions

Focus on practical, actionable feedback."""

        if review_type == "UI/UX Design":
            base_prompt += """

Pay special attention to:
- User experience and usability
- Visual hierarchy and layout
- Accessibility considerations
- Mobile responsiveness
- Brand consistency"""

        elif review_type == "Roku TV Design":
            base_prompt += """

Pay special attention to:
- 10-foot UI principles (viewing from distance)
- Remote control navigation
- Text readability on TV screens
- Focus states and navigation flow
- Performance on TV hardware"""

        return base_prompt
    
    def _get_setup_instructions(self) -> Dict[str, str]:
        """Get setup instructions for Ollama."""
        return {
            'install': 'curl -fsSL https://ollama.ai/install.sh | sh',
            'start': 'ollama serve',
            'models': {
                'text_only': 'ollama pull llama3.1:8b',
                'vision': 'ollama pull llava:7b',
                'code': 'ollama pull codellama:7b'
            },
            'url': 'https://ollama.ai/'
        }
    
    def get_available_models(self) -> List[str]:
        """Get list of available local models."""
        if not self._check_ollama_running():
            return []
        
        try:
            response = requests.get(f"{self.ollama_url}/api/tags")
            if response.status_code == 200:
                data = response.json()
                return [model['name'] for model in data.get('models', [])]
        except:
            pass
        
        return []

# Global instance
local_agent = LocalDesignReviewAgent()
