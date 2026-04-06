"""Response evaluator module for analyzing and scoring interview responses."""
from typing import Dict, List, Any, Optional
from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_MODEL
from memory_manager import MemoryManager


class ResponseEvaluator:
    """Evaluates interview responses and provides comprehensive analysis."""
    
    def __init__(self, memory_manager: MemoryManager):
        """Initialize response evaluator."""
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = OPENAI_MODEL
        self.memory = memory_manager
    
    def evaluate_responses(self, candidate_id: str, candidate_name: str,
                          responses: List[str], questions: List[str]) -> Dict[str, Any]:
        """
        Comprehensively evaluate interview responses.
        
        Args:
            candidate_id: Unique candidate identifier
            candidate_name: Name of candidate
            responses: List of responses given by candidate
            questions: List of questions asked
        
        Returns:
            Dictionary containing detailed evaluation results
        """
        evaluation_result = {
            "candidate_id": candidate_id,
            "candidate_name": candidate_name,
            "total_responses": len(responses),
            "dimensions": {},
            "raw_feedback": ""
        }
        
        # Evaluate across different dimensions
        dimensions = [
            ("technical_skills", "technical knowledge and proficiency"),
            ("communication", "clarity, articulation, and presentation"),
            ("problem_solving", "analytical approach and solution thinking"),
            ("cultural_fit", "alignment with team values and work style"),
            ("confidence", "self-assurance and conviction in responses")
        ]
        
        for dimension_key, dimension_desc in dimensions:
            score = self._evaluate_dimension(
                candidate_name, responses, questions, dimension_desc
            )
            evaluation_result["dimensions"][dimension_key] = score
        
        # Generate comprehensive feedback
        feedback = self._generate_feedback(candidate_name, evaluation_result["dimensions"])
        evaluation_result["raw_feedback"] = feedback
        
        print(f"✓ Evaluated responses for {candidate_name}")
        return evaluation_result
    
    def _evaluate_dimension(self, candidate_name: str, responses: List[str],
                           questions: List[str], dimension: str) -> float:
        """
        Evaluate a specific dimension of interview performance.
        
        Args:
            candidate_name: Name of candidate
            responses: Interview responses
            questions: Interview questions
            dimension: Dimension to evaluate
        
        Returns:
            Score for this dimension (0-100)
        """
        try:
            prompt = f"""Evaluate {candidate_name}'s interview performance on {dimension}.

Responses provided:
{chr(10).join(f'{i+1}. {resp[:150]}' for i, resp in enumerate(responses))}

Rate this candidate on {dimension} from 0-100.
Respond ONLY with a number between 0-100."""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": f"You are an expert interviewer. Rate candidates strictly on {dimension}. Respond with only a number 0-100."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=10
            )
            
            score_text = response.choices[0].message.content.strip()
            score = int(''.join(filter(str.isdigit, score_text)) or '75')
            return float(min(max(score, 0), 100))
        except Exception as e:
            print(f"Error evaluating dimension {dimension}: {e}")
            return 75.0
    
    def _generate_feedback(self, candidate_name: str, 
                          dimension_scores: Dict[str, float]) -> str:
        """
        Generate comprehensive feedback summary.
        
        Args:
            candidate_name: Name of candidate
            dimension_scores: Scores across different dimensions
        
        Returns:
            Feedback summary text
        """
        try:
            score_text = "\n".join(
                f"- {dim.replace('_', ' ').title()}: {score:.1f}/100"
                for dim, score in dimension_scores.items()
            )
            
            prompt = f"""Generate a brief (2-3 sentences) summary of {candidate_name}'s interview performance based on these scores:

{score_text}

Provide constructive and professional feedback."""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert HR analyst providing interview feedback."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=150
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating feedback: {e}")
            return "Unable to generate detailed feedback at this time."
    
    def compute_interview_score(self, candidate_id: str,
                               dimension_scores: Dict[str, float]) -> float:
        """
        Compute overall interview score from dimension evaluations.
        
        Args:
            candidate_id: Candidate identifier
            dimension_scores: Scores for each dimension
        
        Returns:
            Weighted overall score (0-100)
        """
        # Weight distribution for interview performance
        weights = {
            "technical_skills": 0.35,
            "communication": 0.20,
            "problem_solving": 0.25,
            "cultural_fit": 0.15,
            "confidence": 0.05
        }
        
        overall_score = sum(
            dimension_scores.get(dim, 0) * weights.get(dim, 0)
            for dim in dimension_scores
        )
        
        return float(overall_score)
    
    def compare_rounds(self, candidate_id: str, round_evaluations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compare evaluations across multiple interview rounds.
        
        Args:
            candidate_id: Candidate identifier
            round_evaluations: List of evaluations from different rounds
        
        Returns:
            Comparative analysis across rounds
        """
        comparison = {
            "candidate_id": candidate_id,
            "total_rounds": len(round_evaluations),
            "dimension_progression": {}
        }
        
        if not round_evaluations:
            return comparison
        
        # Track dimension scores across rounds
        dimensions = set()
        for eval_data in round_evaluations:
            dimensions.update(eval_data.get("dimensions", {}).keys())
        
        for dimension in dimensions:
            scores = [
                eval_data.get("dimensions", {}).get(dimension, 0)
                for eval_data in round_evaluations
            ]
            
            comparison["dimension_progression"][dimension] = {
                "scores_by_round": scores,
                "trend": self._calculate_trend(scores),
                "average": sum(scores) / len(scores) if scores else 0
            }
        
        # Calculate consistency
        comparison["consistency_score"] = self._calculate_consistency(round_evaluations)
        
        return comparison
    
    def _calculate_trend(self, scores: List[float]) -> str:
        """Determine if performance is improving, declining, or stable."""
        if len(scores) < 2:
            return "insufficient_data"
        
        if scores[-1] > scores[0] + 5:
            return "improving"
        elif scores[-1] < scores[0] - 5:
            return "declining"
        else:
            return "stable"
    
    def _calculate_consistency(self, round_evaluations: List[Dict[str, Any]]) -> float:
        """
        Calculate consistency score across rounds.
        
        Args:
            round_evaluations: Evaluations from multiple rounds
        
        Returns:
            Consistency score (0-100, higher = more consistent)
        """
        if len(round_evaluations) < 2:
            return 100.0
        
        try:
            all_dimension_scores = []
            for eval_data in round_evaluations:
                all_dimension_scores.extend(eval_data.get("dimensions", {}).values())
            
            if not all_dimension_scores:
                return 100.0
            
            # Calculate coefficient of variation
            mean_score = sum(all_dimension_scores) / len(all_dimension_scores)
            if mean_score == 0:
                return 0.0
            
            variance = sum((score - mean_score) ** 2 for score in all_dimension_scores) / len(all_dimension_scores)
            std_dev = variance ** 0.5
            cv = (std_dev / mean_score) * 100  # Coefficient of variation
            
            # Convert to 0-100 scale (lower CV = higher consistency)
            consistency = max(0, 100 - cv)
            return float(min(consistency, 100.0))
        except Exception as e:
            print(f"Error calculating consistency: {e}")
            return 50.0
