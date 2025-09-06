from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import Counter
import logging
from app.models.conversation import Conversation, Topic, ConversationTopic

logger = logging.getLogger(__name__)

class InsightsGenerator:
    """Generate insights and analytics from conversation data."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_sentiment_overview(self, agent_id: Optional[str] = None, days: int = 30) -> Dict[str, Any]:
        """
        Get sentiment overview for conversations.
        
        Args:
            agent_id: Filter by ElevenLabs agent ID (from raw_data)
            days: Number of days to look back
            
        Returns:
            Sentiment overview with counts and percentages
        """
        try:
            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Base query
            query = self.db.query(Conversation).filter(
                Conversation.created_at >= start_date,
                Conversation.sentiment_label.isnot(None)
            )
            
            # Filter by agent ID if provided
            if agent_id:
                # Skip agent filtering for SQLite - will filter in Python instead
                pass
            
            conversations = query.all()
            
            if not conversations:
                return {
                    "total_conversations": 0,
                    "sentiment_breakdown": {
                        "positive": {"count": 0, "percentage": 0},
                        "negative": {"count": 0, "percentage": 0},
                        "neutral": {"count": 0, "percentage": 0}
                    },
                    "average_sentiment_score": 0.0,
                    "period": {"start": start_date.isoformat(), "end": end_date.isoformat()}
                }
            
            # Count sentiments
            sentiment_counts = Counter([conv.sentiment_label for conv in conversations])
            total = len(conversations)
            
            # Calculate average sentiment score
            avg_sentiment = sum([conv.sentiment_score or 0 for conv in conversations]) / total
            
            return {
                "total_conversations": total,
                "sentiment_breakdown": {
                    "positive": {
                        "count": sentiment_counts.get("positive", 0),
                        "percentage": round((sentiment_counts.get("positive", 0) / total) * 100, 1)
                    },
                    "negative": {
                        "count": sentiment_counts.get("negative", 0),
                        "percentage": round((sentiment_counts.get("negative", 0) / total) * 100, 1)
                    },
                    "neutral": {
                        "count": sentiment_counts.get("neutral", 0),
                        "percentage": round((sentiment_counts.get("neutral", 0) / total) * 100, 1)
                    }
                },
                "average_sentiment_score": round(avg_sentiment, 3),
                "period": {"start": start_date.isoformat(), "end": end_date.isoformat()}
            }
            
        except Exception as e:
            logger.error(f"Error generating sentiment overview: {str(e)}")
            raise
    
    def get_key_insights(self, agent_id: Optional[str] = None, days: int = 30) -> Dict[str, Any]:
        """
        Get key positive and negative insights from conversations.
        
        Args:
            agent_id: Filter by ElevenLabs agent ID
            days: Number of days to look back
            
        Returns:
            Key insights with positive and negative feedback examples
        """
        try:
            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Base query
            query = self.db.query(Conversation).filter(
                Conversation.created_at >= start_date,
                Conversation.sentiment_label.isnot(None),
                Conversation.summary.isnot(None)
            )
            
            # Filter by agent ID if provided
            if agent_id:
                # Skip agent filtering for SQLite - will filter in Python instead
                pass
            
            # Get positive feedback (top 5 most positive)
            positive_conversations = query.filter(
                Conversation.sentiment_label == "positive"
            ).order_by(desc(Conversation.sentiment_score)).limit(5).all()
            
            # Get negative feedback (top 5 most negative)
            negative_conversations = query.filter(
                Conversation.sentiment_label == "negative"
            ).order_by(Conversation.sentiment_score).limit(5).all()
            
            # Extract key phrases and summaries
            positive_insights = []
            for conv in positive_conversations:
                positive_insights.append({
                    "summary": conv.summary,
                    "sentiment_score": conv.sentiment_score,
                    "created_at": conv.created_at.isoformat(),
                    "conversation_id": conv.elevenlabs_conversation_id
                })
            
            negative_insights = []
            for conv in negative_conversations:
                negative_insights.append({
                    "summary": conv.summary,
                    "sentiment_score": conv.sentiment_score,
                    "created_at": conv.created_at.isoformat(),
                    "conversation_id": conv.elevenlabs_conversation_id
                })
            
            return {
                "positive_feedback": {
                    "count": len(positive_insights),
                    "examples": positive_insights
                },
                "negative_feedback": {
                    "count": len(negative_insights),
                    "examples": negative_insights
                },
                "period": {"start": start_date.isoformat(), "end": end_date.isoformat()}
            }
            
        except Exception as e:
            logger.error(f"Error generating key insights: {str(e)}")
            raise
    
    def get_trending_topics(self, agent_id: Optional[str] = None, days: int = 30, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get trending topics from conversations.
        
        Args:
            agent_id: Filter by ElevenLabs agent ID
            days: Number of days to look back
            limit: Maximum number of topics to return
            
        Returns:
            List of trending topics with mention counts
        """
        try:
            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Base query for conversations
            conv_query = self.db.query(Conversation.id).filter(
                Conversation.created_at >= start_date
            )
            
            # Filter by agent ID if provided (simplified for SQLite)
            if agent_id:
                # Skip agent filtering for SQLite
                pass
            
            conversation_ids = [conv.id for conv in conv_query.all()]
            
            if not conversation_ids:
                return []
            
            # Get topics with their mention counts
            topic_stats = self.db.query(
                Topic.name,
                Topic.category,
                func.count(ConversationTopic.id).label('mention_count'),
                func.avg(ConversationTopic.relevance_score).label('avg_relevance'),
                func.sum(ConversationTopic.mentions_count).label('total_mentions')
            ).join(
                ConversationTopic, Topic.id == ConversationTopic.topic_id
            ).filter(
                ConversationTopic.conversation_id.in_(conversation_ids)
            ).group_by(
                Topic.id, Topic.name, Topic.category
            ).order_by(
                desc('mention_count')
            ).limit(limit).all()
            
            trending_topics = []
            for topic_stat in topic_stats:
                trending_topics.append({
                    "name": topic_stat.name,
                    "category": topic_stat.category,
                    "mention_count": topic_stat.mention_count,
                    "total_mentions": topic_stat.total_mentions or 0,
                    "average_relevance": round(topic_stat.avg_relevance or 0, 3)
                })
            
            return trending_topics
            
        except Exception as e:
            logger.error(f"Error getting trending topics: {str(e)}")
            raise
    
    def get_sentiment_trend(self, agent_id: Optional[str] = None, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get sentiment trend over time (daily breakdown).
        
        Args:
            agent_id: Filter by ElevenLabs agent ID
            days: Number of days to look back
            
        Returns:
            Daily sentiment breakdown
        """
        try:
            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Base query
            query = self.db.query(
                func.date(Conversation.created_at).label('date'),
                Conversation.sentiment_label,
                func.count(Conversation.id).label('count'),
                func.avg(Conversation.sentiment_score).label('avg_score')
            ).filter(
                Conversation.created_at >= start_date,
                Conversation.sentiment_label.isnot(None)
            )
            
            # Filter by agent ID if provided
            if agent_id:
                # Skip agent filtering for SQLite - will filter in Python instead
                pass
            
            results = query.group_by(
                func.date(Conversation.created_at),
                Conversation.sentiment_label
            ).order_by('date').all()
            
            # Organize by date
            trend_data = {}
            for result in results:
                date_str = result.date.isoformat()
                if date_str not in trend_data:
                    trend_data[date_str] = {
                        "date": date_str,
                        "positive": {"count": 0, "avg_score": 0},
                        "negative": {"count": 0, "avg_score": 0},
                        "neutral": {"count": 0, "avg_score": 0}
                    }
                
                trend_data[date_str][result.sentiment_label] = {
                    "count": result.count,
                    "avg_score": round(result.avg_score or 0, 3)
                }
            
            return list(trend_data.values())
            
        except Exception as e:
            logger.error(f"Error generating sentiment trend: {str(e)}")
            raise
