# 🎯 ElevenLabs Voice Agent Insights & Analytics

Generate actionable business insights from ElevenLabs voice agent conversations using local LLM analysis with **qwen2:1.5b** for ultra-fast inference (2-3 seconds).

## ✨ Key Features

- **🚀 Ultra-Fast Analysis**: 2-3 second inference with qwen2:1.5b (934MB model)
- **🎯 Smart Processing**: Analyzes latest conversation + saves all transcripts
- **📊 Priority Classification**: P0/P1/P2 insights based on business impact
- **💡 Actionable Recommendations**: Specific actions with effort/impact/timeline
- **🔒 Privacy-First**: Local LLM processing, no external API costs
- **📁 Auto-Archive**: All conversations saved to `conversation_transcripts.json`

## 🚀 Quick Start

```bash
# 1. Clone the repository
git clone <repository-url>
cd windsurf-project

# 2. Install Ollama (Required)
curl -fsSL https://ollama.ai/install.sh | sh

# 3. Pull the optimized model (ultra-fast inference)
ollama pull qwen2:1.5b

# 4. Set up environment
cp .env.example .env
# Edit .env and add your ELEVENLABS_API_KEY

# 5. Install Python dependencies
pip install -r requirements.txt

# 6. Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 7. Open API docs
open http://localhost:8000/docs
```

## 🎯 Main Endpoint

**Get comprehensive insights with actionable recommendations:**

```bash
curl http://localhost:8000/agent/YOUR_AGENT_ID/insights
```

**Example Response:**
```json
{
  "agent_id": "agent_123",
  "insights": {
    "priority_insights": {
      "P2": {
        "title": "Usability Issues: Customer frustrated with reporting tools",
        "recommended_actions": [
          {
            "title": "Upgrade to premium plan",
            "description": "Offer upgrade for better reporting capabilities",
            "effort": "High",
            "impact": "Medium",
            "timeline": "1 month"
          }
        ]
      }
    }
  }
}
```

## 📊 API Endpoints

| Endpoint | Description | Response Time |
|----------|-------------|---------------|
| `GET /` | API info with feature overview | Instant |
| `GET /health` | Health check for LLM and services | <1s |
| `GET /agent/{agent_id}/insights` | **🎯 Main endpoint: Business insights + recommendations** | 2-3s |
| `GET /agent/{agent_id}/conversations` | P0/P1/P2 categorized conversations | 1-2s |
| `POST /analyze` | Analyze custom text sentiment | <1s |

## 🏗️ Architecture

- **Frontend**: FastAPI with auto-generated docs
- **LLM Engine**: Ollama + qwen2:1.5b (934MB, ultra-fast)
- **Data Source**: ElevenLabs Voice Agent API
- **Processing**: Latest conversation analysis + full transcript archive
- **Output**: Structured JSON with actionable business insights

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

### 🎯 Get Business Insights (Main Feature)
```bash
# Replace with your actual ElevenLabs agent ID
curl http://localhost:8000/agent/agent_4801k4g17sssf22v5ydh5bgddm63/insights
```

**Insights Response:**
```json
{
  "agent_id": "agent_4801k4g17sssf22v5ydh5bgddm63",
  "insights": {
    "summary": {
      "total_conversations": 26,
      "critical_issues_identified": 3,
      "revenue_at_risk": "$127,000/month"
    },
    "priority_insights": {
      "P0": {
        "title": "Pricing Page Failures Driving User Churn",
        "business_impact": {
          "revenue_at_risk": "$82,000/month",
          "conversion_loss": "65%"
        },
        "recommended_actions": [
          {
            "title": "Emergency pricing page redesign",
            "effort": "High",
            "impact": "Critical",
            "timeline": "2 weeks"
          }
        ]
      }
    }
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

# Pull the optimized model (ultra-fast inference)
ollama pull qwen2:1.5b

# Verify installation
ollama list
```

**Note**: qwen2:1.5b (934MB) provides ultra-fast 1-2 second inference with high-quality actionable insights.

## 📁 Project Structure

```
windsurf-project/
├── app/
│   ├── main.py                    # FastAPI app with insights API
│   └── services/
│       ├── insights_generator.py  # LLM-powered insights generation
│       ├── elevenlabs.py         # ElevenLabs API client
│       └── simple_analyzer.py    # Sentiment analysis utilities
├── .env.example                   # Environment variables template
├── requirements.txt               # Python dependencies
├── conversation_transcripts.json  # Auto-generated transcript archive
└── README.md                     # This file
```

## 🔧 Environment Setup

**Required Environment Variables:**
```bash
# Copy template and edit
cp .env.example .env

# Add your ElevenLabs API key
ELEVENLABS_API_KEY=your_api_key_here
```

## 🚀 Production Deployment

```bash
# Production server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Docker (optional)
docker build -t elevenlabs-insights .
docker run -p 8000:8000 -e ELEVENLABS_API_KEY=your_key elevenlabs-insights
```

## 📊 What Gets Generated

**JSON Response Only** - No file persistence, pure API responses:

1. **P0/P1/P2 Priority Insights** - Business impact classification
2. **Actionable Recommendations** - Specific actions with effort/impact/timeline  
3. **Business Metrics** - Revenue impact, conversion rates, customer satisfaction
4. **Customer Sentiment Analysis** - Key quotes and sentiment scores

## 🎯 Perfect For

- **Product Teams**: Identify critical user experience issues
- **Customer Success**: Understand customer pain points and satisfaction
- **Engineering**: Prioritize bug fixes and feature development
- **Business Intelligence**: Track revenue impact and conversion metrics

That's it! 🎉 Clone, configure, and start generating insights in minutes.
