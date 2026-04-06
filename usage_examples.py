"""
AUTONOMOUS HIRING AGENT - USAGE GUIDE & EXAMPLES
================================================

This guide shows practical examples of how to use the hiring agent.
"""

# ============================================================================
# EXAMPLE 1: Basic Usage with Mock Data
# ============================================================================
"""
The simplest way to run the agent - perfect for testing and demos.
"""

from hiring_agent import HiringAgent

def example_basic():
    # Initialize the agent
    agent = HiringAgent()
    
    # Run with mock candidates (no real data needed)
    results = agent.run_workflow(use_mock_data=True)
    
    # Print summary
    agent.print_summary(results)
    
    # Export results to JSON
    agent.export_results("hiring_results.json")

# Run: python -c "from usage_examples import example_basic; example_basic()"


# ============================================================================
# EXAMPLE 2: Using Real API Endpoint
# ============================================================================
"""
Fetch candidates from your own API instead of using mock data.
"""

def example_real_api():
    agent = HiringAgent()
    
    # Provide your API endpoint
    api_endpoint = "https://your-company-api.com/candidates"
    
    # Run workflow with real data
    results = agent.run_workflow(
        api_endpoint=api_endpoint,
        use_mock_data=False  # Disable mock data
    )
    
    agent.print_summary(results)
    agent.export_results("hiring_results_real_data.json")


# ============================================================================
# EXAMPLE 3: Custom Configuration
# ============================================================================
"""
Customize thresholds, scoring weights, and interview questions.
"""

import config
from hiring_agent import HiringAgent

def example_custom_config():
    # Modify config before running
    config.PASSING_SCORE_THRESHOLD = 75.0  # Higher threshold
    config.SHORTLIST_SIZE = 5  # Smaller shortlist
    config.INTERVIEW_ROUNDS = 2  # Fewer rounds
    
    # Update scoring weights to emphasize technical skills
    config.SCORING_WEIGHTS = {
        "technical_skills": 0.50,  # Increased from 0.35
        "communication": 0.15,
        "problem_solving": 0.20,
        "cultural_fit": 0.10,
        "authenticity": 0.05
    }
    
    # Custom interview questions
    config.INTERVIEW_QUESTIONS = {
        "round_1": [
            "Describe your most complex technical project.",
            "How do you stay updated with industry trends?"
        ],
        "round_2": [
            "How would you handle a critical production issue?",
            "Describe your coding philosophy."
        ]
    }
    
    agent = HiringAgent()
    results = agent.run_workflow()
    agent.print_summary(results)


# ============================================================================
# EXAMPLE 4: Get Individual Candidate Reports
# ============================================================================
"""
Retrieve and analyze detailed reports for specific candidates.
"""

from hiring_agent import HiringAgent
import json

def example_candidate_reports():
    agent = HiringAgent()
    results = agent.run_workflow()
    
    # Access detailed results for each candidate
    for candidate_id in results["detailed_results"]:
        report = agent.get_candidate_report(candidate_id)
        
        print(f"\n{'='*60}")
        print(f"CANDIDATE REPORT: {report['candidate']['name']}")
        print(f"{'='*60}")
        
        # Basic Info
        print(f"\n📋 Basic Information:")
        print(f"   Email: {report['candidate']['email']}")
        print(f"   Experience: {report['candidate']['experience_years']} years")
        print(f"   Skills: {', '.join(report['candidate']['skills'])}")
        
        # Interview Scores
        print(f"\n🎤 Interview Scores by Round:")
        for i, round_data in enumerate(report['interview'], 1):
            avg_score = sum(round_data['scores'].values()) / len(round_data['scores'])
            print(f"   Round {i}: {avg_score:.2f}/100")
        
        # Evaluation Dimensions
        print(f"\n📊 Evaluation Dimensions:")
        for dimension, score in report['evaluation']['dimensions'].items():
            print(f"   {dimension.replace('_', ' ').title()}: {score:.2f}/100")
        
        # Authenticity Analysis
        print(f"\n🔐 Authenticity Analysis:")
        print(f"   Authentic: {report['authenticity']['is_authentic']}")
        print(f"   Confidence: {report['authenticity']['confidence_score']:.2f}/1.00")
        print(f"   Flags: {', '.join(report['authenticity']['flags']) if report['authenticity']['flags'] else 'None'}")
        
        # Final Decision
        print(f"\n✨ Final Score: {report['final_score']:.2f}/100")
        print(f"   Feedback: {report['evaluation']['raw_feedback']}")


# ============================================================================
# EXAMPLE 5: Batch Process Multiple Job Openings
# ============================================================================
"""
Run the hiring agent for multiple job positions sequentially.
"""

from hiring_agent import HiringAgent
import json
from datetime import datetime

def example_batch_processing():
    job_openings = [
        {"role": "Senior Python Developer", "shortlist_size": 5},
        {"role": "ML Engineer", "shortlist_size": 5},
        {"role": "DevOps Engineer", "shortlist_size": 5}
    ]
    
    all_results = {}
    
    for job in job_openings:
        print(f"\n\n{'#'*60}")
        print(f"Processing Job: {job['role']}")
        print(f"{'#'*60}\n")
        
        # Update config for this job
        import config
        config.SHORTLIST_SIZE = job['shortlist_size']
        
        # Run agent for this job
        agent = HiringAgent()
        results = agent.run_workflow(use_mock_data=True)
        
        # Store results
        all_results[job['role']] = results
        
        # Export individual results
        filename = f"hiring_{job['role'].replace(' ', '_').lower()}.json"
        agent.export_results(filename)
    
    # Generate summary report
    print("\n\n" + "="*60)
    print("BATCH PROCESSING SUMMARY")
    print("="*60)
    
    for role, results in all_results.items():
        print(f"\n{role}:")
        print(f"  Candidates Processed: {results['total_candidates_processed']}")
        print(f"  Shortlisted: {results['candidates_shortlisted']}")
        print(f"  Hired: {results['candidates_hired']}")
        print(f"  Hiring Rate: {results['hiring_rate']:.1f}%")


# ============================================================================
# EXAMPLE 6: Direct Memory Access for Analytics
# ============================================================================
"""
Access Supabase memory directly to query hiring data and analytics.
"""

from memory_manager import MemoryManager

def example_analytics():
    memory = MemoryManager()
    
    # Get overall statistics
    stats = memory.get_stats()
    print(f"Overall Hiring Statistics:")
    print(f"  Total Candidates: {stats.get('total_candidates_processed', 0)}")
    print(f"  Total Hired: {stats.get('total_hired', 0)}")
    print(f"  Hiring Rate: {stats.get('hiring_rate', 0):.1f}%")
    
    # Get all shortlisted candidates
    latest_shortlist = memory.get_latest_shortlist()
    print(f"\nLatest Shortlist ({len(latest_shortlist)} candidates):")
    for candidate_id in latest_shortlist:
        candidate_data = memory.get_candidate(candidate_id)
        if candidate_data:
            score = memory.get_evaluation_score(candidate_id)
            print(f"  • {candidate_data.get('name')} - Score: {score.get('final_score', 0):.2f}")


# ============================================================================
# EXAMPLE 7: Custom Candidate Filtering Before Interview
# ============================================================================
"""
Run custom filtering logic before sending candidates to interview rounds.
"""

from hiring_agent import HiringAgent
from candidate_manager import CandidateManager

def example_custom_filtering():
    agent = HiringAgent()
    
    # Fetch candidates
    candidates = agent.candidate_manager.fetch_candidates(use_mock_data=True)
    
    # Custom filter logic - e.g., only candidates with 5+ years experience
    filtered = [c for c in candidates if c.experience_years >= 5]
    
    print(f"Filtered {len(candidates)} candidates down to {len(filtered)}")
    print("Candidates with 5+ years experience:")
    for c in filtered:
        print(f"  • {c.name} ({c.experience_years} years)")
    
    # Continue workflow with filtered candidates
    # (This would require modifying the agent code slightly)


# ============================================================================
# EXAMPLE 8: Compare Candidates Head-to-Head
# ============================================================================
"""
Analyze and compare specific candidates side-by-side.
"""

from hiring_agent import HiringAgent

def example_candidate_comparison():
    agent = HiringAgent()
    results = agent.run_workflow()
    
    # Get top 2 candidates
    candidate_ids = list(results['detailed_results'].keys())[:2]
    
    print("\nCANDIDATE COMPARISON")
    print("="*70)
    
    # Comparison headers
    print(f"{'Metric':<30} | {'Candidate 1':<15} | {'Candidate 2':<15}")
    print("-"*70)
    
    for i, cand_id in enumerate(candidate_ids, 1):
        report = agent.get_candidate_report(cand_id)
        
        if i == 1:
            cand1_name = report['candidate']['name']
            cand1_score = report['final_score']
            cand1_auth = report['authenticity']['is_authentic']
        else:
            cand2_name = report['candidate']['name']
            cand2_score = report['final_score']
            cand2_auth = report['authenticity']['is_authentic']
    
    # Print comparisons
    print(f"{'Final Score':<30} | {cand1_score:<15.2f} | {cand2_score:<15.2f}")
    print(f"{'Authentic':<30} | {str(cand1_auth):<15} | {str(cand2_auth):<15}")
    
    # Technical skills comparison
    cand1_tech = agent.get_candidate_report(candidate_ids[0])['evaluation']['dimensions'].get('technical_skills', 0)
    cand2_tech = agent.get_candidate_report(candidate_ids[1])['evaluation']['dimensions'].get('technical_skills', 0)
    print(f"{'Technical Skills':<30} | {cand1_tech:<15.2f} | {cand2_tech:<15.2f}")
    
    print("="*70)


# ============================================================================
# EXAMPLE 9: Scheduled Workflow Execution
# ============================================================================
"""
Run the hiring agent on a schedule (e.g., daily, weekly).
"""

from hiring_agent import HiringAgent
from datetime import datetime
import time

def example_scheduled_execution():
    """
    This would typically be run with a scheduler like APScheduler.
    """
    
    def run_daily_hiring():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        agent = HiringAgent()
        results = agent.run_workflow(use_mock_data=True)
        
        # Export with timestamp
        filename = f"hiring_results_{timestamp}.json"
        agent.export_results(filename)
        
        print(f"✓ Completed daily hiring run: {filename}")
        
        return results
    
    # For production, use APScheduler:
    # from apscheduler.schedulers.background import BackgroundScheduler
    # scheduler = BackgroundScheduler()
    # scheduler.add_job(run_daily_hiring, 'cron', hour=9, minute=0)
    # scheduler.start()


# ============================================================================
# EXAMPLE 10: Error Handling & Retry Logic
# ============================================================================
"""
Implement robust error handling and retry logic.
"""

from hiring_agent import HiringAgent
import time
from typing import Optional

def example_error_handling():
    """
    Run the hiring agent with error handling and retry logic.
    """
    
    def run_with_retry(max_retries: int = 3) -> Optional[dict]:
        for attempt in range(max_retries):
            try:
                print(f"Attempt {attempt + 1}/{max_retries}...")
                
                agent = HiringAgent()
                results = agent.run_workflow(use_mock_data=True)
                
                # Validate results
                if results.get('total_candidates_processed', 0) > 0:
                    print("✓ Workflow completed successfully")
                    return results
                else:
                    raise ValueError("No candidates processed")
            
            except Exception as e:
                print(f"✗ Attempt {attempt + 1} failed: {e}")
                
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    print(f"  Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    print("✗ All retry attempts exhausted")
                    return None
    
    results = run_with_retry(max_retries=3)
    if results:
        print(f"\nFinal Results: {results['candidates_hired']} candidates hired")


# ============================================================================
# RUNNING EXAMPLES
# ============================================================================

if __name__ == "__main__":
    print("Autonomous Hiring Agent - Usage Examples")
    print("="*60)
    print("\nChoose an example to run:")
    print("  1. Basic usage with mock data")
    print("  2. Real API endpoint")
    print("  3. Custom configuration")
    print("  4. Candidate reports")
    print("  5. Batch processing")
    print("  6. Analytics & memory access")
    print("  7. Custom filtering")
    print("  8. Candidate comparison")
    print("  9. Scheduled execution")
    print("  10. Error handling")
    
    choice = input("\nSelect example (1-10): ").strip()
    
    examples = {
        "1": example_basic,
        "2": example_real_api,
        "3": example_custom_config,
        "4": example_candidate_reports,
        "5": example_batch_processing,
        "6": example_analytics,
        "7": example_custom_filtering,
        "8": example_candidate_comparison,
        "9": example_scheduled_execution,
        "10": example_error_handling
    }
    
    if choice in examples:
        print(f"\nRunning Example {choice}...\n")
        examples[choice]()
    else:
        print("Invalid choice")
