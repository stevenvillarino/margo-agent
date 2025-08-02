#!/bin/bash

# Knowledge Manager Launcher
# Simple script to launch the knowledge management interface

echo "🧠 Starting Margo Knowledge Manager..."
echo "📍 Interface will open in your browser"
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "✅ Activating virtual environment..."
    source venv/bin/activate
fi

# Install required packages if needed
pip install streamlit requests > /dev/null 2>&1

# Launch the knowledge manager
echo "🚀 Launching knowledge manager interface..."
streamlit run knowledge_manager.py --server.port 8502

echo ""
echo "💡 Add knowledge through the web interface at http://localhost:8502"
echo "🔄 All knowledge automatically syncs to your Cloudflare Worker backend"
