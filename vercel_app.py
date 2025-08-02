"""
Vercel-compatible wrapper for the Streamlit app
This creates a Flask app that can serve the same functionality
"""
import os
import sys
import traceback

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from flask import Flask, render_template, request, jsonify
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
    
    print("Flask app initialized successfully")
    
except ImportError as e:
    print(f"Import error during initialization: {e}")
    print(f"Python path: {sys.path}")
    # Create a minimal app for error reporting
    from flask import Flask, jsonify
    app = Flask(__name__)
    
    @app.route('/')
    def error_page():
        return jsonify({
            'error': f'Import error: {str(e)}',
            'python_path': sys.path,
            'working_directory': os.getcwd(),
            'files': os.listdir('.')
        })
        
except Exception as e:
    print(f"Unexpected error during initialization: {e}")
    print(traceback.format_exc())
    raise

@app.route('/')
def index():
    """Serve the main application interface"""
    try:
        return render_template('index.html')
    except Exception as e:
        return jsonify({
            'error': f'Template error: {str(e)}',
            'message': 'Could not load main page'
        })

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        
        # Import the actual agents here
        try:
            from agents.enhanced_system import create_enhanced_design_review_system
            from agents.orchestrator import ReviewOrchestrator
        except ImportError as e:
            return jsonify({
                'error': f'Agent import error: {str(e)}',
                'response': 'Hello! The AI agents are not available in this environment.'
            })
        
        # Initialize the system
        try:
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
                'error': f'Processing error: {str(e)}',
                'response': f'Hello! I got your message: "{message}" but encountered an error processing it.'
            })
        
    except Exception as e:
        return jsonify({
            'error': f'Request error: {str(e)}',
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
        try:
            from agents.enhanced_system import create_enhanced_design_review_system
            from agents.orchestrator import ReviewOrchestrator
        except ImportError as e:
            return jsonify({
                'error': f'Agent import error: {str(e)}',
                'response': 'File upload is not available in this environment.'
            })
        
        # Initialize the system
        try:
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
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            return jsonify({
                'error': f'Processing error: {str(e)}',
                'response': 'Could not analyze the uploaded file.'
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

@app.route('/api/status')
def status():
    """API status endpoint with environment info"""
    try:
        # Try to import agents to check availability
        from agents.enhanced_system import create_enhanced_design_review_system
        agents_available = True
        agent_error = None
    except Exception as e:
        agents_available = False
        agent_error = str(e)
    
    return jsonify({
        'status': 'running',
        'agents_available': agents_available,
        'agent_error': agent_error,
        'environment': {
            'python_version': sys.version,
            'working_directory': os.getcwd(),
            'environment_vars': {
                'OPENAI_API_KEY': bool(os.getenv('OPENAI_API_KEY')),
                'EXA_API_KEY': bool(os.getenv('EXA_API_KEY'))
            }
        },
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    app.run(debug=True)
