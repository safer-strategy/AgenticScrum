#!/bin/bash
# Quick Patcher Install - One-liner script for installing standalone patcher
# Usage: curl -fsSL https://raw.githubusercontent.com/Anthropic/AgenticScrum/main/scripts/quick-install-patcher.sh | bash

set -euo pipefail

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() { echo -e "${YELLOW}ℹ️  $1${NC}"; }
print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_header() { echo -e "${BLUE}🔧 $1${NC}"; }

print_header "AgenticScrum Standalone Patcher Installer"

# Create installation directory
INSTALL_DIR="$HOME/.local/bin"
mkdir -p "$INSTALL_DIR"

# Download standalone patcher
GITHUB_RAW_URL="https://raw.githubusercontent.com/safer-strategy/AgenticScrum/refs/heads/main"

print_info "Downloading standalone patcher..."

if curl -fsSL "${GITHUB_RAW_URL}/scripts/agentic-patch" -o "$INSTALL_DIR/agentic-patch"; then
    chmod +x "$INSTALL_DIR/agentic-patch"
    print_success "Installed agentic-patch to $INSTALL_DIR"
    
    # Check if in PATH
    if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
        print_info "Add $INSTALL_DIR to your PATH to use agentic-patch globally"
        print_info "Add this to your shell profile (.bashrc, .zshrc, etc.):"
        echo "  export PATH=\"\$PATH:$INSTALL_DIR\""
        echo
    fi
    
    print_success "Installation complete!"
    print_info "Usage: agentic-patch <operation>"
    print_info "Try: agentic-patch --help"
    
else
    print_error "Failed to download standalone patcher"
    exit 1
fi