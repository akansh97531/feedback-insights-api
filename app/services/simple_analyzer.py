import logging
import re
from typing import Dict, List, Any
import asyncio
import httpx

logger = logging.getLogger(__name__)

class SimpleAnalyzer:
    """
    Ultra-simple sentiment analyzer with Ollama fallback.
    """
    
    def __init__(self):
        self.ollama_url = "http://localhost:11434"
        self.use_ollama = self._check_ollama()
        
        # Simple word lists for rule-based analysis
        self.positive_words = {
            'excellent', 'amazing', 'great', 'good', 'fantastic', 'wonderful', 'awesome',
            'love', 'perfect', 'best', 'outstanding', 'satisfied', 'happy', 'pleased',
            'helpful', 'friendly', 'professional', 'quick', 'fast', 'efficient',
            'thank', 'thanks', 'grateful', 'appreciate', 'recommend'
        }
        
        self.negative_words = {
            'terrible', 'awful', 'bad', 'horrible', 'worst', 'hate', 'frustrated',
            'angry', 'disappointed', 'annoyed', 'upset', 'useless', 'broken',
            'failed', 'error', 'problem', 'issue', 'slow', 'confusing', 'rude',
            'waste', 'regret', 'complaint', 'dissatisfied'
        }
        
        logger.info(f"✅ Simple analyzer initialized ({'Ollama' if self.use_ollama else 'Rule-based'})")
    
    def _check_ollama(self) -> bool:
        """Check if Ollama is available."""
        try:
            import httpx
            with httpx.Client(timeout=5.0) as client:
                response = client.get(f"{self.ollama_url}/api/tags")
                if response.status_code == 200:
                    models = response.json().get("models", [])
                    # Check if we have qwen2:7b available
                    return any("qwen2" in model.get("name", "") for model in models)
                return False
        except:
            return False
    
    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment using Ollama or rules."""
        if not text:
            return self._neutral_response("No text provided")
        
        if self.use_ollama:
            try:
                return await self._ollama_analysis(text)
            except:
                logger.warning("Ollama failed, using rules")
                return self._rule_analysis(text)
        else:
            return self._rule_analysis(text)
    
    async def _ollama_analysis(self, text: str) -> Dict[str, Any]:
        """Simple Ollama analysis."""
        prompt = f"Analyze sentiment of: '{text}'. Reply with just: positive, negative, or neutral"
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": "qwen2:7b",
                    "prompt": prompt,
                    "stream": False
                }
            )
            
            if response.status_code == 200:
                result = response.json().get("response", "").strip().lower()
                
                if "positive" in result:
                    return {"sentiment_label": "positive", "sentiment_score": 0.7, "confidence": 0.8}
                elif "negative" in result:
                    return {"sentiment_label": "negative", "sentiment_score": -0.7, "confidence": 0.8}
                else:
                    return {"sentiment_label": "neutral", "sentiment_score": 0.0, "confidence": 0.6}
            
            return self._rule_analysis(text)
    
    def _rule_analysis(self, text: str) -> Dict[str, Any]:
        """Simple rule-based analysis."""
        words = re.findall(r'\b\w+\b', text.lower())
        
        positive_count = sum(1 for word in words if word in self.positive_words)
        negative_count = sum(1 for word in words if word in self.negative_words)
        
        sentiment_score = 0.6 if positive_count > negative_count else -0.6
        sentiment_label = "positive" if positive_count > negative_count else "negative"
        confidence = 0.7
        emotions = ["happy", "sad", "angry"]
        
        if positive_count > negative_count:
            return {
                "sentiment_label": "positive",
                "sentiment_score": 0.6,
                "confidence": 0.7
            }
        elif negative_count > positive_count:
            return {
                "sentiment_label": "negative", 
                "sentiment_score": -0.6,
                "confidence": 0.7
            }
        else:
            return self._neutral_response("No clear sentiment detected")
    
    def _neutral_response(self, reason: str) -> Dict[str, Any]:
        """Return neutral sentiment."""
        return {
            "sentiment_label": "neutral",
            "sentiment_score": 0.0,
            "confidence": 0.5
        }
    
    async def extract_topics(self, text: str, max_topics: int = 5) -> List[Dict[str, Any]]:
        """Simple topic extraction."""
        words = re.findall(r'\b\w{4,}\b', text.lower())
        word_count = {}
        
        # Skip common words
        skip_words = {'this', 'that', 'with', 'have', 'will', 'from', 'they', 'been', 'were', 'said', 'each', 'which', 'their', 'time', 'about'}
        
        for word in words:
            if word not in skip_words:
                word_count[word] = word_count.get(word, 0) + 1
        
        topics = []
        for word, count in sorted(word_count.items(), key=lambda x: x[1], reverse=True)[:max_topics]:
            if count > 1:
                topics.append({
                    "name": word,
                    "relevance_score": min(count / len(words) * 3, 1.0),
                    "mentions_count": count
                })
        
        return topics
    
    async def generate_summary(self, text: str, max_length: int = 100) -> str:
        """Simple summary generation."""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
        
        if not sentences:
            return "No summary available"
        
        # Return first sentence or truncated text
        summary = sentences[0]
        if len(summary) > max_length:
            summary = summary[:max_length] + "..."
        
        return summary
    
    async def health_check(self) -> bool:
        """Check if analyzer works."""
        try:
            result = await self.analyze_sentiment("test")
            return "sentiment_label" in result
        except:
            return False
    
    async def close(self):
        """Cleanup."""
        pass
