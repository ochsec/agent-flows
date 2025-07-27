#!/usr/bin/env python3
"""
Advanced Code Review Workflow - Multi-LLM Implementation

This module implements AI-powered code review with support for
multiple LLM providers (OpenRouter and LM Studio).
"""

import os
import sys
import argparse
import json
from pathlib import Path
from typing import List, Dict, Optional, Union
from datetime import datetime
import subprocess

# Import our LLM clients
sys.path.append(str(Path(__file__).parent.parent.parent))
from clients.llm_client import LLMClient, WorkflowType
from clients.openrouter_client import OpenRouterClient
from clients.lmstudio_client import LMStudioClient


class CodeReviewWorkflow:
    """
    Advanced code review workflow with multi-LLM support.
    """
    
    def __init__(self, client: LLMClient):
        """Initialize the code review workflow with specified LLM client."""
        self.client = client
        self.provider_name = client.get_provider_name()
        
    def get_git_diff(self, base_branch: str = "main") -> str:
        """Get the git diff against the base branch."""
        try:
            cmd = ["git", "diff", f"{base_branch}...HEAD"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"❌ Error getting git diff: {e}")
            return ""
    
    def get_changed_files(self, base_branch: str = "main") -> List[str]:
        """Get list of changed files."""
        try:
            cmd = ["git", "diff", "--name-only", f"{base_branch}...HEAD"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return [f.strip() for f in result.stdout.split('\n') if f.strip()]
        except subprocess.CalledProcessError as e:
            print(f"❌ Error getting changed files: {e}")
            return []
    
    def review_code(self, diff: str, context: Optional[str] = None) -> Dict[str, any]:
        """Perform comprehensive code review using the configured LLM."""
        
        prompt = f"""You are an expert code reviewer. Please review the following code changes and provide comprehensive feedback.

{f'Context: {context}' if context else ''}

Code changes to review:
```diff
{diff}
```

Please provide your review with the following structure:
1. **Summary**: Brief overview of the changes
2. **Strengths**: What's done well
3. **Issues**: Problems or concerns (categorized by severity: critical, major, minor)
4. **Suggestions**: Specific improvements
5. **Security**: Any security concerns
6. **Performance**: Performance implications
7. **Testing**: Test coverage recommendations
8. **Overall Rating**: Score out of 10 with justification

Format your response in clear markdown with proper sections."""

        print(f"🤖 Performing code review using {self.provider_name}...")
        
        try:
            result = self.client.execute_prompt(
                prompt=prompt,
                temperature=0.3,  # Lower temperature for more consistent reviews
                timeout=600  # 10 minute timeout
            )
            
            if result.get("success", False):
                return {
                    "review": result["content"],
                    "model": result.get("model", self.client.default_model.name),
                    "tokens": result.get("usage", {}).get("total_tokens", 0),
                    "execution_time": result.get("execution_time", 0)
                }
            else:
                raise Exception(result.get("error", "Unknown error"))
                
        except Exception as e:
            print(f"❌ Error during code review: {e}")
            return {
                "review": f"Error performing code review: {str(e)}",
                "model": self.client.default_model.name,
                "tokens": 0,
                "execution_time": 0
            }
    
    def analyze_complexity(self, files: List[str]) -> Dict[str, any]:
        """Analyze code complexity of changed files."""
        
        file_contents = {}
        for file in files[:10]:  # Limit to 10 files to avoid token limits
            if file.endswith(('.py', '.js', '.ts', '.java', '.cpp', '.go')):
                try:
                    with open(file, 'r') as f:
                        file_contents[file] = f.read()
                except Exception as e:
                    print(f"⚠️  Could not read {file}: {e}")
        
        if not file_contents:
            return {"analysis": "No source files to analyze", "metrics": {}}
        
        files_summary = "\n".join([f"- {f} ({len(content)} chars)" for f, content in file_contents.items()])
        
        prompt = f"""Analyze the complexity of the following code files and provide metrics:

Files to analyze:
{files_summary}

For each file, provide:
1. Cyclomatic complexity estimate
2. Code maintainability assessment
3. Potential refactoring opportunities

Focus on the most complex or problematic areas."""

        print(f"📊 Analyzing code complexity using {self.provider_name}...")
        
        try:
            result = self.client.execute_prompt(
                prompt=prompt,
                temperature=0.2,
                max_tokens=2000
            )
            
            if result.get("success", False):
                return {
                    "analysis": result["content"],
                    "files_analyzed": len(file_contents),
                    "model": result.get("model", self.client.default_model.name)
                }
            else:
                raise Exception(result.get("error", "Unknown error"))
                
        except Exception as e:
            print(f"❌ Error analyzing complexity: {e}")
            return {
                "analysis": f"Error analyzing complexity: {str(e)}",
                "files_analyzed": 0,
                "model": self.client.default_model.name
            }
    
    def suggest_improvements(self, diff: str) -> Dict[str, any]:
        """Suggest specific code improvements."""
        
        prompt = f"""As a code improvement specialist, analyze these changes and suggest specific improvements:

```diff
{diff}
```

Provide actionable suggestions for:
1. Code organization and structure
2. Naming conventions
3. Error handling
4. Documentation
5. Design patterns
6. Best practices

For each suggestion, provide a concrete example of the improved code."""

        print(f"💡 Generating improvement suggestions using {self.provider_name}...")
        
        try:
            result = self.client.execute_prompt(
                prompt=prompt,
                temperature=0.4,
                max_tokens=3000
            )
            
            if result.get("success", False):
                return {
                    "suggestions": result["content"],
                    "model": result.get("model", self.client.default_model.name)
                }
            else:
                raise Exception(result.get("error", "Unknown error"))
                
        except Exception as e:
            print(f"❌ Error generating suggestions: {e}")
            return {
                "suggestions": f"Error generating suggestions: {str(e)}",
                "model": self.client.default_model.name
            }
    
    def run_full_review(self, base_branch: str = "main", context: Optional[str] = None, 
                       output_file: Optional[str] = None) -> Dict[str, any]:
        """Run complete code review workflow."""
        
        print(f"🚀 Starting code review workflow with {self.provider_name}")
        print(f"📍 Base branch: {base_branch}")
        
        # Get changes
        diff = self.get_git_diff(base_branch)
        if not diff:
            print("❌ No changes detected")
            return {"error": "No changes to review"}
        
        changed_files = self.get_changed_files(base_branch)
        print(f"📝 Files changed: {len(changed_files)}")
        
        # Perform review
        review_result = self.review_code(diff, context)
        
        # Analyze complexity
        complexity_result = self.analyze_complexity(changed_files)
        
        # Get improvement suggestions
        suggestions_result = self.suggest_improvements(diff)
        
        # Compile results
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        full_report = f"""# Code Review Report
**Generated by**: {self.provider_name}
**Model**: {review_result.get('model', 'Unknown')}
**Timestamp**: {timestamp}
**Base Branch**: {base_branch}
**Files Changed**: {len(changed_files)}

## Files Modified
{chr(10).join(['- ' + f for f in changed_files])}

## Code Review
{review_result['review']}

## Complexity Analysis
{complexity_result['analysis']}

## Improvement Suggestions
{suggestions_result['suggestions']}

---
*Review completed in {review_result.get('execution_time', 0):.2f} seconds*
*Total tokens used: {review_result.get('tokens', 0)}*
"""
        
        # Save report if requested
        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                f.write(full_report)
            print(f"✅ Review report saved to: {output_path}")
        else:
            print("\n" + "="*80)
            print(full_report)
            print("="*80 + "\n")
        
        return {
            "status": "success",
            "files_reviewed": len(changed_files),
            "report": full_report,
            "model": review_result.get('model', 'Unknown'),
            "provider": self.provider_name,
            "execution_time": review_result.get('execution_time', 0),
            "tokens_used": review_result.get('tokens', 0)
        }


def main():
    """Main entry point for multi-LLM code review."""
    parser = argparse.ArgumentParser(description="AI-Powered Code Review with Multi-LLM Support")
    parser.add_argument("--base", "-b", default="main", help="Base branch to compare against")
    parser.add_argument("--context", "-c", help="Additional context for the review")
    parser.add_argument("--output", "-o", help="Output file for the review report")
    default_provider = os.getenv("DEFAULT_LLM_PROVIDER", "openrouter")
    parser.add_argument("--provider", "-p", choices=["openrouter", "lmstudio"], default=default_provider,
                       help=f"LLM provider to use (default: {default_provider})")
    parser.add_argument("--model", "-m", help="Specific model to use")
    parser.add_argument("--api-key", help="API key for OpenRouter")
    parser.add_argument("--lmstudio-url", help="LM Studio API URL (default: http://localhost:1234/v1)")
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
                workflow_type=WorkflowType.CODE_REVIEW
            )
            
            # Override model if specified
            if args.model:
                from clients.openrouter_client import ModelConfig
                client.default_model = ModelConfig(
                    name=args.model,
                    max_tokens=8192,
                    context_window=200000,
                    cost_per_1k_tokens=0.003,
                    best_for=[WorkflowType.CODE_REVIEW],
                    description=f"User-specified model: {args.model}"
                )
        
        elif args.provider == "lmstudio":
            client = LMStudioClient(
                base_url=args.lmstudio_url,
                workflow_type=WorkflowType.CODE_REVIEW,
                model_name=args.model
            )
        
        # List models if requested
        if args.list_models:
            print(f"Available {args.provider.upper()} Models for Code Review:")
            print("=" * 60)
            models = client.get_available_models()
            for model in models:
                print(f"• {model['name']}")
                print(f"  {model['description']}")
                if args.provider == "openrouter":
                    print(f"  Cost: ${model['cost_per_1k_tokens']:.4f}/1K tokens")
                print()
            return 0
        
        # Run code review
        workflow = CodeReviewWorkflow(client)
        result = workflow.run_full_review(
            base_branch=args.base,
            context=args.context,
            output_file=args.output
        )
        
        if result.get("status") == "success":
            print("\n✨ Code review completed successfully!")
            print(f"📊 Files reviewed: {result['files_reviewed']}")
            print(f"🤖 Model used: {result['model']}")
            print(f"⏱️  Execution time: {result['execution_time']:.2f}s")
            if args.provider == "openrouter":
                print(f"🪙 Tokens used: {result['tokens_used']}")
            return 0
        else:
            print(f"❌ Review failed: {result.get('error', 'Unknown error')}")
            return 1
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())