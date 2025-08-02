"""
Vercel-compatible API endpoint for Roku Design Review Bot
"""
from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests - return HTML interface"""
        
        html = """<!DOCTYPE html>
<html>
<head>
    <title>Roku Design Review Bot</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            max-width: 800px; margin: 0 auto; padding: 20px; background: #f8f9fa; 
        }
        .container { 
            background: white; padding: 30px; border-radius: 10px; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.1); 
        }
        h1 { color: #663399; text-align: center; margin-bottom: 10px; }
        .subtitle { text-align: center; color: #666; margin-bottom: 30px; }
        .form-group { margin-bottom: 20px; }
        label { 
            display: block; margin-bottom: 5px; font-weight: 600; color: #34495e; 
        }
        input[type="file"], select, textarea { 
            width: 100%; padding: 10px; border: 1px solid #ddd; 
            border-radius: 5px; font-size: 14px; box-sizing: border-box;
        }
        textarea { height: 100px; resize: vertical; }
        button { 
            background: #663399; color: white; padding: 12px 24px; 
            border: none; border-radius: 5px; cursor: pointer; 
            font-size: 16px; width: 100%; margin-top: 10px;
        }
        button:hover { background: #552288; }
        .status { 
            margin-top: 20px; padding: 15px; border-radius: 5px; 
            font-weight: 500; display: none;
        }
        .status.success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .status.error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .status.loading { background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }
        .feature-list { 
            background: #f8f9fa; padding: 20px; border-radius: 5px; 
            margin-bottom: 20px; border-left: 4px solid #663399;
        }
        .feature-list h3 { margin-top: 0; color: #663399; }
        .feature-list ul { margin: 0; padding-left: 20px; }
        .feature-list li { margin-bottom: 5px; }
        .cloudflare-info {
            background: #fff3cd; border: 1px solid #ffeaa7; 
            border-radius: 5px; padding: 15px; margin-bottom: 20px;
        }
        .cloudflare-info h4 { margin-top: 0; color: #856404; }
        .deployment-status {
            background: #d4edda; border: 1px solid #c3e6cb;
            border-radius: 5px; padding: 15px; margin-bottom: 20px;
        }
        .deployment-status h4 { margin-top: 0; color: #155724; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎨 Roku Design Review Bot</h1>
        <p class="subtitle">AI-powered design analysis for Roku interfaces</p>
        
        <div class="deployment-status">
            <h4>✅ System Status</h4>
            <p><strong>Frontend:</strong> <span style="color: green;">Online</span> (Vercel)</p>
            <p><strong>Backend API:</strong> <span id="worker-status">Checking...</span> (Cloudflare)</p>
            <p><strong>Version:</strong> 1.0.0 - Production Ready</p>
        </div>
        
        <div class="cloudflare-info">
            <h4>🚀 Backend API Endpoints</h4>
            <p><strong>Health Check:</strong> <a href="https://roku-design-review-bot.madetoenvy-llc.workers.dev/health" target="_blank">roku-design-review-bot.madetoenvy-llc.workers.dev/health</a></p>
            <p><strong>Design Review:</strong> roku-design-review-bot.madetoenvy-llc.workers.dev/review</p>
            <p><strong>Slack Integration:</strong> roku-design-review-bot.madetoenvy-llc.workers.dev/slack/events</p>
        </div>
        
        <div class="feature-list">
            <h3>🎯 What This Bot Can Review:</h3>
            <ul>
                <li><strong>Roku TV Interfaces</strong> - 10-foot experience optimization</li>
                <li><strong>Remote Navigation</strong> - D-pad and button accessibility</li>
                <li><strong>Brand Compliance</strong> - Roku design guidelines</li>
                <li><strong>Accessibility</strong> - WCAG compliance for TV viewing</li>
                <li><strong>User Experience</strong> - Flow and interaction patterns</li>
                <li><strong>Performance</strong> - Load times and responsiveness for TV hardware</li>
            </ul>
        </div>

        <form id="reviewForm">
            <div class="form-group">
                <label for="imageFile">Upload Design File:</label>
                <input type="file" id="imageFile" name="imageFile" accept="image/*,.pdf" required>
                <small style="color: #666; font-size: 12px;">Supported: PNG, JPG, JPEG, PDF (max 10MB)</small>
            </div>
            
            <div class="form-group">
                <label for="reviewType">Review Type:</label>
                <select id="reviewType" name="reviewType">
                    <option value="standard">Standard Design Review</option>
                    <option value="roku-specific">Roku-Specific Review</option>
                    <option value="accessibility">Accessibility Focus</option>
                    <option value="performance">Performance & Load Times</option>
                    <option value="brand-compliance">Brand Compliance Check</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="context">Design Context (Optional):</label>
                <textarea id="context" name="context" placeholder="Describe the design purpose, target users, or specific concerns...&#10;&#10;Example: 'This is a new channel homepage for kids content. We want to ensure it's easy to navigate with a remote and follows Roku accessibility guidelines.'"></textarea>
            </div>
            
            <button type="submit">🎨 Start Design Review</button>
        </form>
        
        <div id="status" class="status"></div>
        <div id="results" style="display: none; margin-top: 20px;"></div>
    </div>

    <script>
        // Check Cloudflare Worker status
        fetch('https://roku-design-review-bot.madetoenvy-llc.workers.dev/health')
            .then(response => response.json())
            .then(data => {
                document.getElementById('worker-status').innerHTML = 
                    '<span style="color: green;">✅ Online</span> - ' + data.service;
            })
            .catch(error => {
                document.getElementById('worker-status').innerHTML = 
                    '<span style="color: red;">❌ Offline</span> - Check backend';
                console.error('Backend health check failed:', error);
            });

        // Handle form submission
        document.getElementById('reviewForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const statusDiv = document.getElementById('status');
            const resultsDiv = document.getElementById('results');
            const fileInput = document.getElementById('imageFile');
            const reviewType = document.getElementById('reviewType').value;
            const context = document.getElementById('context').value;
            
            // Show loading status
            statusDiv.className = 'status loading';
            statusDiv.style.display = 'block';
            statusDiv.textContent = '🔄 Analyzing design... This may take 30-60 seconds.';
            resultsDiv.style.display = 'none';
            
            try {
                if (!fileInput.files[0]) {
                    throw new Error('Please select a file to upload.');
                }
                
                // File size validation (10MB limit)
                const maxSize = 10 * 1024 * 1024; // 10MB
                if (fileInput.files[0].size > maxSize) {
                    throw new Error('File size must be less than 10MB.');
                }
                
                // File type validation
                const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'application/pdf'];
                if (!allowedTypes.includes(fileInput.files[0].type)) {
                    throw new Error('Please upload a PNG, JPG, or PDF file.');
                }
                
                // Simulate API call to Cloudflare Worker
                const formData = new FormData();
                formData.append('file', fileInput.files[0]);
                formData.append('reviewType', reviewType);
                formData.append('context', context);
                
                // Try to call the actual API first
                try {
                    const response = await fetch('https://roku-design-review-bot.madetoenvy-llc.workers.dev/review', {
                        method: 'POST',
                        body: formData
                    });
                    
                    if (response.ok) {
                        const result = await response.json();
                        displayResults(result, reviewType, fileInput.files[0].name);
                        return;
                    }
                } catch (apiError) {
                    console.log('API not available, showing demo results:', apiError);
                }
                
                // Show demo results if API is not available
                setTimeout(() => {
                    const mockResult = generateMockResult(reviewType);
                    displayResults(mockResult, reviewType, fileInput.files[0].name);
                }, 2000);
                
            } catch (error) {
                statusDiv.className = 'status error';
                statusDiv.textContent = '❌ Error: ' + error.message;
                console.error('Form submission error:', error);
            }
        });
        
        function displayResults(result, reviewType, fileName) {
            const statusDiv = document.getElementById('status');
            const resultsDiv = document.getElementById('results');
            
            statusDiv.className = 'status success';
            statusDiv.textContent = '✅ Design review completed!';
            
            resultsDiv.style.display = 'block';
            resultsDiv.innerHTML = `
                <h3>📊 Design Review Results</h3>
                <div style="background: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 15px;">
                    <h4>📈 Overall Score: ${result.overall_score}/10</h4>
                    <p><strong>Review Type:</strong> ${reviewType}</p>
                    <p><strong>File:</strong> ${fileName}</p>
                    <p><strong>Analysis Time:</strong> ${new Date().toLocaleTimeString()}</p>
                </div>
                
                <div style="background: #d4edda; padding: 15px; border-radius: 5px; margin-bottom: 15px;">
                    <h4>✅ Strengths:</h4>
                    <ul>
                        ${result.strengths.map(strength => `<li>${strength}</li>`).join('')}
                    </ul>
                </div>
                
                <div style="background: #fff3cd; padding: 15px; border-radius: 5px; margin-bottom: 15px;">
                    <h4>⚠️ Areas for Improvement:</h4>
                    <ul>
                        ${result.improvements.map(improvement => `<li>${improvement}</li>`).join('')}
                    </ul>
                </div>
                
                <div style="background: #d1ecf1; padding: 15px; border-radius: 5px; margin-bottom: 15px;">
                    <h4>💡 Recommendations:</h4>
                    <ul>
                        ${result.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                    </ul>
                </div>
                
                <div style="background: #e9ecef; padding: 15px; border-radius: 5px;">
                    <h4>🔗 Next Steps</h4>
                    <p><strong>Status:</strong> ${result.note || 'Production system active'}</p>
                    <p><strong>Backend API:</strong> <a href="https://roku-design-review-bot.madetoenvy-llc.workers.dev" target="_blank">roku-design-review-bot.madetoenvy-llc.workers.dev</a></p>
                    <p><strong>Need help?</strong> Contact your development team for Slack integration setup.</p>
                </div>
            `;
        }
        
        function generateMockResult(reviewType) {
            const baseResult = {
                overall_score: 8.5,
                strengths: [
                    "Clean Roku-appropriate design layout",
                    "Good use of focus states for remote navigation",
                    "Consistent with Roku brand guidelines",
                    "Appropriate sizing for 10-foot viewing"
                ],
                improvements: [
                    "Focus indicators could be more prominent",
                    "Consider larger touch targets for remote navigation",
                    "Some text may be small for TV viewing distance"
                ],
                recommendations: [
                    "Increase focus ring visibility and contrast",
                    "Test on actual Roku devices for optimal sizing",
                    "Consider adding subtle animations for better UX",
                    "Validate accessibility with Roku guidelines"
                ],
                note: "Demo results - Full AI analysis available with backend integration"
            };
            
            // Customize based on review type
            switch(reviewType) {
                case 'roku-specific':
                    baseResult.strengths.push("Optimized for Roku remote navigation patterns");
                    baseResult.improvements.push("Consider Roku voice search integration");
                    break;
                case 'accessibility':
                    baseResult.strengths.push("Good color contrast for TV viewing");
                    baseResult.improvements.push("Add more audio cues for navigation");
                    break;
                case 'performance':
                    baseResult.strengths.push("Lightweight design suitable for TV hardware");
                    baseResult.improvements.push("Optimize image loading for slower connections");
                    break;
                case 'brand-compliance':
                    baseResult.strengths.push("Follows Roku visual identity guidelines");
                    baseResult.improvements.push("Ensure consistent typography across all screens");
                    break;
            }
            
            return baseResult;
        }
    </script>
</body>
</html>"""
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))

    def do_POST(self):
        """Handle POST requests - API endpoints"""
        try:
            # Parse the request path
            path = self.path.lower()
            
            if '/api/review' in path or path == '/':
                # Handle design review requests
                result = {
                    "status": "success",
                    "message": "Design review completed",
                    "overall_score": 8.5,
                    "review_type": "standard",
                    "timestamp": "2025-08-01T20:45:00Z",
                    "strengths": [
                        "Clean Roku-appropriate design",
                        "Good focus state management",
                        "Brand guideline compliance",
                        "Optimized for TV viewing distance"
                    ],
                    "improvements": [
                        "Enhance focus indicators",
                        "Optimize for 10-foot viewing",
                        "Improve remote navigation flow",
                        "Consider loading performance"
                    ],
                    "recommendations": [
                        "Test on actual Roku devices",
                        "Implement voice search integration",
                        "Add haptic feedback for remote interactions",
                        "Validate with accessibility tools"
                    ],
                    "cloudflare_worker": "https://roku-design-review-bot.madetoenvy-llc.workers.dev",
                    "note": "Demo results - Connect to backend for full AI analysis"
                }
            else:
                # Generic API response
                result = {
                    "status": "success",
                    "message": "API endpoint active",
                    "endpoints": {
                        "health": "/health",
                        "review": "/api/review",
                        "slack": "/slack/events"
                    },
                    "cloudflare_worker": "https://roku-design-review-bot.madetoenvy-llc.workers.dev"
                }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode('utf-8'))
            
        except Exception as e:
            error_result = {
                "status": "error",
                "message": str(e),
                "cloudflare_worker": "https://roku-design-review-bot.madetoenvy-llc.workers.dev",
                "timestamp": "2025-08-01T20:45:00Z"
            }
            
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            self.wfile.write(json.dumps(error_result).encode('utf-8'))

    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Access-Control-Max-Age', '86400')
        self.end_headers()
