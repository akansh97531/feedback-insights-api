"""
Test script for the Chat API with Graph DB and Cohere Rerank.
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
BASE_URL = "http://localhost:8000"  # Update if your server runs on a different port
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

if not COHERE_API_KEY:
    raise ValueError("COHERE_API_KEY environment variable not set")

async def test_health():
    """Test the health check endpoint."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/health")
        print("\n=== Health Check ===")
        pprint(response.json())
        return response.status_code == 200

async def create_sample_graph():
    """Create a sample knowledge graph for testing."""
    async with httpx.AsyncClient() as client:
        # Create nodes
        products = [
            {"label": "Smartphone", "properties": {"type": "electronics", "price": 699.99, "in_stock": True}},
            {"label": "Laptop", "properties": {"type": "electronics", "price": 1299.99, "in_stock": True}},
            {"label": "Headphones", "properties": {"type": "electronics", "price": 199.99, "in_stock": False}},
            {"label": "Book", "properties": {"type": "books", "price": 19.99, "in_stock": True}},
            {"label": "Customer Support", "properties": {"type": "service", "availability": "24/7"}},
            {"label": "Express Shipping", "properties": {"type": "shipping", "delivery_time": "1-2 days", "price": 9.99}}
        ]
        
        node_ids = []
        for product in products:
            response = await client.post(
                f"{BASE_URL}/nodes",
                json={"label": product["label"], "properties": product["properties"]}
            )
            node_data = response.json()
            node_id = node_data.get("node_id")
            if node_id is not None:
                node_ids.append(node_id)
                print(f"Created node {node_id}: {product['label']}")
        
        # Create relationships
        relationships = [
            (0, 4, "HAS_SUPPORT", {}),  # Smartphone -> Customer Support
            (1, 4, "HAS_SUPPORT", {}),  # Laptop -> Customer Support
            (0, 5, "HAS_SHIPPING_OPTION", {}),  # Smartphone -> Express Shipping
            (1, 5, "HAS_SHIPPING_OPTION", {}),  # Laptop -> Express Shipping
            (2, 5, "HAS_SHIPPING_OPTION", {})   # Headphones -> Express Shipping
        ]
        
        for src_idx, tgt_idx, rel_type, props in relationships:
            if src_idx < len(node_ids) and tgt_idx < len(node_ids):
                response = await client.post(
                    f"{BASE_URL}/edges",
                    json={
                        "source": node_ids[src_idx],
                        "target": node_ids[tgt_idx],
                        "relationship": rel_type,
                        "properties": props
                    }
                )
                print(f"Created edge: {node_ids[src_idx]} --[{rel_type}]--> {node_ids[tgt_idx]}")
        
        return node_ids

async def test_chat(query: str, max_results: int = 3):
    """Test the chat endpoint with a query."""
    async with httpx.AsyncClient() as client:
        messages = [{"role": "user", "content": query}]
        
        print(f"\n=== Chat Query ===\nUser: {query}")
        
        response = await client.post(
            f"{BASE_URL}/chat",
            json={
                "messages": messages,
                "max_results": max_results
            }
        )
        
        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            print(response.text)
            return
        
        result = response.json()
        print("\nResponse:")
        print("-" * 50)
        print(result["response"])
        print("\nRelevant Nodes:")
        for node in result["relevant_nodes"]:
            print(f"- {node['label']} (ID: {node['id']}, Score: {node.get('score', 0):.2f})")
        print("=" * 50)
        
        return result

async def main():
    """Run all tests."""
    print("=== Starting Chat API Tests ===\n")
    
    # Test health check
    health_ok = await test_health()
    if not health_ok:
        print("Health check failed. Is the server running?")
        return
    
    # Create sample data
    print("\n=== Creating Sample Graph ===")
    await create_sample_graph()
    
    # Test chat queries
    test_queries = [
        "What electronics do you have in stock?",
        "Tell me about your shipping options",
        "What's the price of the most expensive item?",
        "Do you offer customer support for laptops?"
    ]
    
    for query in test_queries:
        await test_chat(query)
        await asyncio.sleep(1)  # Rate limiting

if __name__ == "__main__":
    asyncio.run(main())
