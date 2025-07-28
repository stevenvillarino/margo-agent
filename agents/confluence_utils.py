"""
Confluence URL utilities for easier integration
"""

import re
from typing import Dict, Optional, Tuple
from urllib.parse import urlparse, parse_qs

class ConfluenceURLParser:
    """
    Utility class to parse Confluence URLs and extract space keys and page IDs.
    """
    
    @staticmethod
    def parse_confluence_url(url: str) -> Dict[str, Optional[str]]:
        """
        Parse a Confluence URL to extract space key and page ID.
        
        Supports various Confluence URL formats:
        - https://domain.atlassian.net/wiki/spaces/SPACE/pages/123456/Page+Title
        - https://domain.atlassian.net/wiki/display/SPACE/Page+Title
        - https://domain.atlassian.net/wiki/pages/viewpage.action?pageId=123456
        - https://domain.atlassian.net/wiki/spaces/SPACE/overview
        
        Args:
            url: Confluence URL
            
        Returns:
            Dictionary with 'space_key', 'page_id', 'domain', and 'type'
        """
        parsed_url = urlparse(url)
        domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        result = {
            'domain': domain,
            'space_key': None,
            'page_id': None,
            'type': None,
            'url': url
        }
        
        path = parsed_url.path
        query = parse_qs(parsed_url.query)
        
        # Format 1: /wiki/spaces/SPACE/pages/123456/Page+Title
        spaces_match = re.search(r'/wiki/spaces/([^/]+)/pages/(\d+)', path)
        if spaces_match:
            result['space_key'] = spaces_match.group(1)
            result['page_id'] = spaces_match.group(2)
            result['type'] = 'page'
            return result
        
        # Format 2: /wiki/spaces/SPACE/overview (space overview)
        space_overview_match = re.search(r'/wiki/spaces/([^/]+)/?(?:overview)?$', path)
        if space_overview_match:
            result['space_key'] = space_overview_match.group(1)
            result['type'] = 'space'
            return result
        
        # Format 3: /wiki/display/SPACE/Page+Title
        display_match = re.search(r'/wiki/display/([^/]+)', path)
        if display_match:
            result['space_key'] = display_match.group(1)
            result['type'] = 'page'
            return result
        
        # Format 4: /wiki/pages/viewpage.action?pageId=123456
        if 'pageId' in query:
            result['page_id'] = query['pageId'][0]
            result['type'] = 'page'
            return result
        
        # Format 5: Extract space from spaceKey parameter
        if 'spaceKey' in query:
            result['space_key'] = query['spaceKey'][0]
            result['type'] = 'space'
            return result
        
        return result
    
    @staticmethod
    def validate_confluence_url(url: str) -> Tuple[bool, str]:
        """
        Validate if the URL is a valid Confluence URL.
        
        Args:
            url: URL to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not url:
            return False, "URL is empty"
        
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return False, "Invalid URL format"
            
            # Check if it's an Atlassian domain or contains /wiki/
            is_atlassian = 'atlassian.net' in parsed.netloc
            has_wiki_path = '/wiki/' in parsed.path
            
            if not (is_atlassian or has_wiki_path):
                return False, "URL doesn't appear to be a Confluence URL"
            
            # Try to parse and see if we can extract meaningful info
            result = ConfluenceURLParser.parse_confluence_url(url)
            if not result['space_key'] and not result['page_id']:
                return False, "Unable to extract space or page information from URL"
            
            return True, "Valid Confluence URL"
            
        except Exception as e:
            return False, f"Error parsing URL: {str(e)}"
    
    @staticmethod
    def extract_space_and_page(url: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Simple extraction of space key and page ID from URL.
        
        Args:
            url: Confluence URL
            
        Returns:
            Tuple of (space_key, page_id)
        """
        result = ConfluenceURLParser.parse_confluence_url(url)
        return result['space_key'], result['page_id']
    
    @staticmethod
    def get_helpful_examples() -> Dict[str, str]:
        """
        Get examples of supported Confluence URL formats.
        
        Returns:
            Dictionary with format names and example URLs
        """
        return {
            "Page URL (new format)": "https://yourcompany.atlassian.net/wiki/spaces/TEAM/pages/123456/Page+Title",
            "Page URL (old format)": "https://yourcompany.atlassian.net/wiki/display/TEAM/Page+Title",
            "Page URL (direct)": "https://yourcompany.atlassian.net/wiki/pages/viewpage.action?pageId=123456",
            "Space Overview": "https://yourcompany.atlassian.net/wiki/spaces/TEAM/overview",
            "Space Home": "https://yourcompany.atlassian.net/wiki/spaces/TEAM/"
        }

# Convenience function for easy import
def parse_confluence_url(url: str) -> Dict[str, Optional[str]]:
    """Parse a Confluence URL and return extracted information."""
    return ConfluenceURLParser.parse_confluence_url(url)

def validate_confluence_url(url: str) -> Tuple[bool, str]:
    """Validate if URL is a valid Confluence URL."""
    return ConfluenceURLParser.validate_confluence_url(url)
