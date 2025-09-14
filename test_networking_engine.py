"""
Test script for the Professional Network Matching Engine MVP
Demonstrates the core functionality with sample queries.
"""
import asyncio
import json
import os
from pprint import pprint
from typing import Dict, Any, List
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BASE_URL = "http://localhost:8000"
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

if not COHERE_API_KEY:
    print("⚠️  COHERE_API_KEY environment variable not set")
    print("Please add your Cohere API key to the .env file")
    exit(1)

async def test_health():
    """Test the health check endpoint."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/health")
        print("\n=== Health Check ===")
        pprint(response.json())
        return response.status_code == 200

async def initialize_network(num_profiles: int = 50):
    """Initialize the professional network."""
    async with httpx.AsyncClient(timeout=120.0) as client:  # Extended timeout for initialization
        print(f"\n=== Initializing Network with {num_profiles} Profiles ===")
        
        response = await client.post(
            f"{BASE_URL}/initialize",
            json={"num_profiles": num_profiles}
        )
        
        if response.status_code != 200:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            return False
        
        result = response.json()
        print("✅ Network initialized successfully!")
        print(f"📊 Stats: {result['initialization_stats']}")
        return True

async def get_network_stats():
    """Get network statistics."""
    async with httpx.AsyncClient() as client:
        print("\n=== Network Statistics ===")
        
        response = await client.get(f"{BASE_URL}/network-stats")
        
        if response.status_code != 200:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            return
        
        stats = response.json()
        print(f"👥 Total Profiles: {stats['total_profiles']}")
        print(f"🔗 Total Connections: {stats['total_connections']}")
        print(f"📈 Avg Connections per Person: {stats['average_connections_per_person']}")
        print(f"🏢 Top Companies: {stats['top_companies'][:5]}")
        print(f"🏭 Top Industries: {stats['top_industries']}")

async def list_sample_profiles():
    """List some sample profiles to get IDs for testing."""
    async with httpx.AsyncClient() as client:
        print("\n=== Sample Profiles ===")
        
        response = await client.get(f"{BASE_URL}/profiles?limit=10")
        
        if response.status_code != 200:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            return []
        
        result = response.json()
        profiles = result["profiles"]
        
        print("📋 Available profiles for testing:")
        for i, profile in enumerate(profiles):
            print(f"{i+1}. {profile['name']} - {profile['job_title']} at {profile['company']} (ID: {profile['id']})")
        
        return profiles

async def test_networking_query(requester_id: str, query: str, max_results: int = 5):
    """Test a networking query."""
    async with httpx.AsyncClient(timeout=60.0) as client:
        print(f"\n=== Networking Query ===")
        print(f"👤 Requester: {requester_id}")
        print(f"🔍 Query: '{query}'")
        
        response = await client.post(
            f"{BASE_URL}/find-connections",
            json={
                "requester_id": requester_id,
                "query": query,
                "max_results": max_results,
                "include_explanations": True
            }
        )
        
        if response.status_code != 200:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            return None
        
        result = response.json()
        
        print(f"⚡ Processing time: {result['metadata']['processing_time_seconds']}s")
        print(f"🎯 Query parsed as: {result['parsed_query']}")
        print(f"📊 Found {len(result['results'])} matches:")
        
        for i, match in enumerate(result['results'][:3]):  # Show top 3
            profile = match['profile']
            print(f"\n{i+1}. {profile['name']} - {profile['job_title']} at {profile['company']}")
            print(f"   📈 Match Score: {match['match_score']}")
            print(f"   💡 Explanation: {match.get('explanation', 'N/A')}")
            print(f"   🤝 Mutual Connections: {len(match['mutual_connections'])}")
            
            # Show score breakdown
            scores = match['score_breakdown']
            print(f"   📊 Score Breakdown:")
            print(f"      • Semantic: {scores['semantic_similarity']}")
            print(f"      • Relationship: {scores['relationship_strength']}")
            print(f"      • Mutual Connections: {scores['mutual_connections']}")
            print(f"      • Company Overlap: {scores['company_overlap']}")
            print(f"      • Education: {scores['education_similarity']}")
            print(f"      • Query Relevance: {scores['query_relevance']}")
        
        return result

async def test_introduction_email(requester_id: str, target_id: str, context: str = None):
    """Test introduction email generation."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        print(f"\n=== Introduction Email Generation ===")
        print(f"👤 From: {requester_id}")
        print(f"🎯 To: {target_id}")
        print(f"📝 Context: {context or 'General networking'}")
        
        response = await client.post(
            f"{BASE_URL}/generate-introduction",
            json={
                "requester_id": requester_id,
                "target_id": target_id,
                "context": context
            }
        )
        
        if response.status_code != 200:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            return None
        
        result = response.json()
        
        if "error" in result:
            print(f"❌ {result['error']}")
            print(f"💡 {result.get('suggestion', '')}")
            return None
        
        print(f"✅ Email generated via: {result['mutual_connection']['name']}")
        print(f"📧 Email Draft:")
        print("=" * 50)
        print(result['email_draft'])
        print("=" * 50)
        
        return result

async def run_comprehensive_test():
    """Run a comprehensive test of the networking engine."""
    print("🚀 Starting Professional Network Matching Engine Test")
    print("=" * 60)
    
    # Test health
    health_ok = await test_health()
    if not health_ok:
        print("❌ Health check failed. Is the server running?")
        return
    
    # Initialize network
    init_ok = await initialize_network(50)
    if not init_ok:
        print("❌ Network initialization failed.")
        return
    
    # Get network stats
    await get_network_stats()
    
    # List sample profiles
    profiles = await list_sample_profiles()
    if len(profiles) < 2:
        print("❌ Not enough profiles for testing.")
        return
    
    # Test networking queries
    test_queries = [
        "Find AI engineers who have worked at Google or DeepMind",
        "Connect me to senior product managers with startup experience",
        "Looking for data scientists in healthcare or biotech",
        "Find software engineers with Python and machine learning skills",
        "Connect me to VPs or directors in technology companies"
    ]
    
    requester_id = profiles[0]["id"]  # Use first profile as requester
    
    query_results = []
    for query in test_queries:
        result = await test_networking_query(requester_id, query, max_results=3)
        if result and result['results']:
            query_results.append((query, result))
        await asyncio.sleep(1)  # Rate limiting
    
    # Test introduction email generation
    if query_results:
        query, result = query_results[0]  # Use first successful query
        if result['results']:
            target_id = result['results'][0]['profile']['id']
            await test_introduction_email(
                requester_id, 
                target_id, 
                f"collaboration on {query.lower()}"
            )
    
    print("\n🎉 Comprehensive test completed!")
    print("=" * 60)

async def run_quick_demo():
    """Run a quick demo with predefined scenarios."""
    print("⚡ Quick Demo - Professional Network Matching Engine")
    print("=" * 50)
    
    # Health check
    if not await test_health():
        return
    
    # Initialize with smaller network for speed
    if not await initialize_network(30):
        return
    
    # Get some profiles
    profiles = await list_sample_profiles()
    if len(profiles) < 2:
        return
    
    requester_id = profiles[0]["id"]
    
    # Test one query
    await test_networking_query(
        requester_id, 
        "Find AI engineers at technology companies", 
        max_results=3
    )
    
    print("\n✅ Quick demo completed!")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        asyncio.run(run_quick_demo())
    else:
        asyncio.run(run_comprehensive_test())
