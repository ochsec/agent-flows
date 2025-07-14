#!/usr/bin/env python3
"""
Phase 5 Agent-Flows Mode-Based Workflow Example

This example demonstrates how to use the Phase 5 agent-flows mode-based 
JIRA workflow for intelligent task orchestration.
"""

import os
import sys
import subprocess
from pathlib import Path

# Add the parent directory to the path so we can import the jira_task package
sys.path.insert(0, str(Path(__file__).parent.parent))

def demo_phase5_workflow():
    """Demonstrate Phase 5 agent-flows mode-based workflow"""
    
    print("🎭 Phase 5 Agent-Flows Mode-Based JIRA Workflow Demo")
    print("=" * 60)
    
    # Check if modes directory exists (try multiple locations)
    possible_modes_dirs = [
        Path("modes"),
        Path("../../../modes"),  # From jira_task directory to root
        Path("../../../../modes")  # Alternative path
    ]
    
    modes_dir = None
    for path in possible_modes_dirs:
        if path.exists():
            modes_dir = path
            break
    
    if not modes_dir:
        print(f"⚠️  Modes directory not found in any of these locations:")
        for path in possible_modes_dirs:
            print(f"     {path.absolute()}")
        print("   This demo requires the agent-flows modes directory.")
        print("   Please ensure you have the modes/ directory with:")
        print("   - orchestrator.md")
        print("   - architect.md") 
        print("   - code.md")
        print("   - researcher.md")
        print("   - etc.")
        return False
    
    # Check for required mode files
    required_modes = [
        "orchestrator.md",
        "architect.md", 
        "code.md",
        "researcher.md",
        "user_story.md"
    ]
    
    missing_modes = []
    for mode in required_modes:
        if not (modes_dir / mode).exists():
            missing_modes.append(mode)
    
    if missing_modes:
        print(f"⚠️  Missing required mode files: {missing_modes}")
        print(f"   Please ensure these files exist in: {modes_dir.absolute()}")
        return False
    
    print("✅ All required mode files found")
    print("\n📋 Example Usage:")
    
    # Show example commands
    examples = [
        {
            "description": "Start Phase 5 agent-flows workflow",
            "command": "python jira_task.py PROJ-123 --agent-modes --user john.doe"
        },
        {
            "description": "Start with custom modes directory",
            "command": "python jira_task.py PROJ-123 --agent-modes --modes-path /path/to/modes --user john.doe"
        },
        {
            "description": "Test configuration and setup",
            "command": "python example.py --test-all"
        },
        {
            "description": "Create sample configuration", 
            "command": "python example.py --create-config"
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n{i}. {example['description']}:")
        print(f"   {example['command']}")
    
    print("\n🎭 Agent-Flows Workflow Features:")
    features = [
        "🎭 Orchestrator mode for strategic workflow coordination",
        "📖 User story mode for requirements breakdown", 
        "🔍 Research modes for investigation and analysis",
        "🏗️  Architect mode for system design",
        "🛠️  Code mode for implementation",
        "🐛 Debug mode for troubleshooting",
        "👨‍💼 Expert consultant mode for technical review",
        "✅ Fact checker mode for validation",
        "📝 Writer mode for documentation",
        "🚀 DevOps mode for deployment",
        "🔄 Dynamic mode selection based on JIRA issue analysis",
        "📊 Comprehensive workflow synthesis and reporting"
    ]
    
    for feature in features:
        print(f"   {feature}")
    
    print("\n📚 Workflow Process:")
    process_steps = [
        "1. 🔍 Analyze JIRA issue to determine requirements and complexity",
        "2. 🎭 Orchestrator creates master coordination plan",
        "3. 📖 Delegate to specialized modes based on issue requirements",
        "4. 🔄 Interactive mode-based development with dynamic sequencing",
        "5. 👨‍💼 Expert review and validation of all work",
        "6. 📝 Comprehensive synthesis of all phase results",
        "7. 💬 Update JIRA with detailed workflow completion report"
    ]
    
    for step in process_steps:
        print(f"   {step}")
    
    print("\n🔧 Configuration Required:")
    config_items = [
        "JIRA_BASE_URL - Your JIRA instance URL",
        "JIRA_API_TOKEN - JIRA API token for authentication", 
        "JIRA_USERNAME - Your JIRA username/email",
        "Agent-flows modes directory with .md instruction files"
    ]
    
    for item in config_items:
        print(f"   • {item}")
    
    return True

def check_dependencies():
    """Check if all dependencies are available"""
    
    print("\n🔧 Checking Dependencies:")
    
    # Check Python packages
    try:
        import requests
        print("   ✅ requests - Available")
    except ImportError:
        print("   ❌ requests - Missing (pip install requests)")
        return False
    
    try:
        import pydantic
        print("   ✅ pydantic - Available")
    except ImportError:
        print("   ❌ pydantic - Missing (pip install pydantic)")
        return False
    
    try:
        from dotenv import load_dotenv
        print("   ✅ python-dotenv - Available")
    except ImportError:
        print("   ❌ python-dotenv - Missing (pip install python-dotenv)")
        return False
    
    # Check Claude Code
    try:
        result = subprocess.run(["claude", "--version"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("   ✅ Claude Code - Available")
        else:
            print("   ⚠️  Claude Code - Found but may not be properly configured")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("   ❌ Claude Code - Missing or not in PATH")
        print("      Please install Claude Code CLI")
        return False
    
    return True

def main():
    """Main demo function"""
    
    print("🎭 Phase 5 Agent-Flows Mode-Based JIRA Workflow")
    print("=" * 60)
    
    # Check dependencies first
    if not check_dependencies():
        print("\n❌ Missing dependencies - please install required packages")
        return 1
    
    # Run the demo
    if demo_phase5_workflow():
        print("\n✅ Phase 5 demo completed successfully!")
        print("\n🚀 To get started:")
        print("   1. Set up your .env file with JIRA credentials")
        print("   2. Ensure agent-flows modes directory is available")  
        print("   3. Run: python jira_task.py YOUR-ISSUE-KEY --agent-modes --user your.username")
        return 0
    else:
        print("\n❌ Demo failed - please check the requirements above")
        return 1

if __name__ == "__main__":
    sys.exit(main())