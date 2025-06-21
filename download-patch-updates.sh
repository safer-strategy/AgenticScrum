#!/bin/bash
# AgenticScrum Remote Patch Downloader
# Downloads and applies patches from GitHub repository without requiring full framework installation

set -euo pipefail

# Configuration
GITHUB_RAW_URL="https://raw.githubusercontent.com/safer-strategy/AgenticScrum/refs/heads/main"
BACKUP_DIR=".agentic_patch_backup_$(date +%Y%m%d_%H%M%S)"
TEMP_DIR=".agentic_patch_temp"
VERSION_FILE="VERSION"
CURRENT_VERSION="unknown"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Progress indicators
SPINNER_PID=""

# Print colored output
print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_header() { echo -e "${PURPLE}🔧 $1${NC}"; }

# Spinner for long operations
show_spinner() {
    local msg="$1"
    local pid="$2"
    local delay=0.1
    local spinstr='|/-\'
    echo -n "$msg "
    while kill -0 "$pid" 2>/dev/null; do
        local temp=${spinstr#?}
        printf "[%c]" "$spinstr"
        local spinstr=$temp${spinstr%"$temp"}
        sleep $delay
        printf "\b\b\b"
    done
    printf "\b\b\b"
    echo "✅"
}

# Download function with error handling and progress
download_file() {
    local remote_path="$1"
    local local_path="$2"
    local description="${3:-Downloading file}"
    
    print_info "$description..."
    
    # Create directory if needed
    mkdir -p "$(dirname "$local_path")"
    
    # Download with progress and error handling
    if curl -fsSL --connect-timeout 10 --max-time 30 \
        --retry 3 --retry-delay 1 \
        "${GITHUB_RAW_URL}/${remote_path}" \
        -o "$local_path"; then
        print_success "Downloaded: $(basename "$local_path")"
        return 0
    else
        print_error "Failed to download: $remote_path"
        return 1
    fi
}

# Backup existing files
backup_file() {
    local file_path="$1"
    
    if [[ -f "$file_path" ]]; then
        local backup_path="$BACKUP_DIR/$file_path"
        mkdir -p "$(dirname "$backup_path")"
        
        if cp "$file_path" "$backup_path"; then
            print_info "Backed up: $file_path -> $backup_path"
        else
            print_warning "Could not backup: $file_path"
        fi
    fi
}

# Verify downloaded file integrity
verify_file() {
    local file_path="$1"
    local min_size="${2:-10}"
    
    if [[ ! -f "$file_path" ]]; then
        print_error "File not found: $file_path"
        return 1
    fi
    
    local file_size
    file_size=$(wc -c < "$file_path")
    
    if [[ "$file_size" -lt "$min_size" ]]; then
        print_error "File too small (possible download error): $file_path"
        return 1
    fi
    
    # Check for HTML error pages
    if head -n 1 "$file_path" | grep -q "<!DOCTYPE html>"; then
        print_error "Downloaded HTML error page instead of file: $file_path"
        return 1
    fi
    
    return 0
}

# Get current project version
get_current_version() {
    if [[ -f "$VERSION_FILE" ]]; then
        CURRENT_VERSION=$(cat "$VERSION_FILE" 2>/dev/null || echo "unknown")
    elif [[ -f "agentic_config.yaml" ]]; then
        CURRENT_VERSION=$(grep -E "^version:" agentic_config.yaml 2>/dev/null | cut -d: -f2 | tr -d ' "' || echo "unknown")
    else
        CURRENT_VERSION="unknown"
    fi
}

# Check if we're in an AgenticScrum project
check_project_context() {
    if [[ ! -f "agentic_config.yaml" ]] && [[ ! -f "init.sh" ]] && [[ ! -f ".mcp.json" ]]; then
        print_warning "Not in an AgenticScrum project directory"
        print_info "Some operations may not work correctly"
        return 1
    fi
    return 0
}

# Core patch operations
patch_init_sh() {
    print_header "Updating init.sh with latest framework integration"
    
    local init_sh="init.sh"
    
    if [[ ! -f "$init_sh" ]]; then
        print_error "init.sh not found in current directory"
        return 1
    fi
    
    # Backup original
    backup_file "$init_sh"
    
    # Download patch script
    if ! download_file "scripts/patch-project-init.sh" "$TEMP_DIR/patch-project-init.sh" "Downloading init.sh patch"; then
        return 1
    fi
    
    # Make executable and run
    chmod +x "$TEMP_DIR/patch-project-init.sh"
    
    if "$TEMP_DIR/patch-project-init.sh"; then
        print_success "init.sh updated successfully"
        return 0
    else
        print_error "Failed to update init.sh"
        return 1
    fi
}

patch_animated_banner() {
    print_header "Adding animated ASCII banner to init.sh"
    
    local init_sh="init.sh"
    
    if [[ ! -f "$init_sh" ]]; then
        print_error "init.sh not found in current directory"
        return 1
    fi
    
    # Check if banner already exists
    if grep -q "show_animated_banner" "$init_sh"; then
        print_info "Animated banner already present in init.sh"
        return 0
    fi
    
    # Backup original
    backup_file "$init_sh"
    
    # Download banner template
    if ! download_file "agentic_scrum_setup/templates/common/init.sh.j2" "$TEMP_DIR/init.sh.j2" "Downloading banner template"; then
        return 1
    fi
    
    # Extract banner function
    if sed -n '/function show_animated_banner/,/^}/p' "$TEMP_DIR/init.sh.j2" > "$TEMP_DIR/banner_function.sh"; then
        # Create a temporary file with the insertion
        {
            head -n 1 "$init_sh"
            echo ""
            echo "# Animated banner function"
            cat "$TEMP_DIR/banner_function.sh"
            echo ""
            tail -n +2 "$init_sh"
        } > "$TEMP_DIR/new_init.sh"
        
        # Replace the original file
        if mv "$TEMP_DIR/new_init.sh" "$init_sh"; then
            print_success "Animated banner added to init.sh"
            return 0
        fi
    fi
    
    print_error "Failed to add animated banner"
    return 1
}

patch_mcp_config() {
    print_header "Updating MCP configuration"
    
    local mcp_config=".mcp.json"
    
    if [[ ! -f "$mcp_config" ]]; then
        print_info "Creating new MCP configuration"
        
        # Download template
        if download_file "agentic_scrum_setup/templates/claude/.mcp.json.j2" "$TEMP_DIR/.mcp.json.j2" "Downloading MCP template"; then
            # Simple template substitution
            local project_name
            project_name=$(basename "$PWD")
            sed "s/{{ project_name }}/$project_name/g" "$TEMP_DIR/.mcp.json.j2" > "$mcp_config"
            print_success "MCP configuration created"
        else
            return 1
        fi
    else
        print_info "MCP configuration already exists - skipping update"
        print_info "Use 'backup-and-replace' operation to force update"
    fi
    
    return 0
}

patch_security_features() {
    print_header "Adding security training features"
    
    # Download security templates
    local security_files=(
        "agentic_scrum_setup/templates/saa/persona_rules.yaml.j2:agents/saa/persona_rules.yaml"
        "agentic_scrum_setup/templates/saa/training_protocol.yaml.j2:agents/saa/training_protocol.yaml"
        "agentic_scrum_setup/templates/checklists/security_audit_checklist.md.j2:standards/security_audit_checklist.md"
    )
    
    local updated_files=0
    
    for file_mapping in "${security_files[@]}"; do
        IFS=':' read -r remote_path local_path <<< "$file_mapping"
        
        if [[ ! -f "$local_path" ]]; then
            if download_file "$remote_path" "$TEMP_DIR/$(basename "$local_path")" "Downloading $(basename "$local_path")"; then
                mkdir -p "$(dirname "$local_path")"
                
                # Simple template substitution
                local project_name
                project_name=$(basename "$PWD")
                sed "s/{{ project_name }}/$project_name/g" "$TEMP_DIR/$(basename "$local_path")" > "$local_path"
                
                print_success "Added: $local_path"
                ((updated_files++))
            fi
        else
            print_info "Already exists: $local_path"
        fi
    done
    
    if [[ $updated_files -gt 0 ]]; then
        print_success "Added $updated_files security feature files"
    else
        print_info "All security features already present"
    fi
    
    return 0
}

patch_background_agents() {
    print_header "Adding background agent execution system"
    
    # Download background agent templates
    local bg_files=(
        "agentic_scrum_setup/templates/common/background_agents.yaml.j2:background_agents.yaml"
        "agentic_scrum_setup/templates/common/agent_scheduler.py.j2:scripts/agent_scheduler.py"
    )
    
    local updated_files=0
    
    for file_mapping in "${bg_files[@]}"; do
        IFS=':' read -r remote_path local_path <<< "$file_mapping"
        
        if [[ ! -f "$local_path" ]]; then
            if download_file "$remote_path" "$TEMP_DIR/$(basename "$local_path")" "Downloading $(basename "$local_path")"; then
                mkdir -p "$(dirname "$local_path")"
                
                # Simple template substitution
                local project_name
                project_name=$(basename "$PWD")
                sed "s/{{ project_name }}/$project_name/g" "$TEMP_DIR/$(basename "$local_path")" > "$local_path"
                
                # Make Python scripts executable
                if [[ "$local_path" == *.py ]]; then
                    chmod +x "$local_path"
                fi
                
                print_success "Added: $local_path"
                ((updated_files++))
            fi
        else
            print_info "Already exists: $local_path"
        fi
    done
    
    if [[ $updated_files -gt 0 ]]; then
        print_success "Added $updated_files background agent files"
    else
        print_info "Background agent system already configured"
    fi
    
    return 0
}

patch_core_scripts() {
    print_header "Downloading essential patching scripts"
    
    local scripts_dir="scripts"
    mkdir -p "$scripts_dir"
    
    # Core scripts to download
    local core_scripts=(
        "scripts/patch-project-init.sh"
        "scripts/agentic-patch"
        "scripts/animated_ascii_art.py"
    )
    
    local downloaded=0
    
    for script in "${core_scripts[@]}"; do
        local local_script="$scripts_dir/$(basename "$script")"
        
        if download_file "$script" "$local_script" "Downloading $(basename "$script")"; then
            chmod +x "$local_script"
            ((downloaded++))
        fi
    done
    
    if [[ $downloaded -gt 0 ]]; then
        print_success "Downloaded $downloaded core scripts"
    else
        print_error "Failed to download core scripts"
        return 1
    fi
    
    return 0
}

install_standalone_patcher() {
    print_header "Installing standalone patcher globally"
    
    local install_dir="$HOME/.local/bin"
    mkdir -p "$install_dir"
    
    if download_file "scripts/agentic-patch" "$install_dir/agentic-patch" "Downloading standalone patcher"; then
        chmod +x "$install_dir/agentic-patch"
        print_success "Installed agentic-patch to $install_dir"
        
        # Add to PATH if not already there
        if [[ ":$PATH:" != *":$install_dir:"* ]]; then
            print_info "Add $install_dir to your PATH to use agentic-patch globally"
            print_info "Add this to your shell profile: export PATH=\"\$PATH:$install_dir\""
        fi
    else
        return 1
    fi
    
    return 0
}

# Show available operations
show_operations() {
    print_header "Available Patch Operations"
    echo
    echo "Core Operations:"
    echo "  init-sh-update       Update init.sh with latest framework integration"
    echo "  animated-banner      Add animated ASCII banner to init.sh"
    echo "  add-animated-banner  Add animated ASCII banner to init.sh (alias)"
    echo "  mcp-config          Update MCP configuration files"
    echo "  security-update     Add security training features"
    echo "  update-security     Add security training features (alias)"
    echo "  background-agents   Add background agent execution system"
    echo "  add-background-agents Add background agent execution system (alias)"
    echo "  core-scripts        Download essential patching scripts"
    echo "  standalone-installer Install agentic-patch globally"
    echo
    echo "Utility Operations:"
    echo "  check-version       Check current vs latest version"
    echo "  backup-project      Create full project backup"
    echo "  restore-backup      Restore from backup"
    echo "  cleanup             Remove temporary files"
    echo
    echo "Usage: $0 <operation> [--dry-run] [--force]"
    echo "       $0 --help"
}

# Check version
check_version() {
    print_header "Version Check"
    
    get_current_version
    print_info "Current version: $CURRENT_VERSION"
    
    if download_file "VERSION" "$TEMP_DIR/VERSION" "Checking latest version"; then
        local latest_version
        latest_version=$(cat "$TEMP_DIR/VERSION" 2>/dev/null || echo "unknown")
        print_info "Latest version: $latest_version"
        
        if [[ "$CURRENT_VERSION" != "$latest_version" ]]; then
            print_warning "Update available: $CURRENT_VERSION -> $latest_version"
            return 1
        else
            print_success "Project is up to date"
            return 0
        fi
    else
        print_error "Could not check latest version"
        return 1
    fi
}

# Backup project
backup_project() {
    print_header "Creating full project backup"
    
    local backup_name="full_backup_$(date +%Y%m%d_%H%M%S)"
    local backup_path="../$backup_name"
    
    if cp -r . "$backup_path"; then
        print_success "Project backed up to: $backup_path"
        echo "$backup_path" > ".last_backup"
    else
        print_error "Failed to create project backup"
        return 1
    fi
}

# Restore backup
restore_backup() {
    print_header "Restoring from backup"
    
    if [[ -f ".last_backup" ]]; then
        local backup_path
        backup_path=$(cat ".last_backup")
        
        if [[ -d "$backup_path" ]]; then
            print_warning "This will overwrite current project files"
            read -p "Continue? (y/N): " -n 1 -r
            echo
            
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                if cp -r "$backup_path"/* .; then
                    print_success "Project restored from: $backup_path"
                else
                    print_error "Failed to restore project"
                    return 1
                fi
            else
                print_info "Restore cancelled"
            fi
        else
            print_error "Backup directory not found: $backup_path"
            return 1
        fi
    else
        print_error "No backup information found"
        return 1
    fi
}

# Cleanup temporary files
cleanup() {
    print_header "Cleaning up temporary files"
    
    local cleaned=0
    
    if [[ -d "$TEMP_DIR" ]]; then
        rm -rf "$TEMP_DIR"
        print_success "Removed temporary directory: $TEMP_DIR"
        ((cleaned++))
    fi
    
    # Clean old backup directories (keep last 5)
    local backup_dirs
    backup_dirs=($(find . -maxdepth 1 -name ".agentic_patch_backup_*" -type d | sort -r))
    
    if [[ ${#backup_dirs[@]} -gt 5 ]]; then
        for ((i=5; i<${#backup_dirs[@]}; i++)); do
            rm -rf "${backup_dirs[$i]}"
            print_info "Removed old backup: $(basename "${backup_dirs[$i]}")"
            ((cleaned++))
        done
    fi
    
    if [[ $cleaned -gt 0 ]]; then
        print_success "Cleaned up $cleaned items"
    else
        print_info "No cleanup needed"
    fi
}

# Main execution
main() {
    local operation="${1:-}"
    local dry_run=false
    local force=false
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --dry-run)
                dry_run=true
                shift
                ;;
            --force)
                force=true
                shift
                ;;
            --help|-h)
                show_operations
                exit 0
                ;;
            *)
                if [[ -z "$operation" ]]; then
                    operation="$1"
                fi
                shift
                ;;
        esac
    done
    
    # Create temp directory
    mkdir -p "$TEMP_DIR"
    
    # Trap to cleanup on exit
    trap 'rm -rf "$TEMP_DIR"' EXIT
    
    print_header "AgenticScrum Remote Patch Downloader"
    print_info "Working directory: $(pwd)"
    
    # Check project context
    check_project_context
    
    # Handle dry run
    if [[ "$dry_run" == true ]]; then
        print_info "DRY RUN MODE - No changes will be made"
        echo
    fi
    
    # Execute operation
    case "$operation" in
        "init-sh-update")
            if [[ "$dry_run" == true ]]; then
                print_info "Would update init.sh with latest framework integration"
            else
                patch_init_sh
            fi
            ;;
        "animated-banner"|"add-animated-banner")
            if [[ "$dry_run" == true ]]; then
                print_info "Would add animated ASCII banner to init.sh"
            else
                patch_animated_banner
            fi
            ;;
        "mcp-config")
            if [[ "$dry_run" == true ]]; then
                print_info "Would update MCP configuration files"
            else
                patch_mcp_config
            fi
            ;;
        "security-update"|"update-security")
            if [[ "$dry_run" == true ]]; then
                print_info "Would add security training features"
            else
                patch_security_features
            fi
            ;;
        "background-agents"|"add-background-agents")
            if [[ "$dry_run" == true ]]; then
                print_info "Would add background agent execution system"
            else
                patch_background_agents
            fi
            ;;
        "core-scripts")
            if [[ "$dry_run" == true ]]; then
                print_info "Would download essential patching scripts"
            else
                patch_core_scripts
            fi
            ;;
        "standalone-installer")
            if [[ "$dry_run" == true ]]; then
                print_info "Would install agentic-patch globally"
            else
                install_standalone_patcher
            fi
            ;;
        "check-version")
            check_version
            ;;
        "backup-project")
            if [[ "$dry_run" == true ]]; then
                print_info "Would create full project backup"
            else
                backup_project
            fi
            ;;
        "restore-backup")
            if [[ "$dry_run" == true ]]; then
                print_info "Would restore project from backup"
            else
                restore_backup
            fi
            ;;
        "cleanup")
            if [[ "$dry_run" == true ]]; then
                print_info "Would remove temporary files and old backups"
            else
                cleanup
            fi
            ;;
        "")
            print_error "No operation specified"
            echo
            show_operations
            exit 1
            ;;
        *)
            print_error "Unknown operation: $operation"
            echo
            show_operations
            exit 1
            ;;
    esac
    
    if [[ "$dry_run" == false ]]; then
        print_success "Operation completed: $operation"
    fi
}

# Security warning for curl | bash usage
if [[ "${BASH_SOURCE[0]:-$0}" == "${0}" ]]; then
    # Only show warning if piped from curl
    if [[ -t 0 ]]; then
        main "$@"
    else
        print_warning "⚠️  SECURITY WARNING: You are running a script downloaded from the internet"
        print_warning "⚠️  Please review the script before execution for security"
        print_warning "⚠️  Press Ctrl+C to cancel, or wait 5 seconds to continue"
        sleep 5
        main "$@"
    fi
fi