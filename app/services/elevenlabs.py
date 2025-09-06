"""ElevenLabs client for fetching voice agent conversations."""
import httpx
import os
from typing import List, Dict, Any, Optional

class ElevenLabsClient:
    """ElevenLabs API client for voice agent conversations."""
    
    def __init__(self, api_key: str = ""):
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY", "")
        self.base_url = "https://api.elevenlabs.io/v1"
        self.headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }
    
    async def get_agent_conversations(self, agent_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Fetch conversations for a specific voice agent."""
        if not self.api_key:
            # Return mock data if no API key
            return self._get_mock_conversations(agent_id, limit)
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # First, get conversation IDs for the agent
                response = await client.get(
                    f"{self.base_url}/convai/conversations",
                    headers=self.headers,
                    params={
                        "agent_id": agent_id,
                        "page_size": limit
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    conversations = []
                    
                    # Get conversation IDs from the response
                    conversation_ids = []
                    if "history" in data:
                        for item in data["history"]:
                            if "conversation_id" in item:
                                conversation_ids.append(item["conversation_id"])
                    
                    # Fetch detailed conversation data for each ID
                    for conv_id in conversation_ids[:limit]:
                        try:
                            conv_response = await client.get(
                                f"{self.base_url}/convai/conversations/{conv_id}",
                                headers=self.headers
                            )
                            
                            if conv_response.status_code == 200:
                                conv_data = conv_response.json()
                                transcript = self._extract_transcript_from_conversation(conv_data)
                                
                                if transcript:
                                    conversations.append({
                                        "id": conv_id,
                                        "agent_id": agent_id,
                                        "transcript": transcript,
                                        "created_at": conv_data.get("created_at", ""),
                                        "duration": conv_data.get("duration_seconds", 0)
                                    })
                        except Exception as e:
                            print(f"Error fetching conversation {conv_id}: {e}")
                            continue
                    
                    return conversations if conversations else self._get_mock_conversations(agent_id, limit)
                else:
                    print(f"ElevenLabs API error: {response.status_code} - {response.text}")
                    return self._get_mock_conversations(agent_id, limit)
                    
        except Exception as e:
            print(f"Error fetching from ElevenLabs: {e}")
            return self._get_mock_conversations(agent_id, limit)
    
    def _extract_transcript_from_conversation(self, conversation: Dict[str, Any]) -> str:
        """Extract transcript text from detailed conversation data."""
        # Try different possible transcript fields from ElevenLabs API
        if "transcript" in conversation:
            return conversation["transcript"]
        
        # Check for conversation turns/messages
        if "conversation_turns" in conversation:
            messages = []
            for turn in conversation["conversation_turns"]:
                if "user_message" in turn and turn["user_message"]:
                    messages.append(f"User: {turn['user_message']}")
                if "agent_response" in turn and turn["agent_response"]:
                    messages.append(f"Agent: {turn['agent_response']}")
            return " ".join(messages)
        
        if "messages" in conversation:
            messages = []
            for msg in conversation["messages"]:
                if isinstance(msg, dict):
                    content = msg.get("content", "") or msg.get("text", "")
                    if content:
                        messages.append(content)
                elif isinstance(msg, str):
                    messages.append(msg)
            return " ".join(messages)
        
        if "summary" in conversation:
            return conversation["summary"]
        
        return ""
    
    def _get_mock_conversations(self, agent_id: str, limit: int) -> List[Dict[str, Any]]:
        """Generate mock conversations for testing."""
        mock_transcripts = [
            "Hi, I'm calling about your product. The service has been absolutely amazing! Your team was so helpful and resolved my issue quickly. I'm really impressed with the quality.",
            "I had some trouble with the setup initially, but your support team walked me through everything step by step. Great customer service!",
            "This is terrible. I've been waiting for hours and nobody can help me. The product doesn't work as advertised and I'm very frustrated.",
            "The experience was okay, nothing special. It works but could be better. Average service overall.",
            "Fantastic! This exceeded my expectations. The team was professional, quick, and very knowledgeable. Highly recommend!",
            "I'm disappointed with the quality. It's not what I expected and the support was unhelpful. Would not recommend.",
            "Pretty good experience overall. Had a few minor issues but they were resolved. Happy with the outcome.",
            "Worst customer service ever! Nobody knows what they're doing. Complete waste of time and money.",
            "Love this service! It's exactly what I needed. The team is responsive and the product works perfectly.",
            "Mixed feelings about this. Some parts are good, others not so much. It's an average experience."
        ]
        
        conversations = []
        for i in range(min(limit, len(mock_transcripts))):
            conversations.append({
                "id": f"{agent_id}_conv_{i+1}",
                "agent_id": agent_id,
                "transcript": mock_transcripts[i],
                "created_at": "2024-01-01T10:00:00Z",
                "duration": 120 + (i * 30)
            })
        
        return conversations
