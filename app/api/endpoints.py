from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import logging
from app.db.database import get_db
from app.services.conversation_processor import ConversationProcessor
from app.services.insights_generator import InsightsGenerator
from app.core.security import validate_agent_id

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@router.post("/sync-conversations/{agent_id}")
async def sync_conversations(
    agent_id: str,
    project_id: int = Query(..., description="Project ID to associate conversations with"),
    days: int = Query(7, description="Number of days to sync (default: 7)"),
    db: Session = Depends(get_db)
):
    """
    Sync conversations from ElevenLabs for a specific agent ID.
    
    This endpoint fetches the latest conversations from ElevenLabs Voice Agent API
    and processes them for sentiment analysis and topic extraction.
    """
    if not validate_agent_id(agent_id):
        raise HTTPException(status_code=400, detail="Invalid agent ID format")
    
    try:
        processor = ConversationProcessor(db)
        
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Sync conversations
        conversations = await processor.sync_conversations_from_elevenlabs(
            project_id=project_id,
            agent_id=agent_id,
            start_date=start_date,
            end_date=end_date
        )
        
        return {
            "message": f"Successfully synced {len(conversations)} conversations",
            "agent_id": agent_id,
            "project_id": project_id,
            "conversations_processed": len(conversations),
            "sync_period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error syncing conversations for agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to sync conversations: {str(e)}")

@router.get("/sentiment-overview/{agent_id}")
async def get_sentiment_overview(
    agent_id: str,
    days: int = Query(30, description="Number of days to analyze (default: 30)"),
    db: Session = Depends(get_db)
):
    """
    Get real-time sentiment overview for a specific ElevenLabs agent.
    
    Returns sentiment breakdown (positive, negative, neutral) with percentages
    and average sentiment score for the specified time period.
    """
    if not validate_agent_id(agent_id):
        raise HTTPException(status_code=400, detail="Invalid agent ID format")
    
    try:
        insights_generator = InsightsGenerator(db)
        overview = insights_generator.get_sentiment_overview(agent_id=agent_id, days=days)
        
        return {
            "agent_id": agent_id,
            "analysis_period_days": days,
            **overview
        }
        
    except Exception as e:
        logger.error(f"Error generating sentiment overview for agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate sentiment overview: {str(e)}")

@router.get("/insights/{agent_id}")
async def get_key_insights(
    agent_id: str,
    days: int = Query(30, description="Number of days to analyze (default: 30)"),
    db: Session = Depends(get_db)
):
    """
    Get key positive and negative feedback insights for a specific agent.
    
    Returns examples of the most positive and negative user feedback
    with summaries and sentiment scores.
    """
    if not validate_agent_id(agent_id):
        raise HTTPException(status_code=400, detail="Invalid agent ID format")
    
    try:
        insights_generator = InsightsGenerator(db)
        insights = insights_generator.get_key_insights(agent_id=agent_id, days=days)
        
        return {
            "agent_id": agent_id,
            "analysis_period_days": days,
            **insights
        }
        
    except Exception as e:
        logger.error(f"Error generating insights for agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate insights: {str(e)}")

@router.get("/trending-topics/{agent_id}")
async def get_trending_topics(
    agent_id: str,
    days: int = Query(30, description="Number of days to analyze (default: 30)"),
    limit: int = Query(10, description="Maximum number of topics to return (default: 10)"),
    db: Session = Depends(get_db)
):
    """
    Get trending topics and themes from user conversations.
    
    Returns the most frequently mentioned topics with relevance scores
    and mention counts.
    """
    if not validate_agent_id(agent_id):
        raise HTTPException(status_code=400, detail="Invalid agent ID format")
    
    try:
        insights_generator = InsightsGenerator(db)
        topics = insights_generator.get_trending_topics(
            agent_id=agent_id, 
            days=days, 
            limit=limit
        )
        
        return {
            "agent_id": agent_id,
            "analysis_period_days": days,
            "trending_topics": topics,
            "total_topics": len(topics)
        }
        
    except Exception as e:
        logger.error(f"Error getting trending topics for agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get trending topics: {str(e)}")

@router.get("/sentiment-trend/{agent_id}")
async def get_sentiment_trend(
    agent_id: str,
    days: int = Query(30, description="Number of days to analyze (default: 30)"),
    db: Session = Depends(get_db)
):
    """
    Get sentiment trend over time for a specific agent.
    
    Returns daily breakdown of sentiment counts and average scores
    to show how user sentiment is changing over time.
    """
    if not validate_agent_id(agent_id):
        raise HTTPException(status_code=400, detail="Invalid agent ID format")
    
    try:
        insights_generator = InsightsGenerator(db)
        trend = insights_generator.get_sentiment_trend(agent_id=agent_id, days=days)
        
        return {
            "agent_id": agent_id,
            "analysis_period_days": days,
            "sentiment_trend": trend,
            "data_points": len(trend)
        }
        
    except Exception as e:
        logger.error(f"Error generating sentiment trend for agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate sentiment trend: {str(e)}")

@router.get("/dashboard/{agent_id}")
async def get_dashboard_data(
    agent_id: str,
    days: int = Query(30, description="Number of days to analyze (default: 30)"),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive dashboard data for a specific agent.
    
    Returns all key metrics in one endpoint: sentiment overview, 
    key insights, trending topics, and sentiment trend.
    """
    if not validate_agent_id(agent_id):
        raise HTTPException(status_code=400, detail="Invalid agent ID format")
    
    try:
        insights_generator = InsightsGenerator(db)
        
        # Get all dashboard data
        sentiment_overview = insights_generator.get_sentiment_overview(agent_id=agent_id, days=days)
        key_insights = insights_generator.get_key_insights(agent_id=agent_id, days=days)
        trending_topics = insights_generator.get_trending_topics(agent_id=agent_id, days=days, limit=5)
        sentiment_trend = insights_generator.get_sentiment_trend(agent_id=agent_id, days=days)
        
        return {
            "agent_id": agent_id,
            "analysis_period_days": days,
            "last_updated": datetime.utcnow().isoformat(),
            "sentiment_overview": sentiment_overview,
            "key_insights": key_insights,
            "trending_topics": {
                "topics": trending_topics,
                "total_topics": len(trending_topics)
            },
            "sentiment_trend": {
                "trend_data": sentiment_trend,
                "data_points": len(sentiment_trend)
            }
        }
        
    except Exception as e:
        logger.error(f"Error generating dashboard data for agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate dashboard data: {str(e)}")

# Global endpoints (not agent-specific)
@router.get("/sentiment-overview")
async def get_global_sentiment_overview(
    days: int = Query(30, description="Number of days to analyze (default: 30)"),
    db: Session = Depends(get_db)
):
    """
    Get sentiment overview across all agents and conversations.
    """
    try:
        insights_generator = InsightsGenerator(db)
        overview = insights_generator.get_sentiment_overview(days=days)
        
        return {
            "scope": "global",
            "analysis_period_days": days,
            **overview
        }
        
    except Exception as e:
        logger.error(f"Error generating global sentiment overview: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate global sentiment overview: {str(e)}")

@router.get("/trending-topics")
async def get_global_trending_topics(
    days: int = Query(30, description="Number of days to analyze (default: 30)"),
    limit: int = Query(10, description="Maximum number of topics to return (default: 10)"),
    db: Session = Depends(get_db)
):
    """
    Get trending topics across all agents and conversations.
    """
    try:
        insights_generator = InsightsGenerator(db)
        topics = insights_generator.get_trending_topics(days=days, limit=limit)
        
        return {
            "scope": "global",
            "analysis_period_days": days,
            "trending_topics": topics,
            "total_topics": len(topics)
        }
        
    except Exception as e:
        logger.error(f"Error getting global trending topics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get global trending topics: {str(e)}")
