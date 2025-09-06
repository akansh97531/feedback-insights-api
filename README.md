# ElevenLabs Voice Agent Sentiment Analysis

Analyze sentiment and extract insights from ElevenLabs voice agent conversations using Ollama or rule-based fallback.

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 3. Open API docs
open http://localhost:8000/docs
```

## 🎯 Main Feature

**Get comprehensive sentiment analysis for any ElevenLabs voice agent:**

```bash
curl http://localhost:8000/agent/YOUR_AGENT_ID/overview
```

## 📊 API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | API info |
| `GET /health` | Health check |
| `GET /agent/{agent_id}/overview` | **Complete sentiment overview with insights** |
| `GET /agent/{agent_id}/conversations` | Individual conversations with sentiment |
| `POST /analyze` | Analyze custom text sentiment |

## 🔧 Features

- **Agent-Specific Analysis**: Pass any ElevenLabs voice agent ID
- **Key Insights**: Automatically extracts what customers love vs areas for improvement
- **Real ElevenLabs API**: Connects to live data (with mock fallback)
- **Ollama Integration**: Uses local LLM (qwen2:7b) when available
- **Rule-based Fallback**: Works without Ollama
- **No Database**: Simple setup, no external dependencies

## 🎮 Service Management

### Start Service
```bash
# Development mode (auto-reload)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Stop Service
```bash
# Kill by process name
pkill -f uvicorn

# Or use Ctrl+C in the terminal where it's running
```

### Check if Running
```bash
# Check if port 8000 is in use
lsof -ti:8000

# Test health endpoint
curl http://localhost:8000/health
```

## 🧪 Test

```bash
# Test sentiment analysis
python test_simple.py

# Fetch and analyze conversations
python fetch_and_analyze.py
```

## 📝 Example Usage

### Get Agent Overview (Main Feature)
```bash
# Replace 'my-agent-123' with your actual ElevenLabs agent ID
curl http://localhost:8000/agent/my-agent-123/overview
```

**Response:**
```json
{
  "agent_id": "my-agent-123",
  "total_conversations": 25,
  "overall_sentiment": {
    "average_score": 0.234,
    "classification": "positive"
  },
  "sentiment_breakdown": {
    "counts": {"positive": 15, "negative": 5, "neutral": 5},
    "percentages": {"positive": 60.0, "negative": 20.0, "neutral": 20.0}
  },
  "key_insights": {
    "what_customers_love": [
      "Customers praise the helpful and responsive support team",
      "Fast response times and quick issue resolution are highly valued"
    ],
    "areas_for_improvement": [
      "Product quality issues reported - focus on reliability",
      "Slow response times causing customer frustration"
    ]
  }
}
```

### Other Examples
```bash
# Analyze custom text
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Great service!"}'

# Get individual conversations
curl http://localhost:8000/agent/my-agent-123/conversations
```

## ⚙️ Optional: Ollama Setup

For better analysis, install Ollama:

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull model
ollama pull qwen2:7b
```

## 📁 Project Structure

```
app/
├── main.py              # FastAPI app
└── services/
    ├── simple_analyzer.py   # Sentiment analysis
    └── elevenlabs.py       # ElevenLabs client
```

That's it! 🎉.
