from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class ElevenLabsWebhookPayload(BaseModel):
    """Schema for ElevenLabs webhook payload."""
    
    event_type: str = Field(..., description="Type of webhook event")
    conversation_id: str = Field(..., description="Unique conversation identifier")
    agent_id: str = Field(..., description="ElevenLabs agent identifier")
    user_id: Optional[str] = Field(None, description="User identifier")
    
    # Conversation data
    transcript: Optional[str] = Field(None, description="Full conversation transcript")
    summary: Optional[str] = Field(None, description="Conversation summary")
    start_time: datetime = Field(..., description="Conversation start timestamp")
    end_time: Optional[datetime] = Field(None, description="Conversation end timestamp")
    duration_seconds: Optional[float] = Field(None, description="Conversation duration")
    
    # Additional metadata
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class WebhookResponse(BaseModel):
    """Response schema for webhook endpoints."""
    
    status: str = Field(..., description="Processing status")
    message: str = Field(..., description="Response message")
    conversation_id: str = Field(..., description="Processed conversation ID")
    processed_at: datetime = Field(default_factory=datetime.utcnow, description="Processing timestamp")
    
class WebhookValidation(BaseModel):
    """Schema for webhook validation."""
    
    signature: Optional[str] = Field(None, description="Webhook signature for validation")
    timestamp: Optional[str] = Field(None, description="Request timestamp")
    raw_body: Optional[bytes] = Field(None, description="Raw request body for signature validation")
