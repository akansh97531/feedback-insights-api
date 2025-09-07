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
    
    async def get_latest_conversation(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Fetch only the latest conversation for a specific voice agent."""
        conversations = await self.get_agent_conversations(agent_id, limit=50)
        return conversations[0] if conversations else None
    
    async def get_agent_conversations(self, agent_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Fetch conversations for a specific voice agent."""
        if not self.api_key:
            raise ValueError("ElevenLabs API key is required. Set ELEVENLABS_API_KEY environment variable.")
        
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
                    
                    # Get conversation IDs from the response - check multiple possible structures
                    conversation_ids = []
                    
                    # Try different possible response structures
                    if "history" in data:
                        for item in data["history"]:
                            if "conversation_id" in item:
                                conversation_ids.append(item["conversation_id"])
                    elif "conversations" in data:
                        for item in data["conversations"]:
                            if "conversation_id" in item:
                                conversation_ids.append(item["conversation_id"])
                            elif "id" in item:
                                conversation_ids.append(item["id"])
                    elif isinstance(data, list):
                        for item in data:
                            if "conversation_id" in item:
                                conversation_ids.append(item["conversation_id"])
                            elif "id" in item:
                                conversation_ids.append(item["id"])
                    
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
                    
                    return conversations
                else:
                    raise Exception(f"ElevenLabs API error: {response.status_code} - {response.text}")
                    
        except Exception as e:
            raise Exception(f"Error fetching from ElevenLabs: {e}")
    
    def _extract_transcript_from_conversation(self, conversation: Dict[str, Any]) -> str:
        """Extract transcript text from detailed conversation data."""
        # Handle ElevenLabs API format: transcript is array of message objects
        if "transcript" in conversation:
            transcript_data = conversation["transcript"]
            
            # If transcript is already a string, return it
            if isinstance(transcript_data, str):
                return transcript_data
            
            # If transcript is an array of message objects (ElevenLabs format)
            if isinstance(transcript_data, list):
                messages = []
                for msg in transcript_data:
                    if isinstance(msg, dict) and "message" in msg:
                        role = msg.get("role", "unknown")
                        message = msg["message"]
                        messages.append(f"{role.title()}: {message}")
                return " ".join(messages)
        
        # Check for conversation turns/messages (fallback formats)
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
    
