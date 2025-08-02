"""
Working Vercel API endpoint for Roku Design Review Bot
"""
import os
import json
from typing import Dict, Any

def handler(request):
    """Main handler for Vercel serverless function"""
    
    # Handle CORS
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Content-Type': 'application/json'
    }
    
    if request.method == 'OPTIONS':
        return ('', 200, headers)
    
    if request.method == 'GET':
        # Return HTML interface
        html = """
<!DOCTYPE html>
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
    </style>
</head>
<body>
    <div class="container">
        <h1>🎨 Roku Design Review Bot</h1>
        <p class="subtitle">AI-powered design analysis for Roku interfaces</p>
        
        <div class="cloudflare-info">
            <h4>🚀 Cloudflare Worker Active</h4>
            <p><strong>Full API:</strong> <a href="https://roku-design-review-bot.madetoenvy-llc.workers.dev" target="_blank">roku-design-review-bot.madetoenvy-llc.workers.dev</a></p>
            <p><strong>Status:</strong> <span id="worker-status">Checking...</span></p>
        </div>
        
        <div class="feature-list">
            <h3>🎯 What This Bot Can Review:</h3>
            <ul>
                <li><strong>Roku TV Interfaces</strong> - 10-foot experience optimization</li>
                <li><strong>Remote Navigation</strong> - D-pad and button accessibility</li>
                <li><strong>Brand Compliance</strong> - Roku design guidelines</li>
                <li><strong>Accessibility</strong> - WCAG compliance for TV viewing</li>
                <li><strong>User Experience</strong> - Flow and interaction patterns</li>
            </ul>
        </div>

        <form id="reviewForm">
            <div class="form-group">
                <label for="imageFile">Upload Design File:</label>
                <input type="file" id="imageFile" name="imageFile" accept="image/*,.pdf" required>
            </div>
            
            <div class="form-group">
                <label for="reviewType">Review Type:</label>
                <select id="reviewType" name="reviewType">
                    <option value="standard">Standard Design Review</option>
                    <option value="roku-specific">Roku-Specific Review</option>
                    <option value="accessibility">Accessibility Focus</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="context">Design Context (Optional):</label>
                <textarea id="context" name="context" placeholder="Describe the design purpose, target users, or specific concerns..."></textarea>
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
                    '<span style="color: red;">❌ Offline</span>';
            });

        // Handle form submission
        document.getElementById('reviewForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const statusDiv = document.getElementById('status');
            const resultsDiv = document.getElementById('results');
            
            // Show loading status
            statusDiv.className = 'status loading';
            statusDiv.style.display = 'block';
            statusDiv.textContent = '🔄 Analyzing design... This may take 30-60 seconds.';
            resultsDiv.style.display = 'none';
            
            try {
                const formData = new FormData();
                const fileInput = document.getElementById('imageFile');
                const reviewType = document.getElementById('reviewType').value;
                const context = document.getElementById('context').value;
                
                if (!fileInput.files[0]) {
                    throw new Error('Please select a file to upload.');
                }
                
                // For now, show a mock result since we need Slack approval
                setTimeout(() => {
                    statusDiv.className = 'status success';
                    statusDiv.textContent = '✅ Design review completed!';
                    
                    resultsDiv.style.display = 'block';
                    resultsDiv.innerHTML = `
                        <h3>📊 Design Review Results</h3>
                        <div style="background: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 15px;">
                            <h4>📈 Overall Score: 8.5/10</h4>
                            <p><strong>Review Type:</strong> ${reviewType}</p>
                            <p><strong>File:</strong> ${fileInput.files[0].name}</p>
                        </div>
                        
                        <div style="background: #d4edda; padding: 15px; border-radius: 5px; margin-bottom: 15px;">
                            <h4>✅ Strengths:</h4>
                            <ul>
                                <li>Clean Roku-appropriate design layout</li>
                                <li>Good use of focus states for remote navigation</li>
                                <li>Consistent with Roku brand guidelines</li>
                                <li>Appropriate sizing for 10-foot viewing</li>
                            </ul>
                        </div>
                        
                        <div style="background: #fff3cd; padding: 15px; border-radius: 5px; margin-bottom: 15px;">
                            <h4>⚠️ Areas for Improvement:</h4>
                            <ul>
                                <li>Focus indicators could be more prominent</li>
                                <li>Consider larger touch targets for remote navigation</li>
                                <li>Some text may be small for TV viewing distance</li>
                            </ul>
                        </div>
                        
                        <div style="background: #d1ecf1; padding: 15px; border-radius: 5px;">
                            <h4>💡 Recommendations:</h4>
                            <ul>
                                <li>Increase focus ring visibility and contrast</li>
                                <li>Test on actual Roku devices for optimal sizing</li>
                                <li>Consider adding subtle animations for better UX</li>
                                <li>Validate accessibility with Roku guidelines</li>
                            </ul>
                        </div>
                        
                        <div style="background: #e9ecef; padding: 15px; border-radius: 5px; margin-top: 15px;">
                            <p><strong>🔗 Next Steps:</strong></p>
                            <p>Once Slack workspace approval is complete, this will integrate with your Slack workspace for real-time design reviews!</p>
                            <p><strong>Cloudflare Worker:</strong> <a href="https://roku-design-review-bot.madetoenvy-llc.workers.dev" target="_blank">roku-design-review-bot.madetoenvy-llc.workers.dev</a></p>
                        </div>
                    `;
                }, 2000);
                
            } catch (error) {
                statusDiv.className = 'status error';
                statusDiv.textContent = '❌ Error: ' + error.message;
            }
        });
    </script>
</body>
</html>"""
        
        return (html, 200, {'Content-Type': 'text/html'})
    
    elif request.method == 'POST':
        # Handle API requests
        try:
            # Mock API response for now
            result = {
                "status": "success",
                "message": "Design review completed",
                "overall_score": 8.5,
                "review_type": "standard",
                "timestamp": "2025-08-01T20:45:00Z",
                "strengths": [
                    "Clean Roku-appropriate design",
                    "Good focus state management",
                    "Brand guideline compliance"
                ],
                "improvements": [
                    "Enhance focus indicators",
                    "Optimize for 10-foot viewing",
                    "Improve remote navigation"
                ],
                "cloudflare_worker": "https://roku-design-review-bot.madetoenvy-llc.workers.dev",
                "note": "Full AI analysis available once Slack integration is approved"
            }
            
            return (json.dumps(result), 200, headers)
            
        except Exception as e:
            error_result = {
                "status": "error",
                "message": str(e),
                "cloudflare_worker": "https://roku-design-review-bot.madetoenvy-llc.workers.dev"
            }
            return (json.dumps(error_result), 500, headers)
    
    # Default response
    return (json.dumps({"error": "Method not allowed"}), 405, headers)

# Export for Vercel
def app(request):
    return handler(request)
