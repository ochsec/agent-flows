#!/usr/bin/env python3
"""
JIRA Task Workflow Example

Example usage and testing script for the JIRA task workflow.
"""

import os
import sys
from pathlib import Path

# Add the parent directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from workflows.claude_code.jira_task import (
    JiraConfig, 
    load_jira_config, 
    create_sample_env_file,
    JiraClient, 
    JiraWorkflow,
    JiraApiError
)


def test_configuration():
    """Test configuration loading"""
    print("🔧 Testing Configuration...")
    
    try:
        config = load_jira_config()
        print("✅ Configuration loaded successfully!")
        print(f"   JIRA URL: {config.base_url}")
        print(f"   Username: {config.username}")
        print(f"   Project Key: {config.project_key or 'Not set'}")
        return config
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        print("\\n💡 To fix this:")
        print("   1. Run: python example.py --create-config")
        print("   2. Edit the created .env file with your JIRA credentials")
        print("   3. Run this test again")
        return None


def test_jira_connection(config: JiraConfig):
    """Test JIRA API connection"""
    print("\\n🔗 Testing JIRA Connection...")
    
    try:
        client = JiraClient(config)
        client.test_connection()
        return client
    except JiraApiError as e:
        print(f"❌ JIRA connection failed: {e}")
        print("\\n💡 Check your JIRA credentials in .env file")
        return None


def test_git_integration():
    """Test Git integration"""
    print("\\n🌿 Testing Git Integration...")
    
    try:
        from workflows.claude_code.jira_task.git_integration import GitIntegration
        
        git = GitIntegration()
        current_branch = git.get_current_branch()
        print(f"✅ Git integration working!")
        print(f"   Current branch: {current_branch}")
        
        # Test branch name sanitization
        test_summary = "Fix user authentication & login issues!"
        sanitized = git.sanitize_branch_name(test_summary)
        print(f"   Branch name example: feature/proj-123-{sanitized}")
        
        return git
    except Exception as e:
        print(f"❌ Git integration error: {e}")
        return None


def demo_workflow(config: JiraConfig, issue_key: str):
    """Demonstrate workflow with a specific issue"""
    print(f"\\n🚀 Demo: Starting workflow for {issue_key}...")
    
    try:
        workflow = JiraWorkflow(config)
        
        # Test getting issue status
        print("📋 Getting issue status...")
        status = workflow.get_issue_status(issue_key)
        if status:
            print(f"   Issue: {status['summary']}")
            print(f"   Status: {status['status']}")
            print(f"   Assignee: {status['assignee']}")
        else:
            print(f"❌ Could not retrieve issue {issue_key}")
            return
        
        print(f"\\n✅ Workflow demo completed for {issue_key}")
        print("\\n💡 To start actual development work:")
        print(f"   python jira_task.py {issue_key}")
        
    except Exception as e:
        print(f"❌ Workflow demo error: {e}")


def main():
    """Main example and testing function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="JIRA Task Workflow Example & Testing")
    parser.add_argument("--create-config", action="store_true",
                       help="Create sample .env configuration file")
    parser.add_argument("--test-all", action="store_true",
                       help="Run all tests")
    parser.add_argument("--demo", metavar="ISSUE_KEY",
                       help="Demo workflow with specific issue key")
    parser.add_argument("--config", help="Path to .env file")
    
    args = parser.parse_args()
    
    if args.create_config:
        create_sample_env_file()
        return
    
    if args.test_all:
        print("🧪 Running JIRA Task Workflow Tests\\n")
        
        # Test 1: Configuration
        config = test_configuration()
        if not config:
            return
        
        # Test 2: JIRA Connection
        client = test_jira_connection(config)
        if not client:
            return
        
        # Test 3: Git Integration
        git = test_git_integration()
        if not git:
            return
        
        # Test 4: List my issues
        print("\\n📋 Testing issue listing...")
        try:
            workflow = JiraWorkflow(config)
            issues = workflow.find_my_issues()
            if issues:
                print(f"✅ Found {len(issues)} assigned issues:")
                for issue in issues[:3]:  # Show first 3
                    print(f"   {issue['key']}: {issue['summary']}")
                if len(issues) > 3:
                    print(f"   ... and {len(issues) - 3} more")
            else:
                print("ℹ️  No assigned issues found (or no access)")
        except Exception as e:
            print(f"❌ Issue listing error: {e}")
        
        print("\\n🎉 All tests completed!")
        
    elif args.demo:
        config = test_configuration()
        if config:
            demo_workflow(config, args.demo)
    
    else:
        parser.print_help()
        print("\\n💡 Quick start:")
        print("   1. python example.py --create-config")
        print("   2. Edit .env file with your JIRA credentials")
        print("   3. python example.py --test-all")
        print("   4. python jira_task.py YOUR-ISSUE-KEY")


if __name__ == "__main__":
    main()