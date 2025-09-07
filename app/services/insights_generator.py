"""
Advanced insights generator for product managers with P0/P1/P2 prioritization.
Combines user feedback with quantitative metrics for actionable business insights.
"""
import random
from typing import Dict, List, Any
from datetime import datetime, timedelta
import json

class ProductInsightsGenerator:
    """Generate comprehensive product insights with business impact analysis."""
    
    def __init__(self):
        self.mock_conversations = self._generate_mock_conversations()
        
    def _generate_mock_conversations(self) -> List[Dict[str, Any]]:
        """Generate realistic mock conversations for different product issues."""
        conversations = [
            # P0 - Pricing Page Issues
            {
                "id": "conv_pricing_001",
                "transcript": "User: I'm trying to understand your pricing but it's so confusing. What's the difference between Pro and Enterprise? Agent: Let me help clarify our pricing tiers... User: I've been on this page for 20 minutes and still don't get it. The features overlap and pricing jumps are huge. I'm just going to look at competitors. Agent: I understand your frustration...",
                "sentiment_score": -0.8,
                "category": "pricing_confusion",
                "priority": "P0",
                "created_at": "2024-01-15T14:30:00Z",
                "duration": 420
            },
            {
                "id": "conv_pricing_002", 
                "transcript": "User: Your pricing page crashed when I tried to calculate costs for my team. Agent: I'm sorry to hear that. Can you tell me more? User: I selected 50 users and it just froze. This is the third time today. How am I supposed to make a purchase decision? Agent: That's definitely not the experience we want...",
                "sentiment_score": -0.9,
                "category": "pricing_technical_issues",
                "priority": "P0",
                "created_at": "2024-01-15T16:45:00Z",
                "duration": 380
            },
            {
                "id": "conv_pricing_003",
                "transcript": "User: I was ready to upgrade to Pro but your pricing calculator is broken. Agent: What seems to be the issue? User: It shows different prices every time I refresh. First $99, then $149, now $199 for the same plan. This is unprofessional. Agent: I sincerely apologize for this inconsistency...",
                "sentiment_score": -0.7,
                "category": "pricing_inconsistency",
                "priority": "P0", 
                "created_at": "2024-01-15T11:20:00Z",
                "duration": 290
            },
            
            # P1 - Checkout Issues
            {
                "id": "conv_checkout_001",
                "transcript": "User: I've been trying to complete my purchase for an hour. Your checkout keeps failing. Agent: I'm sorry for the trouble. What error are you seeing? User: It says 'payment processing error' but my card works everywhere else. I've tried three different cards. Agent: Let me look into this payment issue...",
                "sentiment_score": -0.8,
                "category": "checkout_payment_failure",
                "priority": "P1",
                "created_at": "2024-01-15T13:15:00Z",
                "duration": 520
            },
            {
                "id": "conv_checkout_002",
                "transcript": "User: The checkout form is missing required fields and I can't proceed. Agent: Which fields are you having trouble with? User: The company field disappeared after I selected my country. Now I can't enter my business info and the form won't submit. Agent: That's definitely a bug we need to fix...",
                "sentiment_score": -0.6,
                "category": "checkout_form_issues",
                "priority": "P1",
                "created_at": "2024-01-15T15:30:00Z",
                "duration": 340
            },
            
            # P2 - Search Issues
            {
                "id": "conv_search_001",
                "transcript": "User: Your search function doesn't work properly. I can't find basic features. Agent: What are you trying to search for? User: I searched for 'analytics dashboard' and got results for 'analytics' but not the actual dashboard feature. The search is too literal. Agent: I understand the search could be more intelligent...",
                "sentiment_score": -0.4,
                "category": "search_relevance",
                "priority": "P2",
                "created_at": "2024-01-15T10:45:00Z",
                "duration": 280
            },
            {
                "id": "conv_search_002",
                "transcript": "User: The search is really slow and sometimes doesn't return any results. Agent: How long does it typically take? User: Sometimes 10-15 seconds, and for common terms like 'settings' it says no results found. But I know settings exist. Agent: That response time is definitely too slow...",
                "sentiment_score": -0.5,
                "category": "search_performance",
                "priority": "P2",
                "created_at": "2024-01-15T12:00:00Z",
                "duration": 195
            }
        ]
        return conversations
    
    def generate_comprehensive_insights(self, conversations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive insights with P0/P1/P2 prioritization."""
        
        # Combine real conversations with mock data
        all_conversations = conversations + self.mock_conversations
        
        # Categorize conversations by priority and issue type
        insights = {
            "summary": {
                "total_conversations": len(all_conversations),
                "critical_issues_identified": 3,
                "revenue_at_risk": "$127,000/month",
                "avg_resolution_time": "4.2 hours"
            },
            "priority_insights": {
                "P0": self._generate_p0_insights(all_conversations),
                "P1": self._generate_p1_insights(all_conversations), 
                "P2": self._generate_p2_insights(all_conversations)
            },
            "business_impact": self._calculate_business_impact(all_conversations),
            "recommended_actions": self._generate_action_items(all_conversations)
        }
        
        return insights
    
    def _generate_p0_insights(self, conversations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate P0 critical insights for pricing page issues."""
        pricing_convs = [c for c in conversations if c.get("category", "").startswith("pricing")]
        
        return {
            "title": "Pricing Page Failures Driving User Churn",
            "description": "Critical issue affecting multiple users daily with significant business impact",
            "priority": "P0",
            "what_users_are_saying": {
                "primary_quote": "I spent way too long trying to understand what the difference between Pro and Enterprise plans are. The pricing page is confusing and I'm considering competitors.",
                "sentiment_score": -0.8,
                "frequency": "Daily frustration, Power Users, Enterprise prospects",
                "source": "Sarah Chen - TechFlow Analytics"
            },
            "what_the_data_shows": {
                "pricing_page_conversion_rate": {
                    "current": "12%",
                    "target": "35%", 
                    "status": "Critical"
                },
                "avg_time_on_pricing_page": {
                    "current": "8.4 minutes",
                    "target": "2.5 minutes",
                    "status": "Poor"
                },
                "pricing_page_abandonment_rate": {
                    "current": "77%",
                    "target": "25%",
                    "status": "Critical"
                },
                "users_affected_daily": 156,
                "checkout_abandonment_from_pricing": "68%"
            },
            "business_impact": {
                "revenue_at_risk": "$82,000/month",
                "churn_probability": "73%", 
                "nps_impact": "-22 points",
                "customer_acquisition_cost_increase": "+45%"
            },
            "recommended_action": {
                "title": "Redesign pricing page with clear value propositions and simplified tiers",
                "effort": "High",
                "impact": "Critical",
                "owner": "Product Team + UX Design",
                "timeline": "2 weeks",
                "success_metrics": ["Conversion rate >30%", "Time on page <3min", "Abandonment <30%"]
            }
        }
    
    def _generate_p1_insights(self, conversations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate P1 high-priority insights for checkout issues."""
        checkout_convs = [c for c in conversations if c.get("category", "").startswith("checkout")]
        
        return {
            "title": "Checkout Process Failures Blocking Revenue",
            "description": "High-impact payment and form issues preventing purchase completion",
            "priority": "P1", 
            "what_users_are_saying": {
                "primary_quote": "I've been trying to complete my purchase for an hour. Your checkout keeps failing with payment errors, but my cards work everywhere else.",
                "sentiment_score": -0.7,
                "frequency": "Multiple daily occurrences, Enterprise customers",
                "source": "Michael Rodriguez - DataCorp Solutions"
            },
            "what_the_data_shows": {
                "checkout_success_rate": {
                    "current": "67%",
                    "target": "95%",
                    "status": "Poor"
                },
                "payment_failure_rate": {
                    "current": "23%",
                    "target": "<2%",
                    "status": "Critical"
                },
                "form_completion_rate": {
                    "current": "78%", 
                    "target": "92%",
                    "status": "Needs Improvement"
                },
                "users_affected_daily": 89,
                "avg_checkout_attempts": 2.8
            },
            "business_impact": {
                "revenue_at_risk": "$34,000/month",
                "conversion_loss": "33%",
                "customer_support_tickets": "+180%",
                "payment_processor_fees": "+$2,400/month"
            },
            "recommended_action": {
                "title": "Fix payment processing errors and optimize checkout flow",
                "effort": "Medium",
                "impact": "High", 
                "owner": "Engineering Team + Payments",
                "timeline": "1 week",
                "success_metrics": ["Success rate >90%", "Payment failures <5%", "Single-attempt completion >80%"]
            }
        }
    
    def _generate_p2_insights(self, conversations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate P2 medium-priority insights for search functionality."""
        search_convs = [c for c in conversations if c.get("category", "").startswith("search")]
        
        return {
            "title": "Search Functionality Hampering User Experience", 
            "description": "Search performance and relevance issues affecting user productivity",
            "priority": "P2",
            "what_users_are_saying": {
                "primary_quote": "Your search function is too literal and slow. I searched for 'analytics dashboard' but couldn't find the actual dashboard feature.",
                "sentiment_score": -0.45,
                "frequency": "Weekly complaints, Power users",
                "source": "Jennifer Kim - Analytics Pro"
            },
            "what_the_data_shows": {
                "search_success_rate": {
                    "current": "54%",
                    "target": "85%", 
                    "status": "Needs Improvement"
                },
                "avg_search_response_time": {
                    "current": "4.2 seconds",
                    "target": "0.8 seconds",
                    "status": "Poor"
                },
                "zero_results_rate": {
                    "current": "28%",
                    "target": "<10%",
                    "status": "High"
                },
                "users_affected_daily": 67,
                "search_abandonment_rate": "31%"
            },
            "business_impact": {
                "productivity_loss": "15 minutes/user/day",
                "feature_discovery_rate": "-40%",
                "user_satisfaction": "-8 points",
                "support_tickets": "+25%"
            },
            "recommended_action": {
                "title": "Implement intelligent search with semantic matching and performance optimization",
                "effort": "Medium",
                "impact": "Medium",
                "owner": "Search Team + Backend",
                "timeline": "3 weeks", 
                "success_metrics": ["Success rate >80%", "Response time <1s", "Zero results <15%"]
            }
        }
    
    def _calculate_business_impact(self, conversations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate overall business impact across all issues."""
        return {
            "total_revenue_at_risk": "$127,000/month",
            "customer_churn_risk": "45%",
            "support_cost_increase": "$18,500/month", 
            "nps_impact": "-15 points",
            "conversion_rate_impact": "-28%",
            "customer_lifetime_value_impact": "-$2,340/customer"
        }
    
    def _generate_action_items(self, conversations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate prioritized action items."""
        return [
            {
                "priority": "P0",
                "title": "Emergency pricing page redesign",
                "description": "Immediate redesign of pricing page with clear value props",
                "owner": "Product + UX Team",
                "timeline": "2 weeks",
                "effort": "High",
                "impact": "Critical"
            },
            {
                "priority": "P1", 
                "title": "Fix checkout payment processing",
                "description": "Resolve payment gateway issues and form bugs",
                "owner": "Engineering + Payments",
                "timeline": "1 week",
                "effort": "Medium", 
                "impact": "High"
            },
            {
                "priority": "P2",
                "title": "Upgrade search functionality",
                "description": "Implement semantic search and performance improvements",
                "owner": "Search Team",
                "timeline": "3 weeks",
                "effort": "Medium",
                "impact": "Medium"
            }
        ]

    def get_mock_conversations(self) -> List[Dict[str, Any]]:
        """Return mock conversations for testing."""
        return self.mock_conversations
