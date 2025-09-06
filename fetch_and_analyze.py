#!/usr/bin/env python3
"""
Fetch all conversations from ElevenLabs and analyze sentiment.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.elevenlabs_client import ElevenLabsClient
from app.services.simple_analyzer import SimpleAnalyzer

async def fetch_and_analyze():
    """Fetch conversations and analyze sentiment."""
    print("🎙️ Fetching ElevenLabs Conversations & Analyzing Sentiment")
    print("=" * 60)
    
    # Initialize services
    client = ElevenLabsClient()
    analyzer = SimpleAnalyzer()
    
    try:
        # Fetch conversations
        print("📡 Fetching conversations from ElevenLabs...")
        conversations = await client.get_conversations(limit=50)
        
        if not conversations:
            print("❌ No conversations found or API key not set")
            return
        
        print(f"✅ Found {len(conversations)} conversations")
        print("\n" + "="*60)
        
        # Analyze each conversation
        for i, conv in enumerate(conversations, 1):
            print(f"\n🔍 Conversation {i}/{len(conversations)}")
            print(f"ID: {getattr(conv, 'conversation_id', 'unknown')}")
            
            # Get full transcript - handle different data structures
            transcript = ""
            if hasattr(conv, 'transcript') and conv.transcript:
                transcript = conv.transcript
            elif hasattr(conv, 'summary') and conv.summary:
                transcript = conv.summary
            elif hasattr(conv, 'messages') and conv.messages:
                # Combine all messages
                messages = []
                for msg in conv.messages:
                    if isinstance(msg, dict):
                        content = msg.get('content', '')
                    else:
                        content = getattr(msg, 'content', '')
                    if content:
                        messages.append(content)
                transcript = " ".join(messages)
            
            if not transcript:
                print("⚠️  No transcript available")
                continue
                
            print(f"Transcript: {transcript[:100]}{'...' if len(transcript) > 100 else ''}")
            
            # Analyze sentiment
            sentiment = await analyzer.analyze_sentiment(transcript)
            
            print(f"📊 Sentiment: {sentiment['sentiment_label'].upper()}")
            print(f"   Score: {sentiment['sentiment_score']:.2f}")
            print(f"   Confidence: {sentiment['confidence']:.2f}")
            print(f"   Reasoning: {sentiment['reasoning']}")
            
            if i < len(conversations):
                print("-" * 40)
        
        print(f"\n✅ Analyzed {len(conversations)} conversations successfully!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        
    finally:
        await analyzer.close()

if __name__ == "__main__":
    asyncio.run(fetch_and_analyze())
