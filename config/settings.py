import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    """Application settings and configuration."""
    
    def __init__(self):
        # API Configuration
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.langchain_api_key = os.getenv("LANGCHAIN_API_KEY")
        self.langchain_project = os.getenv("LANGCHAIN_PROJECT", "design-review-agent")
        
        # Figma Configuration
        self.figma_access_token = os.getenv("FIGMA_ACCESS_TOKEN")
        
        # Confluence Configuration
        self.confluence_url = os.getenv("CONFLUENCE_URL")
        self.confluence_username = os.getenv("CONFLUENCE_USERNAME")
        self.confluence_api_key = os.getenv("CONFLUENCE_API_KEY")
        
        # Model Configuration
        self.default_model = "gpt-4-vision-preview"
        self.chat_model = "gpt-4"
        self.temperature = 0.3
        self.max_tokens = 1500
        
        # File Upload Limits
        self.max_file_size_mb = 10
        self.supported_image_types = ["png", "jpg", "jpeg", "gif", "bmp"]
        self.supported_document_types = ["pdf"]
        
        # UI Configuration
        self.app_title = "Design Review Agent"
        self.page_icon = "🎨"
        self.layout = "wide"
        
        # Review Settings
        self.default_review_type = "General Design"
        self.default_detail_level = 3
        self.max_suggestions = 5
        
        # LangChain Configuration
        self.enable_tracing = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"
        self.langchain_endpoint = os.getenv("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com")
    
    def get_model_config(self) -> Dict[str, Any]:
        """Get model configuration."""
        return {
            "model": self.default_model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
    
    def get_chat_model_config(self) -> Dict[str, Any]:
        """Get chat model configuration."""
        return {
            "model": self.chat_model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
    
    def is_configured(self) -> bool:
        """Check if minimum configuration is present."""
        return bool(self.openai_api_key)
    
    def is_figma_configured(self) -> bool:
        """Check if Figma integration is configured."""
        return bool(self.figma_access_token and 
                   self.figma_access_token != "your_figma_access_token_here" and
                   len(self.figma_access_token) > 20)
    
    def is_confluence_configured(self) -> bool:
        """Check if Confluence integration is configured."""
        # Check if values exist and are not placeholder values
        url_valid = (self.confluence_url and 
                    self.confluence_url != "https://your-domain.atlassian.net" and
                    "atlassian.net" in self.confluence_url)
        
        username_valid = (self.confluence_username and 
                         self.confluence_username != "your_email@domain.com" and
                         "@" in self.confluence_username)
        
        api_key_valid = (self.confluence_api_key and 
                        self.confluence_api_key != "your_confluence_api_token_here" and
                        len(self.confluence_api_key) > 20)
        
        return bool(url_valid and username_valid and api_key_valid)
    
    def get_supported_file_types(self) -> list:
        """Get all supported file types."""
        return self.supported_image_types + self.supported_document_types

# Global settings instance
settings = Settings()
