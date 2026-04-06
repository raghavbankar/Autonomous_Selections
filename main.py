"""Main entry point for the autonomous hiring agent."""
from hiring_agent import HiringAgent
import os


def main():
    """Run the autonomous hiring agent workflow."""
    
    # Check for required environment variables
    required_vars = ["OPENAI_API_KEY", "SUPABASE_URL", "SUPABASE_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("⚠️  Missing environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these in your .env file before running the agent.\n")
        
        # Still run with mock data for demonstration
        print("Running with MOCK DATA for demonstration purposes...\n")
    
    # Initialize and run the hiring agent
    agent = HiringAgent()
    
    # Run the complete workflow
    # Set use_mock_data=True to use dummy candidate data
    # Set api_endpoint to use real API endpoint
    results = agent.run_workflow(api_endpoint=None, use_mock_data=True)
    
    # Print summary
    agent.print_summary(results)
    
    # Export results
    agent.export_results("hiring_results.json")
    
    # Print sample candidate report
    if results["detailed_results"]:
        first_candidate_id = list(results["detailed_results"].keys())[0]
        report = agent.get_candidate_report(first_candidate_id)
        if report:
            print(f"\n📄 Sample Report for {report['candidate']['name']}:")
            print(f"   Final Score: {report['final_score']:.2f}/100")
            print(f"   Authentic: {report['authenticity']['is_authentic']}")
            print(f"   Evaluation: {report['evaluation']['raw_feedback']}")


if __name__ == "__main__":
    main()
