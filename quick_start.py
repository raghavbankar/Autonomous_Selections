#!/usr/bin/env python3
"""
QUICK START GUIDE - Autonomous Hiring Agent
============================================

Follow these steps to get started immediately.
"""

import os
import sys

def check_environment():
    """Check if environment is properly configured."""
    print("🔍 Checking environment setup...\n")
    
    # Python version
    print(f"✓ Python {sys.version.split()[0]}")
    
    # Check for .env file
    if os.path.exists(".env"):
        print("✓ .env file found")
    else:
        print("⚠️  .env file not found")
        print("   Create one from .env.example: cp .env.example .env")
        return False
    
    # Check for required environment variables
    required = ["OPENAI_API_KEY", "SUPABASE_URL", "SUPABASE_KEY"]
    from dotenv import load_dotenv
    load_dotenv()
    
    missing = []
    for var in required:
        if os.getenv(var):
            print(f"✓ {var} configured")
        else:
            print(f"✗ {var} missing")
            missing.append(var)
    
    if missing:
        print(f"\n⚠️  Missing {len(missing)} environment variable(s)")
        print("   Update your .env file with the missing variables")
        return False
    
    print("\n✅ Environment is properly configured!")
    return True


def run_quick_demo():
    """Run a quick demo with mock data."""
    print("\n" + "="*60)
    print("🚀 QUICK DEMO - Running with mock data")
    print("="*60 + "\n")
    
    from hiring_agent import HiringAgent
    
    try:
        agent = HiringAgent()
        results = agent.run_workflow(use_mock_data=True)
        agent.print_summary(results)
        agent.export_results("demo_results.json")
        print("\n✅ Demo completed! Results saved to demo_results.json")
        return True
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def show_help():
    """Show help and options."""
    print("""
AUTONOMOUS HIRING AGENT - Quick Start
======================================

INSTALLATION STEPS:

1. Install dependencies:
   pip install -r requirements.txt

2. Set up environment:
   cp .env.example .env
   Edit .env with your OpenAI API key and Supabase credentials

3. Create Supabase tables:
   Run the SQL scripts from README.md

4. Run the demo:
   python quick_start.py --demo

5. Run the full workflow:
   python main.py

OPTIONS:
  --demo          Run quick demo with mock data
  --check         Check environment configuration
  --examples      Show usage examples
  --help          Show this help message

EXAMPLES:

  # Basic usage
  python main.py

  # Using custom API endpoint
  from hiring_agent import HiringAgent
  agent = HiringAgent()
  results = agent.run_workflow(api_endpoint="https://your-api.com/candidates")

  # Get candidate report
  report = agent.get_candidate_report("candidate_id")
  print(report)

TROUBLESHOOTING:

1. OpenAI API Error?
   - Verify OPENAI_API_KEY is correct
   - Check if account has GPT-4 access

2. Supabase Connection Error?
   - Verify SUPABASE_URL and SUPABASE_KEY
   - Ensure tables are created
   - Check Row Level Security (RLS) policies

3. No Candidates Found?
   - Using --demo flag?
   - Check if API endpoint is valid
   - Verify API response format

NEXT STEPS:

1. Read README.md for detailed documentation
2. Check usage_examples.py for advanced usage
3. Customize config.py for your needs
4. Integrate with your candidate API

Need help? Check the documentation or review error messages.
    """)


def main():
    """Main entry point for quick start."""
    
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        
        if arg == "--help":
            show_help()
        elif arg == "--check":
            check_environment()
        elif arg == "--demo":
            if check_environment():
                run_quick_demo()
        elif arg == "--examples":
            print("\nRunning usage examples...\n")
            os.system("python usage_examples.py")
        else:
            print(f"Unknown option: {arg}")
            show_help()
    else:
        # Interactive menu
        print("\n" + "="*60)
        print("⚙️  AUTONOMOUS HIRING AGENT - QUICK START")
        print("="*60 + "\n")
        
        print("What would you like to do?\n")
        print("1. Check environment setup")
        print("2. Run quick demo (mock data)")
        print("3. Show usage examples")
        print("4. Show help & documentation")
        print("5. Exit")
        
        choice = input("\nSelect option (1-5): ").strip()
        
        if choice == "1":
            check_environment()
        elif choice == "2":
            if check_environment():
                run_quick_demo()
        elif choice == "3":
            os.system("python usage_examples.py")
        elif choice == "4":
            show_help()
        elif choice == "5":
            print("Goodbye!")
        else:
            print("Invalid choice")


if __name__ == "__main__":
    main()
