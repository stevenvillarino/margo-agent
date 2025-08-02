"""
Lightweight API for Vercel deployment
Optimized for serverless function size limits
"""
import os
import json
import base64
from io import BytesIO
from typing import Dict, Any, Optional

from flask import Flask, request, jsonify, render_template_string
from PIL import Image
import httpx

# Simple HTML template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Margo - AI Design Review</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: #f8f9fa;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            text-align: center;
            margin-bottom: 30px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: 600;
            color: #34495e;
        }
        input[type="file"], select, textarea {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
        }
        textarea {
            height: 100px;
            resize: vertical;
        }
        button {
            background: #3498db;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            width: 100%;
        }
        button:hover {
            background: #2980b9;
        }
        button:disabled {
            background: #bdc3c7;
            cursor: not-allowed;
        }
        .results {
            margin-top: 30px;
            padding: 20px;
            background: #ecf0f1;
            border-radius: 5px;
            white-space: pre-wrap;
        }
        .error {
            background: #e74c3c;
            color: white;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }
        .loading {
            text-align: center;
            color: #7f8c8d;
            font-style: italic;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎨 Margo AI Design Review</h1>
        
        <form id="reviewForm" enctype="multipart/form-data">
            <div class="form-group">
                <label for="file">Upload Design File:</label>
                <input type="file" id="file" name="file" accept=".png,.jpg,.jpeg,.pdf" required>
            </div>
            
            <div class="form-group">
                <label for="reviewType">Review Type:</label>
                <select id="reviewType" name="reviewType">
                    <option value="general">General Design Review</option>
                    <option value="accessibility">Accessibility Review</option>
                    <option value="roku">Roku Brand Review</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="context">Additional Context (optional):</label>
                <textarea id="context" name="context" placeholder="Provide any specific requirements or context for the review..."></textarea>
            </div>
            
            <button type="submit">Get AI Review</button>
        </form>
        
        <div id="results" class="results" style="display: none;"></div>
    </div>

    <script>
        document.getElementById('reviewForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const resultsDiv = document.getElementById('results');
            const submitButton = e.target.querySelector('button[type="submit"]');
            
            // Show loading state
            submitButton.disabled = true;
            submitButton.textContent = 'Analyzing...';
            resultsDiv.style.display = 'block';
            resultsDiv.innerHTML = '<div class="loading">🤖 AI is analyzing your design...</div>';
            
            try {
                const formData = new FormData(e.target);
                const response = await fetch('/api/review', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                
                if (result.success) {
                    resultsDiv.innerHTML = result.review;
                } else {
                    resultsDiv.innerHTML = '<div class="error">Error: ' + result.error + '</div>';
                }
            } catch (error) {
                resultsDiv.innerHTML = '<div class="error">Network error: ' + error.message + '</div>';
            } finally {
                submitButton.disabled = false;
                submitButton.textContent = 'Get AI Review';
            }
        });
    </script>
</body>
</html>
"""

class LightweightDesignReviewer:
    """Lightweight design reviewer for Vercel deployment."""
    
    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        
    async def review_design(self, image_data: bytes, review_type: str = "general", context: str = "") -> str:
        """Review design using available AI service."""
        
        # Convert image to base64
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # Try OpenAI first
        if self.openai_api_key:
            return await self._review_with_openai(image_base64, review_type, context)
        
        # Fallback to Anthropic
        elif self.anthropic_api_key:
            return await self._review_with_anthropic(image_base64, review_type, context)
        
        else:
            raise Exception("No AI API keys configured")
    
    async def _review_with_openai(self, image_base64: str, review_type: str, context: str) -> str:
        """Review using OpenAI GPT-4 Vision."""
        
        prompt = self._get_prompt(review_type, context)
        
        payload = {
            "model": "gpt-4-vision-preview",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
                        }
                    ]
                }
            ],
            "max_tokens": 1000
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.openai_api_key}",
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise Exception(f"OpenAI API error: {response.text}")
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
    
    async def _review_with_anthropic(self, image_base64: str, review_type: str, context: str) -> str:
        """Review using Anthropic Claude Vision."""
        
        prompt = self._get_prompt(review_type, context)
        
        payload = {
            "model": "claude-3-sonnet-20240229",
            "max_tokens": 1000,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": image_base64
                            }
                        },
                        {"type": "text", "text": prompt}
                    ]
                }
            ]
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.anthropic_api_key,
                    "Content-Type": "application/json",
                    "anthropic-version": "2023-06-01"
                },
                json=payload,
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise Exception(f"Anthropic API error: {response.text}")
            
            result = response.json()
            return result["content"][0]["text"]
    
    def _get_prompt(self, review_type: str, context: str) -> str:
        """Get review prompt based on type."""
        
        base_prompt = "You are an expert design reviewer. Analyze this design and provide detailed feedback."
        
        prompts = {
            "general": f"""
            {base_prompt}
            
            Focus on:
            - Visual hierarchy and layout
            - Color usage and contrast
            - Typography and readability
            - User experience and usability
            - Overall aesthetic appeal
            
            Provide specific, actionable feedback.
            """,
            
            "accessibility": f"""
            {base_prompt}
            
            Focus specifically on accessibility:
            - Color contrast ratios (WCAG compliance)
            - Text readability and font sizes
            - Interactive element sizing (touch targets)
            - Visual indicators and feedback
            - Information hierarchy for screen readers
            
            Provide WCAG compliance recommendations.
            """,
            
            "roku": f"""
            {base_prompt}
            
            Review this design against Roku brand guidelines:
            - Roku purple (#662D91) usage
            - Typography (Roku brand fonts)
            - Layout patterns and spacing
            - Button and component styles
            - Overall brand consistency
            
            Provide brand-specific recommendations.
            """
        }
        
        prompt = prompts.get(review_type, prompts["general"])
        
        if context:
            prompt += f"\n\nAdditional context: {context}"
        
        return prompt


# Initialize Flask app
app = Flask(__name__)
reviewer = LightweightDesignReviewer()

@app.route('/')
def index():
    """Serve the main interface."""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/review', methods=['POST'])
async def review_design():
    """Handle design review requests."""
    try:
        # Get uploaded file
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'})
        
        # Get form data
        review_type = request.form.get('reviewType', 'general')
        context = request.form.get('context', '')
        
        # Process image
        image_data = file.read()
        
        # Convert to standard format if needed
        if file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            try:
                image = Image.open(BytesIO(image_data))
                # Convert to RGB if needed
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                
                # Resize if too large (to save bandwidth)
                max_size = (1024, 1024)
                if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
                    image.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                # Save as JPEG
                output = BytesIO()
                image.save(output, format='JPEG', quality=85)
                image_data = output.getvalue()
                
            except Exception as e:
                return jsonify({'success': False, 'error': f'Image processing error: {str(e)}'})
        
        # Get AI review
        review = await reviewer.review_design(image_data, review_type, context)
        
        return jsonify({
            'success': True,
            'review': review,
            'review_type': review_type
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'service': 'margo-design-review'})

# Vercel serverless function handler
def handler(request, context):
    """Vercel serverless function handler."""
    return app(request.environ, context)

# For local development
if __name__ == '__main__':
    app.run(debug=True)
