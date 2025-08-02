from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        html = """<!DOCTYPE html>
<html>
<head>
    <title>🎨 Margo Design Review Agent</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
        .container { background: #f5f5f5; padding: 30px; border-radius: 10px; }
        h1 { color: #663399; text-align: center; }
        .chat { background: white; padding: 20px; border-radius: 5px; margin: 20px 0; min-height: 200px; }
        .input-area { display: flex; gap: 10px; margin-top: 20px; }
        input { flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
        button { padding: 10px 20px; background: #663399; color: white; border: none; border-radius: 5px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎨 Margo Design Review Agent</h1>
        <div class="chat" id="chat">
            <p><strong>Margo:</strong> Hello! I'm working and ready to help with design reviews.</p>
        </div>
        <div class="input-area">
            <input type="text" id="messageInput" placeholder="Type your message...">
            <button onclick="sendMessage()">Send</button>
        </div>
    </div>
    
    <script>
        function sendMessage() {
            const input = document.getElementById('messageInput');
            const chat = document.getElementById('chat');
            const message = input.value.trim();
            
            if (message) {
                chat.innerHTML += '<p><strong>You:</strong> ' + message + '</p>';
                chat.innerHTML += '<p><strong>Margo:</strong> I received: "' + message + '" - The system is working!</p>';
                input.value = '';
                chat.scrollTop = chat.scrollHeight;
            }
        }
        
        document.getElementById('messageInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') sendMessage();
        });
    </script>
</body>
</html>"""
        
        self.wfile.write(html.encode())
        
    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {'status': 'working', 'message': 'API endpoint is functional'}
        self.wfile.write(json.dumps(response).encode())
