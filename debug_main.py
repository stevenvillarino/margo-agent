"""
Simple FastAPI test to debug the blank page issue
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os

app = FastAPI(title="Design Review API - Debug", version="1.0.0")

# Create directories if they don't exist
os.makedirs("templates", exist_ok=True)

templates = Jinja2Templates(directory="templates")

@app.get("/")
async def root():
    """Simple test endpoint"""
    return {"message": "Server is working!"}

@app.get("/test", response_class=HTMLResponse)
async def test_template(request: Request):
    """Test template rendering"""
    try:
        return templates.TemplateResponse(request, "index.html")
    except Exception as e:
        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html>
        <head><title>Template Test</title></head>
        <body>
            <h1>Template Test</h1>
            <p>Error: {str(e)}</p>
            <p>Looking for template at: {os.path.abspath('templates/index.html')}</p>
            <p>Template exists: {os.path.exists('templates/index.html')}</p>
        </body>
        </html>
        """)

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "debug-api"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
