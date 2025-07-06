#!/usr/bin/env python3
"""Quick test of simple PR review approach"""

import subprocess
import sys
from datetime import datetime

def quick_review(pr_number):
    """Simple one-call PR review"""
    
    prompt = f"""Please provide a comprehensive code review of PR #{pr_number} in this repository.

Cover:
- Code quality and best practices
- Security considerations  
- Performance implications
- Documentation and testing
- Overall recommendation

Be specific with file names and provide actionable feedback."""

    try:
        result = subprocess.run(
            ["claude", "-p", "--model", "sonnet", prompt],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
            return None
            
        return result.stdout.strip()
        
    except Exception as e:
        print(f"Failed: {e}")
        return None

if __name__ == "__main__":
    pr_num = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    
    print(f"🔍 Reviewing PR #{pr_num}...")
    review = quick_review(pr_num)
    
    if review:
        # Save to file
        filename = f"simple_review_pr_{pr_num}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(filename, 'w') as f:
            f.write(f"# Code Review: PR #{pr_num}\n\n")
            f.write(review)
        
        print(f"✅ Review saved to: {filename}")
        print(f"\nPreview:")
        print(review[:500] + "..." if len(review) > 500 else review)
    else:
        print("❌ Review failed")