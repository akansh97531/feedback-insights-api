# ElevenLabs Voice Agent Sentiment Analysis

Analyze sentiment and extract insights from ElevenLabs voice agent conversations using Ollama or rule-based fallback.

## 🚀 Quick Start

```bash
# 1. Install Ollama (Required)
curl -fsSL https://ollama.ai/install.sh | sh

# 2. Pull the required model
ollama pull qwen2:7b

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 5. Open API docs
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
- **Ollama Integration**: Uses local LLM (qwen2:7b) for high-quality analysis
- **Rule-based Fallback**: Automatic fallback if Ollama is unavailable
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

**Overview Response:**
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

### Get Individual Conversations
```bash
# Get detailed conversations with sentiment analysis
curl http://localhost:8000/agent/my-agent-123/conversations
```

**Conversations Response:**
```json
{
  "agent_id": "my-agent-123",
  "conversations": [
    {
      "id": "conv_abc123_real_elevenlabs_id",
      "transcript": "Hi, I'm calling about your product. The service has been absolutely amazing! Your team was so helpful...",
      "sentiment": {
        "sentiment_label": "positive",
        "sentiment_score": 0.7,
        "confidence": 0.8
      },
      "created_at": "2024-01-01T10:00:00Z",
      "duration": 180
    },
    {
      "id": "conv_def456_real_elevenlabs_id",
      "transcript": "This is terrible. I've been waiting for hours and nobody can help me. The product doesn't work...",
      "sentiment": {
        "sentiment_label": "negative",
        "sentiment_score": -0.7,
        "confidence": 0.8
      },
      "created_at": "2024-01-01T11:30:00Z",
      "duration": 240
    }
  ]
}
```

### Other Examples
```bash
# Analyze custom text
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Great service!"}'

# Response:
# {
#   "sentiment_label": "positive",
#   "sentiment_score": 0.7,
#   "confidence": 0.8
# }
```

## ⚙️ Prerequisites

### Required: Ollama Setup

Ollama is required for high-quality sentiment analysis:

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull the required model
ollama pull qwen2:7b

# Verify installation
ollama list
```

**Note**: The system will automatically fall back to rule-based analysis if Ollama is unavailable, but Ollama provides significantly better results.

## 📁 Project Structure

```
app/
├── main.py              # FastAPI app
└── services/
    ├── simple_analyzer.py   # Sentiment analysis
    └── elevenlabs.py       # ElevenLabs client
```

That's it! 🎉.
