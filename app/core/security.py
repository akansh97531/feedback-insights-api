# Simplified security for public APIs
from typing import Optional
import secrets

def generate_api_key() -> str:
    """Generate a simple API key for basic rate limiting (optional)."""
    return secrets.token_urlsafe(32)

def validate_agent_id(agent_id: str) -> bool:
    """Basic validation for agent ID format."""
    return bool(agent_id and len(agent_id) > 0 and len(agent_id) < 100)
