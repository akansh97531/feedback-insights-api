"""
Ultra-simple FastAPI app for ElevenLabs sentiment analysis.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List
import logging
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from app.services.simple_analyzer import SimpleAnalyzer
from app.services.elevenlabs import ElevenLabsClient
from app.services.insights_generator import ProductInsightsGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="ElevenLabs Sentiment API",
    description="Simple sentiment analysis for ElevenLabs conversations",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
analyzer = SimpleAnalyzer()
client = ElevenLabsClient()
insights_generator = ProductInsightsGenerator()

@app.get("/")
async def root():
    return {"message": "ElevenLabs Sentiment API", "docs": "/docs"}

@app.get("/health")
async def health():
    healthy = await analyzer.health_check()
    return {"status": "healthy" if healthy else "degraded"}

@app.post("/analyze")
async def analyze(data: Dict[str, str]):
    text = data.get("text", "")
    if not text:
        raise HTTPException(400, "Text required")
    return await analyzer.analyze_sentiment(text)

@app.get("/agent/{agent_id}/overview")
async def agent_sentiment_overview(agent_id: str):
    """Get comprehensive sentiment overview for a voice agent."""
    convs = await client.get_agent_conversations(agent_id, limit=100)
    
    if not convs:
        raise HTTPException(404, f"No conversations found for agent {agent_id}")
    
    # Analyze all conversations
    results = []
    sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
    total_score = 0.0
    positive_themes = []
    negative_themes = []
    
    for conv in convs:
        sentiment = await analyzer.analyze_sentiment(conv["transcript"])
        
        # Count sentiments
        sentiment_counts[sentiment["sentiment_label"]] += 1
        total_score += sentiment["sentiment_score"]
        
        # Extract key themes from high-confidence feedback
        if sentiment["sentiment_label"] == "positive" and sentiment["confidence"] > 0.6:
            positive_themes.extend(_extract_themes(conv["transcript"], "positive"))
        elif sentiment["sentiment_label"] == "negative" and sentiment["confidence"] > 0.6:
            negative_themes.extend(_extract_themes(conv["transcript"], "negative"))
        
        # Don't store individual conversations in overview
    
    # Calculate averages and percentages
    total_conversations = len(convs)
    avg_score = total_score / total_conversations if total_conversations > 0 else 0.0
    
    sentiment_percentages = {
        "positive": round((sentiment_counts["positive"] / total_conversations) * 100, 1),
        "negative": round((sentiment_counts["negative"] / total_conversations) * 100, 1),
        "neutral": round((sentiment_counts["neutral"] / total_conversations) * 100, 1)
    }
    
    # Generate key insights
    good_insights = _generate_insights(positive_themes, "positive")
    improvement_areas = _generate_insights(negative_themes, "negative")
    
    return {
        "agent_id": agent_id,
        "total_conversations": total_conversations,
        "overall_sentiment": {
            "average_score": round(avg_score, 3),
            "classification": "positive" if avg_score > 0.1 else "negative" if avg_score < -0.1 else "neutral"
        },
        "sentiment_breakdown": {
            "counts": sentiment_counts,
            "percentages": sentiment_percentages
        },
        "key_insights": {
            "what_customers_love": good_insights,
            "areas_for_improvement": improvement_areas
        }
    }

def _extract_themes(text: str, sentiment_type: str) -> list:
    """Extract key themes from conversation text."""
    if not text or not isinstance(text, str):
        return []
    text_lower = text.lower()
    
    if sentiment_type == "positive":
        themes = []
        if any(word in text_lower for word in ["helpful", "support", "team", "service"]):
            themes.append("customer_support")
        if any(word in text_lower for word in ["quick", "fast", "resolved", "efficient"]):
            themes.append("response_time")
        if any(word in text_lower for word in ["quality", "excellent", "amazing", "fantastic"]):
            themes.append("product_quality")
        if any(word in text_lower for word in ["professional", "knowledgeable", "expert"]):
            themes.append("staff_expertise")
        if any(word in text_lower for word in ["easy", "simple", "straightforward"]):
            themes.append("ease_of_use")
        return themes
    
    else:  # negative
        themes = []
        if any(word in text_lower for word in ["waiting", "slow", "delay", "hours"]):
            themes.append("response_time")
        if any(word in text_lower for word in ["help", "support", "nobody", "unhelpful"]):
            themes.append("customer_support")
        if any(word in text_lower for word in ["broken", "doesn't work", "quality", "terrible"]):
            themes.append("product_quality")
        if any(word in text_lower for word in ["confusing", "difficult", "complicated"]):
            themes.append("ease_of_use")
        if any(word in text_lower for word in ["expensive", "money", "waste", "cost"]):
            themes.append("pricing")
        return themes

def _generate_insights(themes: list, sentiment_type: str) -> list:
    """Generate concise insights from theme analysis."""
    if not themes:
        return []
    
    # Count theme frequency
    theme_counts = {}
    for theme in themes:
        theme_counts[theme] = theme_counts.get(theme, 0) + 1
    
    # Sort by frequency
    sorted_themes = sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)
    
    insights = []
    theme_messages = {
        "customer_support": {
            "positive": "Customers praise the helpful and responsive support team",
            "negative": "Customer support needs improvement - customers report unhelpful interactions"
        },
        "response_time": {
            "positive": "Fast response times and quick issue resolution are highly valued",
            "negative": "Slow response times causing customer frustration - need faster support"
        },
        "product_quality": {
            "positive": "Product quality consistently exceeds customer expectations",
            "negative": "Product quality issues reported - focus on reliability and functionality"
        },
        "staff_expertise": {
            "positive": "Customers appreciate knowledgeable and professional staff",
            "negative": "Staff training needed to improve expertise and professionalism"
        },
        "ease_of_use": {
            "positive": "Simple and intuitive user experience drives satisfaction",
            "negative": "Product complexity causing confusion - simplify user experience"
        },
        "pricing": {
            "positive": "Customers find good value for money",
            "negative": "Pricing concerns - customers question value proposition"
        }
    }
    
    for theme, count in sorted_themes[:3]:  # Top 3 themes
        if theme in theme_messages:
            insights.append(theme_messages[theme][sentiment_type])
    
    return insights

@app.get("/agent/{agent_id}/conversations")
async def get_agent_conversations(agent_id: str, limit: int = 50):
    """Get conversations for a specific agent with sentiment analysis."""
    convs = await client.get_agent_conversations(agent_id, limit)
    results = []
    
    for conv in convs:
        sentiment = await analyzer.analyze_sentiment(conv["transcript"])
        results.append({
            "id": conv["id"],
            "transcript": conv["transcript"][:150] + "..." if len(conv["transcript"]) > 150 else conv["transcript"],
            "sentiment": sentiment,
            "created_at": conv["created_at"],
            "duration": conv.get("duration", 0)
        })
    
    return {"agent_id": agent_id, "conversations": results}

@app.get("/agent/{agent_id}/insights")
async def get_product_insights(agent_id: str):
    """Get comprehensive product insights with P0/P1/P2 prioritization."""
    try:
        # Get real conversations from ElevenLabs
        convs = await client.get_agent_conversations(agent_id, limit=100)
        
        # Process conversations for sentiment analysis
        processed_conversations = []
        for conv in convs:
            sentiment = await analyzer.analyze_sentiment(conv["transcript"])
            processed_conversations.append({
                **conv,
                "sentiment_score": sentiment["sentiment_score"],
                "sentiment_label": sentiment["sentiment_label"],
                "confidence": sentiment["confidence"]
            })
        
        # Generate comprehensive insights
        insights = insights_generator.generate_comprehensive_insights(processed_conversations)
        
        return {
            "agent_id": agent_id,
            "generated_at": "2024-01-15T18:30:00Z",
            "insights": insights
        }
        
    except Exception as e:
        logger.error(f"Error generating insights for agent {agent_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate insights: {str(e)}")

@app.get("/agent/{agent_id}/mock-conversations")
async def get_mock_conversations(agent_id: str):
    """Get mock conversations for testing insights generation."""
    mock_convs = insights_generator.get_mock_conversations()
    
    # Add sentiment analysis to mock conversations
    processed_mock = []
    for conv in mock_convs:
        sentiment = await analyzer.analyze(conv["transcript"])
        processed_mock.append({
            **conv,
            "agent_id": agent_id,
            "sentiment_label": sentiment["sentiment_label"],
            "confidence": sentiment["confidence"]
        })
    
    return {
        "agent_id": agent_id,
        "mock_conversations": processed_mock,
        "total_count": len(processed_mock)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
