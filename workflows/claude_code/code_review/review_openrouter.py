#!/usr/bin/env python3
"""
Simple PR Review Workflow - OpenRouter Integration

A straightforward code review workflow that uses OpenRouter API
to review pull requests with any supported LLM provider.
"""

import os
import sys
import json
from datetime import datetime
import argparse
import logging
from pathlib import Path
from typing import Optional

# Import our OpenRouter client and GitHub client
sys.path.append(str(Path(__file__).parent.parent.parent))
from openrouter_client import OpenRouterClient, WorkflowType, OpenRouterModels
from github_client import GitHubClient


class OpenRouterPRReviewer:
    """PR reviewer using OpenRouter API"""
    
    def __init__(self, model: Optional[str] = None, api_key: Optional[str] = None, github_token: Optional[str] = None):
        self.client = OpenRouterClient(
            api_key=api_key,
            workflow_type=WorkflowType.CODE_REVIEW
        )
        # Override model if specified
        if model:
            self.client.default_model.name = model
        
        # Initialize GitHub client
        self.github_client = GitHubClient(token=github_token)
        
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"OpenRouter PR Reviewer initialized with model: {self.client.default_model.name}")
        self.logger.info("GitHub client initialized for PR access")
    
    def review_pr(self, pr_number: int, repository: str = "", custom_instructions: str = "") -> str:
        """Review a PR using OpenRouter API and return the result"""
        
        # Fetch PR details from GitHub
        if repository and repository != "current-repo":
            if "/" not in repository:
                raise ValueError("Repository must be in format 'owner/repo'")
            owner, repo = repository.split("/", 1)
        else:
            raise ValueError("Repository must be specified in format 'owner/repo'")
        
        self.logger.info(f"Fetching PR #{pr_number} from {owner}/{repo}")
        pr_details = self.github_client.get_pr_details(owner, repo, pr_number)
        
        if not pr_details.get("success"):
            error_msg = pr_details.get("error", "Unknown error")
            if pr_details.get("status_code") == 404:
                error_msg = f"PR #{pr_number} not found in {repository}. Check the PR number and repository name."
            elif pr_details.get("status_code") == 401:
                error_msg = "GitHub authentication failed. Check your GITHUB_TOKEN."
            raise Exception(error_msg)
        
        # Format PR data for review
        pr_context = self.github_client.format_pr_for_review(pr_details)
        
        # Create comprehensive review prompt with accuracy emphasis
        prompt = f"""{pr_context}

CRITICAL INSTRUCTIONS FOR ACCURACY:
1. ✅ ONLY report issues you can verify exist in the actual code shown
2. ✅ Include exact file names and line numbers from the diff
3. ✅ Quote the actual code when discussing issues
4. ❌ Do NOT make assumptions about code not shown in the diff
5. ❌ Do NOT suggest issues that might exist elsewhere
6. ❌ Do NOT claim security issues without seeing the actual vulnerable code

Please analyze this pull request and provide detailed feedback covering:

## Code Quality & Best Practices
- Code structure and organization
- Naming conventions and readability
- Design patterns and architecture
- Language-specific best practices

## Security Analysis
- Potential security vulnerabilities
- Authentication and authorization issues
- Data exposure risks
- Input validation and sanitization

## Performance Considerations
- Algorithmic efficiency
- Memory usage patterns
- Database query optimization
- Scalability concerns

## Documentation & Testing
- Code comments and documentation
- Test coverage and quality
- API documentation completeness

## Detailed Findings
For each issue found, you MUST provide:
- **Exact file name and line number** from the diff
- **Quoted code snippet** showing the actual issue
- **Severity level** (Critical/High/Medium/Low) with justification
- **Specific fix** with before/after code examples

## Overall Assessment
- Summary of **verified** findings only
- Clear recommendation based on **actual issues found**
- Priority of **confirmed** problems only

{f"Additional instructions: {custom_instructions}" if custom_instructions else ""}

REMEMBER: Only comment on code you can actually see in the diff. If you suggest an issue exists, you must quote the exact code that demonstrates it.

Format your response in clear markdown with proper headers, code blocks, and bullet points."""

        # Execute OpenRouter request
        try:
            self.logger.info(f"Executing OpenRouter review for PR #{pr_number}")
            self.logger.info(f"Using model: {self.client.default_model.name}")
            self.logger.debug(f"Prompt length: {len(prompt)} characters")
            
            result = self.client.execute_prompt(
                prompt=prompt,
                timeout=1200  # 20 minute timeout for comprehensive reviews
            )
            
            if not result.get("success", False):
                error_msg = f"OpenRouter API failed: {result.get('error', 'Unknown error')}"
                self.logger.error(error_msg)
                raise Exception(error_msg)
            
            self.logger.info(f"Review completed in {result.get('execution_time', 0):.2f}s")
            self.logger.info(f"Usage: {result.get('usage', {}).get('total_tokens', 0)} tokens")
            
            return result["content"]
            
        except Exception as e:
            error_msg = f"Failed to execute OpenRouter review: {e}"
            self.logger.error(error_msg)
            raise Exception(error_msg)
    
    def save_review(self, pr_number: int, repository: str, review_content: str, output_path: Optional[str] = None) -> str:
        """Save the review to a markdown file and return file path"""
        
        # Use current working directory if no output path specified
        if output_path is None:
            output_dir = Path(os.getcwd())
        else:
            output_dir = Path(output_path)
        
        # Create output directory if it doesn't exist
        output_dir.mkdir(exist_ok=True)
        
        # Generate file name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        repo_name = repository.replace("/", "_") if repository != "current-repo" else "current-repo"
        
        markdown_file = output_dir / f"pr_review_{repo_name}_#{pr_number}_{timestamp}_openrouter.md"
        
        # Save markdown review
        with open(markdown_file, 'w', encoding='utf-8') as f:
            f.write(f"# Code Review: PR #{pr_number}\n\n")
            f.write(f"**Repository:** {repository}\n")
            f.write(f"**Review Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Model:** {self.client.default_model.name}\n")
            f.write(f"**Provider:** OpenRouter\n\n")
            f.write("---\n\n")
            f.write(review_content)
            f.write("\n\n---\n")
            f.write("*Generated by OpenRouter PR Reviewer*\n")
        
        return str(markdown_file)
    
    def estimate_cost(self, pr_number: int, repository: str = "") -> dict:
        """Estimate the cost of reviewing a PR"""
        # Create a sample prompt to estimate cost
        sample_prompt = f"Review PR #{pr_number} in {repository}"
        return self.client.estimate_cost(sample_prompt)


def main():
    """Main entry point"""
    from dotenv import load_dotenv
    
    # Load environment variables from .env file
    load_dotenv()
    
    # Get the original working directory from the wrapper script
    original_cwd = os.environ.get('ORIGINAL_PWD', os.getcwd())
    
    # Change to the original working directory for the duration of the script
    if original_cwd != os.getcwd():
        print(f"🔄 Changing working directory from {os.getcwd()} to {original_cwd}")
        os.chdir(original_cwd)
    
    parser = argparse.ArgumentParser(description="PR Review using OpenRouter API")
    parser.add_argument("pr_number", type=int, nargs='?', help="Pull request number to review")
    parser.add_argument("--repository", help="Repository in format owner/repo (defaults to current repo)")
    parser.add_argument("--model", help="OpenRouter model to use (e.g., anthropic/claude-3.5-sonnet)")
    parser.add_argument("--api-key", help="OpenRouter API key (or set OPENROUTER_API_KEY env var)")
    parser.add_argument("--github-token", help="GitHub token (or set GITHUB_TOKEN env var)")
    parser.add_argument("--instructions", help="Additional review instructions")
    parser.add_argument("--output", "-o", help="Output directory for review file (default: current directory)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    parser.add_argument("--estimate-cost", action="store_true", help="Estimate cost before review")
    parser.add_argument("--list-models", action="store_true", help="List recommended models for code review")
    
    args = parser.parse_args()
    
    # List models if requested
    if args.list_models:
        print("Recommended OpenRouter Models for Code Review:")
        print("=" * 60)
        models = OpenRouterModels.get_recommended_models(WorkflowType.CODE_REVIEW)
        for model in models:
            print(f"• {model.name}")
            print(f"  {model.description}")
            print(f"  Cost: ${model.cost_per_1k_tokens:.4f}/1K tokens")
            print(f"  Context: {model.context_window:,} tokens")
            print()
        return
    
    # Check if pr_number is provided when not listing models
    if args.pr_number is None:
        parser.error("pr_number is required when not using --list-models")
    
    # Get API keys from args or environment
    api_key = args.api_key or os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ Error: OpenRouter API key required.")
        print("   Set OPENROUTER_API_KEY environment variable or use --api-key")
        sys.exit(1)
    
    github_token = args.github_token or os.getenv("GITHUB_TOKEN")
    if not github_token:
        print("❌ Error: GitHub token required for PR access.")
        print("   Set GITHUB_TOKEN environment variable or use --github-token")
        print("   Get token from: https://github.com/settings/tokens")
        sys.exit(1)
    
    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Initialize reviewer
    reviewer = OpenRouterPRReviewer(model=args.model, api_key=api_key, github_token=github_token)
    repository = args.repository
    
    if not repository:
        print("❌ Error: Repository must be specified in format 'owner/repo'")
        print("   Example: --repository ochsec/agent-flows")
        sys.exit(1)
    
    try:
        # Estimate cost if requested
        if args.estimate_cost:
            cost_estimate = reviewer.estimate_cost(args.pr_number, repository)
            print(f"💰 Estimated cost: ${cost_estimate['estimated_cost']:.4f}")
            print(f"📊 Estimated tokens: {cost_estimate['prompt_tokens']}")
            print(f"🤖 Model: {cost_estimate['model']}")
            
            response = input("Continue with review? (y/N): ")
            if response.lower() != 'y':
                print("Review cancelled.")
                return
        
        print(f"🔍 Starting review of PR #{args.pr_number}...")
        print(f"🤖 Using model: {reviewer.client.default_model.name}")
        
        # Perform review
        review_content = reviewer.review_pr(
            pr_number=args.pr_number,
            repository=repository,
            custom_instructions=args.instructions
        )
        
        # Save results
        markdown_file = reviewer.save_review(
            pr_number=args.pr_number,
            repository=repository,
            review_content=review_content,
            output_path=args.output
        )
        
        print("✅ PR Review completed successfully!")
        print(f"📄 Review saved to: {markdown_file}")
        print("\nTo view the review:")
        print(f"  cat \"{markdown_file}\"")
        
    except Exception as e:
        print(f"❌ Review failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()