#!/bin/bash

# 🎯 ElevenLabs Voice Agent Insights Setup Script
# Automated setup for ultra-fast conversation analysis

set -e

echo "🚀 Setting up ElevenLabs Voice Agent Insights..."

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "📦 Installing Ollama..."
    curl -fsSL https://ollama.ai/install.sh | sh
else
    echo "✅ Ollama already installed"
fi

# Pull the optimized model
echo "🧠 Downloading qwen2:1.5b model (934MB)..."
ollama pull qwen2:1.5b

# Set up environment
if [ ! -f .env ]; then
    echo "⚙️ Setting up environment variables..."
    cp .env.example .env
    echo "📝 Please edit .env and add your ELEVENLABS_API_KEY"
else
    echo "✅ Environment file already exists"
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your ELEVENLABS_API_KEY"
echo "2. Start the server: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo "3. Open API docs: http://localhost:8000/docs"
echo "4. Test insights: curl http://localhost:8000/agent/YOUR_AGENT_ID/insights"
echo ""
echo "🎯 Ready to generate actionable business insights in 2-3 seconds!"
