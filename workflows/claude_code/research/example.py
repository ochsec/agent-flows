#!/usr/bin/env python3
"""
Example usage of the Research Manager Workflow with Claude Code
"""

import os
from dotenv import load_dotenv
from workflows.claude_code.research.research import ResearchManagerWorkflow

def main():
    # Load environment variables
    load_dotenv()
    
    # Get optional Perplexity API key for enhanced research
    perplexity_api_key = os.getenv("PERPLEXITY_API_KEY")
    if not perplexity_api_key:
        print("⚠️  No Perplexity API key found. Research will use Claude's knowledge only.")
        print("   Set PERPLEXITY_API_KEY environment variable for enhanced research capabilities.")
    
    # Initialize workflow (uses Claude Code by default)
    print("🚀 Initializing Research Manager Workflow with Claude Code...")
    workflow = ResearchManagerWorkflow(model="sonnet", perplexity_api_key=perplexity_api_key)
    
    # Example research topics
    research_topics = [
        "Vector databases for AI applications",
        "Microservices architecture patterns",
        "Machine learning deployment strategies",
        "Distributed systems consistency models"
    ]
    
    print("\n📋 Available research topics:")
    for i, topic in enumerate(research_topics, 1):
        print(f"  {i}. {topic}")
    
    # Get user choice
    try:
        choice = int(input("\nSelect a topic (1-4): ")) - 1
        if 0 <= choice < len(research_topics):
            selected_topic = research_topics[choice]
        else:
            print("Invalid selection. Using default topic.")
            selected_topic = research_topics[0]
    except ValueError:
        print("Invalid input. Using default topic.")
        selected_topic = research_topics[0]
    
    print(f"\n🔬 Starting research on: {selected_topic}")
    
    # Execute workflow
    try:
        report_path = workflow.execute_workflow(
            research_topic=selected_topic,
            output_folder="example_reports"
        )
        
        print("\n✅ Research completed successfully!")
        print(f"📄 Report saved to: {report_path}")
        print("📁 Research context: research_context.md")
        
    except Exception as e:
        print(f"❌ Error during research: {e}")
        raise

if __name__ == "__main__":
    main()