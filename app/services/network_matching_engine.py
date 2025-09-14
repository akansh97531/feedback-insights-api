"""
Deep Matching Engine for Professional Network Connections
Combines all components to provide intelligent networking recommendations.
"""
import asyncio
from typing import Dict, List, Any, Optional
import numpy as np
from datetime import datetime

from .cohere_service import CohereService
from .similarity_engine import SimilarityEngine
from .synthetic_data_generator import SyntheticDataGenerator

class NetworkMatchingEngine:
    def __init__(self, cohere_service: CohereService):
        self.cohere = cohere_service
        self.similarity_engine = SimilarityEngine()
        # Store profiles in memory instead of graph DB
        self.profiles_cache = {}
        
    async def initialize_with_synthetic_data(self, num_profiles: int = 20):
        """Initialize the system with synthetic professional network data."""
        print("Initializing Professional Network Matching Engine...")
        
        # Generate synthetic network
        generator = SyntheticDataGenerator()
        network_data = generator.generate_network(num_profiles)
        
        # Store profiles and connections in memory
        # Handle both dict and list formats for profiles
        if isinstance(network_data['profiles'], dict):
            # Profiles are stored as {id: profile} dict
            for profile_id, profile in network_data['profiles'].items():
                self.profiles_cache[profile_id] = profile
        else:
            # Profiles are stored as list
            for profile in network_data['profiles']:
                self.profiles_cache[profile['id']] = profile
            
        # Store connections for lookup from LinkedIn connections in profiles
        self.connections_cache = {}
        for profile_id, profile in self.profiles_cache.items():
            linkedin_connections = profile.get('linkedin_connections', [])
            if linkedin_connections:
                self.connections_cache[profile_id] = linkedin_connections
                
                # Ensure bidirectional connections
                for connection_id in linkedin_connections:
                    if connection_id not in self.connections_cache:
                        self.connections_cache[connection_id] = []
                    if profile_id not in self.connections_cache[connection_id]:
                        self.connections_cache[connection_id].append(profile_id)
        
        print(f"✅ Network initialized with {len(self.profiles_cache)} profiles")
        return {
            "total_profiles": len(self.profiles_cache),
            "total_connections": network_data['metadata']['total_connections'],
            "ready_for_rerank": True
        }
    
    
    async def find_connections(
        self,
        requester_profile_id: str,
        query: str,
        max_results: int = 10,
        include_explanations: bool = True
    ) -> Dict[str, Any]:
        """
        Find the best professional connections based on a natural language query.
        
        Args:
            requester_profile_id: ID of the person making the request
            query: Natural language query like "Find AI engineers at Google"
            max_results: Maximum number of results to return
            include_explanations: Whether to include match explanations
            
        Returns:
            Dictionary with ranked connection recommendations
        """
        start_time = datetime.utcnow()
        
        # Get requester profile
        if requester_profile_id not in self.profiles_cache:
            raise ValueError(f"Profile {requester_profile_id} not found")
        
        requester_profile = self.profiles_cache[requester_profile_id]
        
        # Parse the natural language query
        print(f"Parsing query: '{query}'")
        parsed_query = await self.cohere.parse_networking_query(query)
        
        # Generate query embedding
        query_embedding = None
        try:
            query_embeddings = await self.cohere.generate_embeddings(
                [query], 
                model="embed-v4.0",
                input_type="search_query"
            )
            if query_embeddings:
                query_embedding = query_embeddings[0]
        except Exception as e:
            print(f"Error generating query embedding: {e}")
        
        # Get all candidate profiles (excluding requester)
        candidates = [
            profile for profile in self.profiles_cache.values() 
            if profile["id"] != requester_profile_id
        ]
        
        # For now, use all candidates (no filtering)
        filtered_candidates = candidates
        
        # Prepare documents for reranking
        documents = []
        for candidate in filtered_candidates:
            doc_text = self.cohere.format_profile_for_rerank(candidate)
            documents.append({
                "text": doc_text,
                "id": candidate["id"],
                "profile": candidate
            })
        
        # Use Cohere rerank to get top N results
        ranked_docs = await self.cohere.rerank_documents(
            query=query,
            documents=documents,
            top_n=max_results,
            model="rerank-english-v3.0"
        )
        
        # Convert reranked results to our format
        ranked_results = []
        for i, doc in enumerate(ranked_docs):
            ranked_results.append({
                "profile": doc["profile"],
                "total_score": doc.get("relevance_score", 0.0),
                "scores": {
                    "rerank_score": doc.get("relevance_score", 0.0)
                }
            })
        
        # Format results
        formatted_results = []
        for i, result in enumerate(ranked_results):
            profile = result["profile"]
            scores = result["scores"]
            
            # Find mutual connections
            mutual_connections = self.find_mutual_connections(requester_profile_id, profile["id"])
            
            formatted_result = {
                "rank": i + 1,
                "profile": {
                    "id": profile["id"],
                    "name": profile["name"],
                    "job_title": profile["job_title"],
                    "company": profile["company"],
                    "bio": profile["bio"],
                    "skills": profile["skills"][:5],  # Top 5 skills
                    "education": profile.get("education", {}),
                    "industry": profile.get("industry", "")
                },
                "match_score": round(result["total_score"], 3),
                "score_breakdown": result["scores"],
                "mutual_connections": mutual_connections,
                "connection_path": self._find_shortest_path(requester_profile, profile),
                "explanation": f"Cohere rerank score: {result['total_score']:.3f} • {len(mutual_connections)} mutual connections"
            }
            
            
            formatted_results.append(formatted_result)
        
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        return {
            "query": query,
            "parsed_query": parsed_query,
            "requester": {
                "id": requester_profile["id"],
                "name": requester_profile["name"],
                "job_title": requester_profile["job_title"],
                "company": requester_profile["company"]
            },
            "results": formatted_results,
            "metadata": {
                "total_candidates_evaluated": len(candidates),
                "processing_time_seconds": round(processing_time, 2),
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    
    def find_mutual_connections(self, requester_id: str, target_id: str) -> List[Dict[str, Any]]:
        """Find mutual connections between two profiles."""
        try:
            # Get connections for both profiles from cache
            requester_connections = self.connections_cache.get(requester_id, [])
            target_connections = self.connections_cache.get(target_id, [])
            
            # Find mutual connections
            requester_ids = set(requester_connections)
            target_ids = set(target_connections)
            mutual_ids = requester_ids.intersection(target_ids)
            
            # Get profile details for mutual connections
            mutual_connections = []
            for mutual_id in mutual_ids:
                if mutual_id in self.profiles_cache:
                    profile = self.profiles_cache[mutual_id]
                    mutual_connections.append({
                        "id": profile['id'],
                        "name": profile['name'],
                        "job_title": profile['job_title'],
                        "company": profile['company']
                    })
            
            return mutual_connections[:5]  # Limit to top 5
            
        except Exception as e:
            print(f"Error finding mutual connections: {e}")
            return []
    
    def _find_mutual_connections(self, profile1: Dict[str, Any], profile2: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find mutual connections between two profiles (alias for find_mutual_connections)."""
        return self.find_mutual_connections(profile1["id"], profile2["id"])
    
    def _find_shortest_path(
        self, 
        profile1: Dict[str, Any], 
        profile2: Dict[str, Any]
    ) -> List[str]:
        """Find shortest connection path between two profiles."""
        # For now, return direct connection or 2-hop through mutual connection
        connections1 = set(profile1.get("linkedin_connections", []))
        
        if profile2["id"] in connections1:
            return ["direct"]
        
        # Check for 2-hop connection through mutual connections
        mutual_connections = self._find_mutual_connections(profile1, profile2)
        if mutual_connections:
            return ["2-hop", mutual_connections[0]["name"]]
        
        return ["no_direct_path"]
    
    async def generate_introduction_email(
        self,
        requester_profile_id: str,
        target_profile_id: str,
        context: str = None
    ) -> Dict[str, Any]:
        """Generate a personalized introduction email."""
        if requester_profile_id not in self.profiles_cache:
            raise ValueError(f"Requester profile {requester_profile_id} not found")
        
        if target_profile_id not in self.profiles_cache:
            raise ValueError(f"Target profile {target_profile_id} not found")
        
        requester = self.profiles_cache[requester_profile_id]
        target = self.profiles_cache[target_profile_id]
        
        # Find best mutual connection
        mutual_connections = self._find_mutual_connections(requester, target)
        
        if not mutual_connections:
            return {
                "error": "No mutual connections found for introduction",
                "suggestion": "Consider reaching out directly or finding alternative connection paths"
            }
        
        mutual_connection_id = mutual_connections[0]["id"]
        mutual_connection = self.profiles_cache[mutual_connection_id]
        
        # Generate context if not provided
        if not context:
            context = f"professional networking in {target.get('industry', 'their field')}"
        
        # Generate email
        email_draft = await self.cohere.generate_introduction_email(
            requester, target, mutual_connection, context
        )
        
        return {
            "email_draft": email_draft,
            "mutual_connection": {
                "id": mutual_connection["id"],
                "name": mutual_connection["name"],
                "job_title": mutual_connection["job_title"],
                "company": mutual_connection["company"]
            },
            "context": context
        }
    
    def get_network_stats(self) -> Dict[str, Any]:
        """Get statistics about the professional network."""
        total_profiles = len(self.profiles_cache)
        total_connections = sum(
            len(p.get("linkedin_connections", [])) 
            for p in self.profiles_cache.values()
        ) // 2  # Divide by 2 since connections are bidirectional
        
        # Company distribution
        companies = {}
        industries = {}
        job_titles = {}
        
        for profile in self.profiles_cache.values():
            company = profile.get("company")
            if company:
                companies[company] = companies.get(company, 0) + 1
            
            industry = profile.get("industry")
            if industry:
                industries[industry] = industries.get(industry, 0) + 1
            
            job_title = profile.get("job_title")
            if job_title:
                job_titles[job_title] = job_titles.get(job_title, 0) + 1
        
        return {
            "total_profiles": total_profiles,
            "total_connections": total_connections,
            "average_connections_per_person": round(total_connections * 2 / total_profiles, 1),
            "top_companies": sorted(companies.items(), key=lambda x: x[1], reverse=True)[:10],
            "top_industries": sorted(industries.items(), key=lambda x: x[1], reverse=True)[:5],
            "top_job_titles": sorted(job_titles.items(), key=lambda x: x[1], reverse=True)[:10],
            "rerank_ready": True
        }
