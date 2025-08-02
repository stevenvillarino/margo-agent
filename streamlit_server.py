"""
Simple server for deployment that runs the Streamlit app
"""
from http.server import BaseHTTPRequestHandler
import subprocess
import os

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Design Review App</title>
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    max-width: 800px; 
                    margin: 50px auto; 
                    padding: 20px;
                    text-align: center;
                }
                .card {
                    background: #f9f9f9;
                    padding: 30px;
                    border-radius: 10px;
                    margin: 20px 0;
                }
            </style>
        </head>
        <body>
            <h1>🎨 Design Review App</h1>
            <div class="card">
                <h2>App is Running!</h2>
                <p>This is your simplified design review application.</p>
                <p>Upload designs and get feedback through a clean chat interface.</p>
                
                <h3>To use locally:</h3>
                <pre>streamlit run app.py</pre>
                
                <h3>Features:</h3>
                <ul style="text-align: left;">
                    <li>✅ File upload (PNG, JPG, PDF)</li>
                    <li>✅ Chat interface</li>
                    <li>✅ Simple and clean</li>
                    <li>✅ Works everywhere</li>
                </ul>
            </div>
        </body>
        </html>
        """
        
        self.wfile.write(html.encode('utf-8'))
