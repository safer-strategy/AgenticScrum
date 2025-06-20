"""Init.sh Updater - High-level utility for updating init.sh files."""

from pathlib import Path
from typing import List, Dict, Optional, Tuple
from .init_sh_parser import InitShParser


class InitShUpdater:
    """High-level utility for updating init.sh files with new commands."""
    
    def __init__(self, init_sh_path: Path):
        self.path = init_sh_path
        self.content = init_sh_path.read_text()
        self.parser = InitShParser(self.content)
        self.modified = False
    
    def add_patch_commands(self) -> List[str]:
        """Add patching-related commands to init.sh."""
        updates = []
        
        # Add patch functions
        if not self.parser.function_exists('handle_patch_command'):
            if self.parser.add_function('handle_patch_command', [
                'local patch_cmd="$1"',
                'shift',
                '',
                '# Use the agentic-patch script if available',
                'if command -v agentic-patch &> /dev/null; then',
                '  agentic-patch "$patch_cmd" "$@"',
                'elif [[ -f "$(dirname "$0")/scripts/agentic-patch" ]]; then',
                '  "$(dirname "$0")/scripts/agentic-patch" "$patch_cmd" "$@"',
                'else',
                '  error "agentic-patch script not found"',
                '  info "Install with: pip install agentic-scrum-setup"',
                '  exit 1',
                'fi'
            ]):
                self.modified = True
                updates.append("Added handle_patch_command function")
        
        # Add patch cases
        if not self.parser.case_exists('patch'):
            # Try to add after 'quick', but if that doesn't exist, add after 'test'
            after_case = 'quick' if self.parser.case_exists('quick') else 'test'
            if self.parser.add_case('patch', [
                '# Framework patching operations',
                'shift',
                'handle_patch_command "$@"'
            ], after_case=after_case):
                self.modified = True
                updates.append("Added 'patch' command")
        
        if not self.parser.case_exists('patch-status'):
            if self.parser.add_case('patch-status', [
                '# Quick patch status check',
                'handle_patch_command status'
            ], after_case='patch'):
                self.modified = True
                updates.append("Added 'patch-status' command")
        
        return updates
    
    def add_agent_commands(self) -> List[str]:
        """Add background agent commands to init.sh."""
        updates = []
        
        # Add agent functions
        if not self.parser.function_exists('manage_background_agents'):
            if self.parser.add_function('manage_background_agents', [
                'local cmd="${1:-help}"',
                'shift || true',
                '',
                'case "$cmd" in',
                '  list)',
                '    info "Listing background agents..."',
                '    if command -v mcp &> /dev/null; then',
                '      mcp call agent_monitor list_agents',
                '    else',
                '      warn "MCP CLI not available - install @modelcontextprotocol/cli"',
                '    fi',
                '    ;;',
                '  queue)',
                '    info "Queue management..."',
                '    if command -v mcp &> /dev/null; then',
                '      mcp call agent_queue get_queue_stats',
                '    else',
                '      warn "MCP CLI not available"',
                '    fi',
                '    ;;',
                '  logs)',
                '    info "Recent agent logs:"',
                '    if [[ -d "logs/background_agents" ]]; then',
                '      find logs/background_agents -name "*.log" -mtime -1 -exec basename {} \\; | sort',
                '    else',
                '      warn "No background agent logs found"',
                '    fi',
                '    ;;',
                '  help|*)',
                '    info "Background agent commands:"',
                '    info "  list  - List active agents"',
                '    info "  queue - Show queue statistics"',
                '    info "  logs  - Show recent log files"',
                '    ;;',
                'esac'
            ]):
                self.modified = True
                updates.append("Added manage_background_agents function")
        
        if not self.parser.function_exists('run_background_agent'):
            if self.parser.add_function('run_background_agent', [
                'local agent_type="$1"',
                'local story_id="$2"',
                'local prompt="$3"',
                '',
                'if [[ -z "$agent_type" || -z "$story_id" ]]; then',
                '  error "Usage: $0 agent-run <agent_type> <story_id> [prompt]"',
                '  info "Agent types: deva_python, deva_typescript, qaa, etc."',
                '  exit 1',
                'fi',
                '',
                'local runner_script="scripts/run_background_agent.sh"',
                'if [[ -f "$runner_script" ]]; then',
                '  info "Starting background agent: $agent_type for story $story_id"',
                '  "$runner_script" "$agent_type" "$story_id" "$prompt"',
                'else',
                '  error "Background agent runner not found at $runner_script"',
                '  info "Run \'./init.sh patch add-background-agents\' to install"',
                '  exit 1',
                'fi'
            ]):
                self.modified = True
                updates.append("Added run_background_agent function")
        
        if not self.parser.function_exists('show_agent_status'):
            if self.parser.add_function('show_agent_status', [
                'info "🤖 Background Agent Status"',
                'echo',
                '',
                '# Check if MCP servers are running',
                'if command -v docker-compose &> /dev/null; then',
                '  info "MCP Servers:"',
                '  docker-compose ps 2>/dev/null | grep -E "agent_queue|agent_monitor|agent_permissions" || echo "  No agent MCP servers running"',
                '  echo',
                'fi',
                '',
                '# Check for active agents',
                'if [[ -d "logs/background_agents" ]]; then',
                '  local active_count=$(find logs/background_agents -name "*.log" -mmin -5 2>/dev/null | wc -l)',
                '  local total_count=$(find logs/background_agents -name "*.log" 2>/dev/null | wc -l)',
                '  info "Agent Activity:"',
                '  echo "  Active (last 5 min): $active_count"',
                '  echo "  Total log files: $total_count"',
                'else',
                '  info "No background agent logs directory found"',
                'fi',
                '',
                'echo',
                'info "Use \'./init.sh agent list\' for detailed information"'
            ]):
                self.modified = True
                updates.append("Added show_agent_status function")
        
        # Add agent cases
        if not self.parser.case_exists('agent'):
            if self.parser.add_case('agent', [
                '# Background agent management',
                'shift',
                'manage_background_agents "$@"'
            ], after_case='patch-status'):
                self.modified = True
                updates.append("Added 'agent' command")
        
        if not self.parser.case_exists('agent-run'):
            if self.parser.add_case('agent-run', [
                '# Run a specific story in background',
                'shift',
                'run_background_agent "$@"'
            ], after_case='agent'):
                self.modified = True
                updates.append("Added 'agent-run' command")
        
        if not self.parser.case_exists('agent-status'):
            if self.parser.add_case('agent-status', [
                '# Quick agent status check',
                'show_agent_status'
            ], after_case='agent-run'):
                self.modified = True
                updates.append("Added 'agent-status' command")
        
        return updates
    
    def add_docker_commands(self) -> List[str]:
        """Add Docker/MCP management commands."""
        updates = []
        
        # Add docker functions if not present
        if not self.parser.function_exists('start_services'):
            if self.parser.add_function('start_services', [
                'info "Starting development services..."',
                'if [[ -f "docker-compose.yml" ]]; then',
                '  docker-compose up -d',
                'else',
                '  warn "No docker-compose.yml found"',
                'fi'
            ]):
                self.modified = True
                updates.append("Added start_services function")
        
        if not self.parser.function_exists('stop_services'):
            if self.parser.add_function('stop_services', [
                'info "Stopping development services..."',
                'if [[ -f "docker-compose.yml" ]]; then',
                '  docker-compose down',
                'else',
                '  warn "No docker-compose.yml found"',
                'fi'
            ]):
                self.modified = True
                updates.append("Added stop_services function")
        
        # Add docker cases
        if not self.parser.case_exists('up'):
            # Add after agent-status if it exists, otherwise after test
            after_case = 'agent-status' if self.parser.case_exists('agent-status') else 'test'
            if self.parser.add_case('up', [
                '# Start development services',
                'start_services'
            ], after_case=after_case):
                self.modified = True
                updates.append("Added 'up' command")
        
        if not self.parser.case_exists('down'):
            if self.parser.add_case('down', [
                '# Stop development services',
                'stop_services'
            ], after_case='up'):
                self.modified = True
                updates.append("Added 'down' command")
        
        return updates
    
    def ensure_helper_functions(self) -> List[str]:
        """Ensure helper functions like info, warn, error exist."""
        updates = []
        
        if not self.parser.function_exists('info'):
            if self.parser.add_function('info', [
                'echo -e "\\033[0;36m$*\\033[0m"'
            ], before_marker="# --- Main Functions ---"):
                self.modified = True
                updates.append("Added info function")
        
        if not self.parser.function_exists('warn'):
            if self.parser.add_function('warn', [
                'echo -e "\\033[0;33m⚠️  $*\\033[0m"'
            ], before_marker="# --- Main Functions ---"):
                self.modified = True
                updates.append("Added warn function")
        
        if not self.parser.function_exists('error'):
            if self.parser.add_function('error', [
                'echo -e "\\033[0;31m❌ $*\\033[0m" >&2'
            ], before_marker="# --- Main Functions ---"):
                self.modified = True
                updates.append("Added error function")
        
        if not self.parser.function_exists('success'):
            if self.parser.add_function('success', [
                'echo -e "\\033[0;32m✅ $*\\033[0m"'
            ], before_marker="# --- Main Functions ---"):
                self.modified = True
                updates.append("Added success function")
        
        return updates
    
    def save(self) -> bool:
        """Save the updated init.sh if modified."""
        if self.modified:
            self.path.write_text(self.parser.get_content())
            # Ensure executable
            self.path.chmod(0o755)
            return True
        return False
    
    def update_all(self) -> Tuple[bool, List[str]]:
        """Apply all standard updates to init.sh."""
        all_updates = []
        
        # Ensure helper functions first
        all_updates.extend(self.ensure_helper_functions())
        
        # Add all command categories
        all_updates.extend(self.add_patch_commands())
        all_updates.extend(self.add_agent_commands())
        all_updates.extend(self.add_docker_commands())
        
        # Only save if we actually made updates
        if all_updates:
            saved = self.save()
        else:
            saved = False
        
        return saved, all_updates