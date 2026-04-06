"""Memory management module using Supabase for persistent storage."""
from typing import Dict, List, Any, Optional
from datetime import datetime
from supabase import create_client, Client
import json
from config import SUPABASE_URL, SUPABASE_KEY


class MemoryManager:
    """Manages agent memory using Supabase as the backend."""
    
    def __init__(self):
        """Initialize Supabase client."""
        self.client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        self._initialize_tables()
    
    def _initialize_tables(self):
        """Initialize required Supabase tables if they don't exist."""
        try:
            # Tables should be created via Supabase dashboard or migrations
            # This is a placeholder for initialization logic
            pass
        except Exception as e:
            print(f"Warning: Could not initialize tables: {e}")
    
    # Candidate Memory Operations
    def save_candidate(self, candidate_id: str, candidate_data: Dict[str, Any]) -> bool:
        """Store or update candidate information."""
        try:
            self.client.table("candidates").upsert({
                "id": candidate_id,
                "data": candidate_data,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }).execute()
            return True
        except Exception as e:
            print(f"Error saving candidate: {e}")
            return False
    
    def get_candidate(self, candidate_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve candidate information."""
        try:
            response = self.client.table("candidates").select("*").eq("id", candidate_id).execute()
            if response.data:
                return response.data[0]["data"]
            return None
        except Exception as e:
            print(f"Error retrieving candidate: {e}")
            return None
    
    def get_all_candidates(self) -> List[Dict[str, Any]]:
        """Retrieve all candidates."""
        try:
            response = self.client.table("candidates").select("*").execute()
            return [item["data"] for item in response.data]
        except Exception as e:
            print(f"Error retrieving candidates: {e}")
            return []
    
    # Interview Round Storage
    def save_interview_round(self, candidate_id: str, round_num: int, responses: List[str], 
                            scores: List[float]) -> bool:
        """Store interview round data."""
        try:
            self.client.table("interview_rounds").insert({
                "candidate_id": candidate_id,
                "round_number": round_num,
                "responses": json.dumps(responses),
                "scores": json.dumps(scores),
                "timestamp": datetime.utcnow().isoformat()
            }).execute()
            return True
        except Exception as e:
            print(f"Error saving interview round: {e}")
            return False
    
    def get_interview_history(self, candidate_id: str) -> List[Dict[str, Any]]:
        """Retrieve all interview rounds for a candidate."""
        try:
            response = self.client.table("interview_rounds").select("*").eq(
                "candidate_id", candidate_id
            ).order("round_number").execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Error retrieving interview history: {e}")
            return []
    
    # Scoring & Evaluation
    def save_evaluation_score(self, candidate_id: str, scores: Dict[str, float], 
                             final_score: float) -> bool:
        """Store candidate evaluation scores."""
        try:
            self.client.table("evaluations").upsert({
                "candidate_id": candidate_id,
                "technical_skills": scores.get("technical_skills", 0),
                "communication": scores.get("communication", 0),
                "problem_solving": scores.get("problem_solving", 0),
                "cultural_fit": scores.get("cultural_fit", 0),
                "authenticity": scores.get("authenticity", 0),
                "final_score": final_score,
                "timestamp": datetime.utcnow().isoformat()
            }).execute()
            return True
        except Exception as e:
            print(f"Error saving evaluation score: {e}")
            return False
    
    def get_evaluation_score(self, candidate_id: str) -> Optional[Dict[str, float]]:
        """Retrieve evaluation scores for a candidate."""
        try:
            response = self.client.table("evaluations").select("*").eq(
                "candidate_id", candidate_id
            ).execute()
            if response.data:
                record = response.data[0]
                return {
                    "technical_skills": record.get("technical_skills"),
                    "communication": record.get("communication"),
                    "problem_solving": record.get("problem_solving"),
                    "cultural_fit": record.get("cultural_fit"),
                    "authenticity": record.get("authenticity"),
                    "final_score": record.get("final_score")
                }
            return None
        except Exception as e:
            print(f"Error retrieving evaluation score: {e}")
            return None
    
    # Authenticity Detection
    def save_authenticity_check(self, candidate_id: str, is_authentic: bool, 
                               confidence: float, details: Dict[str, Any]) -> bool:
        """Store authenticity check results."""
        try:
            self.client.table("authenticity_checks").insert({
                "candidate_id": candidate_id,
                "is_authentic": is_authentic,
                "confidence_score": confidence,
                "details": json.dumps(details),
                "timestamp": datetime.utcnow().isoformat()
            }).execute()
            return True
        except Exception as e:
            print(f"Error saving authenticity check: {e}")
            return False
    
    def get_authenticity_check(self, candidate_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve authenticity check for a candidate."""
        try:
            response = self.client.table("authenticity_checks").select("*").eq(
                "candidate_id", candidate_id
            ).order("timestamp", desc=True).limit(1).execute()
            if response.data:
                record = response.data[0]
                return {
                    "is_authentic": record.get("is_authentic"),
                    "confidence": record.get("confidence_score"),
                    "details": json.loads(record.get("details", "{}"))
                }
            return None
        except Exception as e:
            print(f"Error retrieving authenticity check: {e}")
            return None
    
    # Shortlist Management
    def save_shortlist(self, candidate_ids: List[str], status: str = "active") -> bool:
        """Store shortlist results."""
        try:
            self.client.table("shortlists").insert({
                "candidate_ids": json.dumps(candidate_ids),
                "status": status,
                "timestamp": datetime.utcnow().isoformat()
            }).execute()
            return True
        except Exception as e:
            print(f"Error saving shortlist: {e}")
            return False
    
    def get_latest_shortlist(self) -> List[str]:
        """Retrieve the latest shortlist."""
        try:
            response = self.client.table("shortlists").select("*").order(
                "timestamp", desc=True
            ).limit(1).execute()
            if response.data:
                return json.loads(response.data[0]["candidate_ids"])
            return []
        except Exception as e:
            print(f"Error retrieving shortlist: {e}")
            return []
    
    # Outcome Tracking & Learning
    def save_hiring_outcome(self, candidate_id: str, hired: bool, feedback: str = "") -> bool:
        """Record final hiring decision and feedback."""
        try:
            self.client.table("hiring_outcomes").insert({
                "candidate_id": candidate_id,
                "hired": hired,
                "feedback": feedback,
                "timestamp": datetime.utcnow().isoformat()
            }).execute()
            return True
        except Exception as e:
            print(f"Error saving hiring outcome: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get overall hiring statistics for learning and improvement."""
        try:
            outcomes = self.client.table("hiring_outcomes").select("*").execute()
            total = len(outcomes.data)
            hired = sum(1 for item in outcomes.data if item.get("hired"))
            
            return {
                "total_candidates_processed": total,
                "total_hired": hired,
                "hiring_rate": (hired / total * 100) if total > 0 else 0,
                "last_updated": datetime.utcnow().isoformat()
            }
        except Exception as e:
            print(f"Error retrieving stats: {e}")
            return {}
