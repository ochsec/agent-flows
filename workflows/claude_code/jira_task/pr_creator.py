#!/usr/bin/env python3
"""
Pull Request Creation Utility

Handles automated pull request creation with GitHub CLI integration
and comprehensive PR descriptions.
"""

import subprocess
import re
from typing import Dict, Optional, List
from .git_integration import GitIntegration, GitError


class PRCreationError(Exception):
    """Custom exception for PR creation errors"""
    pass


class GitHubPRCreator:
    """GitHub pull request creator using GitHub CLI"""
    
    def __init__(self, git_integration: GitIntegration):
        self.git = git_integration
        self._validate_gh_cli()
    
    def _validate_gh_cli(self) -> None:
        """Validate GitHub CLI is installed and authenticated"""
        try:
            result = subprocess.run(['gh', 'auth', 'status'], capture_output=True, text=True)
            if result.returncode != 0:
                raise PRCreationError("GitHub CLI not authenticated. Run 'gh auth login' first.")
        except FileNotFoundError:
            raise PRCreationError("GitHub CLI not found. Please install: https://cli.github.com/")
    
    def create_pr(self, 
                  issue_key: str, 
                  issue_summary: str,
                  branch_name: str,
                  commit_details: Dict[str, any],
                  base_branch: str = "main") -> Dict[str, str]:
        """
        Create pull request with comprehensive description
        
        Args:
            issue_key: JIRA issue key
            issue_summary: Issue summary/title
            branch_name: Feature branch name
            commit_details: Details about commits and changes
            base_branch: Target branch for PR
            
        Returns:
            Dict with PR information (url, number, etc.)
        """
        
        # Generate PR title and description
        pr_title = self._generate_pr_title(issue_key, issue_summary)
        pr_description = self._generate_pr_description(
            issue_key, issue_summary, commit_details
        )
        
        # Create PR using GitHub CLI
        try:
            cmd = [
                'gh', 'pr', 'create',
                '--title', pr_title,
                '--body', pr_description,
                '--base', base_branch,
                '--head', branch_name
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Extract PR URL from output
            pr_url = result.stdout.strip()
            pr_number = self._extract_pr_number(pr_url)
            
            return {
                'url': pr_url,
                'number': pr_number,
                'title': pr_title,
                'status': 'created'
            }
            
        except subprocess.CalledProcessError as e:
            raise PRCreationError(f"Failed to create PR: {e.stderr}")
    
    def _generate_pr_title(self, issue_key: str, issue_summary: str) -> str:
        """Generate descriptive PR title"""
        # Clean up summary for title
        clean_summary = re.sub(r'[^\w\s-]', '', issue_summary)
        clean_summary = re.sub(r'\s+', ' ', clean_summary).strip()
        
        # Determine change type from summary
        change_type = self._determine_change_type(issue_summary)
        
        return f"{change_type}: {clean_summary} ({issue_key})"
    
    def _determine_change_type(self, summary: str) -> str:
        """Determine change type based on issue summary"""
        summary_lower = summary.lower()
        
        if any(word in summary_lower for word in ['fix', 'bug', 'error', 'issue']):
            return "fix"
        elif any(word in summary_lower for word in ['add', 'new', 'create', 'implement']):
            return "feat"
        elif any(word in summary_lower for word in ['update', 'improve', 'enhance', 'modify']):
            return "improvement"
        elif any(word in summary_lower for word in ['refactor', 'cleanup', 'reorganize']):
            return "refactor"
        elif any(word in summary_lower for word in ['test', 'testing']):
            return "test"
        elif any(word in summary_lower for word in ['doc', 'documentation']):
            return "docs"
        else:
            return "feat"
    
    def _generate_pr_description(self, 
                                issue_key: str, 
                                issue_summary: str,
                                commit_details: Dict[str, any]) -> str:
        """Generate comprehensive PR description"""
        
        # Get git changes summary
        try:
            files_changed = self.git.get_repo_status()
            recent_commits = self._get_recent_commits()
        except GitError:
            files_changed = {}
            recent_commits = []
        
        description = f"""## Summary
Implements solution for JIRA issue [{issue_key}]: {issue_summary}

## Changes Made
{self._format_changes_summary(commit_details)}

## Files Modified
{self._format_files_changed(files_changed)}

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests passing
- [ ] Manual testing completed
- [ ] No breaking changes introduced

## Code Quality
- [ ] Code follows project conventions
- [ ] No linting errors
- [ ] Documentation updated where needed
- [ ] Performance impact assessed

## Additional Notes
{self._format_additional_notes(commit_details)}

## JIRA Issue
- **Issue:** [{issue_key}](https://your-jira-instance.atlassian.net/browse/{issue_key})
- **Type:** {self._determine_change_type(issue_summary)}
- **Priority:** To be determined from JIRA

---
*This PR was created using the JIRA Task Workflow with Claude Code assistance.*
"""
        
        return description
    
    def _format_changes_summary(self, commit_details: Dict[str, any]) -> str:
        """Format summary of changes made"""
        if not commit_details:
            return "- Implementation details to be added"
        
        summary_parts = []
        
        if 'files_modified' in commit_details:
            file_count = len(commit_details['files_modified'])
            summary_parts.append(f"- Modified {file_count} files")
        
        if 'features_added' in commit_details:
            summary_parts.append(f"- Added: {', '.join(commit_details['features_added'])}")
        
        if 'bugs_fixed' in commit_details:
            summary_parts.append(f"- Fixed: {', '.join(commit_details['bugs_fixed'])}")
        
        return '\n'.join(summary_parts) if summary_parts else "- Implementation completed as specified"
    
    def _format_files_changed(self, files_changed: Dict[str, List[str]]) -> str:
        """Format list of changed files"""
        if not any(files_changed.values()):
            return "No files currently staged for commit"
        
        formatted = []
        for change_type, files in files_changed.items():
            if files:
                formatted.append(f"**{change_type.title()}:** {', '.join(files)}")
        
        return '\n'.join(formatted)
    
    def _format_additional_notes(self, commit_details: Dict[str, any]) -> str:
        """Format additional notes for PR"""
        notes = []
        
        if commit_details.get('breaking_changes'):
            notes.append("⚠️ **Breaking Changes:** This PR introduces breaking changes. Review carefully.")
        
        if commit_details.get('dependencies_added'):
            notes.append(f"📦 **New Dependencies:** {', '.join(commit_details['dependencies_added'])}")
        
        if commit_details.get('performance_impact'):
            notes.append(f"⚡ **Performance Impact:** {commit_details['performance_impact']}")
        
        return '\n'.join(notes) if notes else "No additional notes."
    
    def _get_recent_commits(self) -> List[str]:
        """Get recent commits for this branch"""
        try:
            result = self.git._run_git_command(['log', '--oneline', '-5'])
            return result.split('\n') if result else []
        except GitError:
            return []
    
    def _extract_pr_number(self, pr_url: str) -> Optional[str]:
        """Extract PR number from GitHub URL"""
        match = re.search(r'/pull/(\d+)', pr_url)
        return match.group(1) if match else None
    
    def add_pr_labels(self, pr_number: str, labels: List[str]) -> bool:
        """Add labels to PR"""
        try:
            cmd = ['gh', 'pr', 'edit', pr_number, '--add-label', ','.join(labels)]
            subprocess.run(cmd, check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def request_reviewers(self, pr_number: str, reviewers: List[str]) -> bool:
        """Request reviewers for PR"""
        try:
            cmd = ['gh', 'pr', 'edit', pr_number, '--add-reviewer', ','.join(reviewers)]
            subprocess.run(cmd, check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def link_to_jira(self, issue_key: str, pr_url: str) -> str:
        """Generate JIRA comment linking to PR"""
        return f"""🔗 **Pull Request Created**

**PR:** {pr_url}
**Status:** Ready for review
**Created:** {self._get_current_timestamp()}

The implementation is complete and ready for code review. Please review the changes and provide feedback.

**Next Steps:**
1. Code review by team members
2. Address any review feedback
3. Merge after approval
4. Update issue status to completed"""
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp for JIRA comments"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")


if __name__ == "__main__":
    # Example usage
    import argparse
    from .git_integration import GitIntegration
    
    parser = argparse.ArgumentParser(description="GitHub PR Creator")
    parser.add_argument("issue_key", help="JIRA issue key")
    parser.add_argument("issue_summary", help="Issue summary")
    parser.add_argument("--branch", help="Branch name (default: current branch)")
    
    args = parser.parse_args()
    
    try:
        git = GitIntegration()
        pr_creator = GitHubPRCreator(git)
        
        branch_name = args.branch or git.get_current_branch()
        
        # Create PR with minimal details for testing
        pr_info = pr_creator.create_pr(
            args.issue_key,
            args.issue_summary, 
            branch_name,
            {}  # Empty commit details for testing
        )
        
        print(f"✅ PR Created: {pr_info['url']}")
        print(f"📋 Title: {pr_info['title']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")