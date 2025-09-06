from fastapi import APIRouter, Depends, HTTPException, Request, Header, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional
import logging
from app.db.database import get_db
from app.services.webhook_processor import WebhookProcessor
from app.schemas.webhook import ElevenLabsWebhookPayload, WebhookResponse
from app.core.security import validate_agent_id

logger = logging.getLogger(__name__)

webhook_router = APIRouter()

@webhook_router.post("/webhook/elevenlabs", response_model=WebhookResponse)
async def receive_elevenlabs_webhook(
    webhook_payload: ElevenLabsWebhookPayload,
    background_tasks: BackgroundTasks,
    request: Request,
    project_id: Optional[int] = None,
    x_signature: Optional[str] = Header(None, alias="X-Signature"),
    db: Session = Depends(get_db)
):
    """
    Webhook endpoint to receive live conversations from ElevenLabs.
    
    This endpoint receives real-time conversation data from ElevenLabs
    and automatically processes it for sentiment analysis and insights.
    
    Args:
        webhook_payload: Conversation data from ElevenLabs
        project_id: Optional project ID to associate conversation with
        x_signature: Webhook signature for validation
        
    Returns:
        Processing status and details
    """
    try:
        logger.info(f"Received webhook for conversation {webhook_payload.conversation_id}")
        
        # Validate agent ID format
        if not validate_agent_id(webhook_payload.agent_id):
            raise HTTPException(status_code=400, detail="Invalid agent ID format")
        
        # Initialize webhook processor
        webhook_processor = WebhookProcessor(db)
        
        # Validate webhook signature if provided
        if x_signature:
            raw_body = await request.body()
            if not webhook_processor.validate_webhook_signature(raw_body, x_signature):
                raise HTTPException(status_code=401, detail="Invalid webhook signature")
        
        # Process the webhook in the background for faster response
        background_tasks.add_task(
            process_webhook_background,
            webhook_processor,
            webhook_payload,
            project_id
        )
        
        # Return immediate response
        return WebhookResponse(
            status="accepted",
            message="Webhook received and queued for processing",
            conversation_id=webhook_payload.conversation_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Webhook processing failed: {str(e)}")

async def process_webhook_background(
    webhook_processor: WebhookProcessor,
    webhook_payload: ElevenLabsWebhookPayload,
    project_id: Optional[int]
):
    """Background task to process webhook data."""
    try:
        result = await webhook_processor.process_conversation_webhook(
            webhook_payload, 
            project_id
        )
        logger.info(f"Background processing completed: {result.status} for {webhook_payload.conversation_id}")
    except Exception as e:
        logger.error(f"Background webhook processing failed: {str(e)}")

@webhook_router.post("/webhook/elevenlabs/sync", response_model=WebhookResponse)
async def receive_elevenlabs_webhook_sync(
    webhook_payload: ElevenLabsWebhookPayload,
    request: Request,
    project_id: Optional[int] = None,
    x_signature: Optional[str] = Header(None, alias="X-Signature"),
    db: Session = Depends(get_db)
):
    """
    Synchronous webhook endpoint for ElevenLabs conversations.
    
    This endpoint processes the webhook immediately and returns
    the processing result. Use this for testing or when you need
    immediate confirmation of processing.
    """
    try:
        logger.info(f"Received sync webhook for conversation {webhook_payload.conversation_id}")
        
        # Validate agent ID format
        if not validate_agent_id(webhook_payload.agent_id):
            raise HTTPException(status_code=400, detail="Invalid agent ID format")
        
        # Initialize webhook processor
        webhook_processor = WebhookProcessor(db)
        
        # Validate webhook signature if provided
        if x_signature:
            raw_body = await request.body()
            if not webhook_processor.validate_webhook_signature(raw_body, x_signature):
                raise HTTPException(status_code=401, detail="Invalid webhook signature")
        
        # Process the webhook synchronously
        result = await webhook_processor.process_conversation_webhook(
            webhook_payload, 
            project_id
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing sync webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Sync webhook processing failed: {str(e)}")

@webhook_router.get("/webhook/stats")
async def get_webhook_stats(db: Session = Depends(get_db)):
    """
    Get webhook processing statistics.
    
    Returns information about total conversations processed,
    recent activity, and system health.
    """
    try:
        webhook_processor = WebhookProcessor(db)
        stats = webhook_processor.get_webhook_stats()
        
        return {
            "webhook_stats": stats,
            "endpoints": {
                "async_webhook": "/api/v1/webhook/elevenlabs",
                "sync_webhook": "/api/v1/webhook/elevenlabs/sync",
                "stats": "/api/v1/webhook/stats"
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting webhook stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get webhook stats: {str(e)}")

@webhook_router.post("/webhook/test")
async def test_webhook_endpoint(
    agent_id: str = "test_agent_123",
    db: Session = Depends(get_db)
):
    """
    Test webhook endpoint with mock data.
    
    This endpoint creates a test conversation to verify
    that the webhook processing pipeline is working correctly.
    """
    try:
        from datetime import datetime, timedelta
        
        # Create test webhook payload
        test_payload = ElevenLabsWebhookPayload(
            event_type="conversation.completed",
            conversation_id=f"test_conv_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            agent_id=agent_id,
            user_id="test_user_123",
            transcript="This is a test conversation. The user is very happy with the product and thinks it's amazing! The features work perfectly and the experience is excellent.",
            summary="User provided very positive feedback about the product, praising its features and overall experience.",
            start_time=datetime.utcnow() - timedelta(minutes=10),
            end_time=datetime.utcnow(),
            duration_seconds=600.0,
            metadata={"test": True, "source": "webhook_test"}
        )
        
        # Process the test webhook
        webhook_processor = WebhookProcessor(db)
        result = await webhook_processor.process_conversation_webhook(test_payload)
        
        return {
            "message": "Test webhook processed successfully",
            "test_payload": test_payload.dict(),
            "processing_result": result.dict()
        }
        
    except Exception as e:
        logger.error(f"Error testing webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Webhook test failed: {str(e)}")
