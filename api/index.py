from flask import Flask, request, jsonify, render_template_string
import os
from dotenv import load_dotenv
from PIL import Image
import io
import base64
from agents.design_reviewer import DesignReviewAgent
from agents.local_reviewer import local_agent
from agents.cloud_reviewer import cloud_agent
from config.settings import settings

# Load environment variables
load_dotenv()

app = Flask(__name__)

# HTML template for simple web interface
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
            display: none;
        }
        .error {
            background: #e74c3c;
            color: white;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }
        .success {
            background: #27ae60;
            color: white;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }
        .loading {
            text-align: center;
            padding: 20px;
            color: #7f8c8d;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎨 Margo - AI Design Review</h1>
        <p style="text-align: center; color: #7f8c8d;">Upload your design files and get AI-powered feedback!</p>
        
        <!-- AI Provider Info -->
        <div style="background: #e8f4fd; padding: 15px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #3498db;">
            <h4 style="margin: 0 0 10px 0; color: #2980b9;">🤖 AI Provider Options</h4>
            <p style="margin: 0; font-size: 14px; color: #34495e;">
                <strong>📁 File Upload:</strong> Requires OpenAI API key for image/PDF analysis<br>
                <strong>📝 Text Description:</strong> Works with free providers (Groq, Hugging Face, etc.)<br>
                <strong>🔗 Confluence:</strong> Requires OpenAI + Confluence API setup
            </p>
        </div>
        
        <form id="uploadForm" enctype="multipart/form-data">
            <div class="form-group">
                <label>Analysis Type</label>
                <select id="analysis_type" name="analysis_type">
                    <option value="file">📎 Upload File (PNG, JPG, PDF)</option>
                    <option value="text">📝 Text Content</option>
                    <option value="confluence">🔗 Confluence URL</option>
                </select>
            </div>
            
            <div class="form-group" id="file_input">
                <label for="file">Design File (PNG, JPG, PDF)</label>
                <input type="file" id="file" name="file" accept=".png,.jpg,.jpeg,.pdf">
            </div>
            
            <div class="form-group" id="text_input" style="display: none;">
                <label for="content">Content to Review</label>
                <textarea id="content" name="content" rows="8" placeholder="Paste your design description, requirements, or content to review..."></textarea>
            </div>
            
            <div class="form-group" id="confluence_input" style="display: none;">
                <label for="confluence_url">Confluence URL</label>
                <input type="url" id="confluence_url" name="confluence_url" placeholder="https://yourcompany.atlassian.net/wiki/spaces/TEAM/pages/123456/Page+Title">
                <small style="color: #7f8c8d; font-size: 12px;">
                    Supported formats: page URLs, space URLs, or direct page links
                </small>
            </div>
            
            <div class="form-group">
                <label for="review_type">Review Type</label>
                <select id="review_type" name="review_type">
                    <option value="General Design">General Design</option>
                    <option value="UI/UX">UI/UX</option>
                    <option value="Accessibility">Accessibility</option>
                    <option value="Brand Consistency">Brand Consistency</option>
                    <option value="Roku TV Design">Roku TV Design</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="detail_level">Detail Level (1-5)</label>
                <select id="detail_level" name="detail_level">
                    <option value="1">1 - Brief Overview</option>
                    <option value="2">2 - Basic Analysis</option>
                    <option value="3" selected>3 - Standard Review</option>
                    <option value="4">4 - Detailed Analysis</option>
                    <option value="5">5 - Comprehensive Review</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="context">Design Context (Optional)</label>
                <textarea id="context" name="context" placeholder="Describe the design context, user goals, or specific areas to focus on..."></textarea>
            </div>
            
            <button type="submit">🔍 Analyze Design</button>
        </form>
        
        <div id="loading" class="loading" style="display: none;">
            <p>🤖 Analyzing your design... This may take a moment.</p>
        </div>
        
        <div id="results" class="results"></div>
    </div>

    <script>
        // Handle analysis type switching
        document.getElementById('analysis_type').addEventListener('change', function() {
            const type = this.value;
            const fileInput = document.getElementById('file_input');
            const textInput = document.getElementById('text_input');
            const confluenceInput = document.getElementById('confluence_input');
            const fileField = document.getElementById('file');
            
            // Hide all inputs
            fileInput.style.display = 'none';
            textInput.style.display = 'none';
            confluenceInput.style.display = 'none';
            
            // Remove required attributes
            fileField.removeAttribute('required');
            document.getElementById('content').removeAttribute('required');
            document.getElementById('confluence_url').removeAttribute('required');
            
            // Show relevant input and set required
            if (type === 'file') {
                fileInput.style.display = 'block';
                fileField.setAttribute('required', 'required');
            } else if (type === 'text') {
                textInput.style.display = 'block';
                document.getElementById('content').setAttribute('required', 'required');
            } else if (type === 'confluence') {
                confluenceInput.style.display = 'block';
                document.getElementById('confluence_url').setAttribute('required', 'required');
            }
        });
        
        document.getElementById('uploadForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const analysisType = document.getElementById('analysis_type').value;
            const loadingDiv = document.getElementById('loading');
            const resultsDiv = document.getElementById('results');
            const submitBtn = document.querySelector('button[type="submit"]');
            
            // Show loading state
            loadingDiv.style.display = 'block';
            resultsDiv.style.display = 'none';
            submitBtn.disabled = true;
            submitBtn.textContent = 'Analyzing...';
            
            try {
                let response;
                
                if (analysisType === 'file') {
                    // File upload
                    const formData = new FormData(this);
                    response = await fetch('/api/analyze', {
                        method: 'POST',
                        body: formData
                    });
                } else if (analysisType === 'text') {
                    // Text analysis
                    const content = document.getElementById('content').value;
                    const reviewType = document.getElementById('review_type').value;
                    const detailLevel = document.getElementById('detail_level').value;
                    
                    response = await fetch('/api/analyze-text', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            content: content,
                            review_type: reviewType,
                            detail_level: detailLevel
                        })
                    });
                } else if (analysisType === 'confluence') {
                    // Confluence URL
                    const confluenceUrl = document.getElementById('confluence_url').value;
                    const reviewType = document.getElementById('review_type').value;
                    const detailLevel = document.getElementById('detail_level').value;
                    
                    response = await fetch('/api/analyze-confluence', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            url: confluenceUrl,
                            review_type: reviewType,
                            detail_level: detailLevel
                        })
                    });
                }
                
                const result = await response.json();
                
                if (result.error) {
                    let errorHtml = `<div class="error">${result.error}</div>`;
                    
                    if (result.setup_instructions) {
                        errorHtml += '<div style="margin-top: 15px;"><h4>Setup Instructions:</h4>';
                        
                        if (typeof result.setup_instructions === 'string') {
                            errorHtml += `<p>${result.setup_instructions}</p>`;
                        } else if (result.setup_instructions.cloud_options) {
                            errorHtml += '<p><strong>Recommended: Groq (Free & Fast)</strong></p>';
                            errorHtml += '<ol>';
                            errorHtml += '<li>Go to <a href="https://console.groq.com/" target="_blank">Groq Console</a></li>';
                            errorHtml += '<li>Sign up and get your API key</li>';
                            errorHtml += '<li>Set environment variable: GROQ_API_KEY=your_key_here</li>';
                            errorHtml += '</ol>';
                        }
                        
                        errorHtml += '</div>';
                    }
                    
                    resultsDiv.innerHTML = errorHtml;
                } else {
                    let html = '<h3>📋 Analysis Results</h3>';
                    
                    if (result.provider) {
                        html += `<p><strong>AI Provider:</strong> ${result.provider} (${result.model || 'default model'})</p>`;
                    }
                    
                    if (result.url) {
                        html += `<p><strong>Source:</strong> <a href="${result.url}" target="_blank">Confluence Page</a></p>`;
                    }
                    
                    if (result.pages_reviewed) {
                        html += `<p><strong>Pages Reviewed:</strong> ${result.pages_reviewed}</p>`;
                    }
                    
                    if (result.overall_score) {
                        html += `<p><strong>Overall Score:</strong> ${result.overall_score}</p>`;
                    }
                    
                    if (result.review) {
                        html += `<h4>📄 Review</h4><div style="white-space: pre-wrap;">${result.review}</div>`;
                    }
                    
                    if (result.strengths) {
                        html += '<h4>✅ Strengths</h4><ul>';
                        result.strengths.forEach(strength => {
                            html += `<li>${strength}</li>`;
                        });
                        html += '</ul>';
                    }
                    
                    if (result.issues) {
                        html += '<h4>⚠️ Issues Found</h4><ul>';
                        result.issues.forEach(issue => {
                            html += `<li>${issue}</li>`;
                        });
                        html += '</ul>';
                    }
                    
                    if (result.suggestions) {
                        html += '<h4>💡 Suggestions</h4><ul>';
                        result.suggestions.forEach(suggestion => {
                            html += `<li>${suggestion}</li>`;
                        });
                        html += '</ul>';
                    }
                    
                    if (result.summary) {
                        html += `<h4>📄 Summary</h4><p>${result.summary}</p>`;
                    }
                    
                    resultsDiv.innerHTML = html;
                }
                
                resultsDiv.style.display = 'block';
                
            } catch (error) {
                resultsDiv.innerHTML = `<div class="error">Error: ${error.message}</div>`;
                resultsDiv.style.display = 'block';
            } finally {
                loadingDiv.style.display = 'none';
                submitBtn.disabled = false;
                submitBtn.textContent = '🔍 Analyze Design';
            }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Main page with upload form."""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/analyze', methods=['POST'])
def analyze_design():
    """API endpoint to analyze uploaded designs."""
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Get form parameters
        review_type = request.form.get('review_type', 'General Design')
        detail_level = int(request.form.get('detail_level', 3))
        context = request.form.get('context', '')
        
        # Check if OpenAI is configured
        openai_available = bool(os.getenv("OPENAI_API_KEY"))
        cloud_available = cloud_agent.is_available()
        
        if not openai_available and not cloud_available:
            setup_info = cloud_agent.get_setup_instructions()
            return jsonify({
                'error': 'No AI provider configured. Please set up OpenAI or a cloud LLM provider.',
                'setup_instructions': {
                    'openai': 'Get API key from https://platform.openai.com/ and set OPENAI_API_KEY environment variable.',
                    'cloud_options': setup_info
                }
            }), 400
        
        # Initialize the design review agent (try OpenAI first, then cloud)
        if openai_available:
            agent = DesignReviewAgent()
        else:
            # Use cloud agent for text-based review
            agent = None
        
        # Process the uploaded file
        if file.content_type.startswith('image/'):
            # Handle image files
            # Reset file stream position
            file.stream.seek(0)
            image = Image.open(file.stream)
            
            # For cloud agents, we need to convert image to text description first
            if not openai_available:
                # For now, provide a fallback message for images with cloud LLMs
                return jsonify({
                    'error': 'Image analysis requires OpenAI (vision capabilities). Cloud LLMs currently support text-only reviews.',
                    'suggestion': 'Please provide a text description of the image for review, or set up OpenAI API key for image analysis.'
                }), 400
            
            # For Roku TV Design, use specialized review
            if review_type == "Roku TV Design":
                # Reset file stream for agent processing
                file.stream.seek(0)
                review_result = agent.review_roku_design(
                    file,
                    input_type="file",
                    design_context=context,
                    include_grading=True
                )
            else:
                # Reset file stream for agent processing
                file.stream.seek(0)
                review_result = agent.review_design(
                    file,
                    review_type=review_type,
                    detail_level=detail_level,
                    include_suggestions=True
                )
        
        elif file.content_type == 'application/pdf':
            # Handle PDF files
            # Reset file stream position
            file.stream.seek(0)
            
            # For cloud agents, we need to extract text from PDF first
            if not openai_available:
                return jsonify({
                    'error': 'PDF analysis requires OpenAI (document processing). Cloud LLMs currently support text-only reviews.',
                    'suggestion': 'Please extract text from the PDF and paste it for review, or set up OpenAI API key for PDF analysis.'
                }), 400
            
            if review_type == "Roku TV Design":
                review_result = agent.review_roku_design(
                    file,
                    input_type="file",
                    design_context=context,
                    include_grading=True
                )
            else:
                review_result = agent.review_design(
                    file,
                    review_type=review_type,
                    detail_level=detail_level,
                    include_suggestions=True
                )
        else:
            return jsonify({'error': 'Unsupported file type. Please upload PNG, JPG, or PDF files.'}), 400
        
        # Handle errors in review result
        if 'error' in review_result:
            return jsonify(review_result), 400
        
        return jsonify(review_result)
        
    except Exception as e:
        return jsonify({'error': f'Error processing request: {str(e)}'}), 500

@app.route('/api/analyze-text', methods=['POST'])
def analyze_text():
    """API endpoint to analyze text content using cloud LLMs."""
    try:
        data = request.get_json()
        
        if not data or 'content' not in data:
            return jsonify({'error': 'No content provided'}), 400
        
        content = data['content']
        review_type = data.get('review_type', 'General Design')
        detail_level = int(data.get('detail_level', 3))
        
        # Check available providers
        openai_available = bool(os.getenv("OPENAI_API_KEY"))
        cloud_available = cloud_agent.is_available()
        
        if not openai_available and not cloud_available:
            setup_info = cloud_agent.get_setup_instructions()
            return jsonify({
                'error': 'No AI provider configured.',
                'setup_instructions': setup_info
            }), 400
        
        # Use cloud LLM if available, otherwise fallback to OpenAI
        if cloud_available:
            review_result = cloud_agent.review_design_cloud(
                text_content=content,
                review_type=review_type,
                detail_level=detail_level
            )
        else:
            # Fallback to OpenAI for text analysis
            agent = DesignReviewAgent()
            # We'd need to implement a text-only method in DesignReviewAgent
            review_result = {'error': 'Text analysis with OpenAI not implemented yet'}
        
        # Handle errors in review result
        if 'error' in review_result:
            return jsonify(review_result), 400
        
        return jsonify(review_result)
        
    except Exception as e:
        return jsonify({'error': f'Error processing request: {str(e)}'}), 500

@app.route('/api/analyze-confluence', methods=['POST'])
def analyze_confluence():
    """API endpoint to analyze Confluence content by URL."""
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({'error': 'No Confluence URL provided'}), 400
        
        confluence_url = data['url']
        review_type = data.get('review_type', 'General Design')
        detail_level = int(data.get('detail_level', 3))
        
        # Import here to avoid circular imports
        from agents.confluence_utils import validate_confluence_url, parse_confluence_url
        from agents.document_loaders import document_loader_manager
        
        # Validate URL
        is_valid, error_msg = validate_confluence_url(confluence_url)
        if not is_valid:
            return jsonify({'error': f'Invalid Confluence URL: {error_msg}'}), 400
        
        # Parse URL to extract space and page info
        parsed = parse_confluence_url(confluence_url)
        space_key = parsed['space_key']
        page_id = parsed['page_id']
        
        if not space_key and not page_id:
            return jsonify({'error': 'Unable to extract space or page information from URL'}), 400
        
        # Check if Confluence is configured
        if not settings.is_confluence_configured():
            return jsonify({
                'error': 'Confluence is not configured. Please set CONFLUENCE_URL, CONFLUENCE_USERNAME, and CONFLUENCE_API_KEY environment variables.'
            }), 400
        
        # Load Confluence content
        try:
            if page_id:
                # Load specific page
                documents = document_loader_manager.load_confluence_documents(
                    space_key=space_key or "UNKNOWN",
                    page_ids=[page_id]
                )
            else:
                # Load space content (limited)
                documents = document_loader_manager.load_confluence_documents(
                    space_key=space_key,
                    limit=10  # Limit to avoid overwhelming
                )
            
            if not documents:
                return jsonify({'error': 'No content found at the provided URL'}), 400
            
            # Combine document content
            content = "\n\n".join([doc.page_content for doc in documents])
            
            # Review using available AI
            openai_available = bool(os.getenv("OPENAI_API_KEY"))
            cloud_available = cloud_agent.is_available()
            
            if cloud_available:
                review_result = cloud_agent.review_design_cloud(
                    text_content=content,
                    review_type=review_type,
                    detail_level=detail_level
                )
                review_result['source'] = 'confluence_cloud'
                review_result['url'] = confluence_url
                review_result['pages_reviewed'] = len(documents)
            elif openai_available:
                agent = DesignReviewAgent()
                # Would need text review method
                review_result = {'error': 'OpenAI text analysis not implemented yet'}
            else:
                return jsonify({
                    'error': 'No AI provider available for analysis'
                }), 400
            
            return jsonify(review_result)
            
        except Exception as e:
            return jsonify({'error': f'Failed to load Confluence content: {str(e)}'}), 500
        
    except Exception as e:
        return jsonify({'error': f'Error processing request: {str(e)}'}), 500

@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'service': 'margo-design-review'})

# For Vercel deployment - the Flask app is already named 'app'
# which is what Vercel expects

if __name__ == '__main__':
    app.run(debug=True)
