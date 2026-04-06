"""Main autonomous hiring agent orchestrator."""
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
from memory_manager import MemoryManager
from candidate_manager import CandidateManager, Candidate
from interview_conductor import InterviewConductor
from evaluator import ResponseEvaluator
from authenticity_detector import AuthenticityDetector
from config import PASSING_SCORE_THRESHOLD, SHORTLIST_SIZE, INTERVIEW_ROUNDS


class HiringAgent:
    """
    Autonomous hiring agent that orchestrates the complete hiring workflow.
    
    Workflow:
    1. Fetch candidates via API
    2. Preprocess and structure data
    3. Score and rank candidates
    4. Shortlist top candidates
    5. Conduct AI interview rounds
    6. Evaluate responses dynamically
    7. Run authenticity detection
    8. Compute final score
    9. Store results in memory
    10. Update system based on outcomes
    """
    
    def __init__(self):
        """Initialize hiring agent with all components."""
        print("🚀 Initializing Autonomous Hiring Agent\n")
        
        self.memory = MemoryManager()
        self.candidate_manager = CandidateManager(self.memory)
        self.interview_conductor = InterviewConductor(self.memory)
        self.evaluator = ResponseEvaluator(self.memory)
        self.authenticity_detector = AuthenticityDetector(self.memory)
        
        self.workflow_state = {
            "step": 0,
            "candidates_processed": 0,
            "candidates_shortlisted": 0,
            "candidates_hired": 0,
            "start_time": datetime.utcnow().isoformat()
        }
        self.results = {}
    
    def run_workflow(self, api_endpoint: Optional[str] = None, 
                    use_mock_data: bool = True) -> Dict[str, Any]:
        """
        Run the complete hiring workflow.
        
        Args:
            api_endpoint: Optional API endpoint for candidate data
            use_mock_data: Whether to use mock data for demo
        
        Returns:
            Complete hiring results
        """
        try:
            # Step 1: Fetch candidates
            print("═" * 60)
            print("STEP 1: FETCH CANDIDATES VIA API")
            print("═" * 60)
            candidates = self._step_fetch_candidates(api_endpoint, use_mock_data)
            if not candidates:
                print("❌ No candidates found")
                return self._generate_summary()
            
            # Step 2: Preprocess and structure data
            print("\n" + "═" * 60)
            print("STEP 2: PREPROCESS AND STRUCTURE DATA")
            print("═" * 60)
            self._step_preprocess_data()
            
            # Step 3: Score and rank candidates
            print("\n" + "═" * 60)
            print("STEP 3: SCORE AND RANK CANDIDATES")
            print("═" * 60)
            self._step_score_and_rank()
            
            # Step 4: Shortlist top candidates
            print("\n" + "═" * 60)
            print("STEP 4: SHORTLIST TOP CANDIDATES")
            print("═" * 60)
            shortlisted = self._step_shortlist()
            if not shortlisted:
                print("❌ No candidates to shortlist")
                return self._generate_summary()
            
            # Step 5-9: Interview and evaluate shortlisted candidates
            print("\n" + "═" * 60)
            print("STEP 5-9: INTERVIEWS, EVALUATION & AUTHENTICITY")
            print("═" * 60)
            self._step_interview_and_evaluate(shortlisted)
            
            # Step 10: Update system and generate final decisions
            print("\n" + "═" * 60)
            print("STEP 10: FINAL DECISIONS & LEARNING UPDATE")
            print("═" * 60)
            self._step_final_decisions()
            
            return self._generate_summary()
        
        except Exception as e:
            print(f"❌ Error in workflow: {e}")
            import traceback
            traceback.print_exc()
            return self._generate_summary()
    
    def _step_fetch_candidates(self, api_endpoint: Optional[str],
                              use_mock_data: bool) -> List[Candidate]:
        """Step 1: Fetch candidates from API or mock data."""
        self.workflow_state["step"] = 1
        candidates = self.candidate_manager.fetch_candidates(api_endpoint, use_mock_data)
        self.workflow_state["candidates_processed"] = len(candidates)
        return candidates
    
    def _step_preprocess_data(self):
        """Step 2: Preprocess and structure candidate data."""
        self.workflow_state["step"] = 2
        structured_data = self.candidate_manager.preprocess_and_structure()
        print(f"\n📊 Data Structure Sample (first candidate):")
        if structured_data:
            print(json.dumps(structured_data[0], indent=2, default=str)[:500])
    
    def _step_score_and_rank(self):
        """Step 3: Score and rank candidates."""
        self.workflow_state["step"] = 3
        scores = self.candidate_manager.score_candidates()
        ranked = self.candidate_manager.rank_candidates()
        
        print("\n🏆 Top 5 Candidates by Score:")
        for i, (cand_id, score) in enumerate(ranked[:5], 1):
            candidate = self.candidate_manager.get_candidate_by_id(cand_id)
            print(f"{i}. {candidate.name:20} - Score: {score:.2f}/100")
    
    def _step_shortlist(self) -> List[str]:
        """Step 4: Shortlist top candidates."""
        self.workflow_state["step"] = 4
        shortlisted = self.candidate_manager.shortlist_top_candidates(SHORTLIST_SIZE)
        self.workflow_state["candidates_shortlisted"] = len(shortlisted)
        
        print(f"\n✨ Shortlisted {len(shortlisted)} candidates for interview:")
        for candidate_id in shortlisted:
            candidate = self.candidate_manager.get_candidate_by_id(candidate_id)
            if candidate:
                print(f"  • {candidate.name} ({candidate.email})")
        
        return shortlisted
    
    def _step_interview_and_evaluate(self, shortlisted: List[str]):
        """Steps 5-9: Conduct interviews, evaluate, and check authenticity."""
        self.workflow_state["step"] = 5
        
        for candidate_id in shortlisted:
            candidate = self.candidate_manager.get_candidate_by_id(candidate_id)
            if not candidate:
                continue
            
            print(f"\n\n{'▼' * 60}")
            print(f"INTERVIEWING: {candidate.name}")
            print(f"{'▼' * 60}")
            
            # Step 5: Conduct interview rounds
            interview_data = self.interview_conductor.conduct_all_rounds(candidate)
            
            # Collect all responses and questions
            all_responses = []
            all_questions = []
            for round_data in interview_data["rounds"]:
                all_responses.extend(round_data["responses"])
                all_questions.extend(round_data["questions"])
            
            # Step 6: Evaluate responses dynamically
            print(f"\n🔍 Evaluating Responses...")
            evaluation = self.evaluator.evaluate_responses(
                candidate_id, candidate.name, all_responses, all_questions
            )
            
            # Step 7: Run authenticity detection
            print(f"\n🔐 Running Authenticity Detection...")
            authenticity = self.authenticity_detector.analyze_authenticity(
                candidate_id, candidate.name, all_responses, candidate.to_dict()
            )
            
            # Step 8: Compute final score
            print(f"\n📈 Computing Final Score...")
            final_score = self._compute_final_score(candidate_id, evaluation, authenticity)
            
            # Step 9: Store results in memory
            self.results[candidate_id] = {
                "candidate": candidate.to_dict(),
                "interview": interview_data,
                "evaluation": evaluation,
                "authenticity": authenticity,
                "final_score": final_score,
                "interview_timestamp": datetime.utcnow().isoformat()
            }
            
            print(f"\n✅ Final Score for {candidate.name}: {final_score:.2f}/100")
    
    def _compute_final_score(self, candidate_id: str, 
                            evaluation: Dict[str, Any],
                            authenticity: Dict[str, Any]) -> float:
        """
        Compute final combined score from evaluation and authenticity.
        
        Args:
            candidate_id: Candidate ID
            evaluation: Evaluation results
            authenticity: Authenticity analysis
        
        Returns:
            Final score (0-100)
        """
        # Extract dimension scores
        dim_scores = evaluation.get("dimensions", {})
        interview_score = self.evaluator.compute_interview_score(candidate_id, dim_scores)
        
        # Weight interview score and authenticity
        authenticity_score = authenticity.get("confidence_score", 0.5) * 100
        final_score = (interview_score * 0.85) + (authenticity_score * 0.15)
        
        return float(min(max(final_score, 0), 100))
    
    def _step_final_decisions(self):
        """Step 10: Final hiring decisions and system learning."""
        self.workflow_state["step"] = 10
        
        print("\n📋 FINAL HIRING DECISIONS:\n")
        
        for candidate_id, result in self.results.items():
            candidate_name = result["candidate"]["name"]
            final_score = result["final_score"]
            authenticity = result["authenticity"]["is_authentic"]
            
            # Decision logic
            hired = False
            reason = ""
            
            if final_score >= PASSING_SCORE_THRESHOLD and authenticity:
                hired = True
                reason = f"Excellent fit (Score: {final_score:.2f}, Authentic: Yes)"
                self.workflow_state["candidates_hired"] += 1
            elif final_score >= (PASSING_SCORE_THRESHOLD - 10) and authenticity:
                reason = f"Good fit but borderline (Score: {final_score:.2f})"
            elif not authenticity:
                reason = f"Failed authenticity check (Confidence: {result['authenticity']['confidence_score']:.2f})"
            else:
                reason = f"Below threshold (Score: {final_score:.2f})"
            
            # Save outcome to memory
            self.memory.save_hiring_outcome(candidate_id, hired, reason)
            
            decision_icon = "✅ HIRED" if hired else "❌ REJECTED"
            print(f"{decision_icon}: {candidate_name}")
            print(f"   └─ {reason}\n")
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate workflow summary and statistics."""
        summary = {
            "workflow_state": self.workflow_state,
            "total_candidates_processed": self.workflow_state["candidates_processed"],
            "candidates_shortlisted": self.workflow_state["candidates_shortlisted"],
            "candidates_hired": self.workflow_state["candidates_hired"],
            "hiring_rate": (
                self.workflow_state["candidates_hired"] / self.workflow_state["candidates_processed"] * 100
                if self.workflow_state["candidates_processed"] > 0 else 0
            ),
            "detailed_results": self.results,
            "completion_time": datetime.utcnow().isoformat()
        }
        
        return summary
    
    def print_summary(self, summary: Dict[str, Any]):
        """Pretty print workflow summary."""
        print("\n\n" + "═" * 60)
        print("HIRING WORKFLOW SUMMARY")
        print("═" * 60)
        print(f"Total Candidates Processed: {summary['total_candidates_processed']}")
        print(f"Candidates Shortlisted:     {summary['candidates_shortlisted']}")
        print(f"Candidates Hired:           {summary['candidates_hired']}")
        print(f"Overall Hiring Rate:        {summary['hiring_rate']:.1f}%")
        print("═" * 60)
        print("\n✨ Workflow completed successfully!")
    
    def get_candidate_report(self, candidate_id: str) -> Optional[Dict[str, Any]]:
        """Generate detailed report for a specific candidate."""
        return self.results.get(candidate_id)
    
    def export_results(self, filename: str = "hiring_results.json"):
        """Export all results to JSON file."""
        try:
            summary = self._generate_summary()
            with open(filename, 'w') as f:
                json.dump(summary, f, indent=2, default=str)
            print(f"\n✓ Results exported to {filename}")
            return True
        except Exception as e:
            print(f"✗ Error exporting results: {e}")
            return False
