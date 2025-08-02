"""
Simple Vercel-compatible API endpoint using only standard library
"""
from http.server import BaseHTTPRequestHandler
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
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
            max-width: 800px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .header h1 {
            color: #333;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .subtitle {
            color: #666;
            font-size: 1.2em;
        }
        .chat-container {
            background: #f8f9fa;
            border-radius: 15px;
            padding: 20px;
            margin: 20px 0;
            min-height: 300px;
        }
        .input-area {
            display: flex;
            gap: 10px;
            margin-top: 20px;
        }
        .message-input {
            flex: 1;
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 16px;
        }
        .send-btn {
            padding: 15px 30px;
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-weight: bold;
        }
        .send-btn:hover {
            opacity: 0.9;
        }
        .status {
            text-align: center;
            padding: 20px;
            background: #e3f2fd;
            border-radius: 10px;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎨 Margo Design Review Agent</h1>
            <p class="subtitle">AI-Powered Design Analysis & Feedback</p>
        </div>
        
        <div class="status">
            <h3>✅ Service Online</h3>
            <p>Ready to analyze your designs with AI-powered insights!</p>
        </div>
        
        <div class="chat-container">
            <div id="messages">
                <p><strong>Margo:</strong> Hello! I'm ready to help you review designs. You can upload images or ask questions about UI/UX best practices.</p>
            </div>
        </div>
        
        <div class="input-area">
            <input type="text" class="message-input" id="messageInput" placeholder="Ask me about design principles, upload an image, or request a review...">
            <button class="send-btn" onclick="sendMessage()">Send</button>
        </div>
    </div>

    <script>
        function sendMessage() {
            const input = document.getElementById('messageInput');
            const messages = document.getElementById('messages');
            const message = input.value.trim();
            
            if (message) {
                // Add user message
                messages.innerHTML += '<p><strong>You:</strong> ' + message + '</p>';
                
                // Add bot response
                setTimeout(() => {
                    messages.innerHTML += '<p><strong>Margo:</strong> I received your message: "' + message + '". The full AI system is being deployed. For now, I can provide basic design guidance!</p>';
                    messages.scrollTop = messages.scrollHeight;
                }, 1000);
                
                input.value = '';
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
        
        # Simple response for now
        response = {
            'status': 'success',
            'message': 'API is working! Full AI features coming soon.',
            'timestamp': '2025-08-01'
        }
        
        self.wfile.write(json.dumps(response).encode())
