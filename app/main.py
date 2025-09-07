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

# from app.services.simple_analyzer import SimpleAnalyzer
from app.services.elevenlabs import ElevenLabsClient
# from app.services.insights_generator import ProductInsightsGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="ElevenLabs Voice Agent Insights API",
    description="Simplified API for ElevenLabs voice agent conversations - insights generation disabled",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
# analyzer = SimpleAnalyzer()
client = ElevenLabsClient()
# insights_generator = ProductInsightsGenerator()

@app.get("/")
async def root():
    return {
        "message": "ElevenLabs Voice Agent Insights API",
        "version": "2.0.0",
        "description": "Generate actionable business insights from voice agent conversations",
        "features": [
            "Real ElevenLabs API integration",
            "Conversation retrieval and categorization",
            "P0/P1/P2 conversation classification"
        ],
        "endpoints": {
            "conversations": "/agent/{agent_id}/conversations", 
            "health": "/health",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health():
    # healthy = await analyzer.health_check()
    return {"status": "healthy"}

# @app.post("/analyze")
# async def analyze(data: Dict[str, str]):
#     text = data.get("text", "")
#     if not text:
#         raise HTTPException(400, "Text required")
#     return await analyzer.analyze_sentiment(text)


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
    """Get conversations categorized by P0/P1/P2 business impact."""
    convs = await client.get_agent_conversations(agent_id, limit)
    
    # Categorize conversations by business impact
    p0_conversations = []
    p1_conversations = []
    p2_conversations = []
    
    for conv in convs:
        # Analyze for business impact categories
        transcript_lower = conv["transcript"].lower()
        
        # P0 - Pricing issues (critical revenue impact)
        if any(word in transcript_lower for word in ["pricing", "price", "cost", "expensive", "plan", "tier"]):
            p0_conversations.append({
                "id": conv["id"],
                "transcript": conv["transcript"][:150] + "..." if len(conv["transcript"]) > 150 else conv["transcript"],
                "category": "pricing_issues",
                "priority": "P0",
                "business_impact": "Revenue at risk",
                "created_at": conv["created_at"],
                "duration": conv.get("duration", 0)
            })
        # P1 - Checkout/payment issues (high revenue impact)
        elif any(word in transcript_lower for word in ["checkout", "payment", "purchase", "buy", "card", "billing"]):
            p1_conversations.append({
                "id": conv["id"],
                "transcript": conv["transcript"][:150] + "..." if len(conv["transcript"]) > 150 else conv["transcript"],
                "category": "checkout_issues",
                "priority": "P1", 
                "business_impact": "Conversion loss",
                "created_at": conv["created_at"],
                "duration": conv.get("duration", 0)
            })
        # P2 - Search/usability issues (medium impact)
        else:
            p2_conversations.append({
                "id": conv["id"],
                "transcript": conv["transcript"][:150] + "..." if len(conv["transcript"]) > 150 else conv["transcript"],
                "category": "usability_issues",
                "priority": "P2",
                "business_impact": "User experience",
                "created_at": conv["created_at"],
                "duration": conv.get("duration", 0)
            })
    
    return {
        "agent_id": agent_id,
        "total_conversations": len(convs),
        "priority_breakdown": {
            "P0_critical": {
                "count": len(p0_conversations),
                "conversations": p0_conversations
            },
            "P1_high": {
                "count": len(p1_conversations),
                "conversations": p1_conversations
            },
            "P2_medium": {
                "count": len(p2_conversations),
                "conversations": p2_conversations
            }
        }
    }

# @app.get("/agent/{agent_id}/insights")
# async def get_product_insights(agent_id: str):
#     """
#     Get comprehensive business insights with actionable recommendations.
#     
#     Analyzes the latest ElevenLabs conversation using qwen2:1.5b LLM to generate:
#     - P0/P1/P2 priority classification based on business impact
#     - Specific recommended actions with effort, impact, and timeline
#     - Business metrics and revenue impact analysis
#     - Customer sentiment and key quotes
#     
#     Returns comprehensive insights as JSON response without file persistence
#     """
#     try:
#         # Get latest conversation from ElevenLabs
#         latest_conv = await client.get_latest_conversation(agent_id)
#         
#         # Load existing conversations from transcript file
#         import json
#         existing_conversations = []
#         try:
#             with open("conversation_transcripts.json", "r", encoding="utf-8") as f:
#                 transcript_data = json.load(f)
#                 existing_conversations = transcript_data.get("conversations", [])
#         except FileNotFoundError:
#             pass
#         
#         # Combine latest conversation with existing ones
#         convs = []
#         if latest_conv:
#             convs.append(latest_conv)
#         
#         # Convert existing conversations to the expected format
#         for conv in existing_conversations:
#             convs.append({
#                 "id": conv.get("id", ""),
#                 "agent_id": agent_id,
#                 "transcript": conv.get("transcript", ""),
#                 "created_at": conv.get("created_at", ""),
#                 "duration": conv.get("duration", 0)
#             })
#         
#         # Generate comprehensive insights from combined conversations
#         insights = await insights_generator.generate_comprehensive_insights(convs)
#         
#         return {
#             "agent_id": agent_id,
#             "generated_at": "2024-01-15T18:30:00Z",
#             "insights": insights
#         }
#         
#     except Exception as e:
#         logger.error(f"Error generating insights for agent {agent_id}: {e}")
#         raise HTTPException(status_code=500, detail=f"Failed to generate insights: {str(e)}")

# @app.get("/agent/{agent_id}/mock-conversations")
# async def get_mock_conversations(agent_id: str):
#     """Get mock conversations for testing insights generation."""
#     mock_convs = insights_generator.get_mock_conversations()
#     
#     # Add sentiment analysis to mock conversations
#     processed_mock = []
#     for conv in mock_convs:
#         sentiment = await analyzer.analyze_sentiment(conv["transcript"])
#         processed_mock.append({
#             **conv,
#             "agent_id": agent_id,
#             "sentiment_label": sentiment["sentiment_label"],
#             "confidence": sentiment["confidence"]
#         })
#     
#     return {
#         "agent_id": agent_id,
#         "mock_conversations": processed_mock,
#         "total_count": len(processed_mock)
#     }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
