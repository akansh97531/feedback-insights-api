"""
Synthetic Professional Network Data Generator
Creates realistic professional profiles and connections for MVP testing.
"""
import uuid
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
from faker import Faker
import json

fake = Faker()

class SyntheticDataGenerator:
    def __init__(self):
        self.companies = [
            {"name": "Google", "size": "10000+", "industry": "Technology"},
            {"name": "Microsoft", "size": "10000+", "industry": "Technology"},
            {"name": "OpenAI", "size": "100-500", "industry": "AI Research"},
            {"name": "DeepMind", "size": "500-1000", "industry": "AI Research"},
            {"name": "Meta", "size": "10000+", "industry": "Technology"},
            {"name": "Apple", "size": "10000+", "industry": "Technology"},
            {"name": "Tesla", "size": "5000-10000", "industry": "Automotive/Energy"},
            {"name": "Stripe", "size": "1000-5000", "industry": "Fintech"},
            {"name": "Airbnb", "size": "5000-10000", "industry": "Travel"},
            {"name": "Uber", "size": "10000+", "industry": "Transportation"},
            {"name": "Netflix", "size": "5000-10000", "industry": "Entertainment"},
            {"name": "Salesforce", "size": "10000+", "industry": "Enterprise Software"},
            {"name": "Palantir", "size": "1000-5000", "industry": "Data Analytics"},
            {"name": "Anthropic", "size": "100-500", "industry": "AI Research"},
            {"name": "Scale AI", "size": "500-1000", "industry": "AI/ML"},
        ]
        
        self.job_titles = {
            "Engineering": [
                "Software Engineer", "Senior Software Engineer", "Staff Software Engineer",
                "Principal Engineer", "Engineering Manager", "VP of Engineering",
                "AI Engineer", "ML Engineer", "Data Engineer", "DevOps Engineer",
                "Frontend Engineer", "Backend Engineer", "Full Stack Engineer"
            ],
            "Product": [
                "Product Manager", "Senior Product Manager", "Principal Product Manager",
                "VP of Product", "Product Director", "Product Owner", "Growth PM"
            ],
            "Data": [
                "Data Scientist", "Senior Data Scientist", "Principal Data Scientist",
                "Data Analyst", "Research Scientist", "ML Researcher", "AI Researcher"
            ],
            "Business": [
                "Business Development", "Sales Manager", "Account Executive",
                "Customer Success Manager", "Marketing Manager", "Operations Manager"
            ],
            "Leadership": [
                "CEO", "CTO", "CPO", "VP of Engineering", "VP of Product", "VP of Sales",
                "Head of AI", "Head of Data", "Director of Engineering"
            ]
        }
        
        self.skills_by_category = {
            "Programming": ["Python", "JavaScript", "Java", "C++", "Go", "Rust", "TypeScript", "Swift"],
            "AI/ML": ["TensorFlow", "PyTorch", "Scikit-learn", "Keras", "OpenCV", "NLP", "Computer Vision", "Deep Learning"],
            "Cloud": ["AWS", "GCP", "Azure", "Docker", "Kubernetes", "Terraform"],
            "Data": ["SQL", "MongoDB", "PostgreSQL", "Redis", "Spark", "Kafka", "Airflow"],
            "Frontend": ["React", "Vue.js", "Angular", "HTML/CSS", "Node.js"],
            "Product": ["Product Strategy", "User Research", "A/B Testing", "Analytics", "Roadmapping"],
            "Leadership": ["Team Management", "Strategic Planning", "Stakeholder Management", "Mentoring"]
        }
        
        self.universities = [
            "Stanford University", "MIT", "UC Berkeley", "Carnegie Mellon", "Harvard",
            "Caltech", "University of Washington", "Georgia Tech", "Cornell", "Princeton"
        ]
        
    def generate_profile(self) -> Dict[str, Any]:
        """Generate a single professional profile."""
        profile_id = str(uuid.uuid4())
        
        # Select company and role
        company = random.choice(self.companies)
        category = random.choice(list(self.job_titles.keys()))
        job_title = random.choice(self.job_titles[category])
        
        # Generate skills based on role
        skills = self._generate_skills_for_role(category, job_title)
        
        # Generate education
        education = {
            "university": random.choice(self.universities),
            "degree": random.choice(["BS", "MS", "PhD"]),
            "field": random.choice(["Computer Science", "Engineering", "Mathematics", "Physics", "Business"])
        }
        
        # Generate bio
        bio = self._generate_bio(job_title, company["name"], skills[:3])
        
        # Generate work history
        work_history = self._generate_work_history(company)
        
        profile = {
            "id": profile_id,
            "name": fake.name(),
            "job_title": job_title,
            "company": company["name"],
            "company_size": company["size"],
            "industry": company["industry"],
            "bio": bio,
            "skills": skills,
            "education": education,
            "work_history": work_history,
            "linkedin_connections": [],  # Will be populated later
            "email_interactions": {},    # Will be populated later
            "enriched_data": {
                "verified_email": random.choice([True, True, False]),  # 66% verified
                "company_verified": True,
                "last_updated": datetime.utcnow().isoformat(),
                "confidence_score": random.uniform(0.8, 1.0)
            },
            "created_at": datetime.utcnow().isoformat()
        }
        
        return profile
    
    def _generate_skills_for_role(self, category: str, job_title: str) -> List[str]:
        """Generate relevant skills based on job category and title."""
        skills = []
        
        # Base skills by category
        if "Engineer" in job_title or "Engineering" in job_title:
            skills.extend(random.sample(self.skills_by_category["Programming"], 3))
            skills.extend(random.sample(self.skills_by_category["Cloud"], 2))
            
        if "AI" in job_title or "ML" in job_title or "Data" in job_title:
            skills.extend(random.sample(self.skills_by_category["AI/ML"], 4))
            skills.extend(random.sample(self.skills_by_category["Data"], 2))
            
        if "Product" in job_title:
            skills.extend(random.sample(self.skills_by_category["Product"], 3))
            
        if "Frontend" in job_title:
            skills.extend(random.sample(self.skills_by_category["Frontend"], 3))
            
        if any(title in job_title for title in ["VP", "Director", "Head", "Manager"]):
            skills.extend(random.sample(self.skills_by_category["Leadership"], 2))
            
        # Add some random skills
        all_skills = [skill for category_skills in self.skills_by_category.values() for skill in category_skills]
        skills.extend(random.sample([s for s in all_skills if s not in skills], 2))
        
        return list(set(skills))[:8]  # Limit to 8 skills
    
    def _generate_bio(self, job_title: str, company: str, top_skills: List[str]) -> str:
        """Generate a realistic bio."""
        templates = [
            f"Experienced {job_title.lower()} at {company} passionate about {', '.join(top_skills[:2])}. Love building scalable systems and mentoring junior developers.",
            f"{job_title} with expertise in {', '.join(top_skills)}. Currently working on cutting-edge projects at {company}. Always excited to connect with fellow technologists.",
            f"Senior technologist specializing in {top_skills[0]} and {top_skills[1]}. Leading innovative initiatives at {company}. Open to discussing industry trends and collaboration opportunities.",
            f"Passionate {job_title.lower()} focused on {top_skills[0]} and {top_skills[1]}. Building the future of technology at {company}. Happy to share insights and learn from others."
        ]
        return random.choice(templates)
    
    def _generate_work_history(self, current_company: Dict) -> List[Dict]:
        """Generate work history including current role."""
        history = []
        
        # Current role
        start_date = fake.date_between(start_date='-3y', end_date='-6m')
        history.append({
            "company": current_company["name"],
            "title": "Current Role",
            "start_date": start_date.isoformat(),
            "end_date": None,
            "is_current": True
        })
        
        # Previous roles (1-3)
        num_previous = random.randint(1, 3)
        for i in range(num_previous):
            prev_company = random.choice([c for c in self.companies if c["name"] != current_company["name"]])
            end_date = start_date - timedelta(days=random.randint(30, 90))
            start_date = end_date - timedelta(days=random.randint(365, 1095))  # 1-3 years
            
            history.append({
                "company": prev_company["name"],
                "title": f"Previous Role {i+1}",
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "is_current": False
            })
        
        return history
    
    def generate_network(self, num_profiles: int = 20) -> Dict[str, Any]:
        """Generate a complete professional network."""
        print(f"Generating {num_profiles} professional profiles...")
        
        # Generate profiles
        profiles = []
        for i in range(num_profiles):
            profile = self.generate_profile()
            profiles.append(profile)
            if (i + 1) % 10 == 0:
                print(f"Generated {i + 1} profiles...")
        
        # Create connections (LinkedIn-style)
        print("Creating LinkedIn connections...")
        self._create_linkedin_connections(profiles)
        
        # Generate email interactions
        print("Generating email interaction data...")
        self._generate_email_interactions(profiles)
        
        # Create interaction records
        print("Creating interaction records...")
        interactions = self._create_interaction_records(profiles)
        
        network_data = {
            "profiles": {p["id"]: p for p in profiles},
            "interactions": interactions,
            "metadata": {
                "total_profiles": len(profiles),
                "total_connections": sum(len(p["linkedin_connections"]) for p in profiles) // 2,
                "total_interactions": len(interactions),
                "generated_at": datetime.utcnow().isoformat()
            }
        }
        
        print(f"Network generation complete!")
        print(f"- {len(profiles)} profiles")
        print(f"- {network_data['metadata']['total_connections']} connections")
        print(f"- {len(interactions)} interactions")
        
        return network_data
    
    def _create_linkedin_connections(self, profiles: List[Dict]):
        """Create realistic LinkedIn connections between profiles."""
        for profile in profiles:
            # Each person has 10-30 connections
            num_connections = random.randint(10, 30)
            potential_connections = [p for p in profiles if p["id"] != profile["id"]]
            
            # Bias towards same company/industry
            same_company = [p for p in potential_connections if p["company"] == profile["company"]]
            same_industry = [p for p in potential_connections if p["industry"] == profile["industry"]]
            
            connections = []
            
            # 40% same company
            if same_company:
                connections.extend(random.sample(same_company, min(int(num_connections * 0.4), len(same_company))))
            
            # 30% same industry
            remaining = num_connections - len(connections)
            if same_industry and remaining > 0:
                available_industry = [p for p in same_industry if p["id"] not in [c["id"] for c in connections]]
                connections.extend(random.sample(available_industry, min(int(num_connections * 0.3), len(available_industry))))
            
            # Rest random
            remaining = num_connections - len(connections)
            if remaining > 0:
                available_random = [p for p in potential_connections if p["id"] not in [c["id"] for c in connections]]
                connections.extend(random.sample(available_random, min(remaining, len(available_random))))
            
            profile["linkedin_connections"] = [c["id"] for c in connections]
    
    def _generate_email_interactions(self, profiles: List[Dict]):
        """Generate Gmail-style interaction data."""
        for profile in profiles:
            interactions = {}
            
            # Generate interactions with some connections
            for connection_id in profile["linkedin_connections"]:
                if random.random() < 0.3:  # 30% of connections have email interactions
                    # Generate interaction strength
                    frequency = random.randint(1, 20)  # emails per month
                    last_contact = fake.date_between(start_date='-30d', end_date='today')
                    
                    # Calculate relationship strength (0-1)
                    recency_score = max(0, 1 - (datetime.now().date() - last_contact).days / 30)
                    frequency_score = min(1, frequency / 20)
                    strength = (recency_score * 0.6 + frequency_score * 0.4)
                    
                    interactions[connection_id] = {
                        "email_frequency": frequency,
                        "last_contact": last_contact.isoformat(),
                        "relationship_strength": round(strength, 3),
                        "interaction_type": random.choice(["professional", "personal", "mixed"])
                    }
            
            profile["email_interactions"] = interactions
    
    def _create_interaction_records(self, profiles: List[Dict]) -> List[Dict]:
        """Create interaction records for the graph database."""
        interactions = []
        
        for profile in profiles:
            for connection_id, interaction_data in profile["email_interactions"].items():
                interaction = {
                    "id": str(uuid.uuid4()),
                    "source_id": profile["id"],
                    "target_id": connection_id,
                    "interaction_type": "email",
                    "frequency": interaction_data["email_frequency"],
                    "strength": interaction_data["relationship_strength"],
                    "last_contact": interaction_data["last_contact"],
                    "created_at": datetime.utcnow().isoformat()
                }
                interactions.append(interaction)
        
        return interactions
