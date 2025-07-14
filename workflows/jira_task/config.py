#!/usr/bin/env python3
"""
JIRA Task Workflow Configuration

Configuration management for JIRA API integration and workflow settings.
"""

import os
from typing import Optional
from pydantic import BaseModel, Field, validator
from dotenv import load_dotenv


class JiraConfig(BaseModel):
    """JIRA configuration model with validation"""
    
    base_url: str = Field(..., description="JIRA instance URL")
    api_token: str = Field(..., description="JIRA API token or password") 
    username: str = Field(..., description="JIRA username or email")
    project_key: Optional[str] = Field(None, description="Default project key")
    
    @validator('base_url')
    def validate_base_url(cls, v):
        """Ensure base URL is properly formatted"""
        if not v.startswith(('http://', 'https://')):
            raise ValueError('base_url must start with http:// or https://')
        return v.rstrip('/')
    
    @validator('api_token')
    def validate_api_token(cls, v):
        """Ensure API token is not empty"""
        if not v or len(v.strip()) == 0:
            raise ValueError('api_token cannot be empty')
        return v.strip()
    
    @validator('username')
    def validate_username(cls, v):
        """Ensure username is not empty"""
        if not v or len(v.strip()) == 0:
            raise ValueError('username cannot be empty')
        return v.strip()


def load_jira_config(config_path: Optional[str] = None) -> JiraConfig:
    """
    Load JIRA configuration from unified config system or fallback to environment variables
    
    Args:
        config_path: Optional path to .env file (for backward compatibility)
        
    Returns:
        JiraConfig: Validated configuration object
        
    Raises:
        ValueError: If required configuration is missing or invalid
    """
    # Try unified config system first
    try:
        from pathlib import Path
        import sys
        
        # Add project root to path to import config
        project_root = Path(__file__).parent.parent.parent.parent
        sys.path.insert(0, str(project_root))
        
        from config import AgentFlowsConfig
        
        unified_config = AgentFlowsConfig()
        if unified_config.is_jira_configured():
            jira_config = unified_config.get_jira_config()
            return JiraConfig(
                base_url=jira_config['base_url'],
                api_token=jira_config['api_token'],
                username=jira_config['username'],
                project_key=jira_config.get('project_key')
            )
    except Exception:
        # Fall back to environment variables if unified config fails
        pass
    
    # Fallback: Load environment variables
    if config_path:
        load_dotenv(config_path)
    else:
        load_dotenv()
    
    # Get configuration from environment
    base_url = os.getenv("JIRA_BASE_URL", "")
    api_token = os.getenv("JIRA_API_TOKEN", "")
    username = os.getenv("JIRA_USERNAME", "")
    project_key = os.getenv("JIRA_PROJECT_KEY")
    
    # Validate required fields
    missing_fields = []
    if not base_url:
        missing_fields.append("JIRA_BASE_URL")
    if not api_token:
        missing_fields.append("JIRA_API_TOKEN")
    if not username:
        missing_fields.append("JIRA_USERNAME")
    
    if missing_fields:
        raise ValueError(
            f"Missing required JIRA configuration.\n"
            f"Please run 'python config.py configure --jira' to set up JIRA credentials,\n"
            f"or set these environment variables: {', '.join(missing_fields)}"
        )
    
    return JiraConfig(
        base_url=base_url,
        api_token=api_token,
        username=username,
        project_key=project_key
    )


def create_sample_env_file(path: str = ".env") -> None:
    """
    Create a sample .env file with JIRA configuration template
    
    Args:
        path: Path where to create the .env file
    """
    sample_content = """# JIRA Configuration
# Copy this file to .env and fill in your actual values

# Your JIRA instance URL (e.g., https://yourcompany.atlassian.net)
JIRA_BASE_URL=https://your-domain.atlassian.net

# Your JIRA API token (create at: https://id.atlassian.com/manage-profile/security/api-tokens)
JIRA_API_TOKEN=your_api_token_here

# Your JIRA username/email
JIRA_USERNAME=your.email@company.com

# Optional: Default project key for issues
JIRA_PROJECT_KEY=PROJ
"""
    
    with open(path, 'w') as f:
        f.write(sample_content)
    
    print(f"Sample configuration file created at: {path}")
    print("Please edit this file with your actual JIRA credentials.")


if __name__ == "__main__":
    # Example usage and testing
    import argparse
    
    parser = argparse.ArgumentParser(description="JIRA Configuration Management")
    parser.add_argument("--create-sample", action="store_true", 
                       help="Create sample .env file")
    parser.add_argument("--test", action="store_true",
                       help="Test configuration loading")
    parser.add_argument("--config", help="Path to .env file")
    
    args = parser.parse_args()
    
    if args.create_sample:
        create_sample_env_file()
    elif args.test:
        try:
            config = load_jira_config(args.config)
            print("✅ Configuration loaded successfully!")
            print(f"JIRA URL: {config.base_url}")
            print(f"Username: {config.username}")
            print(f"Project Key: {config.project_key or 'Not set'}")
        except Exception as e:
            print(f"❌ Configuration error: {e}")
    else:
        parser.print_help()