#!/usr/bin/env python3
"""
Enhanced JIRA Task Workflow - OpenRouter Implementation

This module implements an enhanced JIRA task workflow using OpenRouter
for sophisticated LLM interactions with context preservation and dynamic tool management.
"""

import os
import json
from datetime import datetime
from typing import Dict, Optional, List, Any, Union
from pathlib import Path

# Import our OpenRouter client
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from openrouter_client import OpenRouterClient, WorkflowType, OpenRouterModels

from .config import JiraConfig, load_jira_config
from .jira_client import JiraClient, JiraApiError
from .git_integration import GitIntegration, GitError


class EnhancedOpenRouterClient:
    """
    Enhanced OpenRouter client with context preservation and dynamic capabilities.
    Replaces the EnhancedClaudeCodeClient functionality.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """Initialize enhanced OpenRouter client"""
        self.client = OpenRouterClient(
            api_key=api_key,
            workflow_type=WorkflowType.JIRA_TASK
        )
        
        # Override model if specified
        if model:
            self.client.default_model.name = model
        
        # Context preservation
        self.session_context = []
        self.workflow_history = []
        self.current_issue = None
        self.current_branch = None
        
        # Available tools simulation (for compatibility with Claude Code patterns)
        self.base_tools = [
            "read", "write", "edit", "multiEdit", "glob", "grep", "ls", 
            "bash", "git", "npm", "cargo", "python", "pytest", "webSearch", "task"
        ]
        
        print(f"🚀 Enhanced OpenRouter client initialized")
        print(f"🤖 Model: {self.client.default_model.name}")
        print(f"🛠️  Available tools: {', '.join(self.base_tools)}")
    
    def preserve_context(self, prompt: str, response: str, metadata: Optional[Dict] = None):
        """Preserve conversation context for enhanced coherence"""
        context_entry = {
            "timestamp": datetime.now().isoformat(),
            "prompt": prompt,
            "response": response,
            "metadata": metadata or {}
        }
        self.session_context.append(context_entry)
        
        # Keep only last 10 interactions to manage context size
        if len(self.session_context) > 10:
            self.session_context = self.session_context[-10:]
    
    def build_enhanced_prompt(self, user_prompt: str, tools: Optional[List[str]] = None) -> str:
        """Build an enhanced prompt with context and tool awareness"""
        
        # Build context summary
        context_summary = ""
        if self.session_context:
            context_summary = "\n\n## PREVIOUS CONTEXT (Last few interactions):\n"
            for i, ctx in enumerate(self.session_context[-3:], 1):  # Last 3 interactions
                context_summary += f"{i}. User asked: {ctx['prompt'][:100]}...\n"
                context_summary += f"   You responded: {ctx['response'][:100]}...\n"
        
        # Build issue context
        issue_context = ""
        if self.current_issue:
            issue_context = f"\n\n## CURRENT JIRA ISSUE:\n"
            issue_context += f"Key: {self.current_issue.get('key', 'Unknown')}\n"
            issue_context += f"Summary: {self.current_issue.get('summary', 'No summary')}\n"
            issue_context += f"Status: {self.current_issue.get('status', 'Unknown')}\n"
            if self.current_issue.get('description'):
                issue_context += f"Description: {self.current_issue['description'][:200]}...\n"
        
        # Build git context
        git_context = ""
        if self.current_branch:
            git_context = f"\n\n## CURRENT GIT CONTEXT:\n"
            git_context += f"Working on branch: {self.current_branch}\n"
        
        # Available tools context
        tools_available = tools or self.base_tools
        tools_context = f"\n\n## AVAILABLE TOOLS:\n"
        tools_context += f"You have access to these development tools: {', '.join(tools_available)}\n"
        tools_context += "Use these tools to read files, make changes, run tests, and interact with git.\n"
        
        # Build the enhanced prompt
        enhanced_prompt = f"""You are an expert software developer working on a JIRA task using OpenRouter.

{issue_context}
{git_context}
{context_summary}
{tools_context}

## USER REQUEST:
{user_prompt}

## INSTRUCTIONS:
1. Consider the JIRA issue context and previous conversation history
2. Use appropriate development tools to complete the task
3. Provide detailed, actionable responses
4. If you need to read files or understand the codebase, use the available tools
5. Always test your changes when appropriate
6. Follow best practices for code quality and documentation

Please proceed with the user's request, taking into account all the context provided above."""

        return enhanced_prompt
    
    def execute_enhanced_request(
        self, 
        prompt: str, 
        tools: Optional[List[str]] = None,
        model: Optional[str] = None,
        preserve_context: bool = True
    ) -> Dict[str, Any]:
        """
        Execute an enhanced request with context preservation
        
        Args:
            prompt: User prompt
            tools: List of tools to enable (for compatibility - not used in API)
            model: Model to use (overrides default)
            preserve_context: Whether to preserve this interaction in context
            
        Returns:
            Dict with response and metadata
        """
        try:
            # Build enhanced prompt with context
            enhanced_prompt = self.build_enhanced_prompt(prompt, tools)
            
            print(f"🧠 Executing enhanced OpenRouter request...")
            print(f"🤖 Model: {model or self.client.default_model.name}")
            print(f"🛠️  Tools available: {', '.join(tools or self.base_tools)}")
            
            # Execute the request
            result = self.client.execute_prompt(
                prompt=enhanced_prompt,
                model=model,
                timeout=1800  # 30 minute timeout for complex tasks
            )
            
            if not result.get("success", False):
                raise Exception(f"OpenRouter API error: {result.get('error', 'Unknown error')}")
            
            response = result["content"]
            
            # Preserve context if requested
            if preserve_context:
                self.preserve_context(
                    prompt=prompt,
                    response=response,
                    metadata={
                        "tools": tools or self.base_tools,
                        "model": model or self.client.default_model.name,
                        "execution_time": result.get('execution_time', 0),
                        "usage": result.get('usage', {})
                    }
                )
            
            print(f"✅ Request completed in {result.get('execution_time', 0):.2f}s")
            print(f"📊 Usage: {result.get('usage', {}).get('total_tokens', 0)} tokens")
            
            return {
                "content": response,
                "success": True,
                "metadata": {
                    "model": model or self.client.default_model.name,
                    "execution_time": result.get('execution_time', 0),
                    "usage": result.get('usage', {}),
                    "tools_available": tools or self.base_tools
                }
            }
            
        except Exception as e:
            error_msg = f"Enhanced OpenRouter request failed: {str(e)}"
            print(f"❌ {error_msg}")
            
            return {
                "content": f"Error: {error_msg}",
                "success": False,
                "error": str(e)
            }
    
    def set_issue_context(self, issue: Dict[str, Any]):
        """Set the current JIRA issue context"""
        self.current_issue = issue
        print(f"📋 Issue context set: {issue.get('key', 'Unknown')} - {issue.get('summary', 'No summary')}")
    
    def set_branch_context(self, branch_name: str):
        """Set the current git branch context"""
        self.current_branch = branch_name
        print(f"🌿 Branch context set: {branch_name}")
    
    def clear_context(self):
        """Clear all context (useful for starting fresh)"""
        self.session_context = []
        self.workflow_history = []
        self.current_issue = None
        self.current_branch = None
        print("🧹 Context cleared")
    
    def get_context_summary(self) -> Dict[str, Any]:
        """Get a summary of current context"""
        return {
            "session_interactions": len(self.session_context),
            "current_issue": self.current_issue.get('key') if self.current_issue else None,
            "current_branch": self.current_branch,
            "model": self.client.default_model.name,
            "available_tools": self.base_tools
        }


class EnhancedJiraWorkflow:
    """Enhanced JIRA workflow with OpenRouter integration"""
    
    def __init__(
        self, 
        jira_config: JiraConfig, 
        repo_path: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ):
        """Initialize enhanced JIRA workflow"""
        self.jira_client = JiraClient(jira_config)
        self.git = GitIntegration(repo_path)
        self.openrouter_client = EnhancedOpenRouterClient(api_key=api_key, model=model)
        
        # Workflow state
        self.current_issue = None
        self.current_branch = None
        self.workflow_state = {}
        
        print("🔄 Enhanced JIRA workflow initialized with OpenRouter")
    
    def start_enhanced_development(self, issue_key: str, development_request: str) -> Dict[str, Any]:
        """
        Start enhanced development on a JIRA issue with OpenRouter assistance
        
        Args:
            issue_key: JIRA issue key
            development_request: Specific development request or task
            
        Returns:
            Dict with development results
        """
        try:
            print(f"🚀 Starting enhanced development on {issue_key}")
            
            # Get issue details and set context
            issue = self.jira_client.get_issue(issue_key)
            self.current_issue = issue
            
            issue_context = {
                "key": issue['key'],
                "summary": issue['fields']['summary'],
                "description": self.jira_client.extract_description_text(issue),
                "status": issue['fields']['status']['name']
            }
            
            # Set issue context in OpenRouter client
            self.openrouter_client.set_issue_context(issue_context)
            
            # Create or switch to feature branch
            summary = issue['fields']['summary']
            branch_name = self.git.create_branch(issue_key, summary)
            self.current_branch = branch_name
            self.openrouter_client.set_branch_context(branch_name)
            
            # Execute the development request
            print(f"🧠 Processing development request with OpenRouter...")
            
            development_prompt = f"""I need help with development work for this JIRA issue.

DEVELOPMENT REQUEST:
{development_request}

Please help me:
1. Understand what needs to be implemented based on the issue description
2. Analyze the existing codebase to understand the context
3. Implement the necessary changes
4. Write appropriate tests
5. Ensure code quality and best practices

Please start by exploring the codebase and understanding the requirements, then proceed with the implementation."""

            result = self.openrouter_client.execute_enhanced_request(
                prompt=development_prompt,
                tools=self.openrouter_client.base_tools
            )
            
            if result["success"]:
                # Add comment to JIRA about AI assistance
                comment = f"""🤖 AI-assisted development started on branch: {branch_name}

Development request: {development_request}

Using OpenRouter with model: {result['metadata']['model']}
Branch: {branch_name}
Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
                
                self.jira_client.add_comment(issue_key, comment)
                
                # Update workflow state
                self.workflow_state[issue_key] = {
                    'status': 'ai_development',
                    'branch': branch_name,
                    'started_at': datetime.now().isoformat(),
                    'model': result['metadata']['model'],
                    'development_request': development_request
                }
                
                return {
                    "status": "success",
                    "issue": issue_context,
                    "branch": branch_name,
                    "ai_response": result["content"],
                    "metadata": result["metadata"],
                    "message": f"AI development assistance started for {issue_key}"
                }
            else:
                return {
                    "status": "error",
                    "error": result.get("error", "Unknown error"),
                    "message": f"Failed to start AI development for {issue_key}"
                }
                
        except Exception as e:
            error_msg = f"Enhanced development failed: {str(e)}"
            print(f"❌ {error_msg}")
            return {
                "status": "error",
                "error": str(e),
                "message": error_msg
            }
    
    def continue_development(self, follow_up_request: str) -> Dict[str, Any]:
        """Continue development with additional requests"""
        if not self.current_issue:
            return {
                "status": "error",
                "error": "No active issue. Start development first.",
                "message": "No active development session"
            }
        
        print(f"🔄 Continuing development with follow-up request...")
        
        result = self.openrouter_client.execute_enhanced_request(
            prompt=follow_up_request,
            tools=self.openrouter_client.base_tools
        )
        
        if result["success"]:
            return {
                "status": "success",
                "ai_response": result["content"],
                "metadata": result["metadata"],
                "context": self.openrouter_client.get_context_summary(),
                "message": "Follow-up request processed successfully"
            }
        else:
            return {
                "status": "error",
                "error": result.get("error", "Unknown error"),
                "message": "Follow-up request failed"
            }
    
    def get_development_status(self) -> Dict[str, Any]:
        """Get current development status and context"""
        return {
            "current_issue": self.current_issue.get('key') if self.current_issue else None,
            "current_branch": self.current_branch,
            "context_summary": self.openrouter_client.get_context_summary(),
            "workflow_state": self.workflow_state
        }


def create_enhanced_workflow(
    jira_config_path: str = "jira_config.json",
    repo_path: Optional[str] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None
) -> EnhancedJiraWorkflow:
    """Create an enhanced JIRA workflow with OpenRouter"""
    
    # Load JIRA configuration
    config_path = Path(jira_config_path)
    if not config_path.exists():
        raise FileNotFoundError(f"JIRA config not found: {jira_config_path}")
    
    jira_config = load_jira_config(str(config_path))
    
    # Get API key from environment if not provided
    if not api_key:
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OpenRouter API key required. Set OPENROUTER_API_KEY or pass api_key parameter.")
    
    return EnhancedJiraWorkflow(
        jira_config=jira_config,
        repo_path=repo_path,
        api_key=api_key,
        model=model
    )


def main():
    """Example usage of enhanced workflow"""
    import argparse
    from dotenv import load_dotenv
    
    load_dotenv()
    
    parser = argparse.ArgumentParser(description="Enhanced JIRA Workflow with OpenRouter")
    parser.add_argument("issue_key", help="JIRA issue key")
    parser.add_argument("development_request", help="Development request description")
    parser.add_argument("--config", default="jira_config.json", help="JIRA config file path")
    parser.add_argument("--repo", help="Repository path (default: current directory)")
    parser.add_argument("--model", help="OpenRouter model to use")
    parser.add_argument("--api-key", help="OpenRouter API key")
    parser.add_argument("--list-models", action="store_true", help="List recommended models")
    
    args = parser.parse_args()
    
    if args.list_models:
        print("Recommended OpenRouter Models for JIRA Development:")
        print("=" * 60)
        models = OpenRouterModels.get_recommended_models(WorkflowType.JIRA_TASK)
        for model in models:
            print(f"• {model.name}")
            print(f"  {model.description}")
            print(f"  Cost: ${model.cost_per_1k_tokens:.4f}/1K tokens")
            print()
        return
    
    try:
        # Create enhanced workflow
        workflow = create_enhanced_workflow(
            jira_config_path=args.config,
            repo_path=args.repo,
            api_key=args.api_key,
            model=args.model
        )
        
        # Start enhanced development
        result = workflow.start_enhanced_development(
            issue_key=args.issue_key,
            development_request=args.development_request
        )
        
        if result["status"] == "success":
            print("✅ Enhanced development started successfully!")
            print(f"📋 Issue: {result['issue']['summary']}")
            print(f"🌿 Branch: {result['branch']}")
            print("\n🤖 AI Response:")
            print(result["ai_response"])
        else:
            print(f"❌ Failed to start development: {result['message']}")
            
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()