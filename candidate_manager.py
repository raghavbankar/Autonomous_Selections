"""Candidate management module for fetching, preprocessing, scoring, and ranking."""
from typing import List, Dict, Any, Optional
import json
import requests
from datetime import datetime
from dataclasses import dataclass
from config import MAX_CANDIDATES_TO_PROCESS, SHORTLIST_SIZE, SCORING_WEIGHTS
from memory_manager import MemoryManager


@dataclass
class Candidate:
    """Data class representing a candidate."""
    id: str
    name: str
    email: str
    experience_years: int
    skills: List[str]
    education: str
    resume_text: str
    raw_data: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert candidate to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "experience_years": self.experience_years,
            "skills": self.skills,
            "education": self.education,
            "resume_text": self.resume_text,
            "raw_data": self.raw_data
        }


class CandidateManager:
    """Manages candidate fetching, preprocessing, scoring, and ranking."""
    
    def __init__(self, memory_manager: MemoryManager):
        """Initialize candidate manager."""
        self.memory = memory_manager
        self.candidates: List[Candidate] = []
        self.candidate_scores: Dict[str, float] = {}
    
    def fetch_candidates(self, api_endpoint: Optional[str] = None, 
                        use_mock_data: bool = True) -> List[Candidate]:
        """
        Fetch candidates from API or use mock data.
        
        Args:
            api_endpoint: Optional API endpoint to fetch candidates
            use_mock_data: Whether to use mock data (default True)
        
        Returns:
            List of candidates
        """
        try:
            if use_mock_data or not api_endpoint:
                self.candidates = self._generate_mock_candidates()
            else:
                self.candidates = self._fetch_from_api(api_endpoint)
            
            print(f"✓ Fetched {len(self.candidates)} candidates")
            return self.candidates
        except Exception as e:
            print(f"✗ Error fetching candidates: {e}")
            return []
    
    def _generate_mock_candidates(self) -> List[Candidate]:
        """Generate mock candidate data for demonstration."""
        mock_data = [
            {
                "id": "cand_001",
                "name": "Alice Johnson",
                "email": "alice@example.com",
                "experience_years": 5,
                "skills": ["Python", "Machine Learning", "Data Analysis"],
                "education": "BS Computer Science",
                "resume_text": "Experienced ML engineer with 5 years in AI/ML projects..."
            },
            {
                "id": "cand_002",
                "name": "Bob Smith",
                "email": "bob@example.com",
                "experience_years": 3,
                "skills": ["Python", "Web Development", "Cloud"],
                "education": "BS Software Engineering",
                "resume_text": "Full-stack developer focused on scalable web applications..."
            },
            {
                "id": "cand_003",
                "name": "Carol Williams",
                "email": "carol@example.com",
                "experience_years": 7,
                "skills": ["Leadership", "Project Management", "Agile"],
                "education": "MBA",
                "resume_text": "Technical leader with strong team management skills..."
            },
            {
                "id": "cand_004",
                "name": "David Brown",
                "email": "david@example.com",
                "experience_years": 2,
                "skills": ["Python", "Data Science", "Statistics"],
                "education": "MS Data Science",
                "resume_text": "Recent graduate specializing in statistical analysis..."
            },
            {
                "id": "cand_005",
                "name": "Emma Davis",
                "email": "emma@example.com",
                "experience_years": 4,
                "skills": ["DevOps", "Kubernetes", "AWS"],
                "education": "BS Information Technology",
                "resume_text": "Cloud infrastructure specialist with 4 years experience..."
            }
        ]
        
        candidates = []
        for data in mock_data[:MAX_CANDIDATES_TO_PROCESS]:
            candidate = Candidate(
                id=data["id"],
                name=data["name"],
                email=data["email"],
                experience_years=data["experience_years"],
                skills=data["skills"],
                education=data["education"],
                resume_text=data["resume_text"],
                raw_data=data
            )
            candidates.append(candidate)
        
        return candidates
    
    def _fetch_from_api(self, api_endpoint: str) -> List[Candidate]:
        """Fetch candidates from external API."""
        try:
            response = requests.get(api_endpoint, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            candidates = []
            for item in data.get("candidates", [])[:MAX_CANDIDATES_TO_PROCESS]:
                candidate = Candidate(
                    id=item.get("id", ""),
                    name=item.get("name", ""),
                    email=item.get("email", ""),
                    experience_years=item.get("experience_years", 0),
                    skills=item.get("skills", []),
                    education=item.get("education", ""),
                    resume_text=item.get("resume_text", ""),
                    raw_data=item
                )
                candidates.append(candidate)
            
            return candidates
        except Exception as e:
            print(f"Error fetching from API: {e}")
            return []
    
    def preprocess_and_structure(self) -> List[Dict[str, Any]]:
        """
        Preprocess and structure candidate data.
        
        Returns:
            List of structured candidate data
        """
        structured_candidates = []
        
        for candidate in self.candidates:
            structured_data = {
                "id": candidate.id,
                "name": candidate.name,
                "email": candidate.email,
                "experience_years": candidate.experience_years,
                "skills": candidate.skills,
                "education": candidate.education,
                "profile_completeness": self._calculate_profile_completeness(candidate),
                "skill_count": len(candidate.skills),
                "seniority_level": self._assess_seniority(candidate.experience_years),
                "resume_quality_score": self._assess_resume_quality(candidate.resume_text),
                "processed_at": datetime.utcnow().isoformat()
            }
            
            # Save to memory
            self.memory.save_candidate(candidate.id, structured_data)
            structured_candidates.append(structured_data)
        
        print(f"✓ Preprocessed and structured {len(structured_candidates)} candidates")
        return structured_candidates
    
    def _calculate_profile_completeness(self, candidate: Candidate) -> float:
        """Calculate profile completeness score (0-100)."""
        score = 0
        if candidate.name:
            score += 20
        if candidate.email:
            score += 20
        if candidate.experience_years > 0:
            score += 20
        if candidate.skills:
            score += 20
        if candidate.education:
            score += 20
        return float(score)
    
    def _assess_seniority(self, years: int) -> str:
        """Assess seniority level based on years of experience."""
        if years < 2:
            return "junior"
        elif years < 5:
            return "mid-level"
        else:
            return "senior"
    
    def _assess_resume_quality(self, resume_text: str) -> float:
        """Assess resume quality based on content length and structure."""
        if not resume_text:
            return 0.0
        
        score = min(len(resume_text) / 500, 1.0) * 100  # Normalize to 100
        return float(score)
    
    def score_candidates(self, interview_scores: Optional[Dict[str, Dict[str, float]]] = None) -> Dict[str, float]:
        """
        Score and rank candidates based on various criteria.
        
        Args:
            interview_scores: Optional interview scores from evaluation rounds
        
        Returns:
            Dictionary mapping candidate IDs to final scores
        """
        structured_data = self.preprocess_and_structure()
        
        for candidate_data in structured_data:
            candidate_id = candidate_data["id"]
            
            # Initialize score components (if no interview scores yet, use defaults)
            scores = {
                "technical_skills": self._score_technical_skills(candidate_data),
                "communication": interview_scores.get(candidate_id, {}).get("communication", 75.0) if interview_scores else 75.0,
                "problem_solving": interview_scores.get(candidate_id, {}).get("problem_solving", 75.0) if interview_scores else 75.0,
                "cultural_fit": interview_scores.get(candidate_id, {}).get("cultural_fit", 75.0) if interview_scores else 75.0,
                "authenticity": interview_scores.get(candidate_id, {}).get("authenticity", 75.0) if interview_scores else 75.0
            }
            
            # Calculate weighted final score
            final_score = sum(
                scores[key] * SCORING_WEIGHTS.get(key, 0) 
                for key in scores
            )
            
            self.candidate_scores[candidate_id] = final_score
            self.memory.save_evaluation_score(candidate_id, scores, final_score)
        
        print(f"✓ Scored {len(self.candidate_scores)} candidates")
        return self.candidate_scores
    
    def _score_technical_skills(self, candidate_data: Dict[str, Any]) -> float:
        """Score technical skills based on skills list and experience."""
        base_score = min(len(candidate_data.get("skills", [])) * 15, 80)  # Max 80
        experience_bonus = min(candidate_data.get("experience_years", 0) * 5, 20)  # Max 20
        return float(min(base_score + experience_bonus, 100))
    
    def rank_candidates(self) -> List[tuple[str, float]]:
        """
        Rank candidates by their scores.
        
        Returns:
            List of (candidate_id, score) tuples sorted by score descending
        """
        ranked = sorted(self.candidate_scores.items(), key=lambda x: x[1], reverse=True)
        print(f"✓ Ranked {len(ranked)} candidates")
        return ranked
    
    def shortlist_top_candidates(self, top_n: int = SHORTLIST_SIZE) -> List[str]:
        """
        Shortlist top N candidates for interview rounds.
        
        Args:
            top_n: Number of candidates to shortlist
        
        Returns:
            List of shortlisted candidate IDs
        """
        ranked = self.rank_candidates()
        shortlisted = [cand_id for cand_id, score in ranked[:top_n]]
        
        self.memory.save_shortlist(shortlisted, status="active")
        print(f"✓ Shortlisted {len(shortlisted)} candidates")
        return shortlisted
    
    def get_candidate_by_id(self, candidate_id: str) -> Optional[Candidate]:
        """Retrieve a specific candidate by ID."""
        for candidate in self.candidates:
            if candidate.id == candidate_id:
                return candidate
        return None
