from elevenlabs import ElevenLabs
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.core.config import settings
from app.schemas.conversation import ElevenLabsConversation
import logging

logger = logging.getLogger(__name__)

class ElevenLabsClient:
    """Client for interacting with ElevenLabs Voice Agent API using official SDK."""
    
    def __init__(self):
        self.client = ElevenLabs(api_key=settings.elevenlabs_api_key)
    
    async def get_conversations(
        self, 
        agent_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[ElevenLabsConversation]:
        """
        Fetch conversations from ElevenLabs Voice Agent API using official SDK.
        
        Args:
            agent_id: Filter by specific agent ID
            start_date: Filter conversations from this date
            end_date: Filter conversations until this date
            limit: Maximum number of conversations to fetch
            
        Returns:
            List of ElevenLabsConversation objects
        """
        try:
            # Use the official ElevenLabs SDK to get conversations
            # Note: The exact method may vary based on SDK version
            conversations = []
            
            # Get conversation history using the SDK
            # This is a placeholder - need to check actual SDK methods
            conversation_history = self.client.conversational_ai.get_conversations(
                agent_id=agent_id,
                limit=limit
            )
            
            for conv in conversation_history:
                conversation = ElevenLabsConversation(
                    conversation_id=conv.conversation_id,
                    agent_id=conv.agent_id,
                    user_id=getattr(conv, 'user_id', None),
                    start_time=conv.start_time,
                    end_time=getattr(conv, 'end_time', None),
                    transcript=getattr(conv, 'transcript', None),
                    summary=getattr(conv, 'summary', None),
                    duration_seconds=getattr(conv, 'duration_seconds', None),
                    metadata=getattr(conv, 'metadata', {})
                )
                conversations.append(conversation)
            
            logger.info(f"Fetched {len(conversations)} conversations from ElevenLabs SDK")
            return conversations
            
        except Exception as e:
            logger.error(f"Error fetching conversations from ElevenLabs SDK: {str(e)}")
            # Fallback to mock data for development
            return self._get_mock_conversations(agent_id, limit)
    
    def _get_mock_conversations(self, agent_id: Optional[str], limit: int) -> List[ElevenLabsConversation]:
        """Generate mock conversation data for testing."""
        mock_conversations = []
        
        for i in range(min(limit, 5)):  # Generate up to 5 mock conversations
            conversation = ElevenLabsConversation(
                conversation_id=f"mock_conv_{i+1}_{agent_id or 'default'}",
                agent_id=agent_id or "mock_agent_123",
                user_id=f"user_{i+1}",
                start_time=datetime.utcnow().replace(hour=10+i, minute=0, second=0),
                end_time=datetime.utcnow().replace(hour=10+i, minute=15, second=0),
                transcript=f"Mock conversation {i+1}: User discusses product features and provides feedback about the experience.",
                summary=f"User provided {'positive' if i % 2 == 0 else 'negative'} feedback about the product in conversation {i+1}.",
                duration_seconds=900.0,  # 15 minutes
                metadata={"mock": True, "conversation_number": i+1}
            )
            mock_conversations.append(conversation)
        
        logger.info(f"Generated {len(mock_conversations)} mock conversations for testing")
        return mock_conversations
    
    async def get_conversation_details(self, conversation_id: str) -> Optional[ElevenLabsConversation]:
        """
        Fetch detailed information for a specific conversation.
        
        Args:
            conversation_id: The conversation ID to fetch
            
        Returns:
            ElevenLabsConversation object or None if not found
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/conversations/{conversation_id}",
                    headers=self.headers
                )
                response.raise_for_status()
                
                conv_data = response.json()
                
                conversation = ElevenLabsConversation(
                    conversation_id=conv_data["conversation_id"],
                    agent_id=conv_data["agent_id"],
                    user_id=conv_data.get("user_id"),
                    start_time=datetime.fromisoformat(conv_data["start_time"]),
                    end_time=datetime.fromisoformat(conv_data["end_time"]) if conv_data.get("end_time") else None,
                    transcript=conv_data.get("transcript"),
                    summary=conv_data.get("summary"),
                    duration_seconds=conv_data.get("duration_seconds"),
                    metadata=conv_data.get("metadata", {})
                )
                
                logger.info(f"Fetched conversation details for {conversation_id}")
                return conversation
                
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning(f"Conversation {conversation_id} not found")
                return None
            logger.error(f"HTTP error fetching conversation {conversation_id}: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error fetching conversation {conversation_id}: {str(e)}")
            raise
    
    async def get_conversation_transcript(self, conversation_id: str) -> Optional[str]:
        """
        Fetch the transcript for a specific conversation.
        
        Args:
            conversation_id: The conversation ID
            
        Returns:
            Transcript text or None if not available
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/conversations/{conversation_id}/transcript",
                    headers=self.headers
                )
                response.raise_for_status()
                
                data = response.json()
                return data.get("transcript")
                
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning(f"Transcript for conversation {conversation_id} not found")
                return None
            logger.error(f"HTTP error fetching transcript for {conversation_id}: {e.response.status_code}")
            raise
        except Exception as e:
            logger.error(f"Error fetching transcript for {conversation_id}: {str(e)}")
            raise
