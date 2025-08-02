"""
Test suite for FastAPI Design Review App
Run with: pytest tests/
"""

import pytest
from fastapi.testclient import TestClient
from main import app
import json
import io

# Create test client
client = TestClient(app)

class TestHealthEndpoint:
    def test_health_check(self):
        """Test health endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy", "service": "design-review-api"}

class TestChatEndpoint:
    def test_chat_without_file(self):
        """Test chat endpoint without file upload"""
        response = client.post(
            "/api/chat",
            json={
                "message": "What are good color practices?",
                "has_file": False
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "color" in data["response"].lower()
        assert "contrast" in data["response"].lower()

    def test_chat_with_file(self):
        """Test chat endpoint with file"""
        response = client.post(
            "/api/chat",
            json={
                "message": "Review this design",
                "has_file": True,
                "filename": "test_design.png"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "test_design.png" in data["response"]
        assert "feedback" in data["response"]

    def test_chat_typography_question(self):
        """Test typography-specific responses"""
        response = client.post(
            "/api/chat",
            json={
                "message": "What font should I use?",
                "has_file": False
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "typography" in data["response"].lower()
        assert "hierarchy" in data["response"].lower()

    def test_chat_accessibility_question(self):
        """Test accessibility-specific responses"""
        response = client.post(
            "/api/chat",
            json={
                "message": "How do I make this accessible?",
                "has_file": False
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "accessibility" in data["response"].lower()
        assert "contrast" in data["response"].lower()

class TestFileUpload:
    def test_valid_image_upload(self):
        """Test uploading a valid image file"""
        # Create a fake PNG file
        fake_image = io.BytesIO(b"fake png content")
        
        response = client.post(
            "/api/upload",
            files={"file": ("test.png", fake_image, "image/png")}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["filename"] == "test.png"
        assert data["content_type"] == "image/png"
        assert "Successfully uploaded" in data["message"]

    def test_invalid_file_type(self):
        """Test uploading an invalid file type"""
        fake_file = io.BytesIO(b"fake txt content")
        
        response = client.post(
            "/api/upload",
            files={"file": ("test.txt", fake_file, "text/plain")}
        )
        assert response.status_code == 400
        assert "Only PNG, JPG, and PDF files are supported" in response.json()["error"]

class TestMainPage:
    def test_home_page_loads(self):
        """Test that the main page loads"""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

class TestResponsePatterns:
    """Test that responses match expected patterns for different input types"""
    
    def test_greeting_responses(self):
        """Test greeting detection"""
        greetings = ["hello", "hi", "hey there"]
        for greeting in greetings:
            response = client.post(
                "/api/chat",
                json={"message": greeting, "has_file": False}
            )
            assert response.status_code == 200
            data = response.json()
            assert "hello" in data["response"].lower() or "hi" in data["response"].lower()

    def test_layout_questions(self):
        """Test layout-specific responses"""
        layout_questions = [
            "How do I improve my layout?",
            "What about spacing?",
            "Grid system help"
        ]
        for question in layout_questions:
            response = client.post(
                "/api/chat",
                json={"message": question, "has_file": False}
            )
            assert response.status_code == 200
            data = response.json()
            assert any(word in data["response"].lower() for word in ["layout", "spacing", "grid"])

if __name__ == "__main__":
    pytest.main([__file__])
