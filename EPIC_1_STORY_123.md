### **User Story Draft**

# Story 123: Configure Advanced DeveloperAgent Persona and Environment

**Epic:** 01 - AgenticScrum Core Configuration
**Story Points:** 3
**Priority:** P1 (High - Enables best-practice integration for a key AI model and local environment)
**Status:** Done
**Assigned To:** [Developer Name]
**Created:** 2025-06-13
**Last Update:** 2025-06-13 20:47

## 📋 User Story

**As a** Developer using the AgenticScrum framework, **I want** the setup utility to generate a specialized `DeveloperAgent` persona for Anthropic's Claude Code **and** a themed, idempotent `init.sh` script for environment management, **so that** I can leverage best practices for both AI interaction and local Docker-based development right from project initialization.

## 🎯 Acceptance Criteria

### Persona & Configuration Generation
- [x] **Claude Agent Scaffolding**: When initializing a project with a Claude developer agent (e.g., `... --agents deva_claude_python`), the utility MUST create a dedicated directory under `agents/developer_agent/claude_python_expert/`.
- [x] [cite_start]**`CLAUDE.md` Generation**: The utility MUST generate a `CLAUDE.md` file in the project's root directory. [cite: 1]
- [x] [cite_start]**Persona Rules Update**: The generated `persona_rules.yaml` for the Claude agent MUST include a specific rule instructing it to always consult the root `CLAUDE.md` file. [cite: 1]
- [x] [cite_start]**MCP Configuration**: The utility MUST generate a template `.mcp.json` file in the project root to configure Model Context Protocol servers. [cite: 1]

### **Environment Scripting (New)**
- [x] **`init.sh` Generation**: The utility MUST generate a themed `init.sh` script in the project's root directory.
- [x] **Executable Permissions**: The generated `init.sh` script MUST have execute permissions set (`chmod +x`).
- [x] **Variable Project Name**: The `init.sh` script MUST use the project name provided during setup as a shell variable for display purposes.
- [x] **Idempotent Actions**: The script's actions (e.g., starting services) MUST be idempotent.
- [x] **`docker-compose.yml` Generation**: The utility MUST generate a placeholder `docker-compose.yml` file in the root directory that the `init.sh` script can use.

### Documentation & Multi-Agent Workflow
- [x] [cite_start]**Multi-Agent Guide**: A section MUST be added to the root `README.md` explaining how to run multiple Claude agents concurrently using techniques like `git worktree`. [cite: 1]

## 🔧 Technical Implementation Details

### Required Changes

#### 1. Update CLI and Agent Logic
**(No changes from previous version)**

#### 2. Create Claude-Specific Templates
**(Adds two new templates for the init script and Docker Compose)**

**[New File Template]:** `templates/common/docker-compose.yml.j2`
```yaml
# docker-compose.yml
# Placeholder for project services.
# The init.sh script uses this file to manage the development environment.

version: '3.8'

services:
  app:
    build: .
    container_name: {{ project_name | lower | replace(' ', '_') }}_app
    ports:
      - "8000:8000" # Example port mapping
    volumes:
      - ./src:/app/src # Mount your source code
    # command: python src/main.py # Example command
```

**[New File Template]:** `templates/common/init.sh.j2`
```bash
#!/bin/bash

# -----------------------------------------------------------------------------
# Init Script for the '{{ project_name }}' project
#
# This script provides a centralized place to manage the development
# environment, including Docker services, testing, and other utilities.
# -----------------------------------------------------------------------------

# --- Configuration ---
PROJECT_NAME="{{ project_name }}"

# --- Theme & Colors ---
C_RESET='\033[0m'
C_BLACK='\033[0;30m'
C_RED='\033[0;31m'
C_GREEN='\033[0;32m'
C_YELLOW='\033[0;33m'
C_BLUE='\033[0;34m'
C_PURPLE='\033[0;35m'
C_CYAN='\033[0;36m'
C_WHITE='\033[0;37m'
C_BOLD='\033[1m'

# --- Helper Functions ---
function header() {
  echo -e "${C_PURPLE}${C_BOLD}"
  echo "    ___    __  __   ____   _____   ____    ___    _   _ "
  echo "   / __|  |  \/  | |  _ \  | ____| |  _ \  / __|  | | | |"
  echo "  | |     | |\/| | | |_) | |  _|   | |_) | \_ \  | |_| |"
  echo "  | |___  | |  | | |  __/  | |___  |  _ <  |___/  |  _  |"
  echo "   \___|  |_|  |_| |_|     |_____| |_| \_\ ____/  |_| |_|"
  echo ""
  echo -e "      >> Welcome to the ${PROJECT_NAME} Environment Manager <<      "
  echo -e "${C_RESET}"
}

function info() {
  echo -e "${C_BLUE}${C_BOLD}INFO:${C_RESET} $1"
}

function success() {
  echo -e "${C_GREEN}${C_BOLD}SUCCESS:${C_RESET} $1"
}

function error() {
  echo -e "${C_RED}${C_BOLD}ERROR:${C_RESET} $1"
}

# --- Core Functions ---
function start_services() {
  info "Starting Docker services in detached mode..."
  if docker-compose up -d --build; then
    success "Services are up and running."
  else
    error "Failed to start Docker services."
    exit 1
  fi
}

function stop_services() {
  info "Stopping Docker services..."
  if docker-compose down; then
    success "Services have been stopped."
  else
    error "Failed to stop Docker services."
  fi
}

function show_logs() {
  info "Tailing logs for all services. Press Ctrl+C to exit."
  docker-compose logs -f
}

function run_tests() {
  info "Running tests inside the app container..."
  # Modify 'app' and the test command as needed
  if docker-compose exec app pytest; then
    success "All tests passed."
  else
    error "Tests failed."
  fi
}

function show_help() {
  header
  echo "Usage: ./init.sh [command]"
  echo ""
  echo "Commands:"
  echo -e "  ${C_YELLOW}up${C_RESET}         - Build and start all Docker services."
  echo -e "  ${C_YELLOW}down${C_RESET}       - Stop and remove all Docker services."
  echo -e "  ${C_YELLOW}logs${C_RESET}       - Tail the logs from all running services."
  echo -e "  ${C_YELLOW}test${C_RESET}       - Run the test suite within the Docker container."
  echo -e "  ${C_YELLOW}help${C_RESET}       - Show this help message."
  echo ""
}

# --- Main Dispatcher ---
function main() {
  case "$1" in
    up)
      start_services
      ;;
    down)
      stop_services
      ;;
    logs)
      show_logs
      ;;
    test)
      run_tests
      ;;
    help|*)
      show_help
      ;;
  esac
}

main "$@"

```

### File Modification Plan

#### Primary Files to Modify:
1.  **`[path/to/setup_utility_core.py]`**
    - Add logic to generate `init.sh` and `docker-compose.yml` from templates.
    - Add a step to `chmod +x` the generated `init.sh` file.

#### New Template Files to Create:
**(List now includes 6 new templates)**
2.  `templates/claude/CLAUDE.md.j2`
3.  `templates/claude/.mcp.json.j2`
4.  `templates/claude/persona_rules.yaml.j2`
5.  `templates/claude/README_addition.md.j2`
6.  **`templates/common/docker-compose.yml.j2`**
7.  **`templates/common/init.sh.j2`**

### Testing Requirements

#### Unit Tests:
- [x] **(New)** Verify `init.sh` is generated with executable permissions.
- [x] **(New)** Verify the project name variable in `init.sh` matches the input.
- [x] **(New)** Verify `docker-compose.yml` is generated with the correct project name in the container name.

#### Integration Tests:
- [x] Run the `init` command end-to-end and inspect the full generated project to ensure all files (`init.sh`, `docker-compose.yml`, Claude-specific files) are present and correctly configured.

#### Manual Testing Scenarios:
- [x] Initialize a project, navigate into the directory, and run `./init.sh help` to confirm the themed output works.
- [ ] Run `./init.sh up` and `./init.sh down` to test the Docker commands (assuming Docker is installed).