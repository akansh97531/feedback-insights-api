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
                # Try to fetch real conversations from ElevenLabs API
                response = await client.get(
                    f"{self.base_url}/convai/conversations",
                    headers=self.headers,
                    params={
                        "agent_id": agent_id,
                        "limit": limit
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    conversations = []
                    
                    for conv in data.get("conversations", []):
                        # Extract transcript from conversation
                        transcript = self._extract_transcript(conv)
                        if transcript:
                            conversations.append({
                                "id": conv.get("conversation_id", "unknown"),
                                "agent_id": agent_id,
                                "transcript": transcript,
                                "created_at": conv.get("created_at", ""),
                                "duration": conv.get("duration_seconds", 0)
                            })
                    
                    return conversations
                else:
                    print(f"ElevenLabs API error: {response.status_code}")
                    return self._get_mock_conversations(agent_id, limit)
                    
        except Exception as e:
            print(f"Error fetching from ElevenLabs: {e}")
            return self._get_mock_conversations(agent_id, limit)
    
    def _extract_transcript(self, conversation: Dict[str, Any]) -> str:
        """Extract transcript text from conversation data."""
        # Try different possible transcript fields
        if "transcript" in conversation:
            return conversation["transcript"]
        
        if "messages" in conversation:
            messages = []
            for msg in conversation["messages"]:
                if isinstance(msg, dict) and "content" in msg:
                    messages.append(msg["content"])
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
