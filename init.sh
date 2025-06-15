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
DEFAULT_LLM_PROVIDER="openai"
DEFAULT_MODEL="gpt-4-turbo-preview"
DEFAULT_AGENTS="poa,sma,deva_python,qaa"

# Function to display the header
show_header() {
    clear
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║${BOLD}                        AgenticScrum Setup Utility Helper                        ${CYAN}║${NC}"
    echo -e "${CYAN}║${WHITE}                    Simplifying agentic-scrum-setup commands                     ${CYAN}║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════════════════════╝${NC}"
    echo
}

# Function to display help
show_help() {
    show_header
    echo -e "${BOLD}Usage:${NC} ./init.sh [command] [options]"
    echo
    echo -e "${BOLD}Commands:${NC}"
    echo -e "  ${GREEN}new${NC}         Create a new AgenticScrum project (interactive)"
    echo -e "  ${GREEN}quick${NC}       Quick setup with sensible defaults"
    echo -e "  ${GREEN}custom${NC}      Custom setup with all options"
    echo -e "  ${GREEN}install${NC}     Install agentic-scrum-setup utility"
    echo -e "  ${GREEN}help${NC}        Show this help message"
    echo
    echo -e "${BOLD}Quick Examples:${NC}"
    echo -e "  ${CYAN}./init.sh new${NC}                    # Interactive project creation"
    echo -e "  ${CYAN}./init.sh quick MyProject${NC}        # Quick Python project with defaults"
    echo -e "  ${CYAN}./init.sh custom${NC}                 # Full customization options"
    echo
    echo -e "${BOLD}Supported Languages:${NC}"
    echo -e "  python, javascript, typescript, java, go, rust, csharp, php, ruby"
    echo
    echo -e "${BOLD}Supported Frameworks:${NC}"
    echo -e "  ${BLUE}Python:${NC} fastapi"
    echo -e "  ${BLUE}JavaScript/TypeScript:${NC} react, nodejs, electron"
    echo
    echo -e "${BOLD}Available Agents:${NC}"
    echo -e "  ${MAGENTA}poa${NC}                 Product Owner Agent"
    echo -e "  ${MAGENTA}sma${NC}                 Scrum Master Agent"
    echo -e "  ${MAGENTA}deva_python${NC}         Python Developer Agent"
    echo -e "  ${MAGENTA}deva_javascript${NC}     JavaScript Developer Agent"
    echo -e "  ${MAGENTA}deva_claude_python${NC}  Claude-powered Python Developer Agent"
    echo -e "  ${MAGENTA}qaa${NC}                 QA Agent"
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
    show_header
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
    
    # Framework selection (if applicable)
    framework=""
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
    
    # Agent selection
    echo
    echo -e "${BOLD}Select Agents (comma-separated):${NC}"
    echo -e "${CYAN}Available: poa, sma, deva_python, deva_javascript, deva_claude_python, qaa${NC}"
    read -p "$(echo -e ${BOLD}Agents [default: poa,sma,deva_${language},qaa]:${NC} )" agents
    if [ -z "$agents" ]; then
        if [ "$language" = "javascript" ] || [ "$language" = "typescript" ]; then
            agents="poa,sma,deva_javascript,qaa"
        else
            agents="poa,sma,deva_python,qaa"
        fi
    fi
    
    # LLM Provider
    echo
    echo -e "${BOLD}Select LLM Provider:${NC}"
    echo "1) OpenAI"
    echo "2) Anthropic"
    echo "3) Google"
    echo "4) Local (Ollama)"
    read -p "$(echo -e ${BOLD}Choice [1-4]:${NC} )" llm_choice
    
    case $llm_choice in
        1) llm_provider="openai"; default_model="gpt-4-turbo-preview";;
        2) llm_provider="anthropic"; default_model="claude-3-opus-20240229";;
        3) llm_provider="google"; default_model="gemini-pro";;
        4) llm_provider="local"; default_model="codellama";;
        *) llm_provider="openai"; default_model="gpt-4-turbo-preview";;
    esac
    
    # Build command
    cmd="agentic-scrum-setup init"
    cmd="$cmd --project-name \"$project_name\""
    cmd="$cmd --language $language"
    cmd="$cmd --agents $agents"
    cmd="$cmd --llm-provider $llm_provider"
    cmd="$cmd --default-model $default_model"
    if [ -n "$framework" ]; then
        cmd="$cmd $framework"
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
        echo
        echo -e "${GREEN}✓ Project created successfully!${NC}"
        echo -e "${CYAN}Navigate to your project: cd $project_name${NC}"
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
    cmd="$cmd --llm-provider openai"
    cmd="$cmd --default-model gpt-4-turbo-preview"
    
    echo -e "${GREEN}$cmd${NC}"
    echo
    echo -e "${YELLOW}Creating project with default settings...${NC}"
    eval $cmd
    echo
    echo -e "${GREEN}✓ Project created successfully!${NC}"
    echo -e "${CYAN}Navigate to your project: cd $project_name${NC}"
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
    read -p "$(echo -e ${BOLD}Language [python]:${NC} )" language
    read -p "$(echo -e ${BOLD}Framework (optional):${NC} )" framework
    read -p "$(echo -e ${BOLD}Agents [poa,sma,deva_python,qaa]:${NC} )" agents
    read -p "$(echo -e ${BOLD}LLM Provider [openai]:${NC} )" llm_provider
    read -p "$(echo -e ${BOLD}Default Model [gpt-4-turbo-preview]:${NC} )" default_model
    read -p "$(echo -e ${BOLD}Output Directory [.]:${NC} )" output_dir
    
    # Set defaults
    language=${language:-python}
    agents=${agents:-poa,sma,deva_python,qaa}
    llm_provider=${llm_provider:-openai}
    default_model=${default_model:-gpt-4-turbo-preview}
    output_dir=${output_dir:-.}
    
    # Build command
    cmd="agentic-scrum-setup init"
    cmd="$cmd --project-name \"$project_name\""
    cmd="$cmd --language $language"
    cmd="$cmd --agents $agents"
    cmd="$cmd --llm-provider $llm_provider"
    cmd="$cmd --default-model $default_model"
    cmd="$cmd --output-dir $output_dir"
    
    if [ -n "$framework" ]; then
        cmd="$cmd --framework $framework"
    fi
    
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
    "install")
        install_utility
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