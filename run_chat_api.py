#!/usr/bin/env python3
"""
Run the Professional Network Matching API server.
"""
import uvicorn
from app.main import app

if __name__ == "__main__":
    # Run the FastAPI app with Uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
