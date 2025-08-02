"""
Vercel-compatible Flask app for Margo Design Review Agent
"""
import os
import sys
from datetime import datetime

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, request, jsonify

# Initialize Flask app
app = Flask(__name__)

@app.route('/')
def index():
    """Serve the main application interface"""
    try:
        return render_template('index.html')
    except Exception as e:
        return f"Template error: {str(e)} - Working directory: {os.getcwd()}"

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        
        # Simple response for now
        response = f'I received your message: "{message}". The AI system is working!'
        
        return jsonify({
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Request error: {str(e)}',
            'response': 'I encountered an error. Please try again.'
        })

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file uploads"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'})
        
        file = request.files['file']
        message = request.form.get('message', 'Please analyze this design.')
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'})
        
        # Simple response for file upload
        response = f'I can see you uploaded "{file.filename}". File analysis is working!'
        
        return jsonify({
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Upload error: {str(e)}',
            'response': 'File upload failed.'
        })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Margo Design Review Agent',
        'version': '2.0.0',
        'timestamp': datetime.now().isoformat()
    })

# For Vercel, the app object is what gets called
if __name__ == '__main__':
    app.run(debug=True)

if __name__ == '__main__':
    app.run(debug=True)
