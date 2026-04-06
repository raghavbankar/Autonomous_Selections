"""Authenticity detection module for identifying genuine vs. inauthentic responses."""
from typing import Dict, List, Any, Optional
from openai import OpenAI
import math
from config import OPENAI_API_KEY, OPENAI_MODEL, AUTHENTICITY_THRESHOLD
from memory_manager import MemoryManager


class AuthenticityDetector:
    """Detects authenticity and consistency in candidate responses."""
    
    def __init__(self, memory_manager: MemoryManager):
        """Initialize authenticity detector."""
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = OPENAI_MODEL
        self.memory = memory_manager
    
    def analyze_authenticity(self, candidate_id: str, candidate_name: str,
                            responses: List[str], candidate_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze authenticity of candidate responses.
        
        Args:
            candidate_id: Unique candidate identifier
            candidate_name: Name of candidate
            responses: List of interview responses
            candidate_profile: Candidate's background information
        
        Returns:
            Authenticity analysis with confidence score
        """
        analysis = {
            "candidate_id": candidate_id,
            "candidate_name": candidate_name,
            "is_authentic": True,
            "confidence_score": 1.0,
            "checks": {},
            "flags": []
        }
        
        # Run multiple authenticity checks
        checks = [
            ("consistency_check", self._check_consistency(responses)),
            ("response_length_variance", self._check_response_variance(responses)),
            ("language_authenticity", self._check_language_patterns(candidate_name, responses)),
            ("profile_alignment", self._check_profile_alignment(responses, candidate_profile)),
            ("plagiarism_detection", self._check_plagiarism_patterns(responses))
        ]
        
        for check_name, result in checks:
            analysis["checks"][check_name] = result
            if not result["passed"] and result["severity"] == "high":
                analysis["flags"].append(check_name)
        
        # Calculate overall authenticity
        authenticity_score = self._calculate_authenticity_score(analysis["checks"])
        analysis["confidence_score"] = authenticity_score
        analysis["is_authentic"] = authenticity_score >= AUTHENTICITY_THRESHOLD
        
        # Save to memory
        self.memory.save_authenticity_check(
            candidate_id,
            analysis["is_authentic"],
            authenticity_score,
            {k: v for k, v in analysis.items() if k not in ["candidate_id", "candidate_name"]}
        )
        
        print(f"✓ Authenticity analysis completed for {candidate_name} (Score: {authenticity_score:.2f})")
        return analysis
    
    def _check_consistency(self, responses: List[str]) -> Dict[str, Any]:
        """
        Check consistency across responses using AI analysis.
        
        Args:
            responses: List of candidate responses
        
        Returns:
            Consistency check result
        """
        try:
            prompt = f"""Analyze these interview responses for consistency in tone, facts, and claims:

Responses:
{chr(10).join(f'{i+1}. {resp}' for i, resp in enumerate(responses))}

Are there any contradictions or inconsistencies? Rate consistency 0-100 where 100 is perfectly consistent.
Respond with: SCORE: XX
DETAILS: <brief explanation>"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at detecting consistency issues in responses."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=100
            )
            
            result_text = response.choices[0].message.content.strip()
            score = self._extract_numeric_score(result_text)
            
            return {
                "passed": score >= 70,
                "score": float(score),
                "severity": "high" if score < 50 else "medium" if score < 70 else "low",
                "details": result_text
            }
        except Exception as e:
            print(f"Error in consistency check: {e}")
            return {"passed": True, "score": 75.0, "severity": "low", "details": "Unable to analyze"}
    
    def _check_response_variance(self, responses: List[str]) -> Dict[str, Any]:
        """
        Check variance in response lengths (unusual patterns may indicate issues).
        
        Args:
            responses: List of candidate responses
        
        Returns:
            Variance check result
        """
        try:
            lengths = [len(resp.split()) for resp in responses]
            
            if not lengths:
                return {"passed": True, "score": 100.0, "severity": "low", "details": "No responses to analyze"}
            
            mean_length = sum(lengths) / len(lengths)
            variance = sum((l - mean_length) ** 2 for l in lengths) / len(lengths)
            std_dev = variance ** 0.5
            
            # Calculate coefficient of variation
            cv = (std_dev / mean_length * 100) if mean_length > 0 else 0
            
            # Flag if variance is too high (possible templated responses)
            passed = cv < 50  # Allow up to 50% variance
            severity = "high" if cv > 70 else "medium" if cv > 50 else "low"
            
            return {
                "passed": passed,
                "score": float(100 - min(cv, 100)),
                "severity": severity,
                "details": f"Response length variance: {cv:.1f}% (μ={mean_length:.0f} words)"
            }
        except Exception as e:
            print(f"Error in variance check: {e}")
            return {"passed": True, "score": 75.0, "severity": "low", "details": "Unable to analyze"}
    
    def _check_language_patterns(self, candidate_name: str, 
                                responses: List[str]) -> Dict[str, Any]:
        """
        Check for natural language patterns (detect AI-generated or templated responses).
        
        Args:
            candidate_name: Candidate name
            responses: List of responses
        
        Returns:
            Language pattern check result
        """
        try:
            prompt = f"""Analyze these responses for naturalness and authenticity. Look for:
- Overly formal or templated language
- Repetitive phrases
- AI-generated patterns
- Natural conversation flow

Responses:
{chr(10).join(f'{i+1}. {resp}' for i, resp in enumerate(responses))}

Rate naturalness 0-100. Respond with: SCORE: XX"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at detecting natural vs. artificial language patterns."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=50
            )
            
            score = self._extract_numeric_score(response.choices[0].message.content.strip())
            
            return {
                "passed": score >= 70,
                "score": float(score),
                "severity": "high" if score < 50 else "medium" if score < 70 else "low",
                "details": f"Language naturalness score: {score}"
            }
        except Exception as e:
            print(f"Error in language pattern check: {e}")
            return {"passed": True, "score": 75.0, "severity": "low", "details": "Unable to analyze"}
    
    def _check_profile_alignment(self, responses: List[str],
                                candidate_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check if responses align with candidate's declared profile.
        
        Args:
            responses: Interview responses
            candidate_profile: Candidate's background
        
        Returns:
            Profile alignment check result
        """
        try:
            profile_summary = f"""
Experience: {candidate_profile.get('experience_years', 0)} years
Skills: {', '.join(candidate_profile.get('skills', []))}
Education: {candidate_profile.get('education', 'N/A')}
Background: {candidate_profile.get('resume_text', 'N/A')[:200]}"""
            
            prompt = f"""Check if these responses align with the candidate's profile:

Profile:
{profile_summary}

Responses:
{chr(10).join(f'{i+1}. {resp}' for i, resp in enumerate(responses))}

Do the responses match their claimed background and expertise? Rate alignment 0-100.
Respond with: SCORE: XX"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at detecting profile misalignment."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=50
            )
            
            score = self._extract_numeric_score(response.choices[0].message.content.strip())
            
            return {
                "passed": score >= 70,
                "score": float(score),
                "severity": "high" if score < 50 else "medium" if score < 70 else "low",
                "details": f"Profile alignment score: {score}"
            }
        except Exception as e:
            print(f"Error in profile alignment check: {e}")
            return {"passed": True, "score": 75.0, "severity": "low", "details": "Unable to analyze"}
    
    def _check_plagiarism_patterns(self, responses: List[str]) -> Dict[str, Any]:
        """
        Check for common plagiarism patterns or overly generic responses.
        
        Args:
            responses: Interview responses
        
        Returns:
            Plagiarism check result
        """
        try:
            common_phrases = [
                "I am passionate about",
                "I am committed to",
                "At the end of the day",
                "It goes without saying",
                "To be honest",
                "24/7",
                "outside the box",
                "low-hanging fruit"
            ]
            
            phrase_count = sum(
                sum(1 for phrase in common_phrases if phrase.lower() in resp.lower())
                for resp in responses
            )
            
            # Flag if too many common phrases detected
            phrase_ratio = phrase_count / (sum(len(r.split()) for r in responses) / 100) if responses else 0
            
            score = max(0, 100 - (phrase_ratio * 10))
            passed = score >= 70
            
            return {
                "passed": passed,
                "score": float(score),
                "severity": "high" if score < 50 else "medium" if score < 70 else "low",
                "details": f"Common phrases detected: {phrase_count}"
            }
        except Exception as e:
            print(f"Error in plagiarism check: {e}")
            return {"passed": True, "score": 75.0, "severity": "low", "details": "Unable to analyze"}
    
    def _calculate_authenticity_score(self, checks: Dict[str, Dict[str, Any]]) -> float:
        """
        Calculate overall authenticity confidence score.
        
        Args:
            checks: Dictionary of check results
        
        Returns:
            Overall authenticity score (0-1)
        """
        if not checks:
            return 0.5
        
        scores = [check.get("score", 50) / 100 for check in checks.values()]
        
        # Weights: emphasize critical checks more
        weights = {
            "consistency_check": 0.35,
            "language_authenticity": 0.25,
            "profile_alignment": 0.25,
            "response_length_variance": 0.10,
            "plagiarism_detection": 0.05
        }
        
        weighted_score = sum(
            checks.get(check_name, {}).get("score", 50) / 100 * weight
            for check_name, weight in weights.items()
        )
        
        return float(min(max(weighted_score, 0), 1))
    
    def _extract_numeric_score(self, text: str) -> int:
        """Extract numeric score from response text."""
        try:
            for word in text.split():
                if word.isdigit():
                    score = int(word)
                    if 0 <= score <= 100:
                        return score
            return 75
        except:
            return 75
