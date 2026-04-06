"""Configuration settings for the autonomous hiring agent."""
import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")

# Supabase Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")

# Hiring Agent Configuration
INTERVIEW_ROUNDS = int(os.getenv("INTERVIEW_ROUNDS", 3))
QUESTIONS_PER_ROUND = int(os.getenv("QUESTIONS_PER_ROUND", 3))
PASSING_SCORE_THRESHOLD = float(os.getenv("PASSING_SCORE_THRESHOLD", 70.0))
AUTHENTICITY_THRESHOLD = float(os.getenv("AUTHENTICITY_THRESHOLD", 0.75))

# Candidate Configuration
MAX_CANDIDATES_TO_PROCESS = int(os.getenv("MAX_CANDIDATES_TO_PROCESS", 50))
SHORTLIST_SIZE = int(os.getenv("SHORTLIST_SIZE", 10))

# Scoring Weights
SCORING_WEIGHTS = {
    "technical_skills": 0.35,
    "communication": 0.20,
    "problem_solving": 0.25,
    "cultural_fit": 0.15,
    "authenticity": 0.05
}

# Interview Questions by Round
INTERVIEW_QUESTIONS = {
    "round_1": [
        "Tell us about your experience with our industry.",
        "What attracts you to this role?",
        "Describe a challenging project you've worked on."
    ],
    "round_2": [
        "How do you approach problem-solving?",
        "Tell us about a time you failed and what you learned.",
        "How do you handle disagreements with team members?"
    ],
    "round_3": [
        "Where do you see yourself in 5 years?",
        "What motivates you professionally?",
        "Why should we hire you over other candidates?"
    ]
}

# Authenticity Detection Triggers
AUTHENTICITY_CHECKS = {
    "response_length_variance": 0.2,  # 20% variance threshold
    "consistency_check": True,
    "plagiarism_detection": True,
    "behavior_analysis": True
}
