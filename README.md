# 🤖 Autonomous Hiring Agent

A sophisticated AI-powered hiring system that automates the candidate evaluation process using OpenAI and Supabase for persistent memory management.

## 📋 Workflow Overview

The agent implements a 10-step autonomous hiring workflow:

1. **Fetch Candidates** - Pull candidate data from API or use mock data
2. **Preprocess & Structure** - Clean and organize candidate information
3. **Score & Rank** - Evaluate candidates based on background and skills
4. **Shortlist Top Candidates** - Select top N candidates for interviews
5. **Conduct AI Interview Rounds** - Run multiple rounds of AI-driven interviews
6. **Evaluate Responses Dynamically** - Assess interview responses on multiple dimensions
7. **Run Authenticity Detection** - Verify response authenticity and consistency
8. **Compute Final Score** - Calculate weighted final hiring scores
9. **Store Results in Memory** - Persist all data to Supabase
10. **Update System Based on Outcomes** - Learn and improve from hiring decisions

## 🛠️ Tech Stack

- **Python 3.8+** - Core language
- **OpenAI GPT-4** - AI interviews and evaluation
- **Supabase** - Persistent memory (Open Brain MCP)
- **Pydantic** - Data validation
- **SQLAlchemy** - Database ORM

## 📦 Installation

### 1. Clone the Repository
```bash
cd e:\projects\Interns_automations
```

### 2. Create Virtual Environment
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

Edit `.env` with:

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4

# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key-here

# Hiring Configuration
PASSING_SCORE_THRESHOLD=70.0
SHORTLIST_SIZE=10
```

### 5. Setup Supabase Tables

Create these tables in your Supabase project:

#### candidates
```sql
CREATE TABLE candidates (
  id TEXT PRIMARY KEY,
  data JSONB,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);
```

#### interview_rounds
```sql
CREATE TABLE interview_rounds (
  id BIGSERIAL PRIMARY KEY,
  candidate_id TEXT,
  round_number INTEGER,
  responses JSONB,
  scores JSONB,
  timestamp TIMESTAMP
);
```

#### evaluations
```sql
CREATE TABLE evaluations (
  id BIGSERIAL PRIMARY KEY,
  candidate_id TEXT,
  technical_skills FLOAT,
  communication FLOAT,
  problem_solving FLOAT,
  cultural_fit FLOAT,
  authenticity FLOAT,
  final_score FLOAT,
  timestamp TIMESTAMP
);
```

#### authenticity_checks
```sql
CREATE TABLE authenticity_checks (
  id BIGSERIAL PRIMARY KEY,
  candidate_id TEXT,
  is_authentic BOOLEAN,
  confidence_score FLOAT,
  details JSONB,
  timestamp TIMESTAMP
);
```

#### shortlists
```sql
CREATE TABLE shortlists (
  id BIGSERIAL PRIMARY KEY,
  candidate_ids JSONB,
  status TEXT,
  timestamp TIMESTAMP
);
```

#### hiring_outcomes
```sql
CREATE TABLE hiring_outcomes (
  id BIGSERIAL PRIMARY KEY,
  candidate_id TEXT,
  hired BOOLEAN,
  feedback TEXT,
  timestamp TIMESTAMP
);
```

## 🚀 Quick Start

### Run with Mock Data
```bash
python main.py
```

### Run with Real API
```python
from hiring_agent import HiringAgent

agent = HiringAgent()
results = agent.run_workflow(
    api_endpoint="https://your-api.com/candidates",
    use_mock_data=False
)
agent.print_summary(results)
agent.export_results("results.json")
```

## 📊 Project Structure

```
├── config.py                    # Configuration settings
├── memory_manager.py            # Supabase memory management
├── candidate_manager.py         # Candidate fetching & scoring
├── interview_conductor.py       # AI interview orchestration
├── evaluator.py               # Response evaluation
├── authenticity_detector.py    # Authenticity analysis
├── hiring_agent.py            # Main orchestrator
├── main.py                    # Entry point
├── requirements.txt           # Dependencies
├── .env.example              # Environment variable template
└── README.md                 # This file
```

## 🎯 Key Features

### 1. Intelligent Candidate Scoring
- Technical skills assessment
- Experience evaluation
- Profile completeness analysis
- Multi-factor ranking

### 2. AI-Driven Interviews
- 3-round interview process
- Context-aware questions
- Dynamic response evaluation
- Authenticity verification

### 3. Multi-Dimensional Evaluation
- Technical skills (35%)
- Communication skills (20%)
- Problem-solving ability (25%)
- Cultural fit (15%)
- Authenticity (5%)

### 4. Authenticity Detection
- **Consistency Check** - Detect contradictions across responses
- **Response Variance** - Flag unusual response length patterns
- **Language Patterns** - Identify AI-generated or templated responses
- **Profile Alignment** - Verify responses match claimed background
- **Plagiarism Detection** - Detect common/generic phrases

### 5. Persistent Memory
- All candidate data stored in Supabase
- Complete interview history
- Evaluation scores and feedback
- Authenticity reports
- Hiring outcomes for system learning

### 6. Learning & Improvement
- Track hiring outcomes
- Analyze success patterns
- Update scoring weights based on results
- Continuous system improvement

## 🔧 Configuration

Edit `config.py` to customize:

```python
# Scoring weights
SCORING_WEIGHTS = {
    "technical_skills": 0.35,
    "communication": 0.20,
    "problem_solving": 0.25,
    "cultural_fit": 0.15,
    "authenticity": 0.05
}

# Interview questions
INTERVIEW_QUESTIONS = {
    "round_1": ["Question 1", "Question 2", "Question 3"],
    "round_2": ["Question 1", "Question 2", "Question 3"],
    "round_3": ["Question 1", "Question 2", "Question 3"]
}

# Thresholds
PASSING_SCORE_THRESHOLD = 70.0
AUTHENTICITY_THRESHOLD = 0.75
SHORTLIST_SIZE = 10
```

## 📈 Output Format

The agent generates comprehensive results:

```json
{
  "workflow_state": {
    "step": 10,
    "candidates_processed": 5,
    "candidates_shortlisted": 3,
    "candidates_hired": 1
  },
  "detailed_results": {
    "cand_001": {
      "candidate": {...},
      "interview": {...},
      "evaluation": {...},
      "authenticity": {...},
      "final_score": 82.5
    }
  }
}
```

## 🔐 Security Considerations

1. **API Keys** - Keep OPENAI_API_KEY and SUPABASE_KEY in .env (never commit)
2. **Supabase RLS** - Enable Row Level Security policies for data protection
3. **Data Privacy** - Consider GDPR/compliance requirements for candidate data
4. **Authentication** - Use JWT tokens for Supabase access

## 🤝 API Integration

To use a real candidate API instead of mock data:

```python
agent = HiringAgent()
results = agent.run_workflow(
    api_endpoint="https://api.example.com/candidates",
    use_mock_data=False
)
```

Expected API response format:
```json
{
  "candidates": [
    {
      "id": "cand_001",
      "name": "John Doe",
      "email": "john@example.com",
      "experience_years": 5,
      "skills": ["Python", "AI"],
      "education": "BS Computer Science",
      "resume_text": "..."
    }
  ]
}
```

## 📝 Logging & Monitoring

The agent provides detailed progress output:

```
🚀 Initializing Autonomous Hiring Agent

============================================================
STEP 1: FETCH CANDIDATES VIA API
============================================================
✓ Fetched 5 candidates

============================================================
STEP 2: PREPROCESS AND STRUCTURE DATA
============================================================
✓ Preprocessed and structured 5 candidates
...
```

## 🧪 Testing

Run with mock data to test the complete workflow:

```bash
# Uses 5 mock candidates for demonstration
python main.py
```

Check `hiring_results.json` for detailed output.

## 🚀 Advanced Usage

### Custom Interview Questions
```python
custom_questions = [
    "Tell us about your proudest achievement",
    "How do you handle team conflicts?"
]

agent.interview_conductor.conduct_interview_round(
    candidate, 
    round_num=1,
    custom_questions=custom_questions
)
```

### Get Candidate Report
```python
report = agent.get_candidate_report("cand_001")
print(f"Final Score: {report['final_score']}")
print(f"Feedback: {report['evaluation']['raw_feedback']}")
```

### Export Results
```python
agent.export_results("hiring_results.json")
```

## 🐛 Troubleshooting

### OpenAI API Errors
- Check OPENAI_API_KEY is valid
- Verify account has GPT-4 access
- Check rate limits and quota

### Supabase Connection Issues
- Verify SUPABASE_URL and SUPABASE_KEY
- Check table permissions and RLS policies
- Ensure tables are created correctly

### No Results Generated
- Check .env file is loaded
- Verify candidates were fetched
- Check OpenAI API quota

## 📚 Documentation

Each module includes comprehensive docstrings:
- `memory_manager.py` - Memory operations
- `candidate_manager.py` - Candidate lifecycle
- `interview_conductor.py` - Interview orchestration
- `evaluator.py` - Response evaluation
- `authenticity_detector.py` - Authenticity analysis
- `hiring_agent.py` - Main workflow

## 🔄 Workflow Example

```python
from hiring_agent import HiringAgent

# Initialize agent
agent = HiringAgent()

# Run complete workflow (uses mock data by default)
results = agent.run_workflow()

# Print summary
agent.print_summary(results)

# Export results
agent.export_results("hiring_2024.json")

# Get specific candidate report
report = agent.get_candidate_report("cand_001")
```

## 📊 Metrics & Analytics

The system tracks:
- Candidate sourcing metrics
- Interview performance by dimension
- Authenticity scores and flags
- Final hiring decisions
- Hiring success rate
- System improvement over time

## 🎓 Learning Framework

The agent improves through:
1. Outcome tracking (hired vs rejected)
2. Performance correlation analysis
3. Weight adjustment based on results
4. Pattern recognition from successful hires

## 💡 Future Enhancements

- [ ] Multi-language interview support
- [ ] Video interview analysis
- [ ] Competitor benchmarking
- [ ] Skill gap analysis
- [ ] Diversity metrics tracking
- [ ] Predictive performance scoring
- [ ] Custom scoring model training

## 📞 Support

For issues or questions:
1. Check `.env` configuration
2. Review Supabase table setup
3. Check API endpoints and keys
4. Review error messages in output

## 📄 License

MIT License - Feel free to use and modify

## 🙏 Acknowledgments

- OpenAI for GPT-4 API
- Supabase for database and memory management
- Python community for excellent libraries

---

**Status**: ✅ Ready for production use with proper configuration

**Last Updated**: April 2026
