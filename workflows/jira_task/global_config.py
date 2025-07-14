#!/usr/bin/env python3
"""
Global JIRA Configuration Management

Provides AWS CLI-style global configuration storage for JIRA credentials.
Credentials are stored in ~/.agent-flows/jira/ directory with proper permissions.
"""

import os
import json
import stat
from pathlib import Path
from typing import Optional, Dict, Any
from getpass import getpass


class GlobalJiraConfig:
    """Global JIRA configuration manager similar to AWS CLI"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".agent-flows" / "jira"
        self.credentials_file = self.config_dir / "credentials"
        self.config_file = self.config_dir / "config"
        
        # Ensure config directory exists with proper permissions
        self._ensure_config_dir()
    
    def _ensure_config_dir(self):
        """Create config directory with secure permissions"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        # Set directory permissions to 700 (owner read/write/execute only)
        os.chmod(self.config_dir, stat.S_IRWXU)
    
    def _secure_file_permissions(self, file_path: Path):
        """Set secure file permissions (600 - owner read/write only)"""
        if file_path.exists():
            os.chmod(file_path, stat.S_IRUSR | stat.S_IWUSR)
    
    def configure_interactive(self):
        """Interactive configuration setup like 'aws configure'"""
        print("🔧 JIRA Configuration Setup")
        print("Enter your JIRA server details (leave blank to keep current value):")
        
        # Load existing config if available
        current_config = self.get_config()
        current_creds = self.get_credentials()
        
        # Get JIRA server URL
        current_url = current_config.get('default', {}).get('base_url', '')
        if current_url:
            print(f"Current JIRA URL: {current_url}")
        
        base_url = input("JIRA Base URL [https://your-company.atlassian.net]: ").strip()
        if not base_url and not current_url:
            print("❌ JIRA Base URL is required")
            return False
        
        # Get username
        current_username = current_creds.get('default', {}).get('username', '')
        if current_username:
            print(f"Current username: {current_username}")
        
        username = input("JIRA Username/Email: ").strip()
        if not username and not current_username:
            print("❌ Username is required")
            return False
        
        # Get API token (hidden input)
        print("\\nJIRA API Token (create at: https://id.atlassian.com/manage-profile/security/api-tokens)")
        api_token = getpass("API Token (input hidden): ").strip()
        if not api_token and not current_creds.get('default', {}).get('api_token'):
            print("❌ API Token is required")
            return False
        
        # Get optional project key
        current_project = current_config.get('default', {}).get('project_key', '')
        if current_project:
            print(f"Current project key: {current_project}")
        
        project_key = input("Default Project Key (optional): ").strip()
        
        # Save configuration
        config_data = {
            'default': {
                'base_url': base_url or current_url,
                'project_key': project_key or current_project
            }
        }
        
        credentials_data = {
            'default': {
                'username': username or current_username,
                'api_token': api_token or current_creds.get('default', {}).get('api_token', '')
            }
        }
        
        self.save_config(config_data)
        self.save_credentials(credentials_data)
        
        print("\\n✅ JIRA configuration saved successfully!")
        print(f"📁 Configuration stored in: {self.config_dir}")
        print("\\n💡 You can now use 'jira_task ISSUE-KEY' without additional setup")
        
        return True
    
    def save_config(self, config_data: Dict[str, Any]):
        """Save configuration data to config file"""
        with open(self.config_file, 'w') as f:
            json.dump(config_data, f, indent=2)
        self._secure_file_permissions(self.config_file)
    
    def save_credentials(self, credentials_data: Dict[str, Any]):
        """Save credentials to secure credentials file"""
        with open(self.credentials_file, 'w') as f:
            json.dump(credentials_data, f, indent=2)
        self._secure_file_permissions(self.credentials_file)
    
    def get_config(self, profile: str = 'default') -> Dict[str, Any]:
        """Load configuration from config file"""
        if not self.config_file.exists():
            return {}
        
        try:
            with open(self.config_file, 'r') as f:
                data = json.load(f)
                return data.get(profile, {})
        except (json.JSONDecodeError, IOError):
            return {}
    
    def get_credentials(self, profile: str = 'default') -> Dict[str, Any]:
        """Load credentials from credentials file"""
        if not self.credentials_file.exists():
            return {}
        
        try:
            with open(self.credentials_file, 'r') as f:
                data = json.load(f)
                return data.get(profile, {})
        except (json.JSONDecodeError, IOError):
            return {}
    
    def get_full_config(self, profile: str = 'default') -> Optional[Dict[str, str]]:
        """Get complete configuration by merging config and credentials"""
        config = self.get_config(profile)
        credentials = self.get_credentials(profile)
        
        if not config or not credentials:
            return None
        
        # Merge configuration and credentials
        full_config = {
            'base_url': config.get('base_url'),
            'username': credentials.get('username'),
            'api_token': credentials.get('api_token'),
            'project_key': config.get('project_key')
        }
        
        # Validate required fields
        if not all([full_config['base_url'], full_config['username'], full_config['api_token']]):
            return None
        
        return full_config
    
    def list_profiles(self) -> list:
        """List available configuration profiles"""
        profiles = set()
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)
                    profiles.update(config_data.keys())
            except (json.JSONDecodeError, IOError):
                pass
        
        if self.credentials_file.exists():
            try:
                with open(self.credentials_file, 'r') as f:
                    creds_data = json.load(f)
                    profiles.update(creds_data.keys())
            except (json.JSONDecodeError, IOError):
                pass
        
        return sorted(list(profiles))
    
    def is_configured(self, profile: str = 'default') -> bool:
        """Check if JIRA is properly configured for the given profile"""
        config = self.get_full_config(profile)
        return config is not None
    
    def show_config(self, profile: str = 'default'):
        """Display current configuration (without sensitive data)"""
        config = self.get_config(profile)
        credentials = self.get_credentials(profile)
        
        if not config and not credentials:
            print(f"❌ No configuration found for profile '{profile}'")
            print("💡 Run 'jira_task configure' to set up your JIRA credentials")
            return
        
        print(f"📋 JIRA Configuration (Profile: {profile})")
        print(f"   Base URL: {config.get('base_url', 'Not set')}")
        print(f"   Username: {credentials.get('username', 'Not set')}")
        print(f"   API Token: {'*' * 20 if credentials.get('api_token') else 'Not set'}")
        print(f"   Project Key: {config.get('project_key', 'Not set')}")
        print(f"   Config Directory: {self.config_dir}")


def main():
    """CLI interface for global configuration management"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Global JIRA Configuration Management")
    parser.add_argument("command", choices=["configure", "show", "list"], 
                       help="Configuration command")
    parser.add_argument("--profile", default="default", 
                       help="Configuration profile name")
    
    args = parser.parse_args()
    
    global_config = GlobalJiraConfig()
    
    if args.command == "configure":
        global_config.configure_interactive()
    elif args.command == "show":
        global_config.show_config(args.profile)
    elif args.command == "list":
        profiles = global_config.list_profiles()
        if profiles:
            print("📋 Available JIRA profiles:")
            for profile in profiles:
                status = "✅" if global_config.is_configured(profile) else "❌"
                print(f"   {status} {profile}")
        else:
            print("❌ No JIRA profiles configured")
            print("💡 Run 'jira_task configure' to set up your JIRA credentials")


if __name__ == "__main__":
    main()