from http.server import BaseHTTPRequestHandler
import json
import urllib.parse

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        
        html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chat</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f5f5;
            height: 100vh;
            display: flex;
            flex-direction: column;
        }
        .chat-container {
            flex: 1;
            max-width: 800px;
            margin: 0 auto;
            width: 100%;
            background: white;
            display: flex;
            flex-direction: column;
        }
        .messages {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            background: white;
        }
        .message {
            margin-bottom: 15px;
            padding: 12px 16px;
            border-radius: 8px;
            max-width: 70%;
        }
        .message.user {
            background: #007cba;
            color: white;
            margin-left: auto;
        }
        .message.assistant {
            background: #f1f1f1;
            color: #333;
        }
        .input-area {
            padding: 20px;
            border-top: 1px solid #eee;
            display: flex;
            gap: 10px;
            background: white;
        }
        .message-input {
            flex: 1;
            padding: 12px 16px;
            border: 1px solid #ddd;
            border-radius: 25px;
            font-size: 16px;
            outline: none;
        }
        .message-input:focus {
            border-color: #007cba;
        }
        .send-btn {
            background: #007cba;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 25px;
            cursor: pointer;
            font-weight: 500;
        }
        .send-btn:hover {
            background: #005a8a;
        }
        .send-btn:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="messages" id="messages">
            <div class="message assistant">
                Hello! How can I help you today?
            </div>
        </div>
        <div class="input-area">
            <input type="text" class="message-input" id="messageInput" placeholder="Type your message...">
            <button class="send-btn" id="sendBtn" onclick="sendMessage()">Send</button>
        </div>
    </div>

    <script>
        function addMessage(content, isUser = false) {
            const messages = document.getElementById('messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${isUser ? 'user' : 'assistant'}`;
            messageDiv.textContent = content;
            messages.appendChild(messageDiv);
            messages.scrollTop = messages.scrollHeight;
        }
        
        async function sendMessage() {
            const input = document.getElementById('messageInput');
            const sendBtn = document.getElementById('sendBtn');
            const message = input.value.trim();
            
            if (!message) return;
            
            // Disable input
            input.disabled = true;
            sendBtn.disabled = true;
            sendBtn.textContent = 'Sending...';
            
            // Add user message
            addMessage(message, true);
            input.value = '';
            
            try {
                // Send to API
                const response = await fetch(window.location.pathname, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ message: message })
                });
                
                const data = await response.json();
                
                if (data.error) {
                    addMessage(`Error: ${data.error}`);
                } else {
                    addMessage(data.response || 'I received your message.');
                }
                
            } catch (error) {
                addMessage(`Connection error: ${error.message}`);
            }
            
            // Re-enable input
            input.disabled = false;
            sendBtn.disabled = false;
            sendBtn.textContent = 'Send';
            input.focus();
        }
        
        // Enter key to send
        document.getElementById('messageInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
        
        // Focus input on load
        document.getElementById('messageInput').focus();
    </script>
</body>
</html>"""
        
        self.wfile.write(html.encode('utf-8'))

    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            message = data.get('message', '')
            
            # Simple response
            response = {
                'response': f'I received your message: "{message}". This is a working chat interface. The message was successfully processed.'
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        except Exception as e:
            error_response = {'error': str(e)}
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(error_response).encode('utf-8'))
