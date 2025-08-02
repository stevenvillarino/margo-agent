"""
Vercel-compatible API endpoint using BaseHTTPRequestHandler
"""
from http.server import BaseHTTPRequestHandler
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests - serve the proper template"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        # Read the actual template file
        template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'index.html')
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                html = f.read()
        except FileNotFoundError:
            # Fallback minimal HTML if template not found
            html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎨 Margo Design Review Agent</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }
        h1 {
            color: #663399;
            text-align: center;
            margin-bottom: 10px;
            font-size: 2.5em;
        }
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
            font-size: 1.2em;
        }
        .chat-container {
            display: flex;
            gap: 20px;
            height: 600px;
        }
        .chat-area {
            flex: 2;
            display: flex;
            flex-direction: column;
        }
        .upload-area {
            flex: 1;
            border: 2px dashed #663399;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            display: flex;
            flex-direction: column;
            justify-content: center;
            background: #f8f9fa;
        }
        .messages {
            flex: 1;
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            overflow-y: auto;
            margin-bottom: 20px;
            border: 1px solid #e0e0e0;
        }
        .input-area {
            display: flex;
            gap: 10px;
        }
        .message-input {
            flex: 1;
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 25px;
            font-size: 16px;
            outline: none;
        }
        .send-btn {
            padding: 15px 30px;
            background: linear-gradient(45deg, #663399, #9966cc);
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-weight: bold;
        }
        .send-btn:hover {
            opacity: 0.9;
        }
        .upload-btn {
            background: #663399;
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 10px;
            cursor: pointer;
            margin-top: 10px;
        }
        .upload-btn:hover {
            background: #552288;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎨 Margo Design Review Agent</h1>
        <p class="subtitle">AI-Powered Design Analysis & Feedback</p>
        
        <div class="chat-container">
            <div class="chat-area">
                <div class="messages" id="messages">
                    <p><strong>Margo:</strong> Hello! I'm ready to help you review designs. Upload an image or ask me questions about UI/UX best practices.</p>
                </div>
                <div class="input-area">
                    <input type="text" class="message-input" id="messageInput" placeholder="Ask me about your design...">
                    <button class="send-btn" onclick="sendMessage()">Send</button>
                </div>
            </div>
            
            <div class="upload-area">
                <div>
                    <h3>📁 Upload Design</h3>
                    <p>Drop files here or click to browse</p>
                    <input type="file" id="fileInput" accept="image/*,.pdf" style="display: none;" onchange="handleFile(this)">
                    <button class="upload-btn" onclick="document.getElementById('fileInput').click()">Choose File</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        function sendMessage() {
            const input = document.getElementById('messageInput');
            const messages = document.getElementById('messages');
            const message = input.value.trim();
            
            if (message) {
                messages.innerHTML += '<p><strong>You:</strong> ' + message + '</p>';
                
                // Simulate response
                setTimeout(() => {
                    messages.innerHTML += '<p><strong>Margo:</strong> I received your message about "' + message + '". The full AI system is being set up - this is a working deployment!</p>';
                    messages.scrollTop = messages.scrollHeight;
                }, 1000);
                
                input.value = '';
                messages.scrollTop = messages.scrollHeight;
            }
        }
        
        function handleFile(input) {
            const messages = document.getElementById('messages');
            if (input.files && input.files[0]) {
                const fileName = input.files[0].name;
                messages.innerHTML += '<p><strong>You:</strong> Uploaded file: ' + fileName + '</p>';
                messages.innerHTML += '<p><strong>Margo:</strong> I can see you uploaded "' + fileName + '". File analysis will be available once the full AI system is deployed!</p>';
                messages.scrollTop = messages.scrollHeight;
            }
        }
        
        document.getElementById('messageInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    </script>
</body>
</html>"""
        
        self.wfile.write(html.encode())

    def do_POST(self):
        """Handle POST requests"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        # Simple API response
        response = {
            'response': 'Hello! The AI system is being set up. This confirms the API is working.',
            'timestamp': '2025-08-01'
        }
        
        self.wfile.write(json.dumps(response).encode())
