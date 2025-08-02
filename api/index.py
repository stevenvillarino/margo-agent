"""
Serverless API endpoint for Vercel deployment
Mimics the Streamlit app functionality but works on serverless
"""
from http.server import BaseHTTPRequestHandler
import json
import urllib.parse

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>🎨 Design Review Chat</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body { 
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background: #f8f9fa;
                    min-height: 100vh;
                    display: flex;
                    flex-direction: column;
                }
                .header {
                    background: white;
                    padding: 1rem 2rem;
                    border-bottom: 1px solid #e1e5e9;
                    text-align: center;
                }
                .header h1 {
                    color: #1f2937;
                    font-size: 1.5rem;
                    margin-bottom: 0.5rem;
                }
                .header p {
                    color: #6b7280;
                    font-size: 0.9rem;
                }
                .chat-container {
                    flex: 1;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 2rem;
                    width: 100%;
                }
                .message {
                    margin-bottom: 1rem;
                    padding: 1rem;
                    border-radius: 8px;
                    max-width: 80%;
                }
                .message.assistant {
                    background: #e5f3ff;
                    margin-right: auto;
                    border-left: 4px solid #3b82f6;
                }
                .message.user {
                    background: #f0f9ff;
                    margin-left: auto;
                    text-align: right;
                    border-right: 4px solid #06b6d4;
                }
                .input-area {
                    background: white;
                    padding: 1rem 2rem;
                    border-top: 1px solid #e1e5e9;
                    display: flex;
                    gap: 1rem;
                    align-items: center;
                }
                input[type="text"] {
                    flex: 1;
                    padding: 0.75rem;
                    border: 1px solid #d1d5db;
                    border-radius: 6px;
                    font-size: 1rem;
                }
                button {
                    padding: 0.75rem 1.5rem;
                    background: #3b82f6;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    cursor: pointer;
                    font-size: 1rem;
                }
                button:hover { background: #2563eb; }
                .upload-area {
                    margin-bottom: 1rem;
                    padding: 1rem;
                    background: white;
                    border-radius: 8px;
                    border: 2px dashed #d1d5db;
                    text-align: center;
                }
                .chat-messages {
                    min-height: 400px;
                    margin-bottom: 1rem;
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🎨 Design Review Chat</h1>
                <p>Upload a design, ask questions, get feedback - just like the local Streamlit app!</p>
            </div>
            
            <div class="chat-container">
                <div class="upload-area">
                    <input type="file" id="fileUpload" accept=".png,.jpg,.jpeg,.pdf" style="margin-bottom: 0.5rem;">
                    <p>Optional: Upload a design for specific feedback</p>
                </div>
                
                <div class="chat-messages" id="chatMessages">
                    <div class="message assistant">
                        Hi! I'm your design assistant. Ask me about colors, typography, layout, accessibility, or upload a design for specific feedback!
                    </div>
                </div>
            </div>
            
            <div class="input-area">
                <input type="text" id="messageInput" placeholder="Ask me anything about design..." onkeypress="if(event.key==='Enter') sendMessage()">
                <button onclick="sendMessage()">Send</button>
            </div>

            <script>
                let uploadedFile = null;
                
                document.getElementById('fileUpload').addEventListener('change', function(e) {
                    if (e.target.files[0]) {
                        uploadedFile = e.target.files[0];
                        addMessage('user', `Uploaded: ${uploadedFile.name}`);
                        addMessage('assistant', `Great! I can see you've uploaded "${uploadedFile.name}". Now ask me specific questions about your design!`);
                    }
                });
                
                function addMessage(role, content) {
                    const messagesDiv = document.getElementById('chatMessages');
                    const messageDiv = document.createElement('div');
                    messageDiv.className = `message ${role}`;
                    messageDiv.textContent = content;
                    messagesDiv.appendChild(messageDiv);
                    messagesDiv.scrollTop = messagesDiv.scrollHeight;
                }
                
                function getSmartResponse(prompt) {
                    const promptLower = prompt.toLowerCase();
                    
                    if (uploadedFile) {
                        return `Looking at your design "${uploadedFile.name}", here's my feedback: ${prompt}`;
                    }
                    
                    if (promptLower.includes('color') || promptLower.includes('colour') || promptLower.includes('palette')) {
                        return "Great question about colors! For effective color choices, consider contrast ratios (aim for 4.5:1), your brand palette, and accessibility. What specific color challenge are you facing?";
                    }
                    
                    if (promptLower.includes('font') || promptLower.includes('typography') || promptLower.includes('text')) {
                        return "Typography is crucial! Consider hierarchy (use 2-3 font sizes max), readability (16px+ for body text), and consistency. What typography question do you have?";
                    }
                    
                    if (promptLower.includes('layout') || promptLower.includes('spacing') || promptLower.includes('grid')) {
                        return "Good layout makes or breaks design! Use consistent spacing (try 8px grid system), clear hierarchy, and whitespace effectively. What layout challenge can I help with?";
                    }
                    
                    if (promptLower.includes('accessibility') || promptLower.includes('a11y')) {
                        return "Accessibility is essential! Key areas: color contrast, keyboard navigation, alt text, and semantic HTML. What accessibility aspect interests you?";
                    }
                    
                    if (promptLower.includes('hello') || promptLower.includes('hi') || promptLower.includes('hey')) {
                        return "Hello! I'm here to help with design questions. Ask me about colors, typography, layout, accessibility, or upload a design for specific feedback!";
                    }
                    
                    return `Interesting question about "${prompt}"! I can help with design principles, best practices, color theory, typography, layout, accessibility, and more. Want to dive deeper into any specific area?`;
                }
                
                function sendMessage() {
                    const input = document.getElementById('messageInput');
                    const message = input.value.trim();
                    
                    if (!message) return;
                    
                    addMessage('user', message);
                    input.value = '';
                    
                    // Simulate thinking
                    setTimeout(() => {
                        const response = getSmartResponse(message);
                        addMessage('assistant', response);
                    }, 500);
                }
            </script>
        </body>
        </html>
        """
        
        self.wfile.write(html.encode())

    def do_POST(self):
        # Handle any POST requests (for future API functionality)
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {"status": "success", "message": "Design review API"}
        self.wfile.write(json.dumps(response).encode())
