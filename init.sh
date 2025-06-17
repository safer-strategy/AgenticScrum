#!/bin/bash

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                        AgenticScrum Setup Utility Helper                        ║
# ║                    Simplifying agentic-scrum-setup commands                     ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

set -e

# ANSI color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Project configuration defaults
DEFAULT_LANGUAGE="python"
DEFAULT_LLM_PROVIDER="anthropic"
DEFAULT_MODEL="claude-sonnet-4-0"
DEFAULT_AGENTS="poa,sma,deva_python,qaa"

# MCP Service Management Functions
start_mcp_services() {
    echo -e "${BOLD}Starting MCP services...${NC}"
    
    # Start DateTime service
    if [[ -f "mcp_servers/datetime/server.py" ]]; then
        echo -e "${CYAN}Starting DateTime MCP service...${NC}"
        python mcp_servers/datetime/server.py &
        DATETIME_PID=$!
        echo $DATETIME_PID > .datetime_service.pid
        echo -e "${GREEN}✓ DateTime MCP service started (PID: $DATETIME_PID)${NC}"
    else
        echo -e "${YELLOW}⚠ DateTime service not found at mcp_servers/datetime/server.py${NC}"
    fi
}

stop_mcp_services() {
    echo -e "${BOLD}Stopping MCP services...${NC}"
    
    if [[ -f ".datetime_service.pid" ]]; then
        PID=$(cat .datetime_service.pid)
        if kill -0 $PID 2>/dev/null; then
            kill $PID 2>/dev/null
            echo -e "${GREEN}✓ DateTime MCP service stopped (PID: $PID)${NC}"
        else
            echo -e "${YELLOW}⚠ DateTime service was already stopped${NC}"
        fi
        rm .datetime_service.pid
    else
        echo -e "${YELLOW}⚠ No DateTime service PID file found${NC}"
    fi
}

status_mcp_services() {
    echo -e "${BOLD}MCP Service Status:${NC}"
    
    if [[ -f ".datetime_service.pid" ]]; then
        PID=$(cat .datetime_service.pid)
        if kill -0 $PID 2>/dev/null; then
            echo -e "  DateTime Service: ${GREEN}✅ Running${NC} (PID: $PID)"
        else
            echo -e "  DateTime Service: ${RED}❌ Stopped${NC} (stale PID file)"
            rm .datetime_service.pid
        fi
    else
        echo -e "  DateTime Service: ${RED}❌ Stopped${NC}"
    fi
    
    # Check if .mcp.json exists
    if [[ -f ".mcp.json" ]]; then
        echo -e "  MCP Configuration: ${GREEN}✅ Found${NC}"
    else
        echo -e "  MCP Configuration: ${RED}❌ Missing${NC}"
    fi
}

test_datetime_service() {
    echo -e "${BOLD}Testing DateTime MCP service...${NC}"
    
    if [[ ! -f "mcp_servers/datetime/datetime_tools.py" ]]; then
        echo -e "${RED}❌ DateTime service not found${NC}"
        return 1
    fi
    
    # Test the DateTime tools directly
    python -c "
import sys
sys.path.append('mcp_servers/datetime')
from datetime_tools import DateTimeTools
dt = DateTimeTools()
result = dt.get_current_time('UTC')
print(f'✓ DateTime service test passed: {result[\"timestamp\"]}')
" 2>/dev/null
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ DateTime service is functional${NC}"
    else
        echo -e "${RED}❌ DateTime service test failed${NC}"
    fi
}

# Function to show success message with style
show_success() {
    local project_name=$1
    echo
    if [ -f "scripts/generate_ascii_art.py" ]; then
        python scripts/generate_ascii_art.py "SUCCESS" --style blocks --border none --color gradient
    else
        echo -e "${GREEN}╔══════════════════════════════════════╗${NC}"
        echo -e "${GREEN}║         SUCCESS!                     ║${NC}"
        echo -e "${GREEN}╚══════════════════════════════════════╝${NC}"
    fi
    echo
    echo -e "${GREEN}✨ Project '$project_name' created successfully!${NC}"
    echo
    echo -e "${YELLOW}Next steps:${NC}"
    echo -e "  ${CYAN}1. cd $project_name${NC}"
    echo -e "  ${CYAN}2. ./init.sh help${NC} - See available commands"
    echo -e "  ${CYAN}3. ./init.sh up${NC} - Start your development environment"
    echo
    echo -e "${YELLOW}▓▒░ Happy coding with AgenticScrum! ░▒▓${NC}"
}

# Function to display the header with ASCII art
show_header() {
    clear
    
    # Check if we should use animated version (for first run or special commands)
    if [ "$1" = "animated" ] && [ -f "scripts/animated_ascii_art.py" ]; then
        # Use animated ASCII art for special occasions
        python scripts/animated_ascii_art.py "AGENTIC" --effect scan
        echo
    elif [ -f "scripts/generate_ascii_art.py" ]; then
        # Use static ASCII art with 3D effect
        python scripts/generate_ascii_art.py "AGENTIC" --style 3d --subtitle "AI-Driven Development Framework" --color neon --border none
        echo
    else
        # Fallback to simple header if scripts not available
        echo -e "${CYAN}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
        echo -e "${CYAN}║${BOLD}                        AgenticScrum Setup Utility Helper                        ${CYAN}║${NC}"
        echo -e "${CYAN}║${WHITE}                    Simplifying agentic-scrum-setup commands                     ${CYAN}║${NC}"
        echo -e "${CYAN}╚══════════════════════════════════════════════════════════════════════════════╝${NC}"
        echo
    fi
    
    # Add a cool status line
    echo -e "${YELLOW}▓▒░ Ready to create amazing AI-driven projects! ░▒▓${NC}"
    echo
}

# Function to display help
show_help() {
    show_header
    echo -e "${BOLD}Usage:${NC} ./init.sh [command] [options]"
    echo
    echo -e "${BOLD}Commands:${NC}"
    echo -e "  ${GREEN}new${NC}            Create a new AgenticScrum project (interactive)"
    echo -e "  ${GREEN}quick${NC}          Quick setup with sensible defaults"
    echo -e "  ${GREEN}claude-code${NC}    Quick setup optimized for Claude Code"
    echo -e "  ${GREEN}custom${NC}         Custom setup with all options"
    echo -e "  ${GREEN}retrofit${NC} <path> Analyze existing project for integration"
    echo -e "  ${GREEN}create-workspace${NC} Set up a projects directory"
    echo -e "  ${GREEN}install${NC}        Install agentic-scrum-setup utility"
    echo -e "  ${GREEN}mcp-start${NC}      Start MCP DateTime service"
    echo -e "  ${GREEN}mcp-stop${NC}       Stop MCP DateTime service"
    echo -e "  ${GREEN}mcp-status${NC}     Check MCP service status"
    echo -e "  ${GREEN}mcp-test${NC}       Test DateTime service functionality"
    echo -e "  ${GREEN}help${NC}           Show this help message"
    echo
    echo -e "${BOLD}Quick Examples:${NC}"
    echo -e "  ${CYAN}./init.sh new${NC}                    # Interactive project creation"
    echo -e "  ${CYAN}./init.sh quick MyProject${NC}        # Quick project with Claude defaults"
    echo -e "  ${CYAN}./init.sh claude-code MyApp${NC}      # Optimized for Claude Code IDE"
    echo -e "  ${CYAN}./init.sh create-workspace${NC}       # Set up ~/AgenticProjects directory"
    echo -e "  ${CYAN}./init.sh custom${NC}                 # Full customization options"
    echo -e "  ${CYAN}./init.sh mcp-start${NC}              # Start DateTime MCP service"
    echo -e "  ${CYAN}./init.sh mcp-status${NC}             # Check if DateTime service is running"
    echo
    echo -e "${BOLD}Claude Code Integration:${NC}"
    echo -e "  Projects are now optimized for Claude Code by default"
    echo -e "  - Default provider: Anthropic"
    echo -e "  - Default model: claude-sonnet-4-0"
    echo -e "  - Automatic parameter handling by Claude Code IDE"
    echo
    echo -e "${BOLD}Supported Languages:${NC}"
    echo -e "  python, javascript, typescript, java, go, rust, csharp, php, ruby"
    echo
    echo -e "${BOLD}Supported Frameworks:${NC}"
    echo -e "  ${BLUE}Single Language Projects:${NC}"
    echo -e "    Python: fastapi"
    echo -e "    JavaScript/TypeScript: react, nodejs, electron"
    echo -e "  ${BLUE}Fullstack Projects:${NC}"
    echo -e "    Backend: fastapi, express, spring, gin, actix, aspnet"
    echo -e "    Frontend: react, vue, angular, svelte"
    echo
    echo -e "${BOLD}Available Agents:${NC}"
    echo -e "  ${MAGENTA}poa${NC}                 Product Owner Agent"
    echo -e "  ${MAGENTA}sma${NC}                 Scrum Master Agent"
    echo -e "  ${MAGENTA}deva_python${NC}         Python Developer Agent"
    echo -e "  ${MAGENTA}deva_javascript${NC}     JavaScript Developer Agent"
    echo -e "  ${MAGENTA}deva_typescript${NC}     TypeScript Developer Agent"
    echo -e "  ${MAGENTA}deva_claude_python${NC}  Claude-powered Python Developer Agent"
    echo -e "  ${MAGENTA}qaa${NC}                 QA Agent"
    echo -e "  ${MAGENTA}saa${NC}                 Security Audit Agent"
    echo
    echo -e "${BOLD}MCP Services (Model Context Protocol):${NC}"
    echo -e "  This AgenticScrum project includes a DateTime MCP service for time operations."
    echo -e "  The service provides timezone handling, business day calculations, and sprint timing."
    echo -e "  Use 'mcp-start' to enable the service for Claude Code integration."
    echo
}

# Function to check if agentic-scrum-setup is installed
check_installation() {
    if ! command -v agentic-scrum-setup &> /dev/null; then
        echo -e "${RED}Error: agentic-scrum-setup is not installed or not in PATH${NC}"
        echo -e "${YELLOW}Run './init.sh install' to install it${NC}"
        exit 1
    fi
}

# Function to install agentic-scrum-setup
install_utility() {
    show_header animated
    echo -e "${BOLD}Installing agentic-scrum-setup utility...${NC}"
    echo
    
    if [ -d "agentic_scrum_setup" ]; then
        echo -e "${CYAN}Found local agentic_scrum_setup package${NC}"
        echo -e "${YELLOW}Installing from local directory...${NC}"
        pip install -e .
        echo -e "${GREEN}✓ Installation complete!${NC}"
    else
        echo -e "${RED}Error: agentic_scrum_setup directory not found${NC}"
        echo -e "${YELLOW}Please run this script from the AgenticScrum root directory${NC}"
        exit 1
    fi
}

# Function for interactive project creation
create_new_project() {
    show_header
    echo -e "${BOLD}Create New AgenticScrum Project${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo
    
    # Project name
    read -p "$(echo -e ${BOLD}Project Name:${NC} )" project_name
    if [ -z "$project_name" ]; then
        echo -e "${RED}Error: Project name is required${NC}"
        exit 1
    fi
    
    # Output directory selection
    echo
    default_output_dir="~/AgenticProjects"
    if [[ "$PWD" == *"AgenticScrum"* ]]; then
        echo -e "${YELLOW}Note: You're currently in the AgenticScrum directory${NC}"
        echo -e "${YELLOW}Projects should be created outside of this framework${NC}"
    else
        default_output_dir="."
    fi
    read -p "$(echo -e ${BOLD}Where to create project? [${default_output_dir}]:${NC} )" output_dir
    output_dir=${output_dir:-$default_output_dir}
    output_dir=$(eval echo "$output_dir")  # Expand ~
    
    # Project type selection
    echo
    echo -e "${BOLD}Project Type:${NC}"
    echo "1) Single language project"
    echo "2) Fullstack project (backend + frontend)"
    read -p "$(echo -e ${BOLD}Choice [1-2]:${NC} )" type_choice
    
    if [ "$type_choice" = "2" ]; then
        # Fullstack project
        project_type="fullstack"
        
        # Backend language selection
        echo
        echo -e "${BOLD}=== Backend Configuration ===${NC}"
        echo -e "${BOLD}Select Backend Language:${NC}"
        echo "1) Python"
        echo "2) JavaScript"
        echo "3) TypeScript"
        echo "4) Java"
        echo "5) Go"
        echo "6) Rust"
        echo "7) C#"
        read -p "$(echo -e ${BOLD}Choice [1-7]:${NC} )" backend_lang_choice
        
        case $backend_lang_choice in
            1) language="python";;
            2) language="javascript";;
            3) language="typescript";;
            4) language="java";;
            5) language="go";;
            6) language="rust";;
            7) language="csharp";;
            *) language="python";;
        esac
        
        # Backend framework selection
        echo
        echo -e "${BOLD}Select Backend Framework (optional):${NC}"
        case $language in
            "python") 
                echo "1) None"
                echo "2) FastAPI"
                read -p "$(echo -e ${BOLD}Choice [1-2]:${NC} )" fw_choice
                [ "$fw_choice" = "2" ] && backend_framework="--backend-framework fastapi"
                ;;
            "javascript"|"typescript")
                echo "1) None"
                echo "2) Express"
                read -p "$(echo -e ${BOLD}Choice [1-2]:${NC} )" fw_choice
                [ "$fw_choice" = "2" ] && backend_framework="--backend-framework express"
                ;;
            "java")
                echo "1) None"
                echo "2) Spring Boot"
                read -p "$(echo -e ${BOLD}Choice [1-2]:${NC} )" fw_choice
                [ "$fw_choice" = "2" ] && backend_framework="--backend-framework spring"
                ;;
            "go")
                echo "1) None"
                echo "2) Gin"
                read -p "$(echo -e ${BOLD}Choice [1-2]:${NC} )" fw_choice
                [ "$fw_choice" = "2" ] && backend_framework="--backend-framework gin"
                ;;
            "rust")
                echo "1) None"
                echo "2) Actix"
                read -p "$(echo -e ${BOLD}Choice [1-2]:${NC} )" fw_choice
                [ "$fw_choice" = "2" ] && backend_framework="--backend-framework actix"
                ;;
            "csharp")
                echo "1) None"
                echo "2) ASP.NET"
                read -p "$(echo -e ${BOLD}Choice [1-2]:${NC} )" fw_choice
                [ "$fw_choice" = "2" ] && backend_framework="--backend-framework aspnet"
                ;;
        esac
        
        # Frontend configuration
        echo
        echo -e "${BOLD}=== Frontend Configuration ===${NC}"
        echo -e "${BOLD}Select Frontend Language:${NC}"
        echo "1) JavaScript"
        echo "2) TypeScript"
        read -p "$(echo -e ${BOLD}Choice [1-2]:${NC} )" frontend_lang_choice
        
        frontend_language=$( [ "$frontend_lang_choice" = "2" ] && echo "typescript" || echo "javascript" )
        
        # Frontend framework
        echo
        echo -e "${BOLD}Select Frontend Framework:${NC}"
        echo "1) React"
        echo "2) Vue"
        echo "3) Angular"
        echo "4) Svelte"
        read -p "$(echo -e ${BOLD}Choice [1-4]:${NC} )" frontend_fw_choice
        
        case $frontend_fw_choice in
            1) frontend_framework="react";;
            2) frontend_framework="vue";;
            3) frontend_framework="angular";;
            4) frontend_framework="svelte";;
            *) frontend_framework="react";;
        esac
        
        # Default agents for fullstack
        default_agents="poa,sma,deva_${language},deva_${frontend_language},qaa,saa"
        
    else
        # Single language project
        project_type="single"
        
        # Language selection
        echo
        echo -e "${BOLD}Select Language:${NC}"
        echo "1) Python"
        echo "2) JavaScript"
        echo "3) TypeScript"
        echo "4) Java"
        echo "5) Go"
        echo "6) Rust"
        echo "7) C#"
        echo "8) PHP"
        echo "9) Ruby"
        read -p "$(echo -e ${BOLD}Choice [1-9]:${NC} )" lang_choice
        
        case $lang_choice in
            1) language="python";;
            2) language="javascript";;
            3) language="typescript";;
            4) language="java";;
            5) language="go";;
            6) language="rust";;
            7) language="csharp";;
            8) language="php";;
            9) language="ruby";;
            *) language="python";;
        esac
        
        # Default agents for single language
        default_agents="poa,sma,deva_${language},qaa"
    fi
    
    # Framework selection for single language projects
    framework=""
    if [ "$project_type" = "single" ]; then
        if [ "$language" = "python" ]; then
            echo
            echo -e "${BOLD}Select Python Framework (optional):${NC}"
            echo "1) None (standard Python)"
            echo "2) FastAPI"
            read -p "$(echo -e ${BOLD}Choice [1-2]:${NC} )" framework_choice
            case $framework_choice in
                2) framework="--framework fastapi";;
            esac
        elif [ "$language" = "javascript" ] || [ "$language" = "typescript" ]; then
            echo
            echo -e "${BOLD}Select JavaScript/TypeScript Framework (optional):${NC}"
            echo "1) None (vanilla)"
            echo "2) React"
            echo "3) Node.js"
            echo "4) Electron"
            read -p "$(echo -e ${BOLD}Choice [1-4]:${NC} )" framework_choice
            case $framework_choice in
                2) framework="--framework react";;
                3) framework="--framework nodejs";;
                4) framework="--framework electron";;
            esac
        fi
    fi
    
    # Agent selection
    echo
    echo -e "${BOLD}Select Agents (comma-separated):${NC}"
    echo -e "${CYAN}Available: poa, sma, deva_python, deva_javascript, deva_typescript, deva_claude_python, qaa, saa${NC}"
    read -p "$(echo -e ${BOLD}Agents [default: ${default_agents}]:${NC} )" agents
    if [ -z "$agents" ]; then
        agents="$default_agents"
    fi
    
    # Claude Code Integration Check
    echo
    read -p "$(echo -e ${BOLD}Are you using Claude Code? [Y/n]:${NC} )" claude_code
    if [ "$claude_code" != "n" ] && [ "$claude_code" != "N" ]; then
        echo -e "${CYAN}Note: Claude Code controls temperature and token limits${NC}"
        echo -e "${CYAN}Recommended model: claude-sonnet-4-0 for development${NC}"
        # Set flag for later use
        using_claude_code=true
        # Auto-select Anthropic and add --claude-code flag
        llm_provider="anthropic"
        default_model="claude-sonnet-4-0"
        claude_code_flag=" --claude-code"
    else
        using_claude_code=false
        claude_code_flag=""
    fi
    
    # LLM Provider (skip if Claude Code was selected)
    if [ "$using_claude_code" != "true" ]; then
        echo
        echo -e "${BOLD}Select LLM Provider:${NC}"
        echo "1) Anthropic (Claude)"
        echo "2) OpenAI"
        echo "3) Google"
        echo "4) Local (Ollama)"
        read -p "$(echo -e ${BOLD}Choice [1-4]:${NC} )" llm_choice
        
        case $llm_choice in
            1) llm_provider="anthropic"
               # Claude model selection
               echo
               echo -e "${BOLD}Select Claude Model:${NC}"
               echo "1) claude-sonnet-4-0 (Balanced - Recommended)"
               echo "2) claude-opus-4-0 (Most capable - Complex tasks)"
               echo "3) claude-3-5-sonnet-latest (Previous generation)"
               echo "4) claude-3-5-haiku-latest (Fastest - Simple tasks)"
               read -p "$(echo -e ${BOLD}Choice [1-4]:${NC} )" model_choice
               case $model_choice in
                   1) default_model="claude-sonnet-4-0";;
                   2) default_model="claude-opus-4-0";;
                   3) default_model="claude-3-5-sonnet-latest";;
                   4) default_model="claude-3-5-haiku-latest";;
                   *) default_model="claude-sonnet-4-0";;
               esac
               ;;
            2) llm_provider="openai"; default_model="gpt-4-turbo-preview";;
            3) llm_provider="google"; default_model="gemini-pro";;
            4) llm_provider="local"; default_model="codellama";;
            *) llm_provider="anthropic"; default_model="claude-sonnet-4-0";;
        esac
    fi
    
    # Build command
    cmd="agentic-scrum-setup init"
    cmd="$cmd --project-name \"$project_name\""
    
    if [ "$project_type" = "fullstack" ]; then
        cmd="$cmd --project-type fullstack"
        cmd="$cmd --language $language"
        cmd="$cmd --frontend-language $frontend_language"
        cmd="$cmd --frontend-framework $frontend_framework"
        if [ -n "$backend_framework" ]; then
            cmd="$cmd $backend_framework"
        fi
    else
        cmd="$cmd --language $language"
        if [ -n "$framework" ]; then
            cmd="$cmd $framework"
        fi
    fi
    
    cmd="$cmd --agents $agents"
    cmd="$cmd --llm-provider $llm_provider"
    cmd="$cmd --default-model $default_model"
    
    # Add output directory
    cmd="$cmd --output-dir \"$output_dir\""
    
    # Add Claude Code flag if applicable
    if [ "$using_claude_code" = "true" ]; then
        cmd="$cmd --claude-code"
    fi
    
    # Show command and confirm
    echo
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BOLD}Generated Command:${NC}"
    echo -e "${GREEN}$cmd${NC}"
    echo
    read -p "$(echo -e ${BOLD}Execute this command? [Y/n]:${NC} )" confirm
    
    if [ "$confirm" != "n" ] && [ "$confirm" != "N" ]; then
        echo
        echo -e "${YELLOW}Creating project...${NC}"
        eval $cmd
        show_success "$project_name"
    else
        echo -e "${YELLOW}Command cancelled${NC}"
    fi
}

# Function for quick setup
quick_setup() {
    local project_name=$1
    
    if [ -z "$project_name" ]; then
        echo -e "${RED}Error: Project name required${NC}"
        echo -e "${YELLOW}Usage: ./init.sh quick <project-name>${NC}"
        exit 1
    fi
    
    show_header
    echo -e "${BOLD}Quick Setup: $project_name${NC}"
    echo
    
    cmd="agentic-scrum-setup init"
    cmd="$cmd --project-name \"$project_name\""
    cmd="$cmd --language python"
    cmd="$cmd --agents poa,sma,deva_python,qaa"
    cmd="$cmd --llm-provider anthropic"
    cmd="$cmd --default-model claude-sonnet-4-0"
    cmd="$cmd --claude-code"
    
    echo -e "${GREEN}$cmd${NC}"
    echo
    echo -e "${YELLOW}Creating project with default settings...${NC}"
    eval $cmd
    show_success "$project_name"
}

# Function for custom setup
custom_setup() {
    show_header
    echo -e "${BOLD}Custom Project Setup${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo
    echo -e "${YELLOW}This will guide you through all available options${NC}"
    echo
    
    # Collect all parameters
    read -p "$(echo -e ${BOLD}Project Name:${NC} )" project_name
    read -p "$(echo -e ${BOLD}Project Type [single/fullstack]:${NC} )" project_type
    
    if [ "$project_type" = "fullstack" ]; then
        read -p "$(echo -e ${BOLD}Backend Language [python]:${NC} )" language
        read -p "$(echo -e ${BOLD}Backend Framework (optional):${NC} )" backend_framework
        read -p "$(echo -e ${BOLD}Frontend Language [typescript]:${NC} )" frontend_language
        read -p "$(echo -e ${BOLD}Frontend Framework [react]:${NC} )" frontend_framework
        read -p "$(echo -e ${BOLD}Agents [poa,sma,deva_python,deva_typescript,qaa,saa]:${NC} )" agents
    else
        read -p "$(echo -e ${BOLD}Language [python]:${NC} )" language
        read -p "$(echo -e ${BOLD}Framework (optional):${NC} )" framework
        read -p "$(echo -e ${BOLD}Agents [poa,sma,deva_python,qaa,saa]:${NC} )" agents
    fi
    
    read -p "$(echo -e ${BOLD}LLM Provider [anthropic]:${NC} )" llm_provider
    read -p "$(echo -e ${BOLD}Default Model [claude-sonnet-4-0]:${NC} )" default_model
    read -p "$(echo -e ${BOLD}Output Directory [.]:${NC} )" output_dir
    
    # Set defaults
    project_type=${project_type:-single}
    language=${language:-python}
    frontend_language=${frontend_language:-typescript}
    frontend_framework=${frontend_framework:-react}
    agents=${agents:-poa,sma,deva_python,qaa}
    llm_provider=${llm_provider:-anthropic}
    default_model=${default_model:-claude-sonnet-4-0}
    output_dir=${output_dir:-.}
    
    # Build command
    cmd="agentic-scrum-setup init"
    cmd="$cmd --project-name \"$project_name\""
    
    if [ "$project_type" = "fullstack" ]; then
        cmd="$cmd --project-type fullstack"
        cmd="$cmd --language $language"
        cmd="$cmd --frontend-language $frontend_language"
        cmd="$cmd --frontend-framework $frontend_framework"
        if [ -n "$backend_framework" ]; then
            cmd="$cmd --backend-framework $backend_framework"
        fi
    else
        cmd="$cmd --language $language"
        if [ -n "$framework" ]; then
            cmd="$cmd --framework $framework"
        fi
    fi
    
    cmd="$cmd --agents $agents"
    cmd="$cmd --llm-provider $llm_provider"
    cmd="$cmd --default-model $default_model"
    cmd="$cmd --output-dir $output_dir"
    
    # Show and execute
    echo
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BOLD}Generated Command:${NC}"
    echo -e "${GREEN}$cmd${NC}"
    echo
    read -p "$(echo -e ${BOLD}Execute this command? [Y/n]:${NC} )" confirm
    
    if [ "$confirm" != "n" ] && [ "$confirm" != "N" ]; then
        echo
        eval $cmd
        echo
        echo -e "${GREEN}✓ Project created successfully!${NC}"
    fi
}

# Function to create a workspace directory
create_workspace() {
    local workspace_dir=${1:-~/AgenticProjects}
    workspace_dir=$(eval echo "$workspace_dir")
    
    show_header
    echo -e "${BOLD}Creating AgenticScrum Workspace${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo
    echo -e "${BOLD}Creating workspace at: $workspace_dir${NC}"
    
    # Create directory
    mkdir -p "$workspace_dir"
    
    # Create README
    cat > "$workspace_dir/README.md" << 'EOF'
# AgenticScrum Projects Workspace

This directory contains projects created with AgenticScrum.

## Projects

- Add your projects here

## Quick Start

```bash
# Create a new project in this workspace
agentic-scrum-setup init --project-name MyNewProject --output-dir .

# Or use the init.sh helper from AgenticScrum
~/path/to/AgenticScrum/init.sh new
```

## Environment Setup

To make this your default projects directory, add to your shell profile:

```bash
export AGENTIC_PROJECTS_DIR="$(pwd)"
```

## Organization Tips

- Group related projects in subdirectories
- Use consistent naming conventions
- Keep project documentation updated
- Regular backups recommended
EOF
    
    # Create .gitignore
    cat > "$workspace_dir/.gitignore" << 'EOF'
# OS files
.DS_Store
Thumbs.db
Desktop.ini

# IDE files
.idea/
.vscode/
*.sublime-*
*.swp
*.swo

# Temporary files
*.tmp
*.temp
*.log

# Build artifacts
*.pyc
__pycache__/
node_modules/
dist/
build/
*.egg-info/

# Environment files
.env
.env.local
venv/
.venv/
EOF
    
    echo
    echo -e "${GREEN}✓ Workspace created successfully!${NC}"
    echo
    echo -e "${CYAN}To set as your default project location:${NC}"
    echo -e "  ${YELLOW}export AGENTIC_PROJECTS_DIR=\"$workspace_dir\"${NC}"
    echo
    echo -e "${CYAN}Add the above line to your shell profile (~/.zshrc or ~/.bashrc)${NC}"
}

# Main script logic
case "$1" in
    "new")
        check_installation
        create_new_project
        ;;
    "quick")
        check_installation
        quick_setup "$2"
        ;;
    "custom")
        check_installation
        custom_setup
        ;;
    "claude-code")
        check_installation
        # Quick setup with Claude defaults
        project_name=$2
        if [ -z "$project_name" ]; then
            echo -e "${RED}Error: Project name required${NC}"
            echo -e "${YELLOW}Usage: ./init.sh claude-code <project-name>${NC}"
            exit 1
        fi
        # Run with optimal Claude settings
        show_header
        echo -e "${BOLD}Claude Code Setup: $project_name${NC}"
        echo
        cmd="agentic-scrum-setup init"
        cmd="$cmd --project-name \"$project_name\""
        cmd="$cmd --language python"
        cmd="$cmd --agents poa,sma,deva_python,qaa"
        cmd="$cmd --llm-provider anthropic"
        cmd="$cmd --default-model claude-sonnet-4-0"
        cmd="$cmd --claude-code"
        echo -e "${GREEN}$cmd${NC}"
        echo
        echo -e "${YELLOW}Creating project optimized for Claude Code...${NC}"
        eval $cmd
        show_success "$project_name"
        ;;
    "retrofit")
        shift
        check_installation
        echo -e "${GREEN}🔍 Analyzing project for AgenticScrum integration...${NC}"
        agentic-scrum-setup retrofit "$@"
        ;;
    "create-workspace")
        workspace_dir=$2
        create_workspace "$workspace_dir"
        ;;
    "install")
        install_utility
        ;;
    "mcp-start")
        start_mcp_services
        ;;
    "mcp-stop")
        stop_mcp_services
        ;;
    "mcp-status")
        status_mcp_services
        ;;
    "mcp-test")
        test_datetime_service
        ;;
    "help"|"--help"|"-h"|"")
        show_help
        ;;
    *)
        echo -e "${RED}Unknown command: $1${NC}"
        echo -e "${YELLOW}Run './init.sh help' for usage information${NC}"
        exit 1
        ;;
esac