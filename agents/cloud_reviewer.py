"""
Cloud-based Design Review Agent using free/low-cost APIs that work on Vercel
"""

import requests
import json
from typing import Dict, Any, List, Optional
from PIL import Image
import base64
import io
import os

class CloudDesignReviewAgent:
    """
    Design review agent using cloud-based free/low-cost LLM APIs.
    Works on serverless platforms like Vercel.
    """
    
    def __init__(self):
        self.supported_providers = {
            'huggingface': self._setup_huggingface,
            'groq': self._setup_groq,
            'together': self._setup_together,
            'openrouter': self._setup_openrouter
        }
        self.provider = None
        self.api_key = None
        self.model = None
        self._initialize_provider()
    
    def _initialize_provider(self):
        """Initialize the first available provider."""
        # Try providers in order of preference (free -> low cost)
        
        # 1. Hugging Face (free tier)
        if os.getenv("HUGGINGFACE_API_KEY"):
            self.provider = 'huggingface'
            self.api_key = os.getenv("HUGGINGFACE_API_KEY")
            self.model = "meta-llama/Llama-2-7b-chat-hf"
            return
        
        # 2. Groq (very fast, generous free tier)
        if os.getenv("GROQ_API_KEY"):
            self.provider = 'groq'
            self.api_key = os.getenv("GROQ_API_KEY")
            self.model = "llama3-8b-8192"
            return
        
        # 3. Together AI (good free tier)
        if os.getenv("TOGETHER_API_KEY"):
            self.provider = 'together'
            self.api_key = os.getenv("TOGETHER_API_KEY")
            self.model = "meta-llama/Llama-2-7b-chat-hf"
            return
        
        # 4. OpenRouter (access to many models, some free)
        if os.getenv("OPENROUTER_API_KEY"):
            self.provider = 'openrouter'
            self.api_key = os.getenv("OPENROUTER_API_KEY")
            self.model = "meta-llama/llama-3-8b-instruct:free"
            return
    
    def _setup_huggingface(self):
        return "https://api-inference.huggingface.co/models"
    
    def _setup_groq(self):
        return "https://api.groq.com/openai/v1/chat/completions"
    
    def _setup_together(self):
        return "https://api.together.xyz/v1/chat/completions"
    
    def _setup_openrouter(self):
        return "https://openrouter.ai/api/v1/chat/completions"
    
    def is_available(self) -> bool:
        """Check if any cloud provider is available."""
        return self.provider is not None
    
    def get_setup_instructions(self) -> Dict[str, Any]:
        """Get setup instructions for cloud providers."""
        return {
            'providers': {
                'groq': {
                    'name': 'Groq (Recommended - Fast & Free)',
                    'signup': 'https://console.groq.com/',
                    'env_var': 'GROQ_API_KEY',
                    'free_tier': 'Very generous free tier with fast inference'
                },
                'huggingface': {
                    'name': 'Hugging Face (Free)',
                    'signup': 'https://huggingface.co/settings/tokens',
                    'env_var': 'HUGGINGFACE_API_KEY',
                    'free_tier': 'Free inference API with rate limits'
                },
                'together': {
                    'name': 'Together AI',
                    'signup': 'https://api.together.xyz/',
                    'env_var': 'TOGETHER_API_KEY',
                    'free_tier': 'Good free tier for testing'
                },
                'openrouter': {
                    'name': 'OpenRouter',
                    'signup': 'https://openrouter.ai/',
                    'env_var': 'OPENROUTER_API_KEY',
                    'free_tier': 'Access to free models'
                }
            },
            'recommended': 'Start with Groq for the best free experience'
        }
    
    def review_design_cloud(
        self, 
        text_content: str,
        review_type: str = "General Design",
        detail_level: int = 3
    ) -> Dict[str, Any]:
        """
        Review design using cloud-based LLM.
        
        Args:
            text_content: Text content to review
            review_type: Type of review to perform
            detail_level: Level of detail (1-5)
            
        Returns:
            Dictionary containing review results
        """
        if not self.is_available():
            return {
                'error': 'No cloud LLM provider configured. Please set up at least one provider.',
                'setup_instructions': self.get_setup_instructions()
            }
        
        prompt = self._build_review_prompt(text_content, review_type, detail_level)
        
        try:
            if self.provider == 'huggingface':
                return self._call_huggingface(prompt)
            elif self.provider == 'groq':
                return self._call_groq(prompt)
            elif self.provider == 'together':
                return self._call_together(prompt)
            elif self.provider == 'openrouter':
                return self._call_openrouter(prompt)
        
        except Exception as e:
            return {
                'error': f'Failed to get response from {self.provider}: {str(e)}',
                'setup_instructions': self.get_setup_instructions()
            }
    
    def _build_review_prompt(self, content: str, review_type: str, detail_level: int) -> str:
        """Build the review prompt."""
        return f"""You are an expert {review_type.lower()} reviewer. 
Analyze the provided content and provide detailed feedback.

Detail Level: {detail_level}/5

Please provide:
1. Overall Assessment (score out of 10)
2. Key Strengths
3. Areas for improvement
4. Specific recommendations
5. Priority actions

Content to review:
{content}

Provide practical, actionable feedback in a structured format."""
    
    def _call_groq(self, prompt: str) -> Dict[str, Any]:
        """Call Groq API."""
        url = self._setup_groq()
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 1000
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        return {
            'review': result['choices'][0]['message']['content'],
            'model': self.model,
            'provider': self.provider,
            'source': f'cloud_{self.provider}',
            'success': True
        }
    
    def _call_huggingface(self, prompt: str) -> Dict[str, Any]:
        """Call Hugging Face API."""
        url = f"{self._setup_huggingface()}/{self.model}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "inputs": prompt,
            "parameters": {
                "temperature": 0.3,
                "max_new_tokens": 1000
            }
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        return {
            'review': result[0]['generated_text'],
            'model': self.model,
            'provider': self.provider,
            'source': f'cloud_{self.provider}',
            'success': True
        }
    
    def _call_together(self, prompt: str) -> Dict[str, Any]:
        """Call Together AI API."""
        url = self._setup_together()
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 1000
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        return {
            'review': result['choices'][0]['message']['content'],
            'model': self.model,
            'provider': self.provider,
            'source': f'cloud_{self.provider}',
            'success': True
        }
    
    def _call_openrouter(self, prompt: str) -> Dict[str, Any]:
        """Call OpenRouter API."""
        url = self._setup_openrouter()
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/stevenvillarino/margo-agent",
            "X-Title": "Margo Design Review Agent"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 1000
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        return {
            'review': result['choices'][0]['message']['content'],
            'model': self.model,
            'provider': self.provider,
            'source': f'cloud_{self.provider}',
            'success': True
        }

# Global instance
cloud_agent = CloudDesignReviewAgent()
