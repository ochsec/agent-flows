#!/usr/bin/env python3
"""
JIRA Task Workflow - Multi-LLM Implementation

This module implements JIRA task handling with support for
multiple LLM providers (OpenRouter and LM Studio).
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import subprocess

# Import our LLM clients
sys.path.append(str(Path(__file__).parent.parent.parent))
from clients.llm_client import LLMClient, WorkflowType
from clients.openrouter_client import OpenRouterClient
from clients.lmstudio_client import LMStudioClient

# Import JIRA client if available
try:
    from .jira_client import JiraClient
    JIRA_AVAILABLE = True
except ImportError:
    JIRA_AVAILABLE = False
    print("⚠️  JIRA client not available. Running in analysis-only mode.")


class JiraTaskWorkflow:
    """
    JIRA task workflow with multi-LLM support for task analysis and implementation.
    """
    
    def __init__(self, client: LLMClient, jira_client: Optional[Any] = None):
        """Initialize the JIRA task workflow with specified LLM client."""
        self.client = client
        self.provider_name = client.get_provider_name()
        self.jira_client = jira_client
        
    def analyze_task(self, task_description: str, task_id: Optional[str] = None) -> Dict[str, Any]:
        """Analyze a JIRA task and break it down into implementation steps."""
        
        prompt = f"""You are a senior software engineer analyzing a JIRA task. Please analyze the following task and provide a detailed breakdown.

{f'Task ID: {task_id}' if task_id else ''}
Task Description:
{task_description}

Please provide:
1. **Task Summary**: Brief overview of what needs to be done
2. **Technical Requirements**: Specific technical requirements identified
3. **Implementation Steps**: Detailed step-by-step implementation plan
4. **Acceptance Criteria**: Clear criteria for task completion
5. **Potential Challenges**: Any challenges or considerations
6. **Time Estimate**: Estimated hours for completion
7. **Dependencies**: Any dependencies or prerequisites

Format your response in clear markdown with proper sections."""

        print(f"🔍 Analyzing task using {self.provider_name}...")
        
        try:
            result = self.client.execute_prompt(
                prompt=prompt,
                temperature=0.3,
                timeout=600
            )
            
            if result.get("success", False):
                return {
                    "analysis": result["content"],
                    "model": result.get("model", self.client.default_model.name),
                    "tokens": result.get("usage", {}).get("total_tokens", 0),
                    "execution_time": result.get("execution_time", 0)
                }
            else:
                raise Exception(result.get("error", "Unknown error"))
                
        except Exception as e:
            print(f"❌ Error analyzing task: {e}")
            return {
                "analysis": f"Error analyzing task: {str(e)}",
                "model": self.client.default_model.name,
                "tokens": 0,
                "execution_time": 0
            }
    
    def generate_implementation(self, task_analysis: str, tech_stack: Optional[str] = None) -> Dict[str, Any]:
        """Generate implementation code based on task analysis."""
        
        prompt = f"""Based on the following task analysis, generate the implementation code.

{f'Technology Stack: {tech_stack}' if tech_stack else ''}

Task Analysis:
{task_analysis}

Please provide:
1. Complete, production-ready code implementation
2. Clear code comments explaining the logic
3. Error handling and edge cases
4. Unit test examples
5. Documentation for any complex logic

Ensure the code follows best practices and is well-structured."""

        print(f"💻 Generating implementation using {self.provider_name}...")
        
        try:
            result = self.client.execute_prompt(
                prompt=prompt,
                temperature=0.2,  # Lower temperature for code generation
                max_tokens=4000,
                timeout=900  # 15 minutes for complex implementations
            )
            
            if result.get("success", False):
                return {
                    "implementation": result["content"],
                    "model": result.get("model", self.client.default_model.name),
                    "tokens": result.get("usage", {}).get("total_tokens", 0)
                }
            else:
                raise Exception(result.get("error", "Unknown error"))
                
        except Exception as e:
            print(f"❌ Error generating implementation: {e}")
            return {
                "implementation": f"Error generating implementation: {str(e)}",
                "model": self.client.default_model.name,
                "tokens": 0
            }
    
    def create_pull_request_description(self, task_id: str, task_description: str, 
                                      implementation_summary: str) -> Dict[str, Any]:
        """Generate a pull request description for the completed task."""
        
        prompt = f"""Create a professional pull request description for the following JIRA task implementation.

JIRA Task ID: {task_id}
Task Description: {task_description}

Implementation Summary:
{implementation_summary}

Please create a PR description that includes:
1. **Summary**: Brief overview of changes
2. **JIRA Link**: Reference to {task_id}
3. **Changes Made**: Bullet points of specific changes
4. **Testing**: How the changes were tested
5. **Screenshots**: Placeholder for screenshots if UI changes
6. **Checklist**: Standard PR checklist items

Use proper markdown formatting."""

        print(f"📝 Creating PR description using {self.provider_name}...")
        
        try:
            result = self.client.execute_prompt(
                prompt=prompt,
                temperature=0.3,
                max_tokens=1500
            )
            
            if result.get("success", False):
                return {
                    "pr_description": result["content"],
                    "model": result.get("model", self.client.default_model.name)
                }
            else:
                raise Exception(result.get("error", "Unknown error"))
                
        except Exception as e:
            print(f"❌ Error creating PR description: {e}")
            return {
                "pr_description": f"Error creating PR description: {str(e)}",
                "model": self.client.default_model.name
            }
    
    def review_implementation(self, code: str, requirements: str) -> Dict[str, Any]:
        """Review implementation against requirements."""
        
        prompt = f"""Review the following implementation against the requirements and provide feedback.

Requirements:
{requirements}

Implementation:
```
{code}
```

Please provide:
1. **Requirements Coverage**: Which requirements are met/not met
2. **Code Quality**: Assessment of code quality
3. **Suggestions**: Specific improvements needed
4. **Security Review**: Any security concerns
5. **Performance Considerations**: Performance implications

Be specific and constructive in your feedback."""

        print(f"🔍 Reviewing implementation using {self.provider_name}...")
        
        try:
            result = self.client.execute_prompt(
                prompt=prompt,
                temperature=0.3,
                max_tokens=2000
            )
            
            if result.get("success", False):
                return {
                    "review": result["content"],
                    "model": result.get("model", self.client.default_model.name)
                }
            else:
                raise Exception(result.get("error", "Unknown error"))
                
        except Exception as e:
            print(f"❌ Error reviewing implementation: {e}")
            return {
                "review": f"Error reviewing implementation: {str(e)}",
                "model": self.client.default_model.name
            }
    
    def process_jira_task(self, task_id: Optional[str] = None, task_description: Optional[str] = None,
                         tech_stack: Optional[str] = None, output_dir: Optional[str] = None) -> Dict[str, Any]:
        """Process a complete JIRA task workflow."""
        
        print(f"🚀 Starting JIRA task workflow with {self.provider_name}")
        
        # Get task details from JIRA if available
        if task_id and self.jira_client and JIRA_AVAILABLE:
            try:
                print(f"📥 Fetching task {task_id} from JIRA...")
                task_details = self.jira_client.get_issue(task_id)
                task_description = task_details.get('description', task_description)
                print(f"✅ Retrieved task: {task_details.get('summary', 'Unknown')}")
            except Exception as e:
                print(f"⚠️  Could not fetch from JIRA: {e}")
        
        if not task_description:
            return {"error": "No task description provided"}
        
        # Step 1: Analyze the task
        print("\n📋 Step 1: Analyzing task...")
        analysis_result = self.analyze_task(task_description, task_id)
        
        # Step 2: Generate implementation
        print("\n💻 Step 2: Generating implementation...")
        implementation_result = self.generate_implementation(
            analysis_result['analysis'],
            tech_stack
        )
        
        # Step 3: Review implementation
        print("\n🔍 Step 3: Reviewing implementation...")
        review_result = self.review_implementation(
            implementation_result['implementation'],
            analysis_result['analysis']
        )
        
        # Step 4: Create PR description
        print("\n📝 Step 4: Creating PR description...")
        pr_result = self.create_pull_request_description(
            task_id or "TASK-XXX",
            task_description,
            implementation_result['implementation'][:500] + "..."
        )
        
        # Compile results
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        full_report = f"""# JIRA Task Implementation Report
**Generated by**: {self.provider_name}
**Model**: {analysis_result.get('model', 'Unknown')}
**Timestamp**: {timestamp}
**Task ID**: {task_id or 'N/A'}

## Task Analysis
{analysis_result['analysis']}

## Implementation
{implementation_result['implementation']}

## Code Review
{review_result['review']}

## Pull Request Description
{pr_result['pr_description']}

---
*Workflow completed in {analysis_result.get('execution_time', 0):.2f} seconds*
*Total tokens used: {analysis_result.get('tokens', 0) + implementation_result.get('tokens', 0)}*
"""
        
        # Save outputs if requested
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Save report
            report_file = output_path / f"jira_task_report_{timestamp.replace(':', '-')}.md"
            with open(report_file, 'w') as f:
                f.write(full_report)
            print(f"\n✅ Report saved to: {report_file}")
            
            # Extract and save code files
            self._extract_code_files(implementation_result['implementation'], output_path)
        
        return {
            "status": "success",
            "task_id": task_id,
            "report": full_report,
            "model": analysis_result.get('model', 'Unknown'),
            "provider": self.provider_name,
            "execution_time": analysis_result.get('execution_time', 0),
            "tokens_used": analysis_result.get('tokens', 0) + implementation_result.get('tokens', 0)
        }
    
    def _extract_code_files(self, implementation: str, output_dir: Path):
        """Extract code blocks from implementation and save as files."""
        import re
        
        # Find code blocks with language specification
        code_blocks = re.findall(r'```(\w+)\n(.*?)```', implementation, re.DOTALL)
        
        for i, (lang, code) in enumerate(code_blocks):
            # Determine file extension
            extensions = {
                'python': '.py',
                'javascript': '.js',
                'typescript': '.ts',
                'java': '.java',
                'cpp': '.cpp',
                'go': '.go',
                'rust': '.rs',
                'sql': '.sql'
            }
            
            ext = extensions.get(lang, '.txt')
            filename = f"implementation_{i+1}{ext}"
            
            file_path = output_dir / filename
            with open(file_path, 'w') as f:
                f.write(code.strip())
            
            print(f"💾 Saved {lang} code to: {filename}")


def main():
    """Main entry point for multi-LLM JIRA task workflow."""
    parser = argparse.ArgumentParser(description="JIRA Task Workflow with Multi-LLM Support")
    parser.add_argument("--task-id", "-t", help="JIRA task ID")
    parser.add_argument("--description", "-d", help="Task description (if not fetching from JIRA)")
    parser.add_argument("--tech-stack", "-s", help="Technology stack for implementation")
    parser.add_argument("--output", "-o", help="Output directory for generated files")
    parser.add_argument("--provider", "-p", choices=["openrouter", "lmstudio"], default="openrouter",
                       help="LLM provider to use (default: openrouter)")
    parser.add_argument("--model", "-m", help="Specific model to use")
    parser.add_argument("--api-key", help="API key for OpenRouter")
    parser.add_argument("--lmstudio-url", help="LM Studio API URL (default: http://localhost:1234/v1)")
    parser.add_argument("--jira-url", help="JIRA instance URL")
    parser.add_argument("--jira-user", help="JIRA username")
    parser.add_argument("--jira-token", help="JIRA API token")
    parser.add_argument("--list-models", action="store_true", help="List available models")
    
    args = parser.parse_args()
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    try:
        # Initialize the appropriate client
        if args.provider == "openrouter":
            api_key = args.api_key or os.getenv("OPENROUTER_API_KEY")
            if not api_key:
                print("❌ Error: OpenRouter API key required.")
                print("   Set OPENROUTER_API_KEY environment variable or use --api-key")
                return 1
            
            client = OpenRouterClient(
                api_key=api_key,
                workflow_type=WorkflowType.JIRA_TASK
            )
            
            # Override model if specified
            if args.model:
                from clients.openrouter_client import ModelConfig
                client.default_model = ModelConfig(
                    name=args.model,
                    max_tokens=8192,
                    context_window=200000,
                    cost_per_1k_tokens=0.003,
                    best_for=[WorkflowType.JIRA_TASK],
                    description=f"User-specified model: {args.model}"
                )
        
        elif args.provider == "lmstudio":
            client = LMStudioClient(
                base_url=args.lmstudio_url,
                workflow_type=WorkflowType.JIRA_TASK,
                model_name=args.model
            )
        
        # List models if requested
        if args.list_models:
            print(f"Available {args.provider.upper()} Models for JIRA Tasks:")
            print("=" * 60)
            models = client.get_available_models()
            for model in models:
                print(f"• {model['name']}")
                print(f"  {model['description']}")
                if args.provider == "openrouter":
                    print(f"  Cost: ${model['cost_per_1k_tokens']:.4f}/1K tokens")
                print()
            return 0
        
        # Initialize JIRA client if credentials provided
        jira_client = None
        if JIRA_AVAILABLE and args.jira_url:
            jira_user = args.jira_user or os.getenv("JIRA_USER")
            jira_token = args.jira_token or os.getenv("JIRA_API_TOKEN")
            
            if jira_user and jira_token:
                jira_client = JiraClient(args.jira_url, jira_user, jira_token)
                print(f"✅ Connected to JIRA: {args.jira_url}")
        
        # Run workflow
        workflow = JiraTaskWorkflow(client, jira_client)
        
        # Check if we have task details
        if not args.task_id and not args.description:
            print("❌ Error: Either --task-id or --description is required")
            return 1
        
        result = workflow.process_jira_task(
            task_id=args.task_id,
            task_description=args.description,
            tech_stack=args.tech_stack,
            output_dir=args.output
        )
        
        if result.get("status") == "success":
            print("\n✨ JIRA task workflow completed successfully!")
            print(f"🤖 Model used: {result['model']}")
            print(f"⏱️  Execution time: {result['execution_time']:.2f}s")
            if args.provider == "openrouter":
                print(f"🪙 Tokens used: {result['tokens_used']}")
            return 0
        else:
            print(f"❌ Workflow failed: {result.get('error', 'Unknown error')}")
            return 1
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())