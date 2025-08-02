"""
Vercel-compatible wrapper for the Streamlit app
This creates a Flask app that can serve the same functionality
"""
from flask import Flask, render_template, request, jsonify
import os
import json
import base64
from datetime import datetime
from typing import Dict, List, Any, Optional
from PIL import Image
import io

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

@app.route('/')
def index():
    """Serve the main application interface"""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        
        # Import the actual agents here
        from agents.enhanced_system import create_enhanced_design_review_system
        from agents.orchestrator import ReviewOrchestrator
        
        # Initialize the system
        system = create_enhanced_design_review_system()
        if not system:
            return jsonify({
                'error': 'AI system not available. Please check API keys.',
                'response': 'Hello! I need OpenAI API key to provide intelligent responses.'
            })
        
        # Process the message
        orchestrator = ReviewOrchestrator(system)
        response = orchestrator.process_message(message)
        
        return jsonify({
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'response': 'I encountered an error. Please try again.'
        })

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file uploads and analysis"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'})
        
        file = request.files['file']
        message = request.form.get('message', 'Please analyze this design.')
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'})
        
        # Process the uploaded file
        file_content = file.read()
        
        # Import the actual agents here
        from agents.enhanced_system import create_enhanced_design_review_system
        from agents.orchestrator import ReviewOrchestrator
        
        # Initialize the system
        system = create_enhanced_design_review_system()
        if not system:
            return jsonify({
                'error': 'AI system not available. Please check API keys.'
            })
        
        # Process the file and message
        orchestrator = ReviewOrchestrator(system)
        response = orchestrator.analyze_design(file_content, message, file.filename)
        
        return jsonify({
            'response': response,
            'filename': file.filename,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e)
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

if __name__ == '__main__':
    app.run(debug=True)
