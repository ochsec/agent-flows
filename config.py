#!/usr/bin/env python3
"""
Unified Agent Flows Configuration Management

Centralized TOML-based configuration system for all services including JIRA, Perplexity, and future integrations.
Stores configuration in ~/.agent-flows/config.toml file.
"""

import os
import stat
from pathlib import Path
from typing import Optional, Dict, Any
from getpass import getpass

try:
    import tomllib
    import tomli_w
except ImportError:
    try:
        import tomli as tomllib
        import tomli_w
    except ImportError:
        print("❌ TOML libraries not available. Please install with: pip install tomli tomli-w")
        exit(1)


class AgentFlowsConfig:
    """Unified TOML-based configuration manager for all Agent Flows services"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".agent-flows"
        self.config_file = self.config_dir / "config.toml"
        
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
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from TOML file"""
        if not self.config_file.exists():
            return {}
        
        try:
            with open(self.config_file, 'rb') as f:
                return tomllib.load(f)
        except Exception as e:
            print(f"❌ Error loading config: {e}")
            return {}
    
    def _save_config(self, config_data: Dict[str, Any]):
        """Save configuration to TOML file with secure permissions"""
        try:
            with open(self.config_file, 'wb') as f:
                tomli_w.dump(config_data, f)
            self._secure_file_permissions(self.config_file)
        except Exception as e:
            print(f"❌ Error saving config: {e}")
    
    def _create_sample_config(self):
        """Create a sample configuration file"""
        sample_config = {
            "jira": {
                "base_url": "https://your-company.atlassian.net",
                "username": "your.email@company.com",
                "api_token": "your_jira_api_token_here",
                "project_key": "PROJ"
            },
            "perplexity": {
                "api_key": "your_perplexity_api_key_here"
            },
            "openrouter": {
                "api_key": "your_openrouter_api_key_here",
                "site_url": "https://github.com/yourusername/yourproject",
                "site_name": "Your Project Name"
            },
            "github": {
                "token": "your_github_token_here"
            }
        }
        
        self._save_config(sample_config)
        print(f"📝 Sample configuration created at: {self.config_file}")
        print("Please edit this file with your actual credentials.")
    
    # ===================
    # JIRA Configuration
    # ===================
    
    def configure_jira_interactive(self):
        """Interactive JIRA configuration setup"""
        print("🔧 JIRA Configuration Setup")
        print("Enter your JIRA server details (leave blank to keep current value):")
        
        # Load existing config
        config_data = self._load_config()
        current_jira = config_data.get('jira', {})
        
        # Get JIRA server URL
        current_url = current_jira.get('base_url', '')
        if current_url:
            print(f"Current JIRA URL: {current_url}")
        
        base_url = input("JIRA Base URL [https://your-company.atlassian.net]: ").strip()
        if not base_url and not current_url:
            print("❌ JIRA Base URL is required")
            return False
        
        # Get username
        current_username = current_jira.get('username', '')
        if current_username:
            print(f"Current username: {current_username}")
        
        username = input("JIRA Username/Email: ").strip()
        if not username and not current_username:
            print("❌ Username is required")
            return False
        
        # Get API token (hidden input)
        print("\nJIRA API Token (create at: https://id.atlassian.com/manage-profile/security/api-tokens)")
        api_token = getpass("API Token (input hidden): ").strip()
        if not api_token and not current_jira.get('api_token'):
            print("❌ API Token is required")
            return False
        
        # Get optional project key
        current_project = current_jira.get('project_key', '')
        if current_project:
            print(f"Current project key: {current_project}")
        
        project_key = input("Default Project Key (optional): ").strip()
        
        # Update configuration
        if 'jira' not in config_data:
            config_data['jira'] = {}
        
        config_data['jira'].update({
            'base_url': base_url or current_url,
            'username': username or current_username,
            'api_token': api_token or current_jira.get('api_token', ''),
            'project_key': project_key or current_project
        })
        
        self._save_config(config_data)
        
        print("\n✅ JIRA configuration saved successfully!")
        return True
    
    def get_jira_config(self) -> Dict[str, Any]:
        """Get JIRA configuration"""
        config_data = self._load_config()
        return config_data.get('jira', {})
    
    def is_jira_configured(self) -> bool:
        """Check if JIRA is properly configured"""
        jira_config = self.get_jira_config()
        required_fields = ['base_url', 'username', 'api_token']
        return all(jira_config.get(field) for field in required_fields)
    
    # =======================
    # Perplexity Configuration
    # =======================
    
    def configure_perplexity_interactive(self):
        """Interactive Perplexity configuration setup"""
        print("🔧 Perplexity API Configuration Setup")
        
        current_key = self.get_perplexity_api_key()
        if current_key:
            print(f"Current API key: {current_key[:8]}...{current_key[-4:] if len(current_key) > 12 else '*'*4}")
        
        api_key = getpass("Perplexity API Key (input hidden): ").strip()
        if not api_key and not current_key:
            print("❌ Perplexity API Key is required")
            return False
        
        if api_key:
            config_data = self._load_config()
            if 'perplexity' not in config_data:
                config_data['perplexity'] = {}
            
            config_data['perplexity']['api_key'] = api_key
            self._save_config(config_data)
            
            print("\n✅ Perplexity API key saved successfully!")
        else:
            print("\n✅ Keeping existing Perplexity API key")
        
        return True
    
    def get_perplexity_api_key(self) -> Optional[str]:
        """Get Perplexity API key"""
        config_data = self._load_config()
        return config_data.get('perplexity', {}).get('api_key')
    
    def is_perplexity_configured(self) -> bool:
        """Check if Perplexity is configured"""
        return self.get_perplexity_api_key() is not None
    
    # =======================
    # OpenRouter Configuration
    # =======================
    
    def configure_openrouter_interactive(self):
        """Interactive OpenRouter configuration setup"""
        print("🔧 OpenRouter API Configuration Setup")
        
        config_data = self._load_config()
        current_openrouter = config_data.get('openrouter', {})
        
        current_key = current_openrouter.get('api_key', '')
        if current_key:
            print(f"Current API key: {current_key[:8]}...{current_key[-4:] if len(current_key) > 12 else '*'*4}")
        
        api_key = getpass("OpenRouter API Key (input hidden): ").strip()
        if not api_key and not current_key:
            print("❌ OpenRouter API Key is required")
            return False
        
        # Get site info
        current_site_url = current_openrouter.get('site_url', '')
        if current_site_url:
            print(f"Current site URL: {current_site_url}")
        
        site_url = input("Site URL (optional): ").strip()
        
        current_site_name = current_openrouter.get('site_name', '')
        if current_site_name:
            print(f"Current site name: {current_site_name}")
        
        site_name = input("Site Name (optional): ").strip()
        
        if 'openrouter' not in config_data:
            config_data['openrouter'] = {}
        
        config_data['openrouter'].update({
            'api_key': api_key or current_key,
            'site_url': site_url or current_site_url,
            'site_name': site_name or current_site_name
        })
        
        self._save_config(config_data)
        
        print("\n✅ OpenRouter configuration saved successfully!")
        return True
    
    def get_openrouter_config(self) -> Dict[str, Any]:
        """Get OpenRouter configuration"""
        config_data = self._load_config()
        return config_data.get('openrouter', {})
    
    def is_openrouter_configured(self) -> bool:
        """Check if OpenRouter is configured"""
        openrouter_config = self.get_openrouter_config()
        return bool(openrouter_config.get('api_key'))
    
    # =======================
    # GitHub Configuration
    # =======================
    
    def configure_github_interactive(self):
        """Interactive GitHub configuration setup"""
        print("🔧 GitHub Token Configuration Setup")
        
        current_token = self.get_github_token()
        if current_token:
            print(f"Current token: {current_token[:8]}...{current_token[-4:] if len(current_token) > 12 else '*'*4}")
        
        token = getpass("GitHub Token (input hidden): ").strip()
        if not token and not current_token:
            print("❌ GitHub Token is required")
            return False
        
        if token:
            config_data = self._load_config()
            if 'github' not in config_data:
                config_data['github'] = {}
            
            config_data['github']['token'] = token
            self._save_config(config_data)
            
            print("\n✅ GitHub token saved successfully!")
        else:
            print("\n✅ Keeping existing GitHub token")
        
        return True
    
    def get_github_token(self) -> Optional[str]:
        """Get GitHub token"""
        config_data = self._load_config()
        return config_data.get('github', {}).get('token')
    
    def is_github_configured(self) -> bool:
        """Check if GitHub is configured"""
        return self.get_github_token() is not None
    
    # ===================
    # General Configuration
    # ===================
    
    def configure_interactive(self):
        """Interactive configuration for all services"""
        print("🚀 Agent Flows Configuration Setup")
        print("Configure your service integrations:\n")
        
        # Configure JIRA
        print("1️⃣  JIRA Integration")
        if self.is_jira_configured():
            print("   ✅ Currently configured")
            if input("   Reconfigure JIRA? (y/N): ").lower().startswith('y'):
                self.configure_jira_interactive()
        else:
            print("   ❌ Not configured")
            if input("   Configure JIRA now? (Y/n): ").lower() not in ['n', 'no']:
                self.configure_jira_interactive()
        
        print()
        
        # Configure Perplexity
        print("2️⃣  Perplexity API Integration")
        if self.is_perplexity_configured():
            print("   ✅ Currently configured")
            if input("   Reconfigure Perplexity? (y/N): ").lower().startswith('y'):
                self.configure_perplexity_interactive()
        else:
            print("   ❌ Not configured")
            if input("   Configure Perplexity now? (y/N): ").lower().startswith('y'):
                self.configure_perplexity_interactive()
        
        print()
        
        # Configure OpenRouter
        print("3️⃣  OpenRouter API Integration")
        if self.is_openrouter_configured():
            print("   ✅ Currently configured")
            if input("   Reconfigure OpenRouter? (y/N): ").lower().startswith('y'):
                self.configure_openrouter_interactive()
        else:
            print("   ❌ Not configured")
            if input("   Configure OpenRouter now? (y/N): ").lower().startswith('y'):
                self.configure_openrouter_interactive()
        
        print()
        
        # Configure GitHub
        print("4️⃣  GitHub Token Integration")
        if self.is_github_configured():
            print("   ✅ Currently configured")
            if input("   Reconfigure GitHub? (y/N): ").lower().startswith('y'):
                self.configure_github_interactive()
        else:
            print("   ❌ Not configured")
            if input("   Configure GitHub now? (y/N): ").lower().startswith('y'):
                self.configure_github_interactive()
        
        print()
        print("✅ Configuration complete!")
        print(f"📁 Configuration stored in: {self.config_file}")
        print(f"💡 You can also edit the config file directly with any text editor")
        self.show_status()
    
    def show_status(self):
        """Show configuration status for all services"""
        print("\n📋 Agent Flows Configuration Status")
        print("=" * 40)
        
        # JIRA status
        jira_status = "✅ Configured" if self.is_jira_configured() else "❌ Not configured"
        print(f"JIRA:          {jira_status}")
        if self.is_jira_configured():
            jira_config = self.get_jira_config()
            print(f"   URL:        {jira_config.get('base_url', 'Not set')}")
            print(f"   Username:   {jira_config.get('username', 'Not set')}")
            print(f"   Project:    {jira_config.get('project_key', 'Not set')}")
        
        # Perplexity status
        perplexity_status = "✅ Configured" if self.is_perplexity_configured() else "❌ Not configured"
        print(f"Perplexity:    {perplexity_status}")
        
        # OpenRouter status
        openrouter_status = "✅ Configured" if self.is_openrouter_configured() else "❌ Not configured"
        print(f"OpenRouter:    {openrouter_status}")
        if self.is_openrouter_configured():
            openrouter_config = self.get_openrouter_config()
            if openrouter_config.get('site_url'):
                print(f"   Site URL:   {openrouter_config.get('site_url')}")
            if openrouter_config.get('site_name'):
                print(f"   Site Name:  {openrouter_config.get('site_name')}")
        
        # GitHub status
        github_status = "✅ Configured" if self.is_github_configured() else "❌ Not configured"
        print(f"GitHub:        {github_status}")
        
        print(f"\nConfig File:   {self.config_file}")
        
        # Show next steps
        unconfigured_services = []
        if not self.is_jira_configured():
            unconfigured_services.append("JIRA")
        if not self.is_perplexity_configured():
            unconfigured_services.append("Perplexity")
        if not self.is_openrouter_configured():
            unconfigured_services.append("OpenRouter")
        if not self.is_github_configured():
            unconfigured_services.append("GitHub")
        
        if unconfigured_services:
            print("\n💡 Next steps:")
            if "JIRA" in unconfigured_services:
                print("   - Configure JIRA: python config.py configure --jira")
            if "Perplexity" in unconfigured_services:
                print("   - Configure Perplexity: python config.py configure --perplexity")
            if "OpenRouter" in unconfigured_services:
                print("   - Configure OpenRouter: python config.py configure --openrouter")
            if "GitHub" in unconfigured_services:
                print("   - Configure GitHub: python config.py configure --github")
            print(f"   - Edit config directly: {self.config_file}")
    
    def show_sample_config(self):
        """Show sample configuration format"""
        sample = '''# Agent Flows Configuration
# Edit this file with your actual credentials

[jira]
base_url = "https://your-company.atlassian.net"
username = "your.email@company.com"
api_token = "your_jira_api_token_here"
project_key = "PROJ"  # Optional default project

[perplexity]
api_key = "your_perplexity_api_key_here"

[openrouter]
api_key = "your_openrouter_api_key_here"
site_url = "https://github.com/yourusername/yourproject"
site_name = "Your Project Name"

[github]
token = "your_github_token_here"
'''
        print("📝 Sample Configuration Format:")
        print(sample)
        
        if input("Create this sample config file? (y/N): ").lower().startswith('y'):
            self._create_sample_config()
    
    def reset_configuration(self, service: Optional[str] = None):
        """Reset configuration for a service or all services"""
        config_data = self._load_config()
        
        if service and service in config_data:
            config_data.pop(service, None)
            self._save_config(config_data)
            print(f"✅ {service.title()} configuration removed")
        elif service is None:
            self.config_file.unlink(missing_ok=True)
            print("✅ All configuration removed")
        else:
            print(f"❌ Service '{service}' not found in configuration")


def main():
    """CLI interface for configuration management"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Agent Flows Configuration Management")
    parser.add_argument("command", nargs='?', default="configure",
                       choices=["configure", "show", "reset", "sample"], 
                       help="Configuration command")
    parser.add_argument("--jira", action="store_true", 
                       help="Configure only JIRA")
    parser.add_argument("--perplexity", action="store_true", 
                       help="Configure only Perplexity")
    parser.add_argument("--openrouter", action="store_true", 
                       help="Configure only OpenRouter")
    parser.add_argument("--github", action="store_true", 
                       help="Configure only GitHub")
    parser.add_argument("--service", choices=["jira", "perplexity", "openrouter", "github"],
                       help="Reset specific service (for reset command)")
    
    args = parser.parse_args()
    
    config = AgentFlowsConfig()
    
    if args.command == "configure":
        if args.jira:
            config.configure_jira_interactive()
        elif args.perplexity:
            config.configure_perplexity_interactive()
        elif args.openrouter:
            config.configure_openrouter_interactive()
        elif args.github:
            config.configure_github_interactive()
        else:
            config.configure_interactive()
    elif args.command == "show":
        config.show_status()
    elif args.command == "sample":
        config.show_sample_config()
    elif args.command == "reset":
        service = args.service
        if service:
            confirm = input(f"Are you sure you want to reset {service} configuration? (y/N): ")
        else:
            confirm = input("Are you sure you want to reset ALL configuration? (y/N): ")
        
        if confirm.lower().startswith('y'):
            config.reset_configuration(service)
        else:
            print("❌ Reset cancelled")


if __name__ == "__main__":
    main()