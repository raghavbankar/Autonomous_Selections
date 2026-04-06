# Autonomous Hiring Agent - Project Structure

## 📁 Project Files & Descriptions

### Core Application Files

| File | Purpose |
|------|---------|
| **main.py** | Entry point for running the complete hiring workflow |
| **hiring_agent.py** | Main orchestrator that coordinates all steps (1-10 of workflow) |
| **quick_start.py** | Interactive quick-start guide with environment check and demo |

### Module Files

| File | Purpose |
|------|---------|
| **candidate_manager.py** | Handles candidate fetching, preprocessing, scoring, and ranking |
| **interview_conductor.py** | Orchestrates AI-driven interview rounds using OpenAI |
| **evaluator.py** | Evaluates interview responses across multiple dimensions |
| **authenticity_detector.py** | Detects authenticity and consistency in responses |
| **memory_manager.py** | Manages persistent storage in Supabase database |
| **config.py** | Configuration settings and constants |

### Documentation Files

| File | Purpose |
|------|---------|
| **README.md** | Complete project documentation and setup guide |
| **PROJECT_STRUCTURE.md** | This file - overview of project structure |
| **.env.example** | Template for environment variables |

### Utility Files

| File | Purpose |
|------|---------|
| **usage_examples.py** | 10 comprehensive usage examples with code |
| **db_setup.py** | Supabase SQL schema and database setup |
| **requirements.txt** | Python dependencies |

---

## 🔄 Workflow Steps

### 1. FETCH CANDIDATES VIA API
**File**: `candidate_manager.py`
- Fetches candidates from API or generates mock data
- Supports both real API endpoints and mock data for testing

### 2. PREPROCESS AND STRUCTURE DATA
**File**: `candidate_manager.py`
- Cleans and structures candidate information
- Calculates profile completeness
- Assesses seniority level
- Saves to Supabase via `memory_manager.py`

### 3. SCORE AND RANK CANDIDATES
**File**: `candidate_manager.py`
- Scores candidates based on technical skills and experience
- Ranks candidates by score
- Saves evaluation scores to Supabase

### 4. SHORTLIST TOP CANDIDATES
**File**: `candidate_manager.py`
- Selects top N candidates for interview
- Saves shortlist to Supabase
- Default shortlist size: 10 candidates

### 5-7. CONDUCT INTERVIEWS & EVALUATION
**Files**: `interview_conductor.py`, `evaluator.py`, `authenticity_detector.py`
- **Interview**: Conducts multi-round AI interviews using OpenAI
- **Evaluation**: Scores responses on 5 dimensions
- **Authenticity**: Runs 5-point authenticity verification

### 8. COMPUTE FINAL SCORE
**File**: `hiring_agent.py`
- Combines interview score (85%) and authenticity score (15%)
- Final score: 0-100

### 9. STORE RESULTS IN MEMORY
**File**: `memory_manager.py`
- Saves all data to Supabase tables
- Stores: candidates, interviews, evaluations, authenticity, outcomes

### 10. UPDATE SYSTEM BASED ON OUTCOMES
**File**: `hiring_agent.py`
- Records hiring decisions
- Tracks statistics for learning
- Enables system improvement over time

---

## 🎯 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up environment
cp .env.example .env
# Edit .env with your API keys

# 3. Run the agent
python main.py
```

---

**Status**: ✅ Production Ready | **Version**: 1.0.0
