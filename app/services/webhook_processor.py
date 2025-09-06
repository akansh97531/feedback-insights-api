from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from datetime import datetime
import logging
import hashlib
import hmac
from app.models.conversation import Conversation, Project
from app.schemas.webhook import ElevenLabsWebhookPayload, WebhookResponse
from app.schemas.conversation import ElevenLabsConversation
from app.services.conversation_processor import ConversationProcessor
from app.core.config import settings

logger = logging.getLogger(__name__)

class WebhookProcessor:
    """Service for processing ElevenLabs webhook events."""
    
    def __init__(self, db: Session):
        self.db = db
        self.conversation_processor = ConversationProcessor(db)
    
    def validate_webhook_signature(
        self, 
        payload: bytes, 
        signature: str, 
        secret: Optional[str] = None
    ) -> bool:
        """
        Validate webhook signature for security.
        
        Args:
            payload: Raw request body
            signature: Signature from webhook headers
            secret: Webhook secret key
            
        Returns:
            True if signature is valid
        """
        if not secret:
            # If no secret configured, skip validation (development mode)
            logger.warning("Webhook signature validation skipped - no secret configured")
            return True
        
        try:
            # Create expected signature
            expected_signature = hmac.new(
                secret.encode('utf-8'),
                payload,
                hashlib.sha256
            ).hexdigest()
            
            # Compare signatures
            return hmac.compare_digest(f"sha256={expected_signature}", signature)
            
        except Exception as e:
            logger.error(f"Error validating webhook signature: {str(e)}")
            return False
    
    async def process_conversation_webhook(
        self, 
        webhook_payload: ElevenLabsWebhookPayload,
        project_id: Optional[int] = None
    ) -> WebhookResponse:
        """
        Process incoming conversation webhook from ElevenLabs.
        
        Args:
            webhook_payload: Webhook data from ElevenLabs
            project_id: Project to associate conversation with
            
        Returns:
            Webhook processing response
        """
        try:
            logger.info(f"Processing webhook for conversation {webhook_payload.conversation_id}")
            
            # Check if conversation already exists
            existing_conv = self.db.query(Conversation).filter(
                Conversation.elevenlabs_conversation_id == webhook_payload.conversation_id
            ).first()
            
            if existing_conv:
                logger.info(f"Conversation {webhook_payload.conversation_id} already exists, updating")
                return await self._update_existing_conversation(existing_conv, webhook_payload)
            
            # Create new conversation from webhook data
            return await self._create_new_conversation(webhook_payload, project_id)
            
        except Exception as e:
            logger.error(f"Error processing webhook: {str(e)}")
            return WebhookResponse(
                status="error",
                message=f"Failed to process webhook: {str(e)}",
                conversation_id=webhook_payload.conversation_id
            )
    
    async def _create_new_conversation(
        self, 
        webhook_payload: ElevenLabsWebhookPayload,
        project_id: Optional[int]
    ) -> WebhookResponse:
        """Create a new conversation from webhook data."""
        try:
            # Get or create default project if none specified
            if not project_id:
                project = self._get_or_create_default_project(webhook_payload.agent_id)
                project_id = project.id
            
            # Convert webhook payload to ElevenLabsConversation format
            elevenlabs_conv = ElevenLabsConversation(
                conversation_id=webhook_payload.conversation_id,
                agent_id=webhook_payload.agent_id,
                user_id=webhook_payload.user_id,
                start_time=webhook_payload.start_time,
                end_time=webhook_payload.end_time,
                transcript=webhook_payload.transcript,
                summary=webhook_payload.summary,
                duration_seconds=webhook_payload.duration_seconds,
                metadata=webhook_payload.metadata or {}
            )
            
            # Process the conversation
            processed_conv = await self.conversation_processor.process_conversation(
                elevenlabs_conv, 
                project_id
            )
            
            if processed_conv:
                logger.info(f"Successfully processed new conversation {webhook_payload.conversation_id}")
                return WebhookResponse(
                    status="success",
                    message="Conversation processed successfully",
                    conversation_id=webhook_payload.conversation_id
                )
            else:
                return WebhookResponse(
                    status="error",
                    message="Failed to process conversation",
                    conversation_id=webhook_payload.conversation_id
                )
                
        except Exception as e:
            logger.error(f"Error creating new conversation: {str(e)}")
            raise
    
    async def _update_existing_conversation(
        self, 
        existing_conv: Conversation,
        webhook_payload: ElevenLabsWebhookPayload
    ) -> WebhookResponse:
        """Update an existing conversation with new webhook data."""
        try:
            # Update conversation fields if new data is available
            updated = False
            
            if webhook_payload.transcript and webhook_payload.transcript != existing_conv.transcript:
                existing_conv.transcript = webhook_payload.transcript
                updated = True
            
            if webhook_payload.summary and webhook_payload.summary != existing_conv.summary:
                existing_conv.summary = webhook_payload.summary
                updated = True
            
            if webhook_payload.end_time and not existing_conv.raw_data.get('end_time'):
                # Update raw_data with end_time
                raw_data = existing_conv.raw_data or {}
                raw_data['end_time'] = webhook_payload.end_time.isoformat()
                existing_conv.raw_data = raw_data
                updated = True
            
            if webhook_payload.duration_seconds and not existing_conv.duration_seconds:
                existing_conv.duration_seconds = webhook_payload.duration_seconds
                updated = True
            
            if updated:
                # Re-analyze the conversation if transcript was updated
                if webhook_payload.transcript:
                    await self.conversation_processor.analyze_conversation(
                        existing_conv, 
                        webhook_payload.transcript
                    )
                
                existing_conv.processed_at = datetime.utcnow()
                self.db.commit()
                
                logger.info(f"Updated existing conversation {webhook_payload.conversation_id}")
                return WebhookResponse(
                    status="updated",
                    message="Conversation updated successfully",
                    conversation_id=webhook_payload.conversation_id
                )
            else:
                return WebhookResponse(
                    status="no_change",
                    message="No updates needed",
                    conversation_id=webhook_payload.conversation_id
                )
                
        except Exception as e:
            logger.error(f"Error updating existing conversation: {str(e)}")
            self.db.rollback()
            raise
    
    def _get_or_create_default_project(self, agent_id: str) -> Project:
        """Get or create a default project for the agent."""
        project_name = f"Agent {agent_id} Project"
        
        # Check if project already exists
        project = self.db.query(Project).filter(
            Project.name == project_name
        ).first()
        
        if not project:
            # Create new project
            project = Project(
                name=project_name,
                description=f"Auto-created project for ElevenLabs agent {agent_id}"
            )
            self.db.add(project)
            self.db.commit()
            self.db.refresh(project)
            logger.info(f"Created new project: {project_name}")
        
        return project
    
    def get_webhook_stats(self) -> Dict[str, Any]:
        """Get webhook processing statistics."""
        try:
            total_conversations = self.db.query(Conversation).count()
            recent_conversations = self.db.query(Conversation).filter(
                Conversation.created_at >= datetime.utcnow().replace(hour=0, minute=0, second=0)
            ).count()
            
            return {
                "total_conversations": total_conversations,
                "conversations_today": recent_conversations,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting webhook stats: {str(e)}")
            return {
                "total_conversations": 0,
                "conversations_today": 0,
                "last_updated": datetime.utcnow().isoformat(),
                "error": str(e)
            }
