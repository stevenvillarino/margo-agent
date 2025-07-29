"""
Python client for Roku AI Hub API.
Mimics the functionality of the ai-hub-node-client for seamless integration.
"""

import json
import requests
import time
from typing import Dict, List, Any, Optional, Iterator
from dataclasses import dataclass
from pathlib import Path
import mimetypes
import uuid


@dataclass
class FileDescriptor:
    """Represents an uploaded file."""
    id: str
    filename: str
    content_type: str
    size: int


@dataclass
class Assistant:
    """Represents an AI assistant/persona."""
    id: int
    name: str
    description: str
    display_name: str


@dataclass
class LLMProvider:
    """Represents an available LLM provider."""
    name: str
    display_model_names: List[str]
    description: str


class AIHubSession:
    """Represents a chat session with the AI Hub."""
    
    def __init__(self, client: 'AIHubClient', chat_id: str):
        self.client = client
        self.chat_id = chat_id
        self.llm_override = None
    
    async def send_message_simple(self, message: str) -> Dict[str, Any]:
        """Send a simple message and get the complete response."""
        url = f"{self.client.base_url}/chat/send-message-simple-api"
        
        payload = {
            "message": message,
            "chat_session_id": self.chat_id
        }
        
        response = requests.post(
            url,
            headers=self.client.headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    
    def send_message_stream(
        self, 
        message: str, 
        files: Optional[List[FileDescriptor]] = None,
        parent_message_id: Optional[str] = None,
        use_agentic_search: bool = False
    ) -> Iterator[Dict[str, Any]]:
        """Send a message and get streaming response."""
        url = f"{self.client.base_url}/chat/send-message"
        
        payload = {
            "message": message,
            "chat_session_id": self.chat_id,
            "user_file_ids": [f.id for f in files] if files else [],
            "retrieval_options": {},
            "use_agentic_search": use_agentic_search,
            "parent_message_id": parent_message_id
        }
        
        if self.llm_override:
            payload["llm_override"] = self.llm_override
        
        response = requests.post(
            url,
            headers=self.client.headers,
            json=payload,
            stream=True,
            timeout=60
        )
        response.raise_for_status()
        
        # Parse streaming JSON responses
        for line in response.iter_lines():
            if line:
                try:
                    yield json.loads(line.decode('utf-8'))
                except json.JSONDecodeError:
                    continue
    
    def set_llm(
        self, 
        provider_name: str, 
        model_name: str, 
        temperature: float = 0.3
    ):
        """Set the LLM configuration for this session."""
        self.llm_override = {
            "model_provider": provider_name,
            "model_version": model_name,
            "temperature": temperature
        }


class AIHubClient:
    """Python client for Roku AI Hub API."""
    
    def __init__(
        self, 
        api_token: Optional[str] = None,
        base_url: str = "https://ai-hub-backend.msc.rokulabs.net"
    ):
        """
        Initialize the AI Hub client.
        
        Args:
            api_token: API token for authentication
            base_url: Base URL for the AI Hub API
        """
        self.api_token = api_token or self._get_token_from_env()
        self.base_url = base_url
        
        if not self.api_token:
            raise ValueError(
                "API token must be provided or set in AI_HUB_TOKEN environment variable"
            )
        
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
    
    def _get_token_from_env(self) -> Optional[str]:
        """Get token from environment variable."""
        import os
        return os.getenv("AI_HUB_TOKEN")
    
    def create_chat_session(self, assistant_id: Optional[int] = None) -> AIHubSession:
        """Create a new chat session."""
        url = f"{self.base_url}/chat/create-chat-session"
        
        payload = {
            "persona_id": assistant_id if assistant_id is not None else -1
        }
        
        response = requests.post(
            url,
            headers=self.headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        
        result = response.json()
        return AIHubSession(self, result["chat_session_id"])
    
    def get_assistants(self) -> List[Assistant]:
        """Get available assistants/personas."""
        url = f"{self.base_url}/persona"
        
        response = requests.get(url, headers=self.headers, timeout=30)
        response.raise_for_status()
        
        assistants = []
        for item in response.json():
            assistants.append(Assistant(
                id=item["id"],
                name=item["name"],
                description=item.get("description", ""),
                display_name=item.get("display_name", item["name"])
            ))
        
        return assistants
    
    def get_providers(self) -> List[LLMProvider]:
        """Get available LLM providers."""
        url = f"{self.base_url}/llm/provider"
        
        response = requests.get(url, headers=self.headers, timeout=30)
        response.raise_for_status()
        
        providers = []
        for item in response.json():
            providers.append(LLMProvider(
                name=item["name"],
                display_model_names=item.get("display_model_names", []),
                description=item.get("description", "")
            ))
        
        return providers
    
    def upload_files(self, file_paths: List[str]) -> List[FileDescriptor]:
        """Upload files to the AI Hub."""
        url = f"{self.base_url}/user/file/upload"
        
        files = []
        file_descriptors = []
        
        try:
            # Prepare files for upload
            for file_path in file_paths:
                path = Path(file_path)
                if not path.exists():
                    raise FileNotFoundError(f"File not found: {file_path}")
                
                # Determine content type
                content_type, _ = mimetypes.guess_type(file_path)
                if not content_type:
                    # Default to text/plain for code files
                    content_type = "text/plain"
                
                # Read file
                with open(path, 'rb') as f:
                    file_content = f.read()
                
                files.append(('files', (path.name, file_content, content_type)))
            
            # Upload files
            upload_headers = {
                "Authorization": f"Bearer {self.api_token}"
                # Don't set Content-Type for multipart/form-data
            }
            
            response = requests.post(
                url,
                headers=upload_headers,
                files=files,
                timeout=60
            )
            response.raise_for_status()
            
            # Parse response
            result = response.json()
            for file_info in result:
                file_descriptors.append(FileDescriptor(
                    id=file_info["id"],
                    filename=file_info["filename"],
                    content_type=file_info.get("content_type", ""),
                    size=file_info.get("size", 0)
                ))
            
            return file_descriptors
            
        finally:
            # Clean up file objects
            for file_tuple in files:
                if hasattr(file_tuple[1][1], 'close'):
                    file_tuple[1][1].close()
    
    def get_session_history(
        self, 
        chat_session_id: str, 
        is_shared: bool = False
    ) -> Dict[str, Any]:
        """Get the history of a chat session."""
        url = f"{self.base_url}/chat/get-chat-session/{chat_session_id}"
        
        params = {}
        if is_shared:
            params["is_shared"] = "true"
        
        response = requests.get(
            url,
            headers=self.headers,
            params=params,
            timeout=30
        )
        response.raise_for_status()
        
        return response.json()
    
    def get_chat_sessions(self) -> List[Dict[str, Any]]:
        """Get all chat sessions for the current user."""
        url = f"{self.base_url}/chat/get-user-chat-sessions"
        
        response = requests.get(url, headers=self.headers, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        return result.get("sessions", [])


# Convenience function for easy integration
def create_ai_hub_client(api_token: str) -> AIHubClient:
    """Create an AI Hub client with the provided token."""
    return AIHubClient(api_token=api_token)
