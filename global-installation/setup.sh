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
chmod +x "$INSTALL_DIR/bin/research"

# Create Python virtual environment
echo -e "${BLUE}🐍 Creating Python virtual environment...${NC}"
cd "$INSTALL_DIR"
python3 -m venv .venv

# Activate virtual environment and install dependencies
echo -e "${BLUE}📦 Installing Python dependencies...${NC}"
source .venv/bin/activate

# Install required packages
pip install --upgrade pip
pip install pydantic python-dotenv

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
echo "2. Test the installation: research --help"
echo "3. Run your first research: research \"Your research topic here\""
echo
echo -e "${BLUE}📝 Optional:${NC}"
echo "- Set PERPLEXITY_API_KEY environment variable for enhanced research capabilities"
echo "- Add it to your shell profile: echo 'export PERPLEXITY_API_KEY=your_key_here' >> ~/.bashrc"
echo
echo -e "${GREEN}✨ Happy researching!${NC}"