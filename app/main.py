"""
Professional Network Matching Engine API
Builds intelligent networking recommendations using Cohere and graph analysis.
"""
from fastapi import FastAPI, HTTPException, Depends, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import logging
import os
from datetime import datetime

from app.services.network_matching_engine import NetworkMatchingEngine
from app.services.cohere_service import CohereService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize services
cohere_service = CohereService()
matching_engine = NetworkMatchingEngine(cohere_service)

# Global flag to track initialization
network_initialized = False

# Create FastAPI app
app = FastAPI(
    title="Professional Network Matching Engine",
    description="AI-powered professional networking recommendations using Cohere and graph analysis",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class NetworkingQuery(BaseModel):
    requester_id: str = Field(..., description="ID of the person making the networking request")
    query: str = Field(..., description="Natural language networking query")
    max_results: int = Field(10, description="Maximum number of connection recommendations")
    include_explanations: bool = Field(True, description="Include match explanations")

class IntroductionRequest(BaseModel):
    requester_id: str = Field(..., description="ID of person requesting introduction")
    target_id: str = Field(..., description="ID of person to be introduced to")
    context: Optional[str] = Field(None, description="Context or reason for introduction")

class InitializeRequest(BaseModel):
    num_profiles: int = Field(50, description="Number of synthetic profiles to generate")

@app.get("/")
async def root():
    return {
        "message": "Professional Network Matching Engine",
        "version": "1.0.0",
        "description": "AI-powered professional networking recommendations",
        "features": [
            "Natural Language Query Processing",
            "Multi-Metric Similarity Scoring",
            "Cohere Embeddings & Re-ranking",
            "Introduction Email Generation",
            "Graph-based Connection Analysis"
        ],
        "endpoints": {
            "initialize": "/initialize",
            "find_connections": "/find-connections",
            "generate_introduction": "/generate-introduction",
            "network_stats": "/network-stats",
            "health": "/health",
            "docs": "/docs"
        },
        "network_initialized": network_initialized
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for Railway deployment."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Professional Network Matching Engine",
        "version": "1.0.0"
    }

@app.post("/initialize")
async def initialize_network(request: InitializeRequest):
    """Initialize the professional network with synthetic data."""
    global network_initialized
    
    try:
        logger.info(f"Initializing network with {request.num_profiles} profiles...")
        
        result = await matching_engine.initialize_with_synthetic_data(request.num_profiles)
        network_initialized = True
        
        return {
            "message": "Professional network initialized successfully",
            "initialization_stats": result,
            "ready_for_queries": True
        }
        
    except Exception as e:
        import traceback
        logger.error(f"Error initializing network: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to initialize network: {str(e)}")

@app.post("/find-connections")
async def find_connections(request: NetworkingQuery):
    """Find professional connections based on natural language query."""
    if not network_initialized:
        raise HTTPException(
            status_code=400, 
            detail="Network not initialized. Please call /initialize first."
        )
    
    try:
        logger.info(f"Processing networking query: '{request.query}' for user {request.requester_id}")
        
        results = await matching_engine.find_connections(
            requester_profile_id=request.requester_id,
            query=request.query,
            max_results=request.max_results,
            include_explanations=request.include_explanations
        )
        
        return results
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error finding connections: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to find connections: {str(e)}")

@app.post("/generate-introduction")
async def generate_introduction(request: IntroductionRequest):
    """Generate a personalized introduction email."""
    if not network_initialized:
        raise HTTPException(
            status_code=400, 
            detail="Network not initialized. Please call /initialize first."
        )
    
    try:
        logger.info(f"Generating introduction from {request.requester_id} to {request.target_id}")
        
        result = await matching_engine.generate_introduction_email(
            requester_profile_id=request.requester_id,
            target_profile_id=request.target_id,
            context=request.context
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating introduction: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate introduction: {str(e)}")

@app.get("/network-stats")
async def get_network_stats():
    """Get statistics about the professional network."""
    if not network_initialized:
        raise HTTPException(
            status_code=400, 
            detail="Network not initialized. Please call /initialize first."
        )
    
    try:
        stats = matching_engine.get_network_stats()
        return stats
        
    except Exception as e:
        logger.error(f"Error getting network stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/profiles")
async def list_profiles(
    limit: int = 20,
    offset: int = 0,
    company: Optional[str] = None,
    job_title: Optional[str] = None
):
    """List professional profiles with optional filtering."""
    if not network_initialized:
        raise HTTPException(
            status_code=400, 
            detail="Network not initialized. Please call /initialize first."
        )
    
    try:
        profiles = list(matching_engine.profiles_cache.values())
        
        # Apply filters
        if company:
            profiles = [p for p in profiles if company.lower() in p.get("company", "").lower()]
        if job_title:
            profiles = [p for p in profiles if job_title.lower() in p.get("job_title", "").lower()]
        
        # Paginate
        total = len(profiles)
        profiles = profiles[offset:offset + limit]
        
        # Format for response
        formatted_profiles = []
        for profile in profiles:
            formatted_profiles.append({
                "id": profile["id"],
                "name": profile["name"],
                "job_title": profile["job_title"],
                "company": profile["company"],
                "industry": profile.get("industry"),
                "skills": profile.get("skills", [])[:5],  # Top 5 skills
                "bio": profile.get("bio", "")[:150] + "..." if len(profile.get("bio", "")) > 150 else profile.get("bio", "")
            })
        
        return {
            "profiles": formatted_profiles,
            "pagination": {
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < total
            }
        }
        
    except Exception as e:
        logger.error(f"Error listing profiles: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
