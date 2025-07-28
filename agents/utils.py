import base64
import io
from typing import Any
from PIL import Image
import PyPDF2

def encode_image(image_file) -> str:
    """
    Encode an image file to base64 string.
    
    Args:
        image_file: Streamlit uploaded file object
        
    Returns:
        Base64 encoded string
    """
    # Read image data
    image_data = image_file.read()
    
    # Reset file pointer
    image_file.seek(0)
    
    # Encode to base64
    return base64.b64encode(image_data).decode('utf-8')

def extract_text_from_pdf(pdf_file) -> str:
    """
    Extract text content from a PDF file.
    
    Args:
        pdf_file: Streamlit uploaded file object
        
    Returns:
        Extracted text content
    """
    try:
        # Create a PDF reader object
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        # Extract text from all pages
        text_content = ""
        for page in pdf_reader.pages:
            text_content += page.extract_text() + "\n"
        
        # Reset file pointer
        pdf_file.seek(0)
        
        return text_content.strip()
        
    except Exception as e:
        return f"Error extracting PDF content: {str(e)}"

def resize_image_if_needed(image: Image.Image, max_size: int = 1024) -> Image.Image:
    """
    Resize image if it's too large for the API.
    
    Args:
        image: PIL Image object
        max_size: Maximum dimension size
        
    Returns:
        Resized image if needed
    """
    width, height = image.size
    
    if max(width, height) > max_size:
        # Calculate new dimensions
        if width > height:
            new_width = max_size
            new_height = int(height * (max_size / width))
        else:
            new_height = max_size
            new_width = int(width * (max_size / height))
        
        # Resize image
        image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    return image

def validate_file_size(file, max_size_mb: int = 10) -> bool:
    """
    Validate that file size is within limits.
    
    Args:
        file: Streamlit uploaded file object
        max_size_mb: Maximum file size in MB
        
    Returns:
        True if file size is acceptable
    """
    file_size = len(file.getvalue())
    max_size_bytes = max_size_mb * 1024 * 1024
    
    return file_size <= max_size_bytes
