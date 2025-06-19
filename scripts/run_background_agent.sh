#!/bin/bash

# AgenticScrum Background Agent Runner
# Uses Claude Code SDK to execute agent tasks autonomously
# Usage: ./run_background_agent.sh <agent_type> <story_id> <story_prompt>

set -euo pipefail

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOGS_DIR="$PROJECT_ROOT/logs/background_agents"
SESSIONS_DIR="$PROJECT_ROOT/.claude_sessions"
WORK_DIR="$PROJECT_ROOT/background_work"

# Validate arguments
if [ $# -lt 3 ]; then
    echo -e "${RED}Error: Insufficient arguments${NC}"
    echo "Usage: $0 <agent_type> <story_id> <story_prompt>"
    echo "Example: $0 deva_python STORY_318 'Implement the core background agent system'"
    exit 1
fi

AGENT_TYPE="$1"
STORY_ID="$2"
STORY_PROMPT="$3"

# Validate agent type exists
AGENT_DIR="$PROJECT_ROOT/agents/$AGENT_TYPE"
if [ ! -d "$AGENT_DIR" ]; then
    echo -e "${RED}Error: Agent type '$AGENT_TYPE' not found${NC}"
    echo "Available agents:"
    ls -1 "$PROJECT_ROOT/agents/" | grep -E '^(poa|sma|deva_|qaa|saa)' | sort
    exit 1
fi

# Create necessary directories
mkdir -p "$LOGS_DIR"
mkdir -p "$SESSIONS_DIR/$AGENT_TYPE"
mkdir -p "$WORK_DIR/$AGENT_TYPE"

# Generate unique session ID
SESSION_ID="${AGENT_TYPE}_${STORY_ID}_$(date +%Y%m%d_%H%M%S)"
LOG_FILE="$LOGS_DIR/${SESSION_ID}.log"
PID_FILE="$LOGS_DIR/${SESSION_ID}.pid"

# Load environment variables if .env exists
if [ -f "$PROJECT_ROOT/.env" ]; then
    set -a
    source "$PROJECT_ROOT/.env"
    set +a
fi

# Extract agent persona from YAML file
extract_agent_persona() {
    local persona_file="$AGENT_DIR/persona_rules.yaml"
    
    if [ ! -f "$persona_file" ]; then
        echo -e "${RED}Error: Persona file not found for $AGENT_TYPE${NC}"
        exit 1
    fi
    
    # Build system prompt from persona components
    local role=$(grep -A10 "^role:" "$persona_file" | head -20 | sed 's/^  //')
    local capabilities=$(grep -A20 "^capabilities:" "$persona_file" | grep "^  -" | sed 's/^  - /- /')
    local rules=$(grep -A50 "^rules:" "$persona_file" | grep "^  -" | sed 's/^  - /- /')
    
    cat <<EOF
You are operating as the $AGENT_TYPE agent for the AgenticScrum project.

$role

Your capabilities include:
$capabilities

You must follow these rules:
$rules

You are working autonomously on $STORY_ID. Focus on completing the story requirements without user interaction.
Remember to:
- Store successful patterns in your agent memory
- Query your memory for relevant past experiences
- Use MCP services for all operations
- Make decisions autonomously using the permission handler
- Document your work as you progress
EOF
}

# Set resource limits for security
set_resource_limits() {
    # CPU time limit (10 minutes)
    ulimit -t 600
    
    # Virtual memory limit (1GB)
    ulimit -v 1048576
    
    # File descriptor limit
    ulimit -n 256
    
    # Core dump size (disabled)
    ulimit -c 0
}

# Build allowed tools list based on agent type
get_allowed_tools() {
    local base_tools="Read,Write,Edit,MultiEdit,Bash,Glob,Grep,LS"
    local mcp_tools="mcp__memory__*,mcp__datetime__*,mcp__filesystem__*"
    local agent_tools="mcp__agent_queue__*,mcp__agent_monitor__*"
    
    # Add agent-specific tools
    case "$AGENT_TYPE" in
        deva_*)
            echo "$base_tools,$mcp_tools,$agent_tools,NotebookRead,NotebookEdit"
            ;;
        sma)
            echo "$base_tools,$mcp_tools,$agent_tools,TodoRead,TodoWrite"
            ;;
        qaa)
            echo "$base_tools,$mcp_tools,$agent_tools,WebSearch"
            ;;
        *)
            echo "$base_tools,$mcp_tools,$agent_tools"
            ;;
    esac
}

# Log start of execution
log_message() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"
}

# Signal handler for cleanup
cleanup() {
    local exit_code=$?
    log_message "INFO" "Background agent terminating (exit code: $exit_code)"
    
    # Remove PID file
    rm -f "$PID_FILE"
    
    # Update task status in queue
    if command -v claude >/dev/null 2>&1; then
        claude -p "Update task $STORY_ID status to completed with exit code $exit_code" \
            --allowedTools "mcp__agent_queue__update_task_status" \
            --output-format json \
            2>/dev/null || true
    fi
    
    exit $exit_code
}

trap cleanup EXIT INT TERM

# Main execution
main() {
    log_message "INFO" "${GREEN}Starting background agent execution${NC}"
    log_message "INFO" "Agent Type: $AGENT_TYPE"
    log_message "INFO" "Story ID: $STORY_ID"
    log_message "INFO" "Session ID: $SESSION_ID"
    log_message "INFO" "Work Directory: $WORK_DIR/$AGENT_TYPE"
    
    # Save PID for monitoring
    echo $$ > "$PID_FILE"
    
    # Extract agent persona
    log_message "INFO" "Loading agent persona..."
    AGENT_PERSONA=$(extract_agent_persona)
    
    # Set resource limits
    log_message "INFO" "Setting resource limits..."
    set_resource_limits
    
    # Get allowed tools
    ALLOWED_TOOLS=$(get_allowed_tools)
    log_message "INFO" "Allowed tools: $ALLOWED_TOOLS"
    
    # Change to work directory
    cd "$WORK_DIR/$AGENT_TYPE"
    
    # Check if MCP config exists
    MCP_CONFIG="$PROJECT_ROOT/.mcp.json"
    if [ ! -f "$MCP_CONFIG" ]; then
        log_message "WARN" "MCP configuration not found at $MCP_CONFIG"
        MCP_CONFIG=""
    else
        # Create agent-specific MCP config with additional servers
        AGENT_MCP_CONFIG="$WORK_DIR/$AGENT_TYPE/.mcp-agent.json"
        if [ -f "$PROJECT_ROOT/mcp_servers/agent_queue/server.py" ]; then
            # Merge agent-specific MCP servers with project config
            python3 -c "
import json
with open('$MCP_CONFIG', 'r') as f:
    config = json.load(f)
    
# Add agent-specific servers
config['mcpServers']['agent_queue'] = {
    'command': 'python',
    'args': ['$PROJECT_ROOT/mcp_servers/agent_queue/server.py'],
    'env': {'AGENT_ID': '$AGENT_TYPE', 'STORY_ID': '$STORY_ID'}
}
config['mcpServers']['agent_monitor'] = {
    'command': 'python',
    'args': ['$PROJECT_ROOT/mcp_servers/agent_monitor/server.py'],
    'env': {'AGENT_ID': '$AGENT_TYPE'}
}
config['mcpServers']['agent_permissions'] = {
    'command': 'python',
    'args': ['$PROJECT_ROOT/mcp_servers/agent_permissions/server.py'],
    'env': {'PERMISSION_MODE': 'autonomous', 'AGENT_ID': '$AGENT_TYPE'}
}

with open('$AGENT_MCP_CONFIG', 'w') as f:
    json.dump(config, f, indent=2)
" 2>/dev/null || cp "$MCP_CONFIG" "$AGENT_MCP_CONFIG"
            MCP_CONFIG="$AGENT_MCP_CONFIG"
        fi
    fi
    
    # Build Claude command
    CLAUDE_CMD=(
        claude -p "$STORY_PROMPT"
        --output-format stream-json
        --system-prompt "$AGENT_PERSONA"
        --append-system-prompt "Current working directory: $PWD. Project root: $PROJECT_ROOT."
        --max-turns 50
        --allowedTools "$ALLOWED_TOOLS"
        --cwd "$PROJECT_ROOT"
    )
    
    # Add MCP config if available
    if [ -n "$MCP_CONFIG" ]; then
        CLAUDE_CMD+=(--mcp-config "$MCP_CONFIG")
        
        # Add permission tool if agent permissions server exists
        if [ -f "$PROJECT_ROOT/mcp_servers/agent_permissions/server.py" ]; then
            CLAUDE_CMD+=(--permission-prompt-tool "mcp__agent_permissions__approve")
        fi
    fi
    
    log_message "INFO" "${BLUE}Executing Claude Code SDK...${NC}"
    log_message "DEBUG" "Command: ${CLAUDE_CMD[*]}"
    
    # Execute Claude with streaming output processing
    {
        "${CLAUDE_CMD[@]}" 2>&1 | while IFS= read -r line; do
            # Log the line
            echo "$line" >> "$LOG_FILE"
            
            # Parse streaming JSON for important events
            if echo "$line" | grep -q '"type":\s*"assistant"'; then
                # Extract and display assistant messages
                message=$(echo "$line" | python3 -c "
import sys, json
try:
    data = json.loads(sys.stdin.read())
    if data.get('type') == 'assistant':
                content = data.get('message', {}).get('content', '')
        if isinstance(content, list):
            for item in content:
                if item.get('type') == 'text':
                    print(item.get('text', ''))
        elif isinstance(content, str):
            print(content)
except: pass
" 2>/dev/null || echo "")
                
                if [ -n "$message" ]; then
                    log_message "AGENT" "$message"
                fi
            elif echo "$line" | grep -q '"type":\s*"result"'; then
                # Process final result
                result=$(echo "$line" | python3 -c "
import sys, json
try:
    data = json.loads(sys.stdin.read())
    if data.get('type') == 'result':
        subtype = data.get('subtype', '')
        if subtype == 'success':
            print(f\"SUCCESS: Task completed in {data.get('num_turns', 0)} turns\")
            print(f\"Duration: {data.get('duration_ms', 0)/1000:.2f}s\")
            print(f\"Cost: ${data.get('total_cost_usd', 0):.4f}\")
        else:
            print(f\"ERROR: {subtype}\")
except: pass
" 2>/dev/null || echo "")
                
                if [ -n "$result" ]; then
                    log_message "RESULT" "$result"
                fi
            fi
        done
    } || {
        exit_code=$?
        log_message "ERROR" "${RED}Claude execution failed with exit code $exit_code${NC}"
        exit $exit_code
    }
    
    log_message "INFO" "${GREEN}Background agent execution completed successfully${NC}"
}

# Run main function
main