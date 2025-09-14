# 🎯 Professional Network Matching Engine MVP

An AI-powered professional networking platform that uses Cohere's state-of-the-art language models to provide intelligent connection recommendations based on natural language queries.

## 🗂️ Project Structure

- `app/main.py`: Main FastAPI application with networking endpoints
- `app/services/network_matching_engine.py`: Core matching engine orchestrating all components
- `app/services/cohere_service.py`: Cohere API integration for embeddings and query processing
- `app/services/similarity_engine.py`: Multi-metric similarity scoring system
- `app/services/synthetic_data_generator.py`: Generates realistic professional network data
- `app/services/mock_graph_db.py`: In-memory graph database using NetworkX
- `test_networking_engine.py`: Comprehensive test script with sample queries

## ✨ Key Features

- **🧠 Natural Language Processing**: Query like "Find AI engineers at Google" using Cohere's language models
- **📊 Multi-Metric Similarity**: Combines semantic similarity, relationship strength, mutual connections, company overlap, and education matching
- **📧 Email Generation**: Automated introduction email drafts using Cohere's chat models
- **🔗 Graph Analysis**: Connection path finding and mutual connection discovery
- **⚡ Fast Embeddings**: Cached Cohere embed-v4.0 vectors for semantic matching

## 🚀 Quick Start

### Local Development

#### 1. Installation dependencies
pip install -r requirements.txt

#### 2. Set up Cohere API key in .env
cp .env.example .env
# Add this line to your .env file:
# COHERE_API_KEY=your_cohere_api_key_here

#### 3. Start the server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

#### 4. In a new terminal, run the test script
python test_networking_engine.py

### Railway Deployment

#### 1. Prerequisites
- Railway account: [railway.app](https://railway.app)
- GitHub repository with your code
- Cohere API key

#### 2. Deploy to Railway
1. **Connect Repository**: Link your GitHub repo to Railway
2. **Set Environment Variables**:
   ```
   COHERE_API_KEY=your_cohere_api_key_here
   PORT=8000
   ENVIRONMENT=production
   ```
3. **Deploy**: Railway will automatically detect the configuration and deploy

#### 3. Railway Configuration Files
- `railway.json`: Railway deployment configuration
- `Procfile`: Process definition for web server
- `.env.railway`: Environment variables template

#### 4. Access Your API
- Railway will provide a public URL (e.g., `https://your-app.railway.app`)
- Health check: `GET /health`
- API documentation: `GET /docs`

# 5. For a quick demo (faster):
python test_networking_engine.py quick

# 6. Access the API docs at:
# http://localhost:8000/docs
```

## 🎮 How It Works

### 1. Initialize the Network
```bash
curl -X POST "http://localhost:8000/initialize" \
  -H "Content-Type: application/json" \
  -d '{"num_profiles": 50}'
```

### 2. Find Professional Connections
```bash
curl -X POST "http://localhost:8000/find-connections" \
  -H "Content-Type: application/json" \
  -d '{
    "requester_id": "user-id-here",
    "query": "Find AI engineers who have worked at Google or DeepMind",
    "max_results": 5
  }'
```

### 3. Generate Introduction Email
```bash
curl -X POST "http://localhost:8000/generate-introduction" \
  -H "Content-Type: application/json" \
  -d '{
    "requester_id": "user-id-here",
    "target_id": "target-user-id",
    "context": "collaboration on AI research projects"
  }'
```

## 🎯 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/initialize` | POST | Initialize network with synthetic professional data |
| `/find-connections` | POST | Find networking matches using natural language queries |
| `/generate-introduction` | POST | Generate personalized introduction emails |
| `/network-stats` | GET | Get network statistics and insights |
| `/profiles` | GET | List professional profiles with filtering |
| `/health` | GET | Health check and system status |

## 🧪 Example Queries

The system understands natural language networking queries:

- **"Find AI engineers who have worked at Google or DeepMind"**
- **"Connect me to senior product managers with startup experience"** 
- **"Looking for data scientists in healthcare or biotech"**
- **"Find software engineers with Python and machine learning skills"**
- **"Connect me to VPs or directors in technology companies"**

## 🏗️ Technical Architecture

### Multi-Metric Similarity Scoring
- **Semantic Similarity (25%)**: Cohere embed-v4.0 cosine similarity
- **Relationship Strength (20%)**: Email interaction frequency and recency
- **Mutual Connections (15%)**: LinkedIn network overlap
- **Company Overlap (15%)**: Current and past company matches
- **Education Similarity (10%)**: University and degree matching
- **Query Relevance (15%)**: Structured criteria matching

### Cohere API Integration
- **embed-v4.0**: 1536-dimensional semantic embeddings
- **command-r-plus-08-2024**: Natural language query parsing and email generation
- **Caching**: Embedding cache to minimize API calls
- **Batch Processing**: Efficient bulk embedding generation

## 📊 Sample Output

```json
{
  "query": "Find AI engineers at Google",
  "results": [
    {
      "rank": 1,
      "profile": {
        "name": "Sarah Chen",
        "job_title": "AI Research Engineer",
        "company": "Google",
        "bio": "Experienced engineer passionate about transformer architectures..."
      },
      "match_score": 0.847,
      "explanation": "Excellent match for your specific criteria • Strong professional profile alignment • Shared LinkedIn connections",
      "mutual_connections": [
        {"name": "Alex Kim", "job_title": "ML Engineer", "company": "DeepMind"}
      ]
    }
  ],
  "metadata": {
    "processing_time_seconds": 2.3,
    "total_candidates_evaluated": 49
  }
}
```
