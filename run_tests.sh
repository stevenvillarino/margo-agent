#!/bin/bash
# Test runner script for the FastAPI app

echo "🧪 Running Design Review API Tests"
echo "=================================="

# Install dependencies if needed
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Run tests with coverage
echo "🔍 Running tests..."
python -m pytest tests/ -v --tb=short

# Optional: Run the app locally for manual testing
echo ""
echo "🚀 To run the app locally:"
echo "uvicorn main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "🌐 Then visit: http://localhost:8000"
