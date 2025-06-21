#!/bin/bash
# Quick Security Update - One-liner script for adding security features
# Usage: curl -fsSL https://raw.githubusercontent.com/Anthropic/AgenticScrum/main/scripts/quick-security-update.sh | bash

set -euo pipefail

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_info() { echo -e "${YELLOW}ℹ️  $1${NC}"; }
print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }

print_info "AgenticScrum Quick Security Update"

# Check if we're in an AgenticScrum project
if [[ ! -f "agentic_config.yaml" ]] && [[ ! -f "init.sh" ]]; then
    print_error "Not in an AgenticScrum project directory"
    exit 1
fi

# Download and run main updater
GITHUB_RAW_URL="https://raw.githubusercontent.com/safer-strategy/AgenticScrum/refs/heads/main"

if curl -fsSL "${GITHUB_RAW_URL}/download-patch-updates.sh" | bash -s security-update; then
    print_success "Security features added successfully!"
else
    print_error "Security update failed"
    exit 1
fi