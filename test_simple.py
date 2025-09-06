#!/usr/bin/env python3
"""
Simple test script for the sentiment analysis system.
"""

import asyncio
import sys
import os

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.simple_analyzer import SimpleAnalyzer

async def test_sentiment():
    """Test sentiment analysis with simple examples."""
    print("🧪 Testing Simple Sentiment Analyzer")
    print("=" * 40)
    
    analyzer = SimpleAnalyzer()
    
    test_cases = [
        "I love this service! It's amazing and very helpful.",
        "This is terrible. Very disappointed with the experience.",
        "The agent helped me with my account. It was okay."
    ]
    
    for i, text in enumerate(test_cases, 1):
        print(f"\nTest {i}: {text}")
        result = await analyzer.analyze_sentiment(text)
        print(f"Result: {result['sentiment_label']} (score: {result['sentiment_score']:.2f})")
        print(f"Reasoning: {result['reasoning']}")
    
    await analyzer.close()
    print("\n✅ Tests completed!")

if __name__ == "__main__":
    asyncio.run(test_sentiment())
