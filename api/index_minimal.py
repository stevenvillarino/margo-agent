"""
Ultra-lightweight API for Vercel deployment
Single file with minimal dependencies
"""
import os
import json
import base64
from io import BytesIO
from typing import Dict, Any

from flask import Flask, request, jsonify

# Minimal HTML for the web interface
MINIMAL_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Margo - AI Design Review</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background: #f8f9fa; }
        .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; text-align: center; margin-bottom: 30px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 5px; font-weight: 600; color: #34495e; }
        input[type="file"], select, textarea { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; font-size: 14px; }
        textarea { height: 100px; resize: vertical; }
        button { background: #3498db; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; width: 100%; }
        button:hover { background: #2980b9; }
        button:disabled { background: #bdc3c7; cursor: not-allowed; }
        .results { margin-top: 30px; padding: 20px; background: #ecf0f1; border-radius: 5px; white-space: pre-wrap; }
        .error { background: #e74c3c; color: white; padding: 15px; border-radius: 5px; margin: 20px 0; }
        .loading { text-align: center; color: #7f8c8d; font-style: italic; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎨 Margo AI Design Review</h1>
        <form id="reviewForm" enctype="multipart/form-data">
            <div class="form-group">
                <label for="file">Upload Design File:</label>
                <input type="file" id="file" name="file" accept=".png,.jpg,.jpeg" required>
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
                <textarea id="context" name="context" placeholder="Provide any specific requirements or context..."></textarea>
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
            submitButton.disabled = true;
            submitButton.textContent = 'Analyzing...';
            resultsDiv.style.display = 'block';
            resultsDiv.innerHTML = '<div class="loading">🤖 AI is analyzing your design...</div>';
            try {
                const formData = new FormData(e.target);
                const response = await fetch('/api/review', { method: 'POST', body: formData });
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

app = Flask(__name__)

class SimpleDesignReviewer:
    """Simple design reviewer using direct API calls."""
    
    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
    
    def review_design(self, image_base64: str, review_type: str = "general", context: str = "") -> str:
        """Review design using OpenAI API."""
        
        if not self.openai_api_key:
            return "Error: OpenAI API key not configured. Please set OPENAI_API_KEY environment variable."
        
        import requests
        
        prompt = self._get_prompt(review_type, context)
        
        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "gpt-4o",
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
        
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code != 200:
                return f"Error: OpenAI API returned status {response.status_code}: {response.text}"
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
            
        except Exception as e:
            return f"Error calling OpenAI API: {str(e)}"
    
    def _get_prompt(self, review_type: str, context: str) -> str:
        """Get review prompt based on type."""
        
        prompts = {
            "general": """
            You are an expert UI/UX designer. Analyze this design and provide detailed feedback on:
            
            1. **Visual Hierarchy**: How well does the design guide the user's eye?
            2. **Layout & Spacing**: Is the layout balanced and well-spaced?
            3. **Color & Contrast**: Are colors used effectively and accessibly?
            4. **Typography**: Is text readable and well-hierarchized?
            5. **User Experience**: How intuitive is the interface?
            6. **Overall Polish**: What improvements would enhance the design?
            
            Provide specific, actionable recommendations.
            """,
            
            "accessibility": """
            You are an accessibility expert. Review this design for WCAG compliance and accessibility:
            
            1. **Color Contrast**: Check if text has sufficient contrast (4.5:1 for normal text, 3:1 for large text)
            2. **Text Size**: Ensure text is readable (minimum 16px for body text)
            3. **Touch Targets**: Interactive elements should be at least 44px
            4. **Visual Indicators**: Clear focus states and interaction feedback
            5. **Information Hierarchy**: Logical structure for screen readers
            6. **Alternative Text**: Consider what alt text would be needed
            
            Rate compliance and provide specific fixes.
            """,
            
            "roku": """
            You are a Roku brand expert. Review this design against Roku brand guidelines:
            
            1. **Brand Colors**: Proper use of Roku purple (#662D91) and supporting colors
            2. **Typography**: Consistency with Roku's font choices and hierarchy
            3. **Layout Patterns**: Alignment with Roku's design system
            4. **Component Style**: Roku-specific button, card, and UI component styles
            5. **Voice & Tone**: Visual representation of Roku's brand personality
            6. **Platform Consistency**: Appropriate for Roku's ecosystem
            
            Provide brand-specific recommendations for better alignment.
            """
        }
        
        prompt = prompts.get(review_type, prompts["general"])
        
        if context:
            prompt += f"\n\n**Additional Context**: {context}"
        
        return prompt

# Initialize reviewer
reviewer = SimpleDesignReviewer()

@app.route('/')
def index():
    """Serve the main interface."""
    return MINIMAL_HTML

@app.route('/api/review', methods=['POST'])
def review_design():
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
        try:
            from PIL import Image
            
            image_data = file.read()
            image = Image.open(BytesIO(image_data))
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize if too large
            max_size = (1024, 1024)
            if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
                image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Convert to base64
            output = BytesIO()
            image.save(output, format='JPEG', quality=85)
            image_base64 = base64.b64encode(output.getvalue()).decode('utf-8')
            
        except Exception as e:
            return jsonify({'success': False, 'error': f'Image processing error: {str(e)}'})
        
        # Get AI review
        review = reviewer.review_design(image_base64, review_type, context)
        
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

# For Vercel
def handler(event, context):
    """Vercel handler."""
    return app(event, context)

# For local development
if __name__ == '__main__':
    app.run(debug=True)
