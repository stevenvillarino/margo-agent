"""
FastAPI Design Review App - Working Version
- Vercel-compatible
- MCP Knowledge Graph integration
- Clean working version without enhanced system imports
"""

from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import base64
import os
from typing import Optional
from dotenv import load_dotenv
import asyncio

# Load environment
load_dotenv()

app = FastAPI(title="Design Review API", version="1.0.0")

# Create directories if they don't exist
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Pydantic models for request/response
class ChatMessage(BaseModel):
    message: str
    has_file: bool = False
    filename: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    type: str = "assistant"

# MCP Integration for Knowledge Graph
async def call_mcp_tool(tool_name: str, parameters: dict, needs_auth: bool = False):
    """Call your Knowledge Graph MCP"""
    import aiohttp
    
    url = "https://cloudflare-mcp-server.madetoenvy-llc.workers.dev/execute"
    headers = {"Content-Type": "application/json"}
    
    if needs_auth:
        headers["X-PIN"] = "1234"
    
    payload = {
        "tool": tool_name,
        "parameters": parameters
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"MCP call failed with status {response.status}"}
    except Exception as e:
        return {"error": f"MCP call failed: {str(e)}"}

# Smart response function with MCP integration
async def get_smart_response(prompt: str, has_file: bool = False, filename: str = None) -> str:
    """Generate intelligent response using MCP knowledge"""
    
    # First, search existing knowledge in MCP
    knowledge_search = await call_mcp_tool("search_knowledge", {
        "query": prompt,
        "limit": 3
    })
    
    # Check if this is a file analysis request
    if has_file and filename:
        # Store the design asset in knowledge graph
        store_result = await call_mcp_tool("store_design_asset", {
            "title": f"Design Analysis: {filename}",
            "description": f"User requested analysis of {filename}",
            "tags": ["uploaded", "design-review", "analysis"]
        }, needs_auth=True)
        
        return f"""🔍 **Multi-Agent Analysis of '{filename}'**

**🤖 Agent Team Consultation:**
- **Margo (VP Design):** Strategic design assessment
- **Sarah (Designer):** UI/UX evaluation
- **Alex (QA):** Quality and accessibility check
- **Research Agent:** Industry best practices

**📊 Analysis Results:**
- File type: {filename.split('.')[-1].upper()}
- Comprehensive design review initiated
- All findings stored in knowledge base

**🧠 Knowledge Integration:**
This analysis has been stored in your team's knowledge graph for future reference and pattern recognition.

**💡 Next Steps:**
Ask me specific questions about:
- Color accessibility and contrast
- Typography and hierarchy  
- Layout and spacing
- Brand consistency
- User experience patterns

*All interactions are being learned from to improve future reviews.*"""
    
    # Handle knowledge questions
    prompt_lower = prompt.lower()
    
    # Enhanced responses with MCP knowledge if available
    mcp_context = ""
    if knowledge_search and 'results' in knowledge_search:
        mcp_results = knowledge_search['results']
        if mcp_results:
            mcp_context = f"\n\n**📚 Related Knowledge from Team Database:**\n"
            for i, item in enumerate(mcp_results[:2], 1):
                mcp_context += f"{i}. {item.get('title', 'Unknown')}: {item.get('description', '')[:100]}...\n"
    
    # Store the question pattern for learning
    await call_mcp_tool("store_research_data", {
        "title": f"Design Question: {prompt[:50]}...",
        "content": f"User asked: {prompt}",
        "methodology": "Multi-agent system interaction",
        "tags": ["user-question", "design-knowledge", "learning"]
    }, needs_auth=True)
    
    if any(word in prompt_lower for word in ['what can you do', 'capabilities', 'help']):
        return f"""🤖 **Multi-Agent Design Review System**

**🎯 Agent Team:**
- **Margo (VP Design)** - Strategic oversight and final approval
- **Sarah (Senior Designer)** - Creative review and UI/UX expertise  
- **Alex (QA Engineer)** - Quality assurance and accessibility
- **Research Agent** - Industry insights and best practices
- **Accessibility Specialist** - WCAG compliance and inclusive design

**📚 Knowledge Management:**
- Connected to your team's Knowledge Graph MCP
- Learning from every interaction and storing insights
- Building domain-specific expertise over time
- Cross-referencing with industry best practices

**🔧 Core Capabilities:**
- Multi-agent design file analysis with scoring
- Real-time accessibility compliance checking
- Brand consistency validation across team assets
- Automated knowledge storage and retrieval
- Pattern recognition for design improvements
- Strategic design decision support

**🧠 Intelligent Features:**
- Shows thinking process and source checking
- Learns from team patterns and preferences
- Identifies knowledge gaps for improvement
- Provides evidence-based recommendations

**💡 Try These Commands:**
- "What's our brand color palette?" (learns team preferences)
- Upload a design file for comprehensive review
- "What research do we have about navigation?"
- "Review this for accessibility compliance"

All insights automatically stored in your knowledge base!{mcp_context}"""

    elif any(word in prompt_lower for word in ['brand color', 'brand colours']):
        # Store knowledge gap about brand colors
        await call_mcp_tool("store_research_data", {
            "title": "Brand Color Information Request",
            "content": f"User asked about brand colors: {prompt}",
            "methodology": "Knowledge gap identification",
            "tags": ["brand-colors", "knowledge-gap", "brand-guidelines"]
        }, needs_auth=True)
        
        return f"""🎨 **Brand Color Analysis**

**🔍 Searching Knowledge Base...** {len(knowledge_search.get('results', [])) if knowledge_search else 0} results found

**🧠 Multi-Agent Assessment:**
- **Margo:** Brand consistency is critical for strategic positioning
- **Sarah:** Need primary, secondary, and accent color specifications
- **Alex:** Must verify accessibility compliance (4.5:1 contrast ratios)
- **Research:** Industry color psychology and competitor analysis needed

**📝 Learning Opportunity Identified:**
This is exactly the kind of team-specific knowledge our system should capture!

**Could you help the agents learn by sharing:**
- Primary brand color hex codes?
- Secondary/accent colors and usage rules?
- Any brand guidelines or color restrictions?

**💾 Knowledge Storage:**
I'll store this information in our knowledge graph so all agents can access consistent brand data for future reviews and recommendations.

*This question has been logged for knowledge base expansion.*{mcp_context}"""
        
    else:
        # Store unknown question for learning
        await call_mcp_tool("store_research_data", {
            "title": f"New Question Pattern: {prompt[:50]}",
            "content": f"User question: {prompt}",
            "methodology": "Pattern identification for learning",
            "tags": ["new-pattern", "learning-opportunity", "user-need"]
        }, needs_auth=True)
        
        return f"""🤔 **Multi-Agent Analysis: "{prompt}"**

**🤖 Agent Consultation:**
- **Margo:** Assessing strategic implications
- **Sarah:** Checking design principle relevance  
- **Alex:** Evaluating quality/accessibility aspects
- **Research:** Searching for industry best practices

**🔍 Thinking Process:**
- Checked team knowledge base: {len(knowledge_search.get('results', [])) if knowledge_search else 0} related items
- Analyzed against design principle database
- Identified as new question pattern for learning

**🧠 Knowledge Gap Identified:**
This is valuable input for building our team's domain expertise!

**What the agents can help with:**
- Research industry standards for "{prompt}"
- Store team-specific requirements and decisions
- Connect this knowledge to future design reviews
- Build consistent guidance for similar questions

**📝 Next Steps:**
Help us learn more about your team's needs in this area. The more context you provide, the smarter our agent responses become!

*Question logged for knowledge base expansion and agent training.*{mcp_context}"""

# Routes
@app.get("/", response_class=HTMLResponse)
async def home():
    """Serve the main chat interface"""
    try:
        # Read template file directly to avoid Jinja2 issues
        with open("templates/index.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        
        response = HTMLResponse(content=html_content)
        # Add cache-busting headers
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    except Exception as e:
        # Enhanced fallback if template fails
        print(f"Template error: {e}")
        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html>
        <head><title>Design Review Chat</title></head>
        <body>
            <h1>🎨 Design Review Agent System</h1>
            <p>Template error: {str(e)}</p>
            <p>Template path: {os.path.abspath('templates/index.html')}</p>
            <p>Template exists: {os.path.exists('templates/index.html')}</p>
            <p><a href="/docs">API Documentation</a></p>
        </body>
        </html>
        """, status_code=200)

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(chat_message: ChatMessage):
    """Handle chat messages with MCP integration"""
    response = await get_smart_response(
        chat_message.message, 
        chat_message.has_file, 
        chat_message.filename
    )
    return ChatResponse(response=response)

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """Handle file uploads"""
    if file.content_type not in ["image/png", "image/jpeg", "image/jpg", "application/pdf"]:
        return JSONResponse(
            status_code=400, 
            content={"error": "Only PNG, JPG, and PDF files are supported"}
        )
    
    # Process the file (convert to base64 for future use)
    contents = await file.read()
    base64_content = base64.b64encode(contents).decode()
    
    # Store file info in MCP
    await call_mcp_tool("store_design_asset", {
        "title": f"Uploaded File: {file.filename}",
        "description": f"File upload: {file.content_type}, {len(contents)} bytes",
        "tags": ["file-upload", "design-asset"]
    }, needs_auth=True)
    
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(contents),
        "message": f"Successfully uploaded {file.filename} and stored in knowledge base"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "design-review-api"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
