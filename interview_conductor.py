"""Interview conductor module using OpenAI for AI-driven interviews."""
from typing import List, Dict, Any, Optional
from openai import OpenAI
from datetime import datetime
from config import OPENAI_API_KEY, OPENAI_MODEL, INTERVIEW_ROUNDS, QUESTIONS_PER_ROUND
from memory_manager import MemoryManager
from candidate_manager import Candidate


class InterviewConductor:
    """Conducts AI-driven interview rounds with candidates."""
    
    def __init__(self, memory_manager: MemoryManager):
        """Initialize interview conductor with OpenAI client."""
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = OPENAI_MODEL
        self.memory = memory_manager
        self.interview_data: Dict[str, List[Dict[str, Any]]] = {}
    
    def conduct_interview_round(self, candidate: Candidate, round_num: int,
                               custom_questions: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Conduct an interview round with a candidate.
        
        Args:
            candidate: Candidate object
            round_num: Interview round number (1, 2, or 3)
            custom_questions: Optional custom questions for this round
        
        Returns:
            Dictionary containing questions, responses, and initial scores
        """
        questions = custom_questions or self._get_round_questions(round_num)
        responses = []
        
        print(f"\n📋 Interview Round {round_num} - {candidate.name}")
        print(f"{'─' * 50}")
        
        for i, question in enumerate(questions[:QUESTIONS_PER_ROUND], 1):
            # Simulate candidate response using AI
            response = self._get_ai_response(
                candidate, question, round_num, i
            )
            responses.append(response)
            print(f"Q{i}: {question}")
            print(f"A{i}: {response[:100]}...\n")
        
        # Score responses
        scores = self._score_responses(questions, responses, candidate, round_num)
        
        # Store interview data
        interview_record = {
            "candidate_id": candidate.id,
            "round_number": round_num,
            "questions": questions[:QUESTIONS_PER_ROUND],
            "responses": responses,
            "scores": scores,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if candidate.id not in self.interview_data:
            self.interview_data[candidate.id] = []
        self.interview_data[candidate.id].append(interview_record)
        
        # Save to memory
        self.memory.save_interview_round(
            candidate.id, round_num, responses, [scores.get(f"q{i+1}_score", 0) for i in range(len(responses))]
        )
        
        print(f"✓ Completed Round {round_num} for {candidate.name}")
        return interview_record
    
    def _get_round_questions(self, round_num: int) -> List[str]:
        """Get standard questions for a round."""
        round_key = f"round_{round_num}"
        from config import INTERVIEW_QUESTIONS
        return INTERVIEW_QUESTIONS.get(round_key, [])
    
    def _get_ai_response(self, candidate: Candidate, question: str, 
                        round_num: int, question_num: int) -> str:
        """
        Generate AI candidate response using OpenAI.
        
        Args:
            candidate: Candidate information
            question: Interview question
            round_num: Round number
            question_num: Question number within round
        
        Returns:
            Simulated candidate response
        """
        try:
            prompt = f"""You are simulating a candidate's response in a job interview.
            
Candidate Profile:
- Name: {candidate.name}
- Experience: {candidate.experience_years} years
- Skills: {', '.join(candidate.skills)}
- Education: {candidate.education}
- Background: {candidate.resume_text[:200]}

Interview Context:
- Round: {round_num}/3
- This is question {question_num}

Question: {question}

Provide a realistic and detailed response as this candidate would give in an interview.
Response should be 2-3 sentences and authentic to their profile."""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a job candidate responding to interview questions authentically based on your profile."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=200
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating AI response: {e}")
            return f"I have relevant experience with this. In my previous role, I worked on similar challenges with {', '.join(candidate.skills[:2])}."
    
    def _score_responses(self, questions: List[str], responses: List[str],
                        candidate: Candidate, round_num: int) -> Dict[str, float]:
        """
        Score interview responses using AI evaluation.
        
        Args:
            questions: List of questions asked
            responses: List of candidate responses
            candidate: Candidate information
            round_num: Round number
        
        Returns:
            Dictionary with scores for each response
        """
        scores = {}
        
        try:
            for i, (question, response) in enumerate(zip(questions, responses), 1):
                prompt = f"""Evaluate this job interview response on a scale of 0-100.

Question: {question}
Candidate Response: {response}
Candidate Skills: {', '.join(candidate.skills)}
Candidate Experience: {candidate.experience_years} years

Provide a score (0-100) and one sentence justification.
Format: SCORE: XX
JUSTIFICATION: <your text>"""
                
                eval_response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are an expert job interviewer scoring candidate responses."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.5,
                    max_tokens=100
                )
                
                evaluation = eval_response.choices[0].message.content.strip()
                score = self._extract_score(evaluation)
                scores[f"q{i}_score"] = float(score)
        except Exception as e:
            print(f"Error scoring responses: {e}")
            scores = {f"q{i}_score": 75.0 for i in range(1, len(responses) + 1)}
        
        return scores
    
    def _extract_score(self, evaluation_text: str) -> int:
        """Extract numeric score from evaluation text."""
        try:
            for word in evaluation_text.split():
                if word.isdigit():
                    score = int(word)
                    if 0 <= score <= 100:
                        return score
            return 75  # Default score
        except:
            return 75
    
    def conduct_all_rounds(self, candidate: Candidate) -> Dict[str, Any]:
        """
        Conduct all interview rounds for a candidate.
        
        Args:
            candidate: Candidate to interview
        
        Returns:
            Complete interview results
        """
        all_results = {
            "candidate_id": candidate.id,
            "candidate_name": candidate.name,
            "rounds": []
        }
        
        for round_num in range(1, INTERVIEW_ROUNDS + 1):
            round_result = self.conduct_interview_round(candidate, round_num)
            all_results["rounds"].append(round_result)
        
        return all_results
    
    def get_interview_data(self, candidate_id: str) -> Optional[List[Dict[str, Any]]]:
        """Retrieve interview data for a candidate."""
        return self.interview_data.get(candidate_id, None)
    
    def get_average_scores(self, candidate_id: str) -> Dict[str, float]:
        """Calculate average scores across all rounds for a candidate."""
        interview_rounds = self.interview_data.get(candidate_id, [])
        
        if not interview_rounds:
            return {}
        
        avg_scores = {}
        for i in range(1, QUESTIONS_PER_ROUND + 1):
            scores = [round_data["scores"].get(f"q{i}_score", 0) for round_data in interview_rounds]
            avg_scores[f"q{i}_average"] = sum(scores) / len(scores)
        
        # Overall average
        all_scores = [score for round_data in interview_rounds for score in round_data["scores"].values()]
        avg_scores["overall_average"] = sum(all_scores) / len(all_scores) if all_scores else 0
        
        return avg_scores
