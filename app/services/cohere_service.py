import os
from typing import List, Dict, Any, Optional
import cohere
import numpy as np
import ssl
import httpx
from dotenv import load_dotenv

load_dotenv()

class CohereService:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Cohere service with API key."""
        self.api_key = api_key or os.getenv("COHERE_API_KEY")
        
        if not self.api_key:
            raise ValueError("Cohere API key not provided and not found in environment variables")
        
        # Try multiple SSL configurations to resolve handshake issues
        try:
            # First attempt: Default SSL context with relaxed settings
            ssl_context = ssl.create_default_context()
            ssl_context.set_ciphers('DEFAULT:@SECLEVEL=1')  # Lower security level
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            http_client = httpx.AsyncClient(
                verify=ssl_context,
                timeout=httpx.Timeout(60.0),
                limits=httpx.Limits(max_keepalive_connections=10, max_connections=20)
            )
            
            self.client = cohere.AsyncClient(
                api_key=self.api_key,
                httpx_client=http_client
            )
        except Exception:
            # Fallback: Use default client without custom SSL
            self.client = cohere.AsyncClient(api_key=self.api_key)
    
    async def rerank_documents(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_n: int = 3,
        model: str = "rerank-english-v3.0"
    ) -> List[Dict[str, Any]]:
        """
        Rerank documents based on their relevance to the query.
        
        Args:
            query: The search query
            documents: List of documents with at least 'text' and 'id' keys
            top_n: Number of top results to return
            model: The Cohere rerank model to use
            
        Returns:
            List of reranked documents with scores
        """
        if not documents:
            return []
            
        # Extract text and IDs from documents
        documents_text = [doc.get("text", "") for doc in documents]
        
        # Call Cohere's rerank API
        response = await self.client.rerank(
            model=model,
            query=query,
            documents=documents_text,
            top_n=top_n,
            return_documents=True
        )
        
        # Map results back to original documents with scores
        results = []
        for idx, result in enumerate(response.results):
            original_doc = documents[result.index].copy()
            original_doc["relevance_score"] = result.relevance_score
            original_doc["rank"] = idx + 1
            results.append(original_doc)
            
        return results
    
    async def generate_embeddings(
        self,
        texts: List[str],
        model: str = "embed-v4.0",
        input_type: str = "search_document"
    ) -> List[List[float]]:
        """
        Generate embeddings for a list of texts using Cohere's embedding model.
        
        Args:
            texts: List of text strings to embed
            model: The Cohere embedding model to use
            input_type: The type of input (search_document, search_query, etc.)
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        response = await self.client.embed(
            texts=texts,
            model=model,
            input_type=input_type,
            embedding_types=["float"]
        )
        
        return response.embeddings.float
    
    def format_profile_for_rerank(self, profile: Dict[str, Any]) -> str:
        """
        Convert a professional profile into text format optimized for reranking.
        
        Args:
            profile: Professional profile dictionary
            
        Returns:
            Formatted text string for reranking
        """
        parts = []
        
        # Name and title
        if profile.get("name"):
            parts.append(f"Name: {profile['name']}")
        if profile.get("job_title"):
            parts.append(f"Role: {profile['job_title']}")
        if profile.get("company"):
            parts.append(f"Company: {profile['company']}")
            
        # Bio
        if profile.get("bio"):
            parts.append(f"Bio: {profile['bio']}")
            
        # Skills
        if profile.get("skills"):
            parts.append(f"Skills: {', '.join(profile['skills'])}")
            
        # Education
        if profile.get("education"):
            edu = profile["education"]
            edu_str = f"{edu.get('degree', '')} in {edu.get('field', '')} from {edu.get('university', '')}"
            parts.append(f"Education: {edu_str.strip()}")
            
        # Work history
        if profile.get("work_history"):
            companies = [work.get("company", "") for work in profile["work_history"] if work.get("company")]
            if companies:
                parts.append(f"Previous companies: {', '.join(set(companies))}")
                
        # Industry
        if profile.get("industry"):
            parts.append(f"Industry: {profile['industry']}")
            
        return " | ".join(parts)
    
    async def parse_networking_query(
        self,
        query: str,
        model: str = "command-r-plus-08-2024"
    ) -> Dict[str, Any]:
        """
        Parse a natural language networking query to extract structured criteria.
        
        Args:
            query: Natural language query like "Find AI engineers at Google"
            model: Cohere model to use for parsing
            
        Returns:
            Structured query parameters
        """
        prompt = f"""
Parse this professional networking query and extract structured criteria. Return a JSON object with the following fields:
- job_titles: List of job titles mentioned (e.g., ["AI Engineer", "Software Engineer"])
- companies: List of companies mentioned (e.g., ["Google", "Microsoft"])
- skills: List of skills mentioned (e.g., ["Python", "Machine Learning"])
- industries: List of industries mentioned (e.g., ["Technology", "Healthcare"])
- experience_level: Experience level if mentioned ("junior", "senior", "executive", or "any")
- education: Education requirements if mentioned (e.g., ["Stanford", "MIT"] or ["PhD", "Masters"])
- location: Location if mentioned
- other_criteria: Any other specific requirements

Query: "{query}"

Return only valid JSON:
"""
        
        response = await self.client.chat(
            model=model,
            message=prompt,
            temperature=0.1,
            max_tokens=500
        )
        
        # Parse JSON response
        import json
        result = json.loads(response.text)
        return result
    
    async def generate_introduction_email(
        self,
        requester_profile: Dict[str, Any],
        target_profile: Dict[str, Any],
        mutual_connection: Dict[str, Any],
        context: str,
        model: str = "command-r-plus-08-2024"
    ) -> str:
        """
        Generate a personalized introduction email draft.
        
        Args:
            requester_profile: Profile of person requesting introduction
            target_profile: Profile of person to be introduced to
            mutual_connection: Profile of mutual connection
            context: Context/reason for the introduction
            model: Cohere model to use
            
        Returns:
            Email draft as string
        """
        prompt = f"""
Write a warm, professional introduction email. The email should be:
- Personal and authentic
- Brief but informative
- Clear about the reason for connection
- Include relevant context about both parties

Context:
- Requester: {requester_profile.get('name')} - {requester_profile.get('job_title')} at {requester_profile.get('company')}
- Target: {target_profile.get('name')} - {target_profile.get('job_title')} at {target_profile.get('company')}
- Mutual Connection: {mutual_connection.get('name')} - {mutual_connection.get('job_title')} at {mutual_connection.get('company')}
- Reason: {context}

Requester Bio: {requester_profile.get('bio', '')}
Target Bio: {target_profile.get('bio', '')}

Write the email from the perspective of the mutual connection introducing the requester to the target.
Include subject line and email body.
"""
        
        response = await self.client.chat(
            model=model,
            message=prompt,
            temperature=0.3,
            max_tokens=800
        )
        
        return response.text
