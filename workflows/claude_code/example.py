#!/usr/bin/env python3
"""
Example usage of the Research Manager Workflow
"""

import os
from dotenv import load_dotenv
from research_manager import ResearchManagerWorkflow

def main():
    # Load environment variables
    load_dotenv()
    
    # Get API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Error: Please set OPENAI_API_KEY environment variable")
        return
    
    # Initialize workflow
    print("🚀 Initializing Research Manager Workflow...")
    workflow = ResearchManagerWorkflow(api_key=api_key, model="gpt-4")
    
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
        
        print(f"\n✅ Research completed successfully!")
        print(f"📄 Report saved to: {report_path}")
        print(f"📁 Research context: research_context.md")
        
    except Exception as e:
        print(f"❌ Error during research: {e}")
        raise

if __name__ == "__main__":
    main()