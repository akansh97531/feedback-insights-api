from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    conversations = relationship("Conversation", back_populates="project")
    insights = relationship("Insight", back_populates="project")

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    elevenlabs_conversation_id = Column(String(255), unique=True, nullable=False, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    
    # Conversation metadata
    duration_seconds = Column(Float)
    participant_count = Column(Integer, default=1)
    language = Column(String(10), default="en")
    
    # Conversation content
    transcript = Column(Text)
    summary = Column(Text)
    
    # Analysis results
    sentiment_score = Column(Float)  # -1 to 1 scale
    sentiment_label = Column(String(20))  # positive, negative, neutral
    confidence_score = Column(Float)  # 0 to 1 scale
    
    # Metadata
    raw_data = Column(JSON)  # Store raw ElevenLabs response
    processed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="conversations")
    topics = relationship("ConversationTopic", back_populates="conversation")

class Topic(Base):
    __tablename__ = "topics"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text)
    category = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    conversations = relationship("ConversationTopic", back_populates="topic")

class ConversationTopic(Base):
    __tablename__ = "conversation_topics"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    relevance_score = Column(Float)  # 0 to 1 scale
    mentions_count = Column(Integer, default=1)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="topics")
    topic = relationship("Topic", back_populates="conversations")

class Insight(Base):
    __tablename__ = "insights"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    
    # Insight metadata
    title = Column(String(255), nullable=False)
    description = Column(Text)
    insight_type = Column(String(50))  # sentiment_trend, topic_analysis, feature_feedback, etc.
    priority = Column(String(20), default="medium")  # high, medium, low
    
    # Insight data
    data = Column(JSON)  # Store structured insight data
    recommendations = Column(Text)
    
    # Time period for the insight
    period_start = Column(DateTime(timezone=True))
    period_end = Column(DateTime(timezone=True))
    
    # Metadata
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    project = relationship("Project", back_populates="insights")
