from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from app.core.config import settings
from app.api.endpoints import router
from app.api.webhook_endpoints import webhook_router
from app.db.database import engine
from app.models import conversation

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
conversation.Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="Feedback Insights API",
    description="Real-time sentiment analysis and insights from ElevenLabs Voice Agent conversations",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware for public API access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1", tags=["insights"])
app.include_router(webhook_router, prefix="/api/v1", tags=["webhooks"])

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Feedback Insights API",
        "version": "1.0.0",
        "description": "Real-time sentiment analysis from ElevenLabs Voice Agent conversations",
        "docs": "/docs",
        "endpoints": {
            "sync_conversations": "/api/v1/sync-conversations/{agent_id}",
            "sentiment_overview": "/api/v1/sentiment-overview/{agent_id}",
            "key_insights": "/api/v1/insights/{agent_id}",
            "trending_topics": "/api/v1/trending-topics/{agent_id}",
            "sentiment_trend": "/api/v1/sentiment-trend/{agent_id}",
            "dashboard": "/api/v1/dashboard/{agent_id}",
            "webhook": "/api/v1/webhook/elevenlabs",
            "webhook_sync": "/api/v1/webhook/elevenlabs/sync",
            "webhook_test": "/api/v1/webhook/test"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
