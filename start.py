#!/usr/bin/env python3
"""
Quick start script for the Feedback Insights API
"""
import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """Check if required packages are installed."""
    try:
        import fastapi
        import sqlalchemy
        import httpx
        import nltk
        import textblob
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("Run: pip install -r requirements.txt")
        return False

def check_env_file():
    """Check if .env file exists."""
    if not Path(".env").exists():
        print("⚠️  .env file not found. Creating from template...")
        subprocess.run(["cp", ".env.example", ".env"])
        print("✅ Created .env file from template")
        print("📝 Please edit .env file with your API keys:")
        print("   - ELEVENLABS_API_KEY")
        print("   - DATABASE_URL")
        print("   - OPENAI_API_KEY (optional)")
        return False
    return True

def main():
    print("🚀 Starting Feedback Insights API...")
    
    if not check_requirements():
        sys.exit(1)
    
    if not check_env_file():
        print("\n💡 After updating .env, run this script again to start the server")
        sys.exit(1)
    
    print("✅ Environment setup complete")
    print("🌐 Starting FastAPI server...")
    print("📊 API Documentation: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/health")
    
    # Start the server
    os.system("uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")

if __name__ == "__main__":
    main()
