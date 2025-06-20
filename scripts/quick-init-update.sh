#!/bin/bash
# Quick Init.sh Update - One-liner script for updating init.sh
# Usage: curl -fsSL https://raw.githubusercontent.com/Anthropic/AgenticScrum/main/scripts/quick-init-update.sh | bash

set -euo pipefail

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_info() { echo -e "${YELLOW}ℹ️  $1${NC}"; }
print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }

print_info "AgenticScrum Quick Init.sh Update"

# Check if we're in the right place
if [[ ! -f "init.sh" ]]; then
    print_error "init.sh not found - are you in an AgenticScrum project directory?"
    exit 1
fi

# Download and run main updater
GITHUB_RAW_URL="https://raw.githubusercontent.com/Anthropic/AgenticScrum/main"

if curl -fsSL "${GITHUB_RAW_URL}/download-patch-updates.sh" | bash -s init-sh-update; then
    print_success "Init.sh updated successfully!"
else
    print_error "Update failed"
    exit 1
fi