#!/bin/bash
# Setup script for global agent-flows installation

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Setting up Agent Flows Global Installation${NC}"

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Default installation directory
INSTALL_DIR="$HOME/.agent-flows"

# Check if installation directory already exists
if [ -d "$INSTALL_DIR" ]; then
    echo -e "${YELLOW}⚠️  Installation directory $INSTALL_DIR already exists.${NC}"
    
    # Backup existing config.toml if it exists
    CONFIG_BACKUP=""
    if [ -f "$INSTALL_DIR/config.toml" ]; then
        CONFIG_BACKUP="/tmp/agent-flows-config-backup-$(date +%s).toml"
        cp "$INSTALL_DIR/config.toml" "$CONFIG_BACKUP"
        echo -e "${BLUE}📋 Backed up existing config.toml to $CONFIG_BACKUP${NC}"
    fi
    
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${RED}❌ Installation cancelled.${NC}"
        exit 1
    fi
    rm -rf "$INSTALL_DIR"
fi

# Create installation directory
echo -e "${BLUE}📁 Creating installation directory at $INSTALL_DIR${NC}"
mkdir -p "$INSTALL_DIR"

# Copy project files to installation directory
echo -e "${BLUE}📋 Copying project files...${NC}"
cp -r "$PROJECT_DIR"/* "$INSTALL_DIR/"

# Create bin directory for wrapper scripts
mkdir -p "$INSTALL_DIR/bin"

# Copy wrapper scripts
echo -e "${BLUE}📜 Installing wrapper scripts...${NC}"
cp "$SCRIPT_DIR/research" "$INSTALL_DIR/bin/"
cp "$SCRIPT_DIR/review" "$INSTALL_DIR/bin/"
cp "$SCRIPT_DIR/jira_task" "$INSTALL_DIR/bin/"
cp "$SCRIPT_DIR/configure" "$INSTALL_DIR/bin/"
chmod +x "$INSTALL_DIR/bin/research"
chmod +x "$INSTALL_DIR/bin/review"
chmod +x "$INSTALL_DIR/bin/jira_task"
chmod +x "$INSTALL_DIR/bin/configure"

# Create Python virtual environment
echo -e "${BLUE}🐍 Creating Python virtual environment...${NC}"
cd "$INSTALL_DIR"
python3 -m venv .venv

# Activate virtual environment and install dependencies
echo -e "${BLUE}📦 Installing Python dependencies...${NC}"
source .venv/bin/activate

# Install required packages
pip install --upgrade pip
pip install pydantic python-dotenv tomli tomli-w requests

# Restore config.toml if it was backed up
if [ -n "$CONFIG_BACKUP" ] && [ -f "$CONFIG_BACKUP" ]; then
    echo
    echo -e "${BLUE}🔧 Previous configuration file found${NC}"
    read -p "Do you want to restore your previous config.toml? (Y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        cp "$CONFIG_BACKUP" "$INSTALL_DIR/config.toml"
        echo -e "${GREEN}✅ Restored existing config.toml${NC}"
    else
        echo -e "${YELLOW}⚠️  Previous config.toml not restored. You'll need to reconfigure.${NC}"
    fi
    rm "$CONFIG_BACKUP"
fi

echo -e "${BLUE}🔗 Setting up PATH...${NC}"

# Check if ~/.bashrc exists and add to PATH
if [ -f "$HOME/.bashrc" ]; then
    if ! grep -q "$INSTALL_DIR/bin" "$HOME/.bashrc"; then
        echo "export PATH=\"$INSTALL_DIR/bin:\$PATH\"" >> "$HOME/.bashrc"
        echo -e "${GREEN}✅ Added $INSTALL_DIR/bin to PATH in ~/.bashrc${NC}"
    else
        echo -e "${YELLOW}⚠️  PATH already contains $INSTALL_DIR/bin in ~/.bashrc${NC}"
    fi
fi

# Check if ~/.zshrc exists and add to PATH
if [ -f "$HOME/.zshrc" ]; then
    if ! grep -q "$INSTALL_DIR/bin" "$HOME/.zshrc"; then
        echo "export PATH=\"$INSTALL_DIR/bin:\$PATH\"" >> "$HOME/.zshrc"
        echo -e "${GREEN}✅ Added $INSTALL_DIR/bin to PATH in ~/.zshrc${NC}"
    else
        echo -e "${YELLOW}⚠️  PATH already contains $INSTALL_DIR/bin in ~/.zshrc${NC}"
    fi
fi

# Check if ~/.bash_profile exists and add to PATH
if [ -f "$HOME/.bash_profile" ]; then
    if ! grep -q "$INSTALL_DIR/bin" "$HOME/.bash_profile"; then
        echo "export PATH=\"$INSTALL_DIR/bin:\$PATH\"" >> "$HOME/.bash_profile"
        echo -e "${GREEN}✅ Added $INSTALL_DIR/bin to PATH in ~/.bash_profile${NC}"
    else
        echo -e "${YELLOW}⚠️  PATH already contains $INSTALL_DIR/bin in ~/.bash_profile${NC}"
    fi
fi

echo -e "${GREEN}🎉 Installation complete!${NC}"
echo
echo -e "${BLUE}📋 Next steps:${NC}"
echo "1. Restart your terminal or run: source ~/.bashrc (or ~/.zshrc)"
echo "2. Configure your services: configure"
echo "3. Test the installation: research --help && review --help && jira_task --help"
echo "4. Run your first research: research \"Your research topic here\""
echo "5. Review a PR: review 123 --repository owner/repo"
echo "6. Work on a JIRA issue: jira_task PROJ-123"
echo
echo -e "${BLUE}📝 Configuration:${NC}"
echo "All service credentials are now managed through the unified config system:"
echo "- Run 'configure' to set up JIRA and Perplexity API keys"
echo "- Config is stored in ~/.agent-flows/config.toml"
echo "- You can edit the TOML file directly or use the interactive setup"
echo
echo -e "${GREEN}✨ Happy researching!${NC}"