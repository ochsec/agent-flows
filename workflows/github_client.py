"""
GitHub API client for fetching PR details and code changes.
"""

import os
import requests
from typing import Dict, List, Optional, Any
import base64


class GitHubClient:
    """GitHub API client for PR operations"""
    
    def __init__(self, token: Optional[str] = None):
        """Initialize GitHub client with API token"""
        self.token = token or os.getenv("GITHUB_TOKEN")
        if not self.token:
            raise ValueError("GitHub token required. Set GITHUB_TOKEN env var or pass token parameter.")
        
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "OpenRouter-PR-Reviewer"
        }
    
    def get_pr_details(self, owner: str, repo: str, pr_number: int) -> Dict[str, Any]:
        """Get PR details including metadata and files changed"""
        try:
            # Get PR info
            pr_url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}"
            pr_response = requests.get(pr_url, headers=self.headers)
            pr_response.raise_for_status()
            pr_data = pr_response.json()
            
            # Get PR files
            files_url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}/files"
            files_response = requests.get(files_url, headers=self.headers)
            files_response.raise_for_status()
            files_data = files_response.json()
            
            # Get PR diff
            diff_headers = self.headers.copy()
            diff_headers["Accept"] = "application/vnd.github.v3.diff"
            diff_response = requests.get(pr_url, headers=diff_headers)
            diff_response.raise_for_status()
            diff_content = diff_response.text
            
            return {
                "pr": pr_data,
                "files": files_data,
                "diff": diff_content,
                "success": True
            }
            
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"GitHub API error: {str(e)}",
                "status_code": getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None
            }
    
    def get_file_content(self, owner: str, repo: str, path: str, ref: str = "main") -> Optional[str]:
        """Get file content from repository"""
        try:
            url = f"{self.base_url}/repos/{owner}/{repo}/contents/{path}"
            params = {"ref": ref}
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            if data.get("encoding") == "base64":
                content = base64.b64decode(data["content"]).decode('utf-8')
                return content
            else:
                return data.get("content", "")
                
        except requests.exceptions.RequestException:
            return None
    
    def format_pr_for_review(self, pr_details: Dict[str, Any]) -> str:
        """Format PR details into a comprehensive text for review"""
        if not pr_details.get("success"):
            return f"Error fetching PR details: {pr_details.get('error', 'Unknown error')}"
        
        pr = pr_details["pr"]
        files = pr_details["files"]
        diff = pr_details["diff"]
        
        # Build comprehensive PR context
        review_text = f"""# Pull Request Review Context

## PR Information
- **Number**: #{pr['number']}
- **Title**: {pr['title']}
- **Author**: {pr['user']['login']}
- **Status**: {pr['state']}
- **Base Branch**: {pr['base']['ref']}
- **Head Branch**: {pr['head']['ref']}
- **Created**: {pr['created_at']}
- **Updated**: {pr['updated_at']}

## Description
{pr['body'] or 'No description provided'}

## Files Changed ({len(files)} files)
"""
        
        # Add file summary
        for file in files:
            status = file['status']
            filename = file['filename']
            additions = file.get('additions', 0)
            deletions = file.get('deletions', 0)
            
            review_text += f"- **{filename}** ({status}): +{additions}/-{deletions} lines\n"
        
        review_text += f"""
## Code Changes (Diff)

```diff
{diff}
```

## Review Instructions
Please analyze this pull request thoroughly, focusing on:
1. Code quality and best practices
2. Security implications
3. Performance considerations
4. Testing coverage
5. Documentation completeness
6. Potential bugs or issues

Provide specific feedback with file names and line numbers where applicable.
"""
        
        return review_text


def test_github_client():
    """Test GitHub client functionality"""
    try:
        client = GitHubClient()
        print("✅ GitHub client initialized successfully")
        
        # Test with a public repo PR
        result = client.get_pr_details("octocat", "Hello-World", 1)
        if result.get("success"):
            print("✅ GitHub API access working")
        else:
            print(f"❌ GitHub API test failed: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ GitHub client test failed: {e}")


if __name__ == "__main__":
    test_github_client()