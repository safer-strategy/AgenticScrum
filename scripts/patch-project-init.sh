#!/bin/bash

# =============================================================================
# AgenticScrum Project init.sh Patcher
# 
# This script updates an existing AgenticScrum project's init.sh file with the
# latest template from the framework, adding remote patching capabilities.
#
# Usage:
#   ./patch-project-init.sh [options]
#   
# Options:
#   --dry-run    Preview changes without applying them
#   --rollback   Restore init.sh from backup
#   --help       Show this help message
#
# Run from the root directory of an AgenticScrum project.
# =============================================================================

set -euo pipefail

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[0;33m'
readonly BLUE='\033[0;34m'
readonly CYAN='\033[0;36m'
readonly BOLD='\033[1m'
readonly RESET='\033[0m'

# Global variables
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(pwd)"
DRY_RUN=false
ROLLBACK=false
BACKUP_SUFFIX=".backup.$(date +%Y%m%d_%H%M%S)"

# Helper functions
info() {
    echo -e "${BLUE}ℹ️  INFO:${RESET} $1"
}

success() {
    echo -e "${GREEN}✅ SUCCESS:${RESET} $1"
}

warning() {
    echo -e "${YELLOW}⚠️  WARNING:${RESET} $1"
}

error() {
    echo -e "${RED}❌ ERROR:${RESET} $1"
}

header() {
    echo -e "${BOLD}${CYAN}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🔧 AgenticScrum Project init.sh Patcher"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${RESET}"
}

show_help() {
    header
    cat << EOF
${BOLD}Usage:${RESET} $0 [options]

${BOLD}Description:${RESET}
Updates an existing AgenticScrum project's init.sh file with the latest template
from the framework, adding remote patching capabilities and other improvements.

${BOLD}Options:${RESET}
  --dry-run    Preview changes without applying them
  --rollback   Restore init.sh from most recent backup
  --help       Show this help message

${BOLD}Examples:${RESET}
  $0                    # Patch current project's init.sh
  $0 --dry-run          # Preview what changes would be made
  $0 --rollback         # Restore from backup

${BOLD}Requirements:${RESET}
  - Must be run from the root directory of an AgenticScrum project
  - Project must have agentic_config.yaml file
  - AgenticScrum framework must be accessible (installed or in parent dirs)

${BOLD}Safety Features:${RESET}
  - Automatic backup creation before patching
  - Project validation before making changes
  - Rollback capability to restore previous version
  - Dry run mode to preview changes

EOF
}

find_framework_location() {
    # Try to locate AgenticScrum framework installation
    local framework_locations=(
        # Check if we're in a known framework structure
        "${SCRIPT_DIR}/.."
        # Check parent directories for framework
        "../AgenticScrum"
        "../../AgenticScrum"
        "../../../AgenticScrum"
        # Check common locations
        "$HOME/proj/AgenticScrum"
        "$HOME/Projects/AgenticScrum"
        "$HOME/AgenticScrum"
    )
    
    # First try to find via pip installation
    if command -v python3 &> /dev/null; then
        local pip_location
        pip_location=$(python3 -c "
try:
    import agentic_scrum_setup
    print(agentic_scrum_setup.__file__.replace('/__init__.py', '/../'))
except ImportError:
    pass
" 2>/dev/null)
        
        if [[ -n "$pip_location" ]] && [[ -d "$pip_location" ]]; then
            framework_locations=("$pip_location" "${framework_locations[@]}")
        fi
    fi
    
    # Check each location
    for location in "${framework_locations[@]}"; do
        local abs_path
        abs_path=$(realpath "$location" 2>/dev/null || echo "$location")
        
        if [[ -d "$abs_path" ]] && 
           [[ -f "$abs_path/agentic_scrum_setup/templates/common/init.sh.j2" ]]; then
            echo "$abs_path"
            return 0
        fi
    done
    
    return 1
}

validate_project() {
    info "Validating AgenticScrum project..."
    
    # Check if we're in a project root
    if [[ ! -f "agentic_config.yaml" ]]; then
        error "Not an AgenticScrum project directory!"
        echo "  - Missing agentic_config.yaml file"
        echo "  - Run this script from the root of an AgenticScrum project"
        return 1
    fi
    
    # Check if init.sh exists
    if [[ ! -f "init.sh" ]]; then
        error "No init.sh file found in current directory!"
        echo "  - This script patches existing init.sh files"
        echo "  - If you need to create a new init.sh, regenerate your project"
        return 1
    fi
    
    # Check if it looks like an AgenticScrum project
    if [[ ! -d "agents" ]] && [[ ! -d "src" ]] && [[ ! -d "docs" ]]; then
        warning "Directory structure doesn't match typical AgenticScrum project"
        echo "  - Expected directories: agents/, src/, docs/"
        echo "  - Continuing anyway..."
    fi
    
    success "Project validation passed"
    return 0
}

get_project_name() {
    # Extract project name from agentic_config.yaml
    if command -v python3 &> /dev/null; then
        python3 -c "
import yaml
try:
    with open('agentic_config.yaml', 'r') as f:
        config = yaml.safe_load(f)
        # Try different possible locations for project name
        name = config.get('project_name', '')
        if not name and 'project' in config:
            name = config['project'].get('name', '')
        print(name)
except Exception:
    pass
" 2>/dev/null
    else
        # Fallback: simple grep (try both flat and nested formats)
        project_name=$(grep -E "^project_name:" agentic_config.yaml 2>/dev/null | \
            sed 's/project_name: *//; s/[\"'\'']/g' | head -n1)
        
        if [[ -z "$project_name" ]]; then
            # Try nested format: project: -> name:
            project_name=$(grep -A 10 "^project:" agentic_config.yaml 2>/dev/null | \
                grep -E "^[[:space:]]*name:" | \
                sed 's/.*name: *//; s/[\"'\'']/g' | head -n1)
        fi
        
        echo "$project_name"
    fi
}

render_template() {
    local template_file="$1"
    local project_name="$2"
    local output_file="$3"
    
    info "Rendering template with project name: $project_name"
    
    # Simple template rendering (replace {{ project_name }} with actual name)
    sed "s/{{ project_name }}/$project_name/g" "$template_file" > "$output_file"
    
    # Make the output file executable
    chmod +x "$output_file"
}

create_backup() {
    local backup_file="init.sh${BACKUP_SUFFIX}"
    
    info "Creating backup: $backup_file"
    cp "init.sh" "$backup_file"
    
    echo "$backup_file"
}

find_latest_backup() {
    # Find the most recent backup file
    local latest_backup
    latest_backup=$(ls -1t init.sh.backup.* 2>/dev/null | head -n1)
    
    if [[ -n "$latest_backup" ]]; then
        echo "$latest_backup"
        return 0
    else
        return 1
    fi
}

perform_rollback() {
    header
    info "Performing rollback..."
    
    local backup_file
    if ! backup_file=$(find_latest_backup); then
        error "No backup files found!"
        echo "  - Backup files should match pattern: init.sh.backup.*"
        echo "  - Cannot rollback without a backup"
        return 1
    fi
    
    info "Found backup: $backup_file"
    
    # Confirm rollback
    echo -e "${YELLOW}This will restore init.sh from backup and overwrite current version.${RESET}"
    read -p "Continue with rollback? [y/N]: " -r
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        info "Rollback cancelled by user"
        return 0
    fi
    
    # Perform rollback
    cp "$backup_file" "init.sh"
    chmod +x "init.sh"
    
    success "Rollback completed successfully!"
    info "Restored from: $backup_file"
    
    return 0
}

perform_patch() {
    local framework_path="$1"
    local project_name="$2"
    
    info "Patching init.sh with latest template..."
    
    # First check if we can use the Python updater for more robust patching
    local python_updater="$framework_path/scripts/update-init-sh.py"
    if [[ -f "$python_updater" ]] && command -v python3 &> /dev/null; then
        info "Using enhanced Python-based updater for robust command injection..."
        
        if [[ "$DRY_RUN" == true ]]; then
            # For dry run, show what would be updated
            info "DRY RUN: Would update init.sh with latest commands"
            echo ""
            echo -e "${BOLD}Commands that would be added/updated:${RESET}"
            echo "  • patch       - Framework patching operations"
            echo "  • patch-status - Quick patch status check"
            echo "  • agent       - Background agent management"
            echo "  • agent-run   - Run stories in background"
            echo "  • agent-status - Check agent status"
            echo "  • up/down     - Docker service management"
            echo ""
            info "DRY RUN: No changes were applied"
            return 0
        fi
        
        # Create backup before Python updater runs
        local backup_file
        backup_file=$(create_backup)
        
        # Run the Python updater
        if (cd "$framework_path" && python3 "$python_updater"); then
            success "init.sh successfully updated with all latest commands!"
            info "Backup saved as: $backup_file"
        else
            error "Python updater failed, falling back to template replacement..."
            # Continue with fallback method below
        fi
    else
        # Fallback to template replacement method
        local template_file="$framework_path/agentic_scrum_setup/templates/common/init.sh.j2"
        local temp_file="/tmp/init.sh.new.$$"
        
        # Render the template
        render_template "$template_file" "$project_name" "$temp_file"
        
        if [[ "$DRY_RUN" == true ]]; then
            info "DRY RUN: Showing differences that would be applied..."
            echo ""
            echo -e "${BOLD}--- Current init.sh${RESET}"
            echo -e "${BOLD}+++ New init.sh (from template)${RESET}"
            
            if command -v diff &> /dev/null; then
                diff -u "init.sh" "$temp_file" || true
            else
                echo "Diff command not available - cannot show differences"
                echo "New file would be $(wc -l < "$temp_file") lines"
                echo "Current file is $(wc -l < "init.sh") lines"
            fi
            
            echo ""
            info "DRY RUN: No changes were applied"
            rm -f "$temp_file"
            return 0
        fi
        
        # Create backup
        local backup_file
        backup_file=$(create_backup)
        
        # Apply the patch
        mv "$temp_file" "init.sh"
        
        success "init.sh successfully replaced with latest template!"
        info "Backup saved as: $backup_file"
    fi
    
    # Show what is new
    echo ""
    echo -e "${BOLD}🎉 New features added to your init.sh:${RESET}"
    echo "  • Remote patching capabilities"
    echo "  • Framework discovery and integration"
    echo "  • Enhanced help system with patch operations"
    echo "  • Background agent execution system"
    echo "  • MCP server testing improvements"
    echo ""
    echo -e "${BOLD}Try these new commands:${RESET}"
    echo "  ./init.sh help          # See all commands including patch ops"
    echo "  ./init.sh patch-status  # Check framework patching status"
    echo "  ./init.sh patch status  # Detailed patching system info"
    echo "  ./init.sh agent-status  # Check background agent status"
    echo "  ./init.sh agent list    # List active background agents"
    
    return 0
}

check_dependencies() {
    local missing_deps=()
    
    # Check for required commands
    if ! command -v realpath &> /dev/null; then
        missing_deps+=("realpath")
    fi
    
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        error "Missing required dependencies: ${missing_deps[*]}"
        echo "Please install missing dependencies and try again"
        return 1
    fi
    
    return 0
}

main() {
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            --rollback)
                ROLLBACK=true
                shift
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            *)
                error "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done
    
    # Handle rollback early
    if [[ "$ROLLBACK" == true ]]; then
        perform_rollback
        exit $?
    fi
    
    header
    
    # Check dependencies
    if ! check_dependencies; then
        exit 1
    fi
    
    # Validate we're in an AgenticScrum project
    if ! validate_project; then
        exit 1
    fi
    
    # Find the framework
    info "Locating AgenticScrum framework..."
    local framework_path
    if ! framework_path=$(find_framework_location); then
        error "Could not locate AgenticScrum framework!"
        echo ""
        echo "The framework must be accessible in one of these ways:"
        echo "  1. Installed via pip: pip install agentic-scrum-setup"
        echo "  2. Available in a parent directory (../AgenticScrum)"
        echo "  3. Located in common development paths"
        echo ""
        echo "If you have the framework locally, you can also run:"
        echo "  /path/to/AgenticScrum/scripts/patch-project-init.sh"
        exit 1
    fi
    
    success "Found framework at: $framework_path"
    
    # Get project name
    info "Reading project configuration..."
    local project_name
    project_name=$(get_project_name)
    
    if [[ -z "$project_name" ]]; then
        error "Could not determine project name from agentic_config.yaml"
        echo "Please ensure your agentic_config.yaml contains a 'project_name' field"
        exit 1
    fi
    
    success "Project name: $project_name"
    
    # Check if template exists
    local template_file="$framework_path/agentic_scrum_setup/templates/common/init.sh.j2"
    if [[ ! -f "$template_file" ]]; then
        error "Template file not found: $template_file"
        echo "The framework installation may be incomplete or corrupted"
        exit 1
    fi
    
    success "Template found: init.sh.j2"
    
    # Perform the patch
    if perform_patch "$framework_path" "$project_name"; then
        echo ""
        success "Project init.sh patching completed successfully!"
        
        if [[ "$DRY_RUN" != true ]]; then
            echo ""
            echo -e "${BOLD}Next steps:${RESET}"
            echo "  1. Test the updated init.sh: ./init.sh help"
            echo "  2. Try new patch commands: ./init.sh patch-status"
            echo "  3. If issues occur, rollback: $0 --rollback"
        fi
    else
        error "Patching failed!"
        exit 1
    fi
}

# Run main function with all arguments
main "$@"