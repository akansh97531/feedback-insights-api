from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
from app.models.conversation import Conversation, Project, Topic, ConversationTopic
from app.schemas.conversation import ConversationCreate, ConversationUpdate, ElevenLabsConversation
from app.services.elevenlabs_client import ElevenLabsClient
from app.services.nlp_analyzer import NLPAnalyzer

logger = logging.getLogger(__name__)

class ConversationProcessor:
    """Service for processing conversations from ElevenLabs and generating insights."""
    
    def __init__(self, db: Session):
        self.db = db
        self.elevenlabs_client = ElevenLabsClient()
        self.nlp_analyzer = NLPAnalyzer()
    
    async def sync_conversations_from_elevenlabs(
        self, 
        project_id: int,
        agent_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Conversation]:
        """
        Sync conversations from ElevenLabs API and process them.
        
        Args:
            project_id: Project to associate conversations with
            agent_id: Filter by specific agent ID
            start_date: Filter conversations from this date
            end_date: Filter conversations until this date
            
        Returns:
            List of processed conversations
        """
        try:
            # Fetch conversations from ElevenLabs
            elevenlabs_conversations = await self.elevenlabs_client.get_conversations(
                agent_id=agent_id,
                start_date=start_date,
                end_date=end_date
            )
            
            processed_conversations = []
            
            for el_conv in elevenlabs_conversations:
                # Check if conversation already exists
                existing_conv = self.db.query(Conversation).filter(
                    Conversation.elevenlabs_conversation_id == el_conv.conversation_id
                ).first()
                
                if existing_conv:
                    logger.info(f"Conversation {el_conv.conversation_id} already exists, skipping")
                    continue
                
                # Process the conversation
                processed_conv = await self.process_conversation(el_conv, project_id)
                if processed_conv:
                    processed_conversations.append(processed_conv)
            
            logger.info(f"Processed {len(processed_conversations)} new conversations")
            return processed_conversations
            
        except Exception as e:
            logger.error(f"Error syncing conversations from ElevenLabs: {str(e)}")
            raise
    
    async def process_conversation(
        self, 
        elevenlabs_conv: ElevenLabsConversation, 
        project_id: int
    ) -> Optional[Conversation]:
        """
        Process a single conversation from ElevenLabs.
        
        Args:
            elevenlabs_conv: ElevenLabs conversation data
            project_id: Project to associate with
            
        Returns:
            Processed conversation or None if processing failed
        """
        try:
            # Create conversation record
            conversation_data = ConversationCreate(
                elevenlabs_conversation_id=elevenlabs_conv.conversation_id,
                project_id=project_id,
                duration_seconds=elevenlabs_conv.duration_seconds,
                transcript=elevenlabs_conv.transcript,
                summary=elevenlabs_conv.summary
            )
            
            conversation = Conversation(**conversation_data.dict())
            conversation.raw_data = elevenlabs_conv.metadata
            
            # Analyze the conversation if we have transcript
            if elevenlabs_conv.transcript:
                await self.analyze_conversation(conversation, elevenlabs_conv.transcript)
            
            # Save to database
            self.db.add(conversation)
            self.db.commit()
            self.db.refresh(conversation)
            
            # Extract and save topics
            if elevenlabs_conv.transcript:
                await self.extract_and_save_topics(conversation, elevenlabs_conv.transcript)
            
            conversation.processed_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Successfully processed conversation {elevenlabs_conv.conversation_id}")
            return conversation
            
        except Exception as e:
            logger.error(f"Error processing conversation {elevenlabs_conv.conversation_id}: {str(e)}")
            self.db.rollback()
            return None
    
    async def analyze_conversation(self, conversation: Conversation, transcript: str):
        """
        Analyze conversation content using NLP.
        
        Args:
            conversation: Conversation object to update
            transcript: Conversation transcript
        """
        try:
            # Sentiment analysis
            sentiment_result = self.nlp_analyzer.analyze_sentiment(transcript)
            conversation.sentiment_score = sentiment_result["sentiment_score"]
            conversation.sentiment_label = sentiment_result["sentiment_label"]
            conversation.confidence_score = sentiment_result["confidence"]
            
            # Generate summary if not provided
            if not conversation.summary:
                summary = await self.nlp_analyzer.generate_summary_with_openai(transcript)
                if summary:
                    conversation.summary = summary
            
            logger.info(f"Analyzed conversation sentiment: {sentiment_result['sentiment_label']} ({sentiment_result['sentiment_score']:.2f})")
            
        except Exception as e:
            logger.error(f"Error analyzing conversation: {str(e)}")
    
    async def extract_and_save_topics(self, conversation: Conversation, transcript: str):
        """
        Extract topics from conversation and save them.
        
        Args:
            conversation: Conversation object
            transcript: Conversation transcript
        """
        try:
            # Extract topics using NLP
            extracted_topics = self.nlp_analyzer.extract_topics(transcript)
            
            for topic_data in extracted_topics:
                # Find or create topic
                topic = self.db.query(Topic).filter(
                    Topic.name == topic_data["name"]
                ).first()
                
                if not topic:
                    topic = Topic(
                        name=topic_data["name"],
                        category=topic_data["type"]
                    )
                    self.db.add(topic)
                    self.db.commit()
                    self.db.refresh(topic)
                
                # Create conversation-topic relationship
                conv_topic = ConversationTopic(
                    conversation_id=conversation.id,
                    topic_id=topic.id,
                    relevance_score=topic_data["relevance_score"],
                    mentions_count=topic_data["mentions_count"]
                )
                self.db.add(conv_topic)
            
            self.db.commit()
            logger.info(f"Extracted {len(extracted_topics)} topics for conversation {conversation.id}")
            
        except Exception as e:
            logger.error(f"Error extracting topics: {str(e)}")
    
    def get_conversations_by_project(
        self, 
        project_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Conversation]:
        """
        Get conversations for a project.
        
        Args:
            project_id: Project ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of conversations
        """
        return self.db.query(Conversation).filter(
            Conversation.project_id == project_id
        ).offset(skip).limit(limit).all()
    
    def get_conversation_by_id(self, conversation_id: int) -> Optional[Conversation]:
        """Get conversation by ID."""
        return self.db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()
    
    def update_conversation(
        self, 
        conversation_id: int, 
        update_data: ConversationUpdate
    ) -> Optional[Conversation]:
        """
        Update conversation data.
        
        Args:
            conversation_id: Conversation ID
            update_data: Update data
            
        Returns:
            Updated conversation or None if not found
        """
        conversation = self.get_conversation_by_id(conversation_id)
        if not conversation:
            return None
        
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(conversation, field, value)
        
        self.db.commit()
        self.db.refresh(conversation)
        return conversation
