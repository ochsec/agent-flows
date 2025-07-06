#!/usr/bin/env python3
"""
Simple PR Review Workflow - Claude Code Integration

A straightforward code review workflow that uses Claude Code's built-in
GitHub integration to review pull requests and save results to files.
"""

import os
import sys
import subprocess
import json
from datetime import datetime
from pathlib import Path
import argparse
import logging


class SimplePRReviewer:
    """Simple PR reviewer using Claude Code"""
    
    def __init__(self, model: str = "sonnet"):
        self.model = model
        self.logger = logging.getLogger(__name__)
    
    def review_pr(self, pr_number: int, repository: str = "", custom_instructions: str = "") -> str:
        """Review a PR using Claude Code and return the result"""
        
        # Create comprehensive review prompt
        prompt = f"""Please analyze the GitHub PR #{pr_number} in the repository {repository if repository != "current-repo" else "this repository"}.

IMPORTANT: Use the Bash tool to first fetch the PR details using `gh pr view {pr_number} --json files,additions,deletions,title,body` and then examine the actual code changes with `gh pr diff {pr_number}`.

After examining the actual code changes, provide a comprehensive code review covering:

## 1. Code Quality & Best Practices
- Analyze the specific code changes for structure and organization
- Review naming conventions and readability in the modified files
- Assess design patterns and architectural decisions
- Evaluate language-specific best practices

## 2. Security Analysis
- Identify potential security vulnerabilities in the changed code
- Check for authentication and authorization issues
- Look for data exposure risks
- Verify input validation and sanitization

## 3. Performance Considerations
- Analyze algorithmic efficiency of new code
- Review memory usage patterns
- Check database query optimization
- Assess scalability concerns

## 4. Documentation & Testing
- Review code comments and documentation
- Assess test coverage for new/modified code
- Check API documentation completeness

## 5. Detailed Findings
For each issue found, provide:
- **File name and line number(s)**
- **Issue description**
- **Severity level (Critical/High/Medium/Low)**
- **Specific recommendation for fix**

## 6. Overall Assessment
- Summary of key findings with specific examples
- Clear recommendation (Approve/Request Changes/Reject)
- Priority issues that need immediate attention

{f"Additional instructions: {custom_instructions}" if custom_instructions else ""}

Please be thorough and specific - include actual code snippets, file names, and line numbers in your analysis."""

        # Execute Claude Code command
        try:
            command = ["claude", "-p", "--model", self.model, "--allowedTools", "Bash,WebFetch"]
            
            self.logger.info(f"Executing Claude Code review for PR #{pr_number}")
            self.logger.info(f"Using model: {self.model}")
            self.logger.debug(f"Command: {' '.join(command)}")
            self.logger.debug(f"Prompt length: {len(prompt)} characters")
            
            result = subprocess.run(
                command,
                input=prompt,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout for comprehensive reviews
            )
            
            if result.returncode != 0:
                error_msg = f"Claude Code failed (exit code {result.returncode}): {result.stderr}"
                self.logger.error(error_msg)
                self.logger.error(f"Command: {' '.join(command)}")
                self.logger.error(f"Stdout: {result.stdout}")
                raise Exception(error_msg)
            
            return result.stdout.strip()
            
        except subprocess.TimeoutExpired:
            error_msg = "Claude Code review timed out (10 minutes)"
            self.logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Failed to execute Claude Code review: {e}"
            self.logger.error(error_msg)
            raise Exception(error_msg)
    
    def save_review(self, pr_number: int, repository: str, review_content: str) -> str:
        """Save the review to a markdown file and return file path"""
        
        # Generate file name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        repo_name = repository.replace("/", "_") if repository != "current-repo" else "current-repo"
        
        markdown_file = f"pr_review_{repo_name}_#{pr_number}_{timestamp}.md"
        
        # Save markdown review
        with open(markdown_file, 'w', encoding='utf-8') as f:
            f.write(f"# Code Review: PR #{pr_number}\n\n")
            f.write(f"**Repository:** {repository}\n")
            f.write(f"**Review Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Claude Model:** {self.model}\n\n")
            f.write("---\n\n")
            f.write(review_content)
            f.write("\n\n---\n")
            f.write("*Generated by Claude Code PR Reviewer*\n")
        
        return markdown_file


def main():
    """Main entry point"""
    
    parser = argparse.ArgumentParser(description="Simple PR Review using Claude Code")
    parser.add_argument("pr_number", type=int, help="Pull request number to review")
    parser.add_argument("--repository", help="Repository in format owner/repo (defaults to current repo)")
    parser.add_argument("--model", default="sonnet", help="Claude model to use (sonnet, opus, haiku)")
    parser.add_argument("--instructions", help="Additional review instructions")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Initialize reviewer
    reviewer = SimplePRReviewer(model=args.model)
    repository = args.repository or "current-repo"
    
    try:
        print(f"🔍 Starting review of PR #{args.pr_number}...")
        
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
            review_content=review_content
        )
        
        print("✅ PR Review completed successfully!")
        print(f"📄 Review saved to: {markdown_file}")
        print(f"\nTo view the review:")
        print(f"  cat {markdown_file}")
        
    except Exception as e:
        print(f"❌ Review failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()