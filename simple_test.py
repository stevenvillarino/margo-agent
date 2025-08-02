"""
Super simple FastAPI test
"""
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
    <head><title>Test</title></head>
    <body>
        <h1>🎨 Working!</h1>
        <p>This is a test page to verify FastAPI is working.</p>
    </body>
    </html>
    """)

@app.get("/health")
async def health():
    return {"status": "healthy"}
