#!/bin/bash

# 🎯 Docker entrypoint for ElevenLabs Voice Agent Insights

set -e

echo "🚀 Starting ElevenLabs Voice Agent Insights..."

# Start Ollama service in background
echo "🧠 Starting Ollama service..."
ollama serve &

# Wait for Ollama to be ready
echo "⏳ Waiting for Ollama to be ready..."
sleep 5

# Pull the model if not already available
echo "📦 Ensuring qwen2:1.5b model is available..."
ollama pull qwen2:1.5b || echo "Model already available"

# Start the main application
echo "🎯 Starting FastAPI application..."
exec "$@"
