import openai
from textblob import TextBlob
import nltk
from typing import Dict, List, Tuple, Optional, Any
import re
from collections import Counter
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize

class NLPAnalyzer:
    """Natural Language Processing analyzer for conversation insights."""
    
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None
        self.stop_words = set(stopwords.words('english'))
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of the given text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with sentiment analysis results
        """
        if not text:
            return {
                "sentiment_score": 0.0,
                "sentiment_label": "neutral",
                "confidence": 0.0
            }
        
        try:
            # Use TextBlob for basic sentiment analysis
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity  # -1 to 1
            subjectivity = blob.sentiment.subjectivity  # 0 to 1
            
            # Determine sentiment label
            if polarity > 0.1:
                label = "positive"
            elif polarity < -0.1:
                label = "negative"
            else:
                label = "neutral"
            
            # Use subjectivity as confidence (more subjective = more confident in sentiment)
            confidence = min(abs(polarity) + subjectivity * 0.5, 1.0)
            
            return {
                "sentiment_score": polarity,
                "sentiment_label": label,
                "confidence": confidence,
                "subjectivity": subjectivity
            }
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {str(e)}")
            return {
                "sentiment_score": 0.0,
                "sentiment_label": "neutral",
                "confidence": 0.0
            }
    
    def extract_topics(self, text: str, max_topics: int = 10) -> List[Dict[str, Any]]:
        """
        Extract key topics from text using keyword extraction.
        
        Args:
            text: Text to analyze
            max_topics: Maximum number of topics to return
            
        Returns:
            List of topics with relevance scores
        """
        if not text:
            return []
        
        try:
            # Clean and tokenize text
            text_clean = re.sub(r'[^\w\s]', '', text.lower())
            tokens = word_tokenize(text_clean)
            
            # Remove stop words and short words
            filtered_tokens = [
                word for word in tokens 
                if word not in self.stop_words and len(word) > 2
            ]
            
            # Count word frequencies
            word_freq = Counter(filtered_tokens)
            
            # Extract phrases (bigrams and trigrams)
            sentences = sent_tokenize(text)
            phrases = []
            
            for sentence in sentences:
                words = word_tokenize(sentence.lower())
                words = [w for w in words if w.isalpha() and w not in self.stop_words]
                
                # Bigrams
                for i in range(len(words) - 1):
                    phrase = f"{words[i]} {words[i+1]}"
                    phrases.append(phrase)
                
                # Trigrams
                for i in range(len(words) - 2):
                    phrase = f"{words[i]} {words[i+1]} {words[i+2]}"
                    phrases.append(phrase)
            
            phrase_freq = Counter(phrases)
            
            # Combine single words and phrases
            all_topics = []
            
            # Add single words
            for word, freq in word_freq.most_common(max_topics):
                relevance = freq / len(filtered_tokens)
                all_topics.append({
                    "name": word,
                    "type": "keyword",
                    "relevance_score": relevance,
                    "mentions_count": freq
                })
            
            # Add phrases
            for phrase, freq in phrase_freq.most_common(max_topics // 2):
                if freq > 1:  # Only include phrases mentioned more than once
                    relevance = freq / len(phrases)
                    all_topics.append({
                        "name": phrase,
                        "type": "phrase",
                        "relevance_score": relevance,
                        "mentions_count": freq
                    })
            
            # Sort by relevance and return top topics
            all_topics.sort(key=lambda x: x["relevance_score"], reverse=True)
            return all_topics[:max_topics]
            
        except Exception as e:
            logger.error(f"Error extracting topics: {str(e)}")
            return []
    
    async def generate_summary_with_openai(self, text: str, max_length: int = 200) -> Optional[str]:
        """
        Generate a summary using OpenAI GPT.
        
        Args:
            text: Text to summarize
            max_length: Maximum length of summary
            
        Returns:
            Generated summary or None if OpenAI is not available
        """
        if not self.openai_client or not text:
            return None
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a helpful assistant that summarizes user feedback conversations. Create a concise summary in {max_length} words or less, focusing on key points, sentiment, and actionable insights."
                    },
                    {
                        "role": "user",
                        "content": f"Please summarize this conversation:\n\n{text}"
                    }
                ],
                max_tokens=max_length,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating summary with OpenAI: {str(e)}")
            return None
    
    def analyze_conversation_quality(self, text: str) -> Dict[str, Any]:
        """
        Analyze the quality and characteristics of a conversation.
        
        Args:
            text: Conversation text
            
        Returns:
            Dictionary with quality metrics
        """
        if not text:
            return {
                "word_count": 0,
                "sentence_count": 0,
                "avg_sentence_length": 0,
                "readability_score": 0,
                "question_count": 0,
                "exclamation_count": 0
            }
        
        try:
            # Basic metrics
            words = word_tokenize(text)
            sentences = sent_tokenize(text)
            
            word_count = len(words)
            sentence_count = len(sentences)
            avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
            
            # Count questions and exclamations
            question_count = text.count('?')
            exclamation_count = text.count('!')
            
            # Simple readability score (based on avg sentence length)
            if avg_sentence_length <= 15:
                readability_score = 1.0  # Easy
            elif avg_sentence_length <= 25:
                readability_score = 0.7  # Medium
            else:
                readability_score = 0.4  # Hard
            
            return {
                "word_count": word_count,
                "sentence_count": sentence_count,
                "avg_sentence_length": round(avg_sentence_length, 2),
                "readability_score": readability_score,
                "question_count": question_count,
                "exclamation_count": exclamation_count
            }
            
        except Exception as e:
            logger.error(f"Error analyzing conversation quality: {str(e)}")
            return {
                "word_count": 0,
                "sentence_count": 0,
                "avg_sentence_length": 0,
                "readability_score": 0,
                "question_count": 0,
                "exclamation_count": 0
            }
