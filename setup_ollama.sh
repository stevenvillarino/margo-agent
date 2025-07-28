#!/bin/bash

echo "🚀 Setting up Free Local AI with Ollama"
echo "======================================"

# Check if Ollama is installed
if command -v ollama &> /dev/null; then
    echo "✅ Ollama is already installed"
else
    echo "📥 Installing Ollama..."
    curl -fsSL https://ollama.ai/install.sh | sh
fi

echo ""
echo "🔄 Starting Ollama service..."
ollama serve &
OLLAMA_PID=$!

# Wait a moment for service to start
sleep 5

echo ""
echo "📦 Downloading recommended models..."
echo "   • llama3.1:8b (8GB) - Best general model"
ollama pull llama3.1:8b

echo "   • llava:7b (4GB) - Vision model for image analysis"
ollama pull llava:7b

echo ""
echo "✅ Setup complete!"
echo ""
echo "🎯 Usage:"
echo "   • Ollama is running in the background (PID: $OLLAMA_PID)"
echo "   • Use 'ollama list' to see installed models"
echo "   • Use 'ollama ps' to see running models"
echo "   • Kill service with: kill $OLLAMA_PID"
echo ""
echo "🔧 Your app can now use local AI instead of OpenAI!"
