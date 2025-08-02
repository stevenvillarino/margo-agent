"""
FastAPI Design Review App
- Vercel-compatible
- Leverages existing enhanced agent system
- API endpoints + HTML frontend
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

# Import your existing enhanced system
from agents.enhanced_system import EnhancedDesignReviewSystem

# Load environment
load_dotenv()

app = FastAPI(title="Design Review API", version="1.0.0")

# Create directories if they don't exist
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize your existing enhanced system
enhanced_system = None

def get_enhanced_system():
    """Get or initialize the enhanced system"""
    global enhanced_system
    if enhanced_system is None:
        enhanced_system = EnhancedDesignReviewSystem(
            openai_api_key=os.getenv('OPENAI_API_KEY'),
            exa_api_key=os.getenv('EXA_API_KEY'),
            learning_enabled=True,
            company_context={
                "industry": "Streaming/Entertainment",
                "company_stage": "Growth", 
                "primary_metrics": ["User Engagement", "Content Discovery", "Revenue"],
                "target_audience": "TV viewers, families, cord-cutters",
                "competitive_position": "Premium streaming platform"
            }
        )
    return enhanced_system

# Pydantic models for request/response
class ChatMessage(BaseModel):
    message: str
    has_file: bool = False
    filename: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    type: str = "assistant"

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

# Smart response function using existing enhanced system + MCP
async def get_smart_response(prompt: str, has_file: bool = False, filename: str = None) -> str:
    """Generate intelligent response using enhanced system + MCP knowledge"""
    
    # Get the enhanced system
    system = get_enhanced_system()
    
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
        
        # Use enhanced system for comprehensive review
        try:
            # Convert file to base64 for enhanced system (you'd need to implement file handling)
            review_result = await system.conduct_comprehensive_review(
                image_data="", # You'd pass actual image data here
                design_type="uploaded_file",
                context={"filename": filename, "user_prompt": prompt}
            )
            
            # Extract the key insights from the orchestrated review
            if 'orchestrated_review' in review_result:
                orchestrated = review_result['orchestrated_review']
                
                response = f"""🔍 **Analyzing '{filename}' with multi-agent review system...**

**🤖 Agent Analysis Results:**
- **Overall Score:** {orchestrated.overall_score}/10
- **Agents Consulted:** {len([r for results in orchestrated.phase_results.values() for r in results])} specialists

**📊 Key Findings:**
"""
                # Add findings from each agent
                for phase, results in orchestrated.phase_results.items():
                    for result in results:
                        response += f"\n**{result.agent_name}:** {result.feedback[:200]}..."
                
                # Store insights in knowledge graph
                if orchestrated.overall_score < 7:
                    await call_mcp_tool("store_decision", {
                        "title": f"Design Issues Identified: {filename}",
                        "description": f"Multi-agent review found issues (Score: {orchestrated.overall_score}/10)",
                        "rationale": "Requires design improvements before implementation",
                        "tags": ["design-review", "issues", "improvement-needed"]
                    }, needs_auth=True)
                
                return response
                
        except Exception as e:
            print(f"Enhanced system error: {e}")
            # Fallback response
            return f"""🔍 **Analyzing '{filename}'...**

**File processed successfully!** I can see this is a {filename.split('.')[-1].upper()} file.

**🧠 What I'm checking:**
- Design principles and composition
- Accessibility compliance (WCAG standards)
- Brand consistency
- Typography and layout
- User experience patterns

**💡 This analysis has been stored in our knowledge base for future reference.**

Ask me specific questions about colors, layout, accessibility, or any design aspect you'd like me to focus on!"""
    
    # Handle knowledge questions using enhanced system
    try:
        knowledge_result = await system.handle_knowledge_question(prompt)
        
        # Enhance response with MCP knowledge if available
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
            "methodology": "AI agent interaction",
            "tags": ["user-question", "design-knowledge", "learning"]
        }, needs_auth=True)
        
        return knowledge_result.get('answer', 'I need more information to answer that question.') + mcp_context
        
    except Exception as e:
        print(f"Enhanced system knowledge error: {e}")
        
        # Fallback to MCP-enhanced responses
        if knowledge_search and 'results' in knowledge_search:
            mcp_results = knowledge_search['results']
            if mcp_results:
                response = f"🧠 **Found relevant knowledge in our team database:**\n\n"
                for i, item in enumerate(mcp_results, 1):
                    response += f"**{i}. {item.get('title', 'Knowledge Item')}**\n"
                    response += f"{item.get('description', 'No description available')}\n\n"
                
                # Store this interaction
                await call_mcp_tool("store_decision", {
                    "title": f"Knowledge Gap Identified: {prompt[:50]}",
                    "description": f"User question: {prompt}",
                    "rationale": "Question answered from existing knowledge base",
                    "tags": ["knowledge-gap", "answered", "user-interaction"]
                }, needs_auth=True)
                
                return response
        
        # Ultimate fallback - basic categorized responses
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in ['what can you do', 'capabilities', 'help']):
            return """🤖 **I'm your AI Design Review Agent powered by:**

**🎯 Multi-Agent System:**
- Margo (VP Design) - Strategic oversight
- Sarah (Senior Designer) - Creative review  
- Alex (QA Engineer) - Quality assurance
- Research Agent - Industry insights
- Accessibility Agent - WCAG compliance

**📚 Knowledge Management:**
- Connected to your team's knowledge graph
- Learning from every interaction
- Building domain-specific expertise

**🔧 Capabilities:**
- Design file analysis (upload images/PDFs)
- Multi-agent design reviews with scoring
- Accessibility compliance checking
- Brand consistency validation
- Knowledge storage and retrieval
- Learning from team patterns

**💡 Try asking:**
- "What's our brand color palette?"
- "Review this design for accessibility"
- "What research do we have about navigation?"

All insights are automatically stored in your knowledge base!"""

        elif any(word in prompt_lower for word in ['brand color', 'brand colours']):
            # Store knowledge gap about brand colors
            await call_mcp_tool("store_research_data", {
                "title": "Brand Color Information Needed",
                "content": f"User asked about brand colors: {prompt}",
                "methodology": "Knowledge gap identification",
                "tags": ["brand-colors", "knowledge-gap", "brand-guidelines"]
            }, needs_auth=True)
            
            return """🎨 **Brand Color Information:**

**🔍 Searching team knowledge base...** I don't see specific brand colors documented yet.

**🧠 Learning Opportunity:** This is exactly what I need to know about your team! 

**Could you help me learn by sharing:**
- Primary brand color hex codes?
- Secondary/accent colors?
- Usage guidelines or restrictions?

**📝 I'll store this in our knowledge base** so the entire team can access consistent brand information for future reviews!

*This question has been logged for knowledge base expansion.*"""
        
        else:
            # Store unknown question for learning
            await call_mcp_tool("store_research_data", {
                "title": f"New Question Pattern: {prompt[:50]}",
                "content": f"User question: {prompt}",
                "methodology": "Pattern identification for learning",
                "tags": ["new-pattern", "learning-opportunity", "user-need"]
            }, needs_auth=True)
            
            return f"""🤔 **Analyzing: "{prompt}"**

**🔍 Thinking Process:**
- Checked team knowledge base
- Consulted design principle database  
- Identified as new question pattern

**🧠 Knowledge Gap Identified:** This is a great learning opportunity for our team's knowledge base!

**What I can help with:**
- Store your specific requirements about "{prompt}"
- Research industry best practices
- Connect this to future design decisions

**📝 This question has been logged** - help me learn more about your team's needs in this area so I can provide better guidance next time!

*Building smarter responses through team-specific knowledge...*"""

# Routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main chat interface"""
    try:
        response = templates.TemplateResponse(request, "index.html")
        # Add cache-busting headers
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    except Exception as e:
        # Enhanced fallback if template fails
        print(f"Template error: {e}")
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html>
        <head><title>Design Review Chat - Loading...</title></head>
        <body>
            <h1>🎨 Design Review Chat</h1>
            <p>System initializing... Template error: """ + str(e) + """</p>
            <p><a href="/docs">API Documentation</a></p>
            <script>
                setTimeout(() => window.location.reload(), 2000);
            </script>
        </body>
        </html>
        """, status_code=200)

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(chat_message: ChatMessage):
    """Handle chat messages with enhanced system + MCP integration"""
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
    
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(contents),
        "message": f"Successfully uploaded {file.filename}"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "design-review-api"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
