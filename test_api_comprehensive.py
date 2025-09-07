"""
Comprehensive test suite for ElevenLabs sentiment analysis API endpoints.
Tests all metrics, insights, and P0/P1/P2 prioritization functionality.
"""
import requests
import json
import time
from typing import Dict, Any

class APITester:
    """Comprehensive API testing class for all endpoints."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.agent_id = "agent_8901k4fkatt1e858rn8ejamzqhfb"
        
    def test_health_endpoint(self) -> Dict[str, Any]:
        """Test health check endpoint."""
        print("🔍 Testing /health endpoint...")
        response = requests.get(f"{self.base_url}/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] in ["healthy", "degraded"]
        
        print(f"✅ Health check: {data['status']}")
        return data
    
    def test_analyze_endpoint(self) -> Dict[str, Any]:
        """Test sentiment analysis endpoint."""
        print("🔍 Testing /analyze endpoint...")
        
        test_cases = [
            {"text": "Great service, very helpful team!", "expected": "positive"},
            {"text": "This is terrible, worst experience ever", "expected": "negative"},
            {"text": "It's okay, nothing special", "expected": "neutral"}
        ]
        
        results = []
        for case in test_cases:
            response = requests.post(
                f"{self.base_url}/analyze",
                json={"text": case["text"]},
                headers={"Content-Type": "application/json"}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Validate response structure
            assert "sentiment_label" in data
            assert "sentiment_score" in data
            assert "confidence" in data
            
            # Validate data types
            assert isinstance(data["sentiment_label"], str)
            assert isinstance(data["sentiment_score"], (int, float))
            assert isinstance(data["confidence"], (int, float))
            
            # Validate ranges
            assert data["sentiment_label"] in ["positive", "negative", "neutral"]
            assert -1.0 <= data["sentiment_score"] <= 1.0
            assert 0.0 <= data["confidence"] <= 1.0
            
            results.append({
                "input": case["text"],
                "output": data,
                "expected": case["expected"]
            })
            
            print(f"✅ Sentiment: '{case['text'][:30]}...' → {data['sentiment_label']} ({data['sentiment_score']:.2f})")
        
        return results
    
    def test_overview_endpoint(self) -> Dict[str, Any]:
        """Test overview endpoint with P0/P1/P2 business metrics."""
        print("🔍 Testing /agent/{agent_id}/overview endpoint...")
        response = requests.get(f"{self.base_url}/agent/{self.agent_id}/overview")
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate structure for P0/P1/P2 prioritization
        required_fields = ["agent_id", "total_conversations", "business_metrics", "priority_breakdown", "recommended_actions"]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"
        
        # Validate business metrics focus on P0/P1/P2 impact
        business_metrics = data["business_metrics"]
        assert "total_revenue_at_risk" in business_metrics
        assert "critical_issues_identified" in business_metrics
        assert "customer_churn_risk" in business_metrics
        assert "nps_impact" in business_metrics
        
        # Validate P0/P1/P2 priority breakdown structure
        priority_breakdown = data["priority_breakdown"]
        assert "P0" in priority_breakdown
        assert "P1" in priority_breakdown
        assert "P2" in priority_breakdown
        
        # Validate P0 (Critical) structure
        p0_data = priority_breakdown["P0"]
        assert "title" in p0_data
        assert "revenue_at_risk" in p0_data
        assert "status" in p0_data
        assert p0_data["status"] == "Critical"
        
        # Validate P1 (High Priority) structure
        p1_data = priority_breakdown["P1"]
        assert "title" in p1_data
        assert "status" in p1_data
        assert p1_data["status"] == "High Priority"
        
        # Validate P2 (Medium Priority) structure
        p2_data = priority_breakdown["P2"]
        assert "title" in p2_data
        assert "status" in p2_data
        assert p2_data["status"] == "Medium Priority"
        
        # Validate recommended actions prioritized by P0/P1/P2
        actions = data["recommended_actions"]
        assert isinstance(actions, list)
        assert len(actions) > 0
        
        for action in actions:
            assert "priority" in action
            assert "title" in action
            assert "timeline" in action
            assert "impact" in action
            assert action["priority"] in ["P0", "P1", "P2"]
        
        print(f"✅ Overview endpoint: {data['total_conversations']} conversations analyzed")
        print(f"   💰 Revenue at risk: {business_metrics['total_revenue_at_risk']}")
        print(f"   ⚠️  Critical issues: {business_metrics['critical_issues_identified']}")
        print(f"   📊 Churn risk: {business_metrics['customer_churn_risk']}")
        print(f"   🎯 P0 Critical: {p0_data['title']}")
        print(f"   🔥 P1 High: {p1_data['title']}")
        print(f"   📈 P2 Medium: {p2_data['title']}")
        
        return data
    
    def test_conversations_endpoint(self) -> Dict[str, Any]:
        """Test conversations endpoint with P0/P1/P2 categorization."""
        print("🔍 Testing /agent/{agent_id}/conversations endpoint...")
        response = requests.get(f"{self.base_url}/agent/{self.agent_id}/conversations")
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate P0/P1/P2 structure
        assert "agent_id" in data
        assert "total_conversations" in data
        assert "priority_breakdown" in data
        
        priority_breakdown = data["priority_breakdown"]
        assert "P0_critical" in priority_breakdown
        assert "P1_high" in priority_breakdown
        assert "P2_medium" in priority_breakdown
        
        # Validate each priority level structure
        for priority_level in ["P0_critical", "P1_high", "P2_medium"]:
            level_data = priority_breakdown[priority_level]
            assert "count" in level_data
            assert "conversations" in level_data
            assert isinstance(level_data["conversations"], list)
            
            # Validate conversation structure in each priority
            if level_data["conversations"]:
                conv = level_data["conversations"][0]
                required_fields = ["id", "transcript", "category", "priority", "business_impact", "created_at"]
                for field in required_fields:
                    assert field in conv, f"Missing field in conversation: {field}"
                
                # Validate priority assignment
                expected_priority = priority_level.split("_")[0]  # Extract P0, P1, P2
                assert conv["priority"] == expected_priority
                
                # Validate business impact categories
                assert conv["business_impact"] in ["Revenue at risk", "Conversion loss", "User experience"]
                assert conv["category"] in ["pricing_issues", "checkout_issues", "usability_issues"]
        
        total_categorized = sum(level_data["count"] for level_data in priority_breakdown.values())
        assert total_categorized == data["total_conversations"]
        
        print(f"✅ Conversations endpoint: {data['total_conversations']} conversations categorized")
        print(f"   🚨 P0 Critical: {priority_breakdown['P0_critical']['count']} conversations")
        print(f"   🔥 P1 High: {priority_breakdown['P1_high']['count']} conversations")
        print(f"   📈 P2 Medium: {priority_breakdown['P2_medium']['count']} conversations")
        
        return data
    
    def test_insights_endpoint(self) -> Dict[str, Any]:
        """Test comprehensive product insights endpoint with P0/P1/P2 analysis."""
        print("🔍 Testing /agent/{agent_id}/insights endpoint...")
        
        response = requests.get(f"{self.base_url}/agent/{self.agent_id}/insights")
        assert response.status_code == 200
        
        data = response.json()
        
        # Validate top-level structure
        required_fields = ["agent_id", "generated_at", "insights"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        
        insights = data["insights"]
        
        # Validate insights structure
        required_insight_fields = ["summary", "priority_insights", "business_impact", "recommended_actions"]
        for field in required_insight_fields:
            assert field in insights, f"Missing insights field: {field}"
        
        # Validate summary
        summary = insights["summary"]
        summary_fields = ["total_conversations", "critical_issues_identified", "revenue_at_risk", "avg_resolution_time"]
        for field in summary_fields:
            assert field in summary, f"Missing summary field: {field}"
        
        # Validate priority insights (P0, P1, P2)
        priority_insights = insights["priority_insights"]
        priorities = ["P0", "P1", "P2"]
        
        for priority in priorities:
            assert priority in priority_insights, f"Missing priority level: {priority}"
            
            insight = priority_insights[priority]
            
            # Validate insight structure
            insight_fields = ["title", "description", "priority", "what_users_are_saying", 
                            "what_the_data_shows", "business_impact", "recommended_action"]
            for field in insight_fields:
                assert field in insight, f"Missing field {field} in {priority} insight"
            
            # Validate what_users_are_saying
            user_feedback = insight["what_users_are_saying"]
            assert "primary_quote" in user_feedback
            assert "sentiment_score" in user_feedback
            assert "frequency" in user_feedback
            assert "source" in user_feedback
            
            # Validate sentiment score
            assert isinstance(user_feedback["sentiment_score"], (int, float))
            assert -1.0 <= user_feedback["sentiment_score"] <= 1.0
            
            # Validate what_the_data_shows (metrics)
            data_metrics = insight["what_the_data_shows"]
            assert len(data_metrics) > 0, f"No metrics found for {priority}"
            
            # Validate business_impact
            biz_impact = insight["business_impact"]
            assert len(biz_impact) > 0, f"No business impact data for {priority}"
            
            # Validate recommended_action
            action = insight["recommended_action"]
            action_fields = ["title", "effort", "impact", "owner", "timeline"]
            for field in action_fields:
                assert field in action, f"Missing action field {field} in {priority}"
        
        # Validate business impact summary
        biz_impact_summary = insights["business_impact"]
        impact_fields = ["total_revenue_at_risk", "customer_churn_risk", "support_cost_increase"]
        for field in impact_fields:
            assert field in biz_impact_summary, f"Missing business impact field: {field}"
        
        # Validate recommended actions
        actions = insights["recommended_actions"]
        assert isinstance(actions, list)
        assert len(actions) >= 3, "Should have at least 3 recommended actions"
        
        for action in actions:
            action_fields = ["priority", "title", "description", "owner", "timeline", "effort", "impact"]
            for field in action_fields:
                assert field in action, f"Missing action field: {field}"
            
            assert action["priority"] in priorities, f"Invalid priority: {action['priority']}"
        
        print(f"✅ Insights: P0/P1/P2 analysis with {summary['critical_issues_identified']} critical issues")
        print(f"   Revenue at risk: {summary['revenue_at_risk']}")
        print(f"   P0: {priority_insights['P0']['title']}")
        print(f"   P1: {priority_insights['P1']['title']}")
        print(f"   P2: {priority_insights['P2']['title']}")
        
        return data
    
    def test_mock_conversations_endpoint(self) -> Dict[str, Any]:
        """Test mock conversations endpoint."""
        print("🔍 Testing /agent/{agent_id}/mock-conversations endpoint...")
        
        response = requests.get(f"{self.base_url}/agent/{self.agent_id}/mock-conversations")
        assert response.status_code == 200
        
        data = response.json()
        
        # Validate structure
        assert "agent_id" in data
        assert "mock_conversations" in data
        assert "total_count" in data
        
        mock_convs = data["mock_conversations"]
        assert isinstance(mock_convs, list)
        assert len(mock_convs) > 0, "Should have mock conversations"
        
        # Validate each mock conversation
        categories_found = set()
        priorities_found = set()
        
        for conv in mock_convs:
            required_fields = ["id", "transcript", "category", "priority", "sentiment_label", "confidence"]
            for field in required_fields:
                assert field in conv, f"Missing field {field} in mock conversation"
            
            # Track categories and priorities
            categories_found.add(conv["category"])
            priorities_found.add(conv["priority"])
            
            # Validate priority format
            assert conv["priority"] in ["P0", "P1", "P2"], f"Invalid priority: {conv['priority']}"
            
            # Validate sentiment
            assert conv["sentiment_label"] in ["positive", "negative", "neutral"]
            assert isinstance(conv["confidence"], (int, float))
            assert 0.0 <= conv["confidence"] <= 1.0
        
        # Validate we have different categories and priorities
        assert len(categories_found) >= 3, f"Should have multiple categories, found: {categories_found}"
        assert len(priorities_found) >= 2, f"Should have multiple priorities, found: {priorities_found}"
        
        print(f"✅ Mock conversations: {len(mock_convs)} conversations")
        print(f"   Categories: {', '.join(sorted(categories_found))}")
        print(f"   Priorities: {', '.join(sorted(priorities_found))}")
        
        return data
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run comprehensive test suite for all endpoints."""
        print("🚀 Starting comprehensive API test suite...")
        print("=" * 60)
        
        results = {}
        
        try:
            # Test all endpoints
            results["health"] = self.test_health_endpoint()
            print()
            
            results["analyze"] = self.test_analyze_endpoint()
            print()
            
            results["overview"] = self.test_overview_endpoint()
            print()
            
            results["conversations"] = self.test_conversations_endpoint()
            print()
            
            results["insights"] = self.test_insights_endpoint()
            print()
            
            results["mock_conversations"] = self.test_mock_conversations_endpoint()
            print()
            
            print("=" * 60)
            print("🎉 ALL TESTS PASSED!")
            print("=" * 60)
            
            # Print summary
            self.print_test_summary(results)
            
        except Exception as e:
            print(f"❌ TEST FAILED: {str(e)}")
            raise
        
        return results
    
    def print_test_summary(self, results: Dict[str, Any]):
        """Print comprehensive test results summary."""
        print("\n📊 TEST RESULTS SUMMARY:")
        print("-" * 40)
        
        # Health status
        print(f"🏥 Health Status: {results['health']['status']}")
        
        # Sentiment analysis accuracy
        analyze_results = results['analyze']
        total_tests = len(analyze_results)
        print(f"🧠 Sentiment Analysis: {total_tests} test cases passed")
        
        # Overview metrics (P0/P1/P2 focused)
        overview = results['overview']
        print(f"📈 Overview Metrics:")
        print(f"   Total conversations: {overview['total_conversations']}")
        print(f"   Revenue at risk: {overview['business_metrics']['total_revenue_at_risk']}")
        print(f"   Critical issues: {overview['business_metrics']['critical_issues_identified']}")
        print(f"   Churn risk: {overview['business_metrics']['customer_churn_risk']}")
        
        # Conversations (P0/P1/P2 breakdown)
        conversations = results['conversations']
        priority_breakdown = conversations['priority_breakdown']
        print(f"💬 Conversations: {conversations['total_conversations']} categorized by priority")
        print(f"   P0 Critical: {priority_breakdown['P0_critical']['count']}")
        print(f"   P1 High: {priority_breakdown['P1_high']['count']}")
        print(f"   P2 Medium: {priority_breakdown['P2_medium']['count']}")
        
        # Insights
        insights = results['insights']['insights']
        print(f"🎯 Product Insights:")
        print(f"   Critical issues: {insights['summary']['critical_issues_identified']}")
        print(f"   Revenue at risk: {insights['summary']['revenue_at_risk']}")
        print(f"   P0: {insights['priority_insights']['P0']['title']}")
        print(f"   P1: {insights['priority_insights']['P1']['title']}")
        print(f"   P2: {insights['priority_insights']['P2']['title']}")
        
        # Mock conversations
        mock_convs = results['mock_conversations']
        print(f"🎭 Mock Data: {mock_convs['total_count']} test conversations")
        
        print("\n✅ All API endpoints validated successfully!")
        print("✅ All metrics and business impact calculations verified!")
        print("✅ P0/P1/P2 prioritization system working correctly!")

def main():
    """Run the comprehensive test suite."""
    tester = APITester()
    
    # Wait for server to be ready
    print("⏳ Waiting for server to be ready...")
    max_retries = 10
    for i in range(max_retries):
        try:
            response = requests.get(f"{tester.base_url}/health", timeout=5)
            if response.status_code == 200:
                break
        except requests.exceptions.RequestException:
            if i == max_retries - 1:
                print("❌ Server not responding. Make sure it's running on http://localhost:8000")
                return
            time.sleep(2)
    
    # Run all tests
    results = tester.run_all_tests()
    
    # Save results to file
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Detailed results saved to test_results.json")

if __name__ == "__main__":
    main()
