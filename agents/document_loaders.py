import os
from typing import List, Dict, Any, Optional
from langchain_community.document_loaders import ConfluenceLoader, FigmaFileLoader
from langchain_core.documents import Document
from config.settings import settings

class DocumentLoaderManager:
    """
    Manager for handling different document loaders including Figma and Confluence.
    """
    
    def __init__(self):
        self.settings = settings
    
    def load_confluence_documents(
        self, 
        space_key: str, 
        page_ids: Optional[List[str]] = None,
        limit: int = 50
    ) -> List[Document]:
        """
        Load documents from Confluence.
        
        Args:
            space_key: Confluence space key
            page_ids: Optional list of specific page IDs to load
            limit: Maximum number of documents to load
            
        Returns:
            List of Document objects
        """
        if not self.settings.is_confluence_configured():
            raise ValueError("Confluence is not properly configured. Please check your environment variables.")
        
        try:
            loader = ConfluenceLoader(
                url=self.settings.confluence_url,
                username=self.settings.confluence_username,
                api_key=self.settings.confluence_api_key,
                space_key=space_key,
                limit=limit
            )
            
            if page_ids:
                # Load specific pages
                documents = []
                for page_id in page_ids:
                    loader.page_ids = [page_id]
                    docs = loader.load()
                    documents.extend(docs)
                return documents
            else:
                # Load all pages from space
                return loader.load()
                
        except Exception as e:
            raise Exception(f"Failed to load Confluence documents: {str(e)}")
    
    def load_figma_file(self, file_key: str, node_ids: Optional[List[str]] = None) -> List[Document]:
        """
        Load design file from Figma.
        
        Args:
            file_key: Figma file key (from the URL)
            node_ids: Optional list of specific node IDs to load
            
        Returns:
            List of Document objects
        """
        if not self.settings.is_figma_configured():
            raise ValueError("Figma is not properly configured. Please check your environment variables.")
        
        try:
            loader = FigmaFileLoader(
                access_token=self.settings.figma_access_token,
                file_key=file_key,
                node_ids=node_ids
            )
            
            return loader.load()
            
        except Exception as e:
            raise Exception(f"Failed to load Figma file: {str(e)}")
    
    def extract_figma_file_key(self, figma_url: str) -> str:
        """
        Extract file key from Figma URL.
        
        Args:
            figma_url: Full Figma file URL
            
        Returns:
            File key string
        """
        # Figma URL format: https://www.figma.com/file/{file_key}/title
        if "figma.com/file/" in figma_url:
            parts = figma_url.split("/file/")
            if len(parts) > 1:
                file_key = parts[1].split("/")[0]
                return file_key
        raise ValueError("Invalid Figma URL format")
    
    def search_confluence_pages(self, query: str, space_key: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search for Confluence pages by query.
        
        Args:
            query: Search query
            space_key: Optional space key to limit search
            
        Returns:
            List of page information dictionaries
        """
        if not self.settings.is_confluence_configured():
            raise ValueError("Confluence is not properly configured.")
        
        try:
            # This would use the Confluence API to search
            # For now, we'll return a placeholder
            return []
        except Exception as e:
            raise Exception(f"Failed to search Confluence: {str(e)}")

# Global instance
document_loader_manager = DocumentLoaderManager()
