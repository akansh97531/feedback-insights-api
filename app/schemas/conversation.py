from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# Project schemas
class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None

class Project(ProjectBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Conversation schemas
class ConversationBase(BaseModel):
    elevenlabs_conversation_id: str
    project_id: int
    duration_seconds: Optional[float] = None
    participant_count: Optional[int] = 1
    language: Optional[str] = "en"
    transcript: Optional[str] = None
    summary: Optional[str] = None

class ConversationCreate(ConversationBase):
    pass

class ConversationUpdate(BaseModel):
    transcript: Optional[str] = None
    summary: Optional[str] = None
    sentiment_score: Optional[float] = Field(None, ge=-1, le=1)
    sentiment_label: Optional[str] = None
    confidence_score: Optional[float] = Field(None, ge=0, le=1)
    raw_data: Optional[Dict[str, Any]] = None

class Conversation(ConversationBase):
    id: int
    sentiment_score: Optional[float] = None
    sentiment_label: Optional[str] = None
    confidence_score: Optional[float] = None
    processed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Topic schemas
class TopicBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = None

class TopicCreate(TopicBase):
    pass

class Topic(TopicBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Conversation Topic schemas
class ConversationTopicBase(BaseModel):
    conversation_id: int
    topic_id: int
    relevance_score: Optional[float] = Field(None, ge=0, le=1)
    mentions_count: Optional[int] = 1

class ConversationTopicCreate(ConversationTopicBase):
    pass

class ConversationTopic(ConversationTopicBase):
    id: int
    topic: Optional[Topic] = None
    
    class Config:
        from_attributes = True

# Insight schemas
class InsightBase(BaseModel):
    project_id: int
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    insight_type: str
    priority: Optional[str] = "medium"
    recommendations: Optional[str] = None
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None

class InsightCreate(InsightBase):
    data: Optional[Dict[str, Any]] = None

class InsightUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    priority: Optional[str] = None
    recommendations: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class Insight(InsightBase):
    id: int
    data: Optional[Dict[str, Any]] = None
    generated_at: datetime
    is_active: bool = True
    
    class Config:
        from_attributes = True

# Response schemas
class ConversationWithTopics(Conversation):
    topics: List[ConversationTopic] = []

class ProjectWithStats(Project):
    total_conversations: int = 0
    avg_sentiment: Optional[float] = None
    recent_insights_count: int = 0

# ElevenLabs API response schemas
class ElevenLabsConversation(BaseModel):
    conversation_id: str
    agent_id: str
    user_id: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    transcript: Optional[str] = None
    summary: Optional[str] = None
    duration_seconds: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
