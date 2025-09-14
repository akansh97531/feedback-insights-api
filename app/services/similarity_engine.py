"""
Multi-Metric Similarity Engine for Professional Network Matching
Implements comprehensive similarity scoring across multiple dimensions.
"""
import numpy as np
from typing import Dict, List, Any
from sklearn.metrics.pairwise import cosine_similarity

class SimilarityEngine:
    def __init__(self):
        # Weights for composite scoring
        self.weights = {
            "semantic_similarity": 0.25,
            "relationship_strength": 0.20,
            "mutual_connections": 0.15,
            "company_overlap": 0.15,
            "education_similarity": 0.10,
            "query_relevance": 0.15
        }
    
    def calculate_semantic_similarity(
        self, 
        profile1_embedding: np.ndarray, 
        profile2_embedding: np.ndarray
    ) -> float:
        """Calculate cosine similarity between profile embeddings."""
        if profile1_embedding is None or profile2_embedding is None:
            return 0.0
            
        # Reshape for sklearn if needed
        emb1 = profile1_embedding.reshape(1, -1)
        emb2 = profile2_embedding.reshape(1, -1)
        
        similarity = cosine_similarity(emb1, emb2)[0][0]
        return max(0.0, float(similarity))  # Ensure non-negative
    
    def calculate_relationship_strength(
        self, 
        profile1: Dict[str, Any], 
        profile2: Dict[str, Any]
    ) -> float:
        """Calculate relationship strength based on email interactions."""
        profile1_id = profile1.get("id")
        profile2_id = profile2.get("id")
        
        # Check if they have email interactions
        interactions1 = profile1.get("email_interactions", {})
        interactions2 = profile2.get("email_interactions", {})
        
        strength = 0.0
        
        # Check interaction from profile1 to profile2
        if profile2_id in interactions1:
            strength = max(strength, interactions1[profile2_id].get("relationship_strength", 0.0))
        
        # Check interaction from profile2 to profile1
        if profile1_id in interactions2:
            strength = max(strength, interactions2[profile1_id].get("relationship_strength", 0.0))
        
        return strength
    
    def calculate_mutual_connections(
        self, 
        profile1: Dict[str, Any], 
        profile2: Dict[str, Any]
    ) -> float:
        """Calculate mutual LinkedIn connections overlap."""
        connections1 = set(profile1.get("linkedin_connections", []))
        connections2 = set(profile2.get("linkedin_connections", []))
        
        if not connections1 or not connections2:
            return 0.0
        
        mutual = len(connections1.intersection(connections2))
        total_unique = len(connections1.union(connections2))
        
        if total_unique == 0:
            return 0.0
        
        # Jaccard similarity
        return mutual / total_unique
    
    def calculate_company_overlap(
        self, 
        profile1: Dict[str, Any], 
        profile2: Dict[str, Any]
    ) -> float:
        """Calculate overlap in current and past companies."""
        # Get all companies for both profiles
        companies1 = set()
        companies2 = set()
        
        # Current company
        if profile1.get("company"):
            companies1.add(profile1["company"].lower())
        if profile2.get("company"):
            companies2.add(profile2["company"].lower())
        
        # Past companies from work history
        for work in profile1.get("work_history", []):
            if work.get("company"):
                companies1.add(work["company"].lower())
        
        for work in profile2.get("work_history", []):
            if work.get("company"):
                companies2.add(work["company"].lower())
        
        if not companies1 or not companies2:
            return 0.0
        
        overlap = len(companies1.intersection(companies2))
        total_unique = len(companies1.union(companies2))
        
        return overlap / total_unique if total_unique > 0 else 0.0
    
    def calculate_education_similarity(
        self, 
        profile1: Dict[str, Any], 
        profile2: Dict[str, Any]
    ) -> float:
        """Calculate education similarity (university and degree level)."""
        edu1 = profile1.get("education", {})
        edu2 = profile2.get("education", {})
        
        if not edu1 or not edu2:
            return 0.0
        
        similarity = 0.0
        
        # University match (70% weight)
        if edu1.get("university") and edu2.get("university"):
            if edu1["university"].lower() == edu2["university"].lower():
                similarity += 0.7
        
        # Degree level match (30% weight)
        if edu1.get("degree") and edu2.get("degree"):
            degree1 = edu1["degree"].lower()
            degree2 = edu2["degree"].lower()
            
            # Exact match
            if degree1 == degree2:
                similarity += 0.3
            # Similar level (BS/MS, MS/PhD)
            elif (degree1 in ["bs", "ba"] and degree2 in ["bs", "ba"]) or \
                 (degree1 == "ms" and degree2 in ["ms", "phd"]) or \
                 (degree1 == "phd" and degree2 in ["ms", "phd"]):
                similarity += 0.15
        
        return similarity
    
    def calculate_query_relevance(
        self, 
        profile: Dict[str, Any], 
        parsed_query: Dict[str, Any],
        query_embedding: np.ndarray = None,
        profile_embedding: np.ndarray = None
    ) -> float:
        """Calculate how well a profile matches the structured query criteria."""
        relevance = 0.0
        total_criteria = 0
        
        # Job title matching
        if parsed_query.get("job_titles"):
            total_criteria += 1
            profile_title = profile.get("job_title", "").lower()
            for query_title in parsed_query["job_titles"]:
                if query_title.lower() in profile_title or profile_title in query_title.lower():
                    relevance += 1.0
                    break
        
        # Company matching
        if parsed_query.get("companies"):
            total_criteria += 1
            profile_companies = set()
            if profile.get("company"):
                profile_companies.add(profile["company"].lower())
            for work in profile.get("work_history", []):
                if work.get("company"):
                    profile_companies.add(work["company"].lower())
            
            for query_company in parsed_query["companies"]:
                if query_company.lower() in profile_companies:
                    relevance += 1.0
                    break
        
        # Skills matching
        if parsed_query.get("skills"):
            total_criteria += 1
            profile_skills = [skill.lower() for skill in profile.get("skills", [])]
            matched_skills = 0
            for query_skill in parsed_query["skills"]:
                if query_skill.lower() in profile_skills:
                    matched_skills += 1
            
            if parsed_query["skills"]:
                relevance += matched_skills / len(parsed_query["skills"])
        
        # Industry matching
        if parsed_query.get("industries"):
            total_criteria += 1
            profile_industry = profile.get("industry", "").lower()
            for query_industry in parsed_query["industries"]:
                if query_industry.lower() in profile_industry:
                    relevance += 1.0
                    break
        
        # Education matching
        if parsed_query.get("education"):
            total_criteria += 1
            profile_edu = profile.get("education", {})
            profile_uni = profile_edu.get("university", "").lower()
            profile_degree = profile_edu.get("degree", "").lower()
            
            for edu_req in parsed_query["education"]:
                edu_req_lower = edu_req.lower()
                if edu_req_lower in profile_uni or edu_req_lower in profile_degree:
                    relevance += 1.0
                    break
        
        # Experience level matching
        if parsed_query.get("experience_level") and parsed_query["experience_level"] != "any":
            total_criteria += 1
            profile_title = profile.get("job_title", "").lower()
            exp_level = parsed_query["experience_level"].lower()
            
            if exp_level == "senior" and ("senior" in profile_title or "principal" in profile_title or "staff" in profile_title):
                relevance += 1.0
            elif exp_level == "junior" and ("junior" in profile_title or ("senior" not in profile_title and "principal" not in profile_title)):
                relevance += 1.0
            elif exp_level == "executive" and any(title in profile_title for title in ["vp", "director", "head", "ceo", "cto", "cpo"]):
                relevance += 1.0
        
        # Semantic relevance using embeddings
        if query_embedding is not None and profile_embedding is not None:
            total_criteria += 1
            semantic_score = self.calculate_semantic_similarity(query_embedding, profile_embedding)
            relevance += semantic_score
        
        return relevance / total_criteria if total_criteria > 0 else 0.0
    
    def calculate_composite_score(
        self,
        profile1: Dict[str, Any],
        profile2: Dict[str, Any],
        profile1_embedding: np.ndarray,
        profile2_embedding: np.ndarray,
        parsed_query: Dict[str, Any] = None,
        query_embedding: np.ndarray = None
    ) -> Dict[str, float]:
        """Calculate comprehensive similarity score between two profiles."""
        
        # Calculate individual metrics
        semantic_sim = self.calculate_semantic_similarity(profile1_embedding, profile2_embedding)
        relationship_strength = self.calculate_relationship_strength(profile1, profile2)
        mutual_connections = self.calculate_mutual_connections(profile1, profile2)
        company_overlap = self.calculate_company_overlap(profile1, profile2)
        education_sim = self.calculate_education_similarity(profile1, profile2)
        
        # Query relevance (how well profile2 matches the query from profile1's perspective)
        query_relevance = 0.0
        if parsed_query and query_embedding is not None:
            query_relevance = self.calculate_query_relevance(
                profile2, parsed_query, query_embedding, profile2_embedding
            )
        
        # Calculate weighted composite score
        composite_score = (
            semantic_sim * self.weights["semantic_similarity"] +
            relationship_strength * self.weights["relationship_strength"] +
            mutual_connections * self.weights["mutual_connections"] +
            company_overlap * self.weights["company_overlap"] +
            education_sim * self.weights["education_similarity"] +
            query_relevance * self.weights["query_relevance"]
        )
        
        return {
            "composite_score": composite_score,
            "semantic_similarity": semantic_sim,
            "relationship_strength": relationship_strength,
            "mutual_connections": mutual_connections,
            "company_overlap": company_overlap,
            "education_similarity": education_sim,
            "query_relevance": query_relevance
        }
    
    def rank_profiles(
        self,
        requester_profile: Dict[str, Any],
        candidate_profiles: List[Dict[str, Any]],
        requester_embedding: np.ndarray,
        candidate_embeddings: List[np.ndarray],
        parsed_query: Dict[str, Any] = None,
        query_embedding: np.ndarray = None,
        top_n: int = 10
    ) -> List[Dict[str, Any]]:
        """Rank candidate profiles based on similarity to requester and query relevance."""
        
        ranked_results = []
        
        for i, candidate in enumerate(candidate_profiles):
            if candidate["id"] == requester_profile["id"]:
                continue  # Skip self
            
            candidate_embedding = candidate_embeddings[i] if i < len(candidate_embeddings) else None
            
            # Calculate similarity scores
            scores = self.calculate_composite_score(
                requester_profile,
                candidate,
                requester_embedding,
                candidate_embedding,
                parsed_query,
                query_embedding
            )
            
            # Add profile and scores to results
            result = {
                "profile": candidate,
                "scores": scores,
                "composite_score": scores["composite_score"]
            }
            
            ranked_results.append(result)
        
        # Sort by composite score (descending)
        ranked_results.sort(key=lambda x: x["composite_score"], reverse=True)
        
        return ranked_results[:top_n]
    
    def explain_match(self, match_result: Dict[str, Any]) -> str:
        """Generate human-readable explanation for why profiles match."""
        profile = match_result["profile"]
        scores = match_result["scores"]
        
        explanations = []
        
        # Semantic similarity
        if scores["semantic_similarity"] > 0.7:
            explanations.append("Strong professional profile alignment")
        elif scores["semantic_similarity"] > 0.5:
            explanations.append("Good professional background match")
        
        # Relationship strength
        if scores["relationship_strength"] > 0.5:
            explanations.append("Existing email communication history")
        
        # Mutual connections
        if scores["mutual_connections"] > 0.1:
            explanations.append(f"Shared LinkedIn connections")
        
        # Company overlap
        if scores["company_overlap"] > 0.5:
            explanations.append("Worked at same companies")
        elif scores["company_overlap"] > 0.0:
            explanations.append("Some company overlap in career history")
        
        # Education
        if scores["education_similarity"] > 0.5:
            explanations.append("Similar educational background")
        
        # Query relevance
        if scores["query_relevance"] > 0.7:
            explanations.append("Excellent match for your specific criteria")
        elif scores["query_relevance"] > 0.4:
            explanations.append("Good match for your requirements")
        
        if not explanations:
            explanations.append("Potential networking opportunity")
        
        return " • ".join(explanations)
