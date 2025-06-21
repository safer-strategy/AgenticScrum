#!/usr/bin/env python3
"""Command-line interface for AgenticScrum setup utility."""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional

from .setup_core import SetupCore
from . import __version__


def get_default_output_dir():
    """Get smart default output directory for project creation."""
    # Check environment variable first
    if env_dir := os.environ.get('AGENTIC_PROJECTS_DIR'):
        return env_dir
    
    # Check if we're inside AgenticScrum
    cwd = Path.cwd()
    if 'AgenticScrum' in str(cwd):
        # Default to user's home projects directory
        return str(Path.home() / 'AgenticProjects')
    
    # Otherwise use current directory
    return '.'


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        prog='agentic-scrum-setup',
        description='AgenticScrum Project Setup Utility - Initialize AI-driven development projects',
        epilog='''Examples:
  # Interactive mode (recommended)
  agentic-scrum-setup init
  
  # Quick setup for Claude Code
  agentic-scrum-setup init --project-name MyProject --language python --agents poa,sma,deva_python,qaa --claude-code
  
  # Single language project  
  agentic-scrum-setup init --project-name MyProject --language python --framework fastapi \\
    --agents poa,sma,deva_python,qaa --llm-provider anthropic --default-model claude-sonnet-4-0
  
  # Fullstack project
  agentic-scrum-setup init --project-name MyApp --project-type fullstack \\
    --language python --backend-framework fastapi \\
    --frontend-language typescript --frontend-framework react \\
    --agents poa,sma,deva_python,deva_typescript,qaa \\
    --llm-provider anthropic --default-model claude-sonnet-4-0
''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Add version argument
    parser.add_argument(
        '--version',
        action='version',
        version=f'agentic-scrum-setup, version {__version__}'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Init command
    init_parser = subparsers.add_parser('init', help='Initialize a new AgenticScrum project')
    init_parser.add_argument(
        '--project-name',
        type=str,
        help='Name of the project to create'
    )
    init_parser.add_argument(
        '--project-type',
        type=str,
        choices=['single', 'fullstack', 'organization'],
        default='single',
        help='Project type: single language, fullstack, or organization (default: single)'
    )
    init_parser.add_argument(
        '--language',
        type=str,
        choices=['python', 'javascript', 'typescript', 'java', 'go', 'rust', 'csharp', 'php', 'ruby'],
        help='Primary programming language (for single) or backend language (for fullstack)'
    )
    init_parser.add_argument(
        '--frontend-language',
        type=str,
        choices=['javascript', 'typescript'],
        help='Frontend language for fullstack projects'
    )
    init_parser.add_argument(
        '--framework',
        type=str,
        choices=['fastapi', 'react', 'nodejs', 'electron'],
        help='Backend framework (for single) - e.g., fastapi for Python'
    )
    init_parser.add_argument(
        '--backend-framework',
        type=str,
        choices=['fastapi', 'express', 'spring', 'gin', 'actix', 'aspnet'],
        help='Backend framework for fullstack projects'
    )
    init_parser.add_argument(
        '--frontend-framework',
        type=str,
        choices=['react', 'vue', 'angular', 'svelte'],
        help='Frontend framework for fullstack projects'
    )
    init_parser.add_argument(
        '--agents',
        type=str,
        help='Comma-separated list of agents (e.g., poa,sma,deva_python,qaa,deva_claude_python)'
    )
    init_parser.add_argument(
        '--llm-provider',
        type=str,
        choices=['anthropic', 'openai', 'azure', 'local'],
        help='LLM provider to use (Note: When using Claude Code, model parameters are controlled by the IDE)'
    )
    init_parser.add_argument(
        '--claude-code',
        action='store_true',
        help='Optimize settings for Claude Code IDE (sets anthropic provider and claude-sonnet-4-0 model)'
    )
    init_parser.add_argument(
        '--default-model',
        type=str,
        help='Default model to use (e.g., claude-sonnet-4-0, gpt-4-turbo-preview)'
    )
    init_parser.add_argument(
        '--output-dir',
        type=str,
        default=get_default_output_dir(),
        help='Directory to create the project in (default: ~/AgenticProjects if in AgenticScrum, else current directory)'
    )
    init_parser.add_argument(
        '--enable-mcp',
        action='store_true',
        help='Enable MCP (Model Context Protocol) integration for persistent memory and enhanced search'
    )
    init_parser.add_argument(
        '--enable-search',
        action='store_true',
        help='Enable Perplexity search integration (requires PERPLEXITY_API_KEY environment variable)'
    )
    init_parser.add_argument(
        '--enable-qa',
        action='store_true',
        default=True,
        help='Enable autonomous QA validation system (enabled by default)'
    )
    init_parser.add_argument(
        '--disable-qa',
        action='store_true',
        help='Disable autonomous QA validation system'
    )
    init_parser.add_argument(
        '--qa-coverage-threshold',
        type=int,
        default=85,
        help='Minimum code coverage threshold for QA validation (default: 85)'
    )
    init_parser.add_argument(
        '--qa-max-performance-regression',
        type=int,
        default=20,
        help='Maximum allowed performance regression percentage (default: 20)'
    )
    init_parser.add_argument(
        '--organization-name',
        type=str,
        help='Name of the organization (required for organization project type)'
    )
    init_parser.add_argument(
        '--conversational',
        action='store_true',
        help='Start with conversational onboarding guided by POA (recommended for new users)'
    )
    
    # Add repository command
    addrepo_parser = subparsers.add_parser('add-repo', help='Add repository to existing organization')
    addrepo_parser.add_argument(
        '--organization-dir',
        type=str,
        required=True,
        help='Path to the organization directory'
    )
    addrepo_parser.add_argument(
        '--repo-name',
        type=str,
        required=True,
        help='Name of the repository to add'
    )
    addrepo_parser.add_argument(
        '--language',
        type=str,
        choices=['python', 'javascript', 'typescript', 'java', 'go', 'rust', 'csharp', 'php', 'ruby'],
        required=True,
        help='Primary programming language for the repository'
    )
    addrepo_parser.add_argument(
        '--framework',
        type=str,
        choices=['fastapi', 'express', 'spring', 'gin', 'actix', 'aspnet', 'react', 'vue', 'angular', 'svelte'],
        help='Framework for the repository'
    )
    addrepo_parser.add_argument(
        '--agents',
        type=str,
        required=True,
        help='Comma-separated list of agents for this repository'
    )
    
    # List repositories command
    listrepos_parser = subparsers.add_parser('list-repos', help='List repositories in organization')
    listrepos_parser.add_argument(
        '--organization-dir',
        type=str,
        required=True,
        help='Path to the organization directory'
    )
    
    # Retrofit command
    retrofit_parser = subparsers.add_parser('retrofit', help='Analyze existing project for AgenticScrum integration')
    retrofit_parser.add_argument(
        'project_path',
        type=str,
        help='Path to the existing project to analyze'
    )
    retrofit_parser.add_argument(
        '--output',
        '-o',
        type=str,
        help='Output directory for retrofit configuration (default: current directory)'
    )
    
    # Patch command
    patch_parser = subparsers.add_parser('patch', help='Apply patches to AgenticScrum framework')
    patch_parser.add_argument(
        'operation',
        choices=['update-all', 'update-security', 'add-background-agents', 'add-template', 'update-mcp', 'fix-cli', 'add-command', 'sync-changes', 'rollback', 'history', 'status'],
        help='Patch operation to perform'
    )
    patch_parser.add_argument(
        '--target',
        type=str,
        help='Target file or path for the operation'
    )
    patch_parser.add_argument(
        '--description',
        type=str,
        help='Description of the patch'
    )
    patch_parser.add_argument(
        '--agent-type',
        type=str,
        help='Agent type for template operations (e.g., deva_rust, qaa_advanced)'
    )
    patch_parser.add_argument(
        '--template-type',
        type=str,
        choices=['persona_rules', 'memory_patterns', 'search_patterns'],
        default='persona_rules',
        help='Type of template for add-template operation'
    )
    patch_parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without applying them'
    )
    patch_parser.add_argument(
        '--force',
        action='store_true',
        help='Force apply patch even with warnings'
    )
    patch_parser.add_argument(
        '--patch-id',
        type=str,
        help='Patch ID for rollback operation'
    )
    
    return parser


def interactive_mode():
    """Run the setup in interactive mode, prompting for required values."""
    print("Welcome to AgenticScrum Setup Utility!")
    print("=" * 50)
    
    # Project name
    project_name = input("Enter project name: ").strip()
    while not project_name:
        print("Project name is required.")
        project_name = input("Enter project name: ").strip()
    
    # Project type
    print("\nProject type:")
    print("  1. Single language project")
    print("  2. Fullstack project (backend + frontend)")
    print("  3. Organization (multi-repository management)")
    
    project_type_choice = input("Select project type [1]: ").strip() or "1"
    if project_type_choice == "2":
        project_type = 'fullstack'
    elif project_type_choice == "3":
        project_type = 'organization'
    else:
        project_type = 'single'
    
    if project_type == 'fullstack':
        # Fullstack setup
        print("\n=== Backend Configuration ===")
        print("\nAvailable backend languages:")
        backend_languages = ['python', 'javascript', 'typescript', 'java', 'go', 'rust', 'csharp']
        for i, lang in enumerate(backend_languages, 1):
            print(f"  {i}. {lang}")
        
        backend_choice = input("Select backend language (number or name): ").strip()
        if backend_choice.isdigit():
            idx = int(backend_choice) - 1
            backend_language = backend_languages[idx] if 0 <= idx < len(backend_languages) else 'python'
        else:
            backend_language = backend_choice if backend_choice in backend_languages else 'python'
        
        # Backend framework
        print("\nAvailable backend frameworks:")
        backend_frameworks = {
            'python': ['fastapi'],
            'javascript': ['express'],
            'typescript': ['express'],
            'java': ['spring'],
            'go': ['gin'],
            'rust': ['actix'],
            'csharp': ['aspnet']
        }
        
        available_backend_fw = backend_frameworks.get(backend_language, [])
        backend_framework = None
        if available_backend_fw:
            for i, fw in enumerate(available_backend_fw, 1):
                print(f"  {i}. {fw}")
            fw_choice = input("Select backend framework (Enter to skip): ").strip()
            if fw_choice:
                if fw_choice.isdigit():
                    idx = int(fw_choice) - 1
                    if 0 <= idx < len(available_backend_fw):
                        backend_framework = available_backend_fw[idx]
                elif fw_choice in available_backend_fw:
                    backend_framework = fw_choice
        
        print("\n=== Frontend Configuration ===")
        print("\nAvailable frontend languages:")
        print("  1. JavaScript")
        print("  2. TypeScript")
        
        frontend_choice = input("Select frontend language [2]: ").strip() or "2"
        frontend_language = 'typescript' if frontend_choice == "2" else 'javascript'
        
        # Frontend framework
        print("\nAvailable frontend frameworks:")
        frontend_frameworks = ['react', 'vue', 'angular', 'svelte']
        for i, fw in enumerate(frontend_frameworks, 1):
            print(f"  {i}. {fw}")
        
        fw_choice = input("Select frontend framework [1]: ").strip() or "1"
        if fw_choice.isdigit():
            idx = int(fw_choice) - 1
            frontend_framework = frontend_frameworks[idx] if 0 <= idx < len(frontend_frameworks) else 'react'
        else:
            frontend_framework = fw_choice if fw_choice in frontend_frameworks else 'react'
        
        # Set values for fullstack
        language = backend_language
        framework = None
        agents_default = f"poa,sma,deva_{backend_language},deva_{frontend_language},qaa,saa"
        
    elif project_type == 'organization':
        # Organization setup
        print("\n=== Organization Configuration ===")
        organization_name = input("Enter organization name: ").strip()
        while not organization_name:
            print("Organization name is required.")
            organization_name = input("Enter organization name: ").strip()
        
        print("\nOrganization agents:")
        print("  - organization_poa (Portfolio Product Owner)")
        print("  - organization_sma (Cross-project Scrum Master)")
        print("  - shared memory and coordination services")
        
        # Set default values for organization
        language = None  # Not applicable for organizations
        framework = None
        backend_language = None
        backend_framework = None
        frontend_language = None
        frontend_framework = None
        agents_default = "organization_poa,organization_sma"
        
    else:
        # Single language setup
        print("\nAvailable languages:")
        languages = ['python', 'javascript', 'typescript', 'java', 'go', 'rust', 'csharp', 'php', 'ruby']
        for i, lang in enumerate(languages, 1):
            print(f"  {i}. {lang}")
        
        language_choice = input("Select language (number or name): ").strip()
        if language_choice.isdigit():
            language_idx = int(language_choice) - 1
            if 0 <= language_idx < len(languages):
                language = languages[language_idx]
            else:
                language = 'python'
        else:
            language = language_choice if language_choice in languages else 'python'
        
        # Framework (optional)
        print("\nAvailable frameworks (optional, press Enter to skip):")
        framework_options = {
            'python': ['fastapi'],
            'javascript': ['react', 'nodejs', 'electron'],
            'typescript': ['react', 'nodejs', 'electron']
        }
        
        available_frameworks = framework_options.get(language, [])
        framework = None
        
        if available_frameworks:
            for i, fw in enumerate(available_frameworks, 1):
                print(f"  {i}. {fw}")
            
            framework_choice = input("Select framework (number, name, or Enter to skip): ").strip()
            if framework_choice:
                if framework_choice.isdigit():
                    fw_idx = int(framework_choice) - 1
                    if 0 <= fw_idx < len(available_frameworks):
                        framework = available_frameworks[fw_idx]
                else:
                    framework = framework_choice if framework_choice in available_frameworks else None
        
        # Set default values for single language
        backend_language = None
        backend_framework = None
        frontend_language = None
        frontend_framework = None
        agents_default = f"poa,sma,deva_{language},qaa"
    
    # Agents
    print("\nAvailable agents:")
    print("  - poa (ProductOwnerAgent)")
    print("  - sma (ScrumMasterAgent)")
    print("  - deva_python (Python DeveloperAgent)")
    print("  - deva_javascript (JavaScript DeveloperAgent)")
    print("  - deva_typescript (TypeScript DeveloperAgent)")
    print("  - deva_claude_python (Claude-specialized Python DeveloperAgent)")
    print("  - qaa (QAAgent)")
    print("  - saa (SecurityAuditAgent)")
    
    agents_input = input(f"Enter agents (comma-separated) [{agents_default}]: ").strip()
    agents = agents_input if agents_input else agents_default
    
    # Check if using Claude Code
    print("\nAre you using Claude Code? (Y/n): ", end='')
    claude_code_input = input().strip().lower()
    using_claude_code = claude_code_input != 'n'
    
    if using_claude_code:
        print("\nNote: Claude Code controls model parameters (temperature, max_tokens) directly.")
        print("The configuration will be optimized for Claude Code usage.")
        llm_provider = 'anthropic'
        default_model = 'claude-sonnet-4-0'
    else:
        # LLM Provider
        print("\nAvailable LLM providers:")
        providers = ['anthropic', 'openai', 'azure', 'local']
        for i, provider in enumerate(providers, 1):
            print(f"  {i}. {provider}")
        
        provider_choice = input("Select LLM provider (number or name) [1]: ").strip() or "1"
        if provider_choice.isdigit():
            provider_idx = int(provider_choice) - 1
            if 0 <= provider_idx < len(providers):
                llm_provider = providers[provider_idx]
            else:
                llm_provider = 'anthropic'
        else:
            llm_provider = provider_choice if provider_choice in providers else 'anthropic'
    
        # Model selection for Anthropic
        if llm_provider == 'anthropic':
            print("\nAvailable Claude models:")
            claude_models = [
                ('claude-opus-4-0', 'Most capable - Best for planning & complex analysis'),
                ('claude-sonnet-4-0', 'Balanced (Recommended) - Fast with 64K output'),
                ('claude-3-5-sonnet-latest', 'Previous generation - Still very capable'),
                ('claude-3-5-haiku-latest', 'Fastest - Good for simple tasks'),
            ]
            for i, (model, desc) in enumerate(claude_models, 1):
                print(f"  {i}. {model} - {desc}")
            
            model_choice = input("Select model (number or alias) [2]: ").strip() or "2"
            if model_choice.isdigit():
                model_idx = int(model_choice) - 1
                if 0 <= model_idx < len(claude_models):
                    default_model = claude_models[model_idx][0]
                else:
                    default_model = 'claude-sonnet-4-0'
            else:
                # Check if it's a valid model alias
                valid_models = [m[0] for m in claude_models]
                default_model = model_choice if model_choice in valid_models else 'claude-sonnet-4-0'
        else:
            # Default model for other providers
            model_suggestions = {
                'openai': 'gpt-4-turbo-preview',
                'azure': 'gpt-4',
                'local': 'llama2'
            }
            default_model = input(f"Default model (suggested: {model_suggestions.get(llm_provider, 'gpt-4')}): ").strip()
            if not default_model:
                default_model = model_suggestions.get(llm_provider, 'gpt-4')
    
    # MCP Integration
    print("\n=== MCP Integration (Model Context Protocol) ===")
    print("MCP enables persistent memory and enhanced search capabilities for agents.")
    print("This allows agents to learn from past experiences and access current information.")
    
    mcp_choice = input("Enable MCP integration? [Y/n]: ").strip().lower()
    enable_mcp = mcp_choice != 'n'
    
    enable_search = False
    if enable_mcp:
        print("\nMCP features available:")
        print("1. Persistent Memory - Agents remember past decisions and patterns")
        print("2. Web Search (Perplexity) - Access current information beyond training data")
        
        search_choice = input("\nEnable Perplexity search integration? (requires API key) [y/N]: ").strip().lower()
        enable_search = search_choice == 'y'
        
        if enable_search:
            import os
            if not os.environ.get('PERPLEXITY_API_KEY'):
                print("\nWarning: PERPLEXITY_API_KEY not found in environment.")
                print("You'll need to set it before using search features:")
                print("  export PERPLEXITY_API_KEY='your-key-here'")
    
    return {
        'project_name': project_name,
        'project_type': project_type,
        'language': language,
        'frontend_language': frontend_language,
        'framework': framework,
        'backend_framework': backend_framework,
        'frontend_framework': frontend_framework,
        'agents': agents,
        'llm_provider': llm_provider,
        'default_model': default_model,
        'output_dir': get_default_output_dir(),
        'enable_mcp': enable_mcp,
        'enable_search': enable_search,
        'organization_name': organization_name if project_type == 'organization' else None
    }


def validate_cli_arguments(args) -> List[str]:
    """Validate CLI arguments and return list of error messages."""
    errors = []
    
    if args.command == 'init':
        # Validate project name
        if args.project_name:
            if not args.project_name.strip():
                errors.append("Project name cannot be empty.")
            else:
                # Check for invalid characters
                invalid_chars = r'[<>:"/\\|?*\x00-\x1f]'
                if re.search(invalid_chars, args.project_name):
                    errors.append(
                        f"Project name '{args.project_name}' contains invalid characters. "
                        "Project names cannot contain: < > : \" / \\ | ? * or control characters. "
                        "Use only letters, numbers, hyphens, and underscores."
                    )
                
                # Check length
                if len(args.project_name) > 200:
                    errors.append(
                        f"Project name '{args.project_name}' is too long ({len(args.project_name)} characters). "
                        "Please use a name shorter than 200 characters."
                    )
                
                # Check reserved names
                reserved_names = {
                    'CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 'COM5',
                    'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2', 'LPT3', 'LPT4',
                    'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
                }
                if args.project_name.upper() in reserved_names:
                    errors.append(
                        f"Project name '{args.project_name}' is a reserved name on Windows. "
                        "Please choose a different name."
                    )
        
        # Validate agents
        if args.agents:
            known_agents = {
                'poa', 'sma', 'deva_python', 'deva_javascript', 'deva_typescript',
                'deva_java', 'deva_go', 'deva_rust', 'deva_csharp',
                'deva_claude_python', 'qaa', 'saa',
                'organization_poa', 'organization_sma'  # Organization-level agents
            }
            
            agent_list = [agent.strip() for agent in args.agents.split(',')]
            unknown_agents = []
            
            for agent in agent_list:
                if agent and agent not in known_agents:
                    unknown_agents.append(agent)
            
            if unknown_agents:
                errors.append(
                    f"Unknown agent types: {', '.join(unknown_agents)}. "
                    f"Valid agents are: {', '.join(sorted(known_agents))}. "
                    "Please check your agent list for typos."
                )
        
        # Validate fullstack requirements
        if args.project_type == 'fullstack':
            if args.frontend_language and args.frontend_language not in ['javascript', 'typescript']:
                errors.append(
                    f"Invalid frontend language '{args.frontend_language}'. "
                    "Supported frontend languages: javascript, typescript"
                )
            
            if args.backend_framework and args.language:
                valid_backend_frameworks = {
                    'python': ['fastapi'],
                    'javascript': ['express'],
                    'typescript': ['express'],
                    'java': ['spring'],
                    'go': ['gin'],
                    'rust': ['actix'],
                    'csharp': ['aspnet']
                }
                
                valid_frameworks = valid_backend_frameworks.get(args.language, [])
                if args.backend_framework not in valid_frameworks:
                    errors.append(
                        f"Backend framework '{args.backend_framework}' is not supported for {args.language}. "
                        f"Supported frameworks: {', '.join(valid_frameworks) if valid_frameworks else 'none'}"
                    )
        
        # Validate organization requirements
        if args.project_type == 'organization':
            if not args.organization_name:
                errors.append("Organization name is required for organization project type.")
            elif args.organization_name:
                # Apply same validation as project names
                invalid_chars = r'[<>:"/\\|?*\x00-\x1f]'
                if re.search(invalid_chars, args.organization_name):
                    errors.append(
                        f"Organization name '{args.organization_name}' contains invalid characters. "
                        "Organization names cannot contain: < > : \" / \\ | ? * or control characters. "
                        "Use only letters, numbers, hyphens, and underscores."
                    )
                
                if len(args.organization_name) > 200:
                    errors.append(
                        f"Organization name '{args.organization_name}' is too long ({len(args.organization_name)} characters). "
                        "Please use a name shorter than 200 characters."
                    )
        
        # Validate output directory path
        if args.output_dir:
            try:
                output_path = Path(args.output_dir)
                # Check for path traversal
                if '..' in str(output_path):
                    errors.append(
                        "Path traversal detected in output directory. "
                        "Relative paths with '..' are not allowed for security reasons."
                    )
            except Exception as e:
                errors.append(f"Invalid output directory path: {e}")
    
    return errors


def main():
    """Main entry point for the CLI."""
    parser = parse_arguments()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    if args.command == 'init':
        # Handle conversational mode
        if hasattr(args, 'conversational') and args.conversational:
            from .conversational_onboarding import ConversationalOnboarding
            
            print("\n🤖 Starting conversational project setup with POA guidance...\n")
            
            # Start conversational onboarding
            onboarding = ConversationalOnboarding(output_dir=args.output_dir)
            initial_prompt = onboarding.start_conversation()
            print(initial_prompt)
            print("\n" + "="*70 + "\n")
            
            # Simulation message for non-interactive environment
            print("💡 Note: In a real Claude Code session, you would continue the conversation here.")
            print("   The POA would guide you through natural dialogue to understand your project needs.\n")
            
            # For now, show what would happen
            if onboarding.is_retrofit:
                print("📊 Codebase Analysis Results:")
                print(f"   - Language: {onboarding.existing_analysis.get('language', 'Unknown')}")
                print(f"   - Project Type: {onboarding.existing_analysis.get('project_type', 'Unknown')}")
                print(f"   - Size: {onboarding.existing_analysis.get('size', {}).get('files', 0)} files")
                print("\n✅ Your existing code will remain untouched.")
                print("   AgenticScrum will add supportive structure around it.\n")
            else:
                print("📝 Example conversation flow:")
                print("   User: 'I want to build a restaurant order management system'")
                print("   POA: 'That sounds interesting! What challenges are you solving?'")
                print("   User: 'Orders from multiple delivery apps are hard to track'")
                print("   POA: 'I see. How many restaurants will use this system?'")
                print("   ... (conversation continues)\n")
            
            print("🎯 The POA would then:")
            print("   1. Extract requirements from your natural description")
            print("   2. Identify any gaps and ask clarifying questions")
            print("   3. Create a structured PRD and project plan")
            print("   4. Generate epics and initial user stories")
            print("   5. Set up your project with all necessary files\n")
            
            print("To use conversational mode in Claude Code:")
            print("   1. Open Claude Code in your project directory")
            print("   2. Say: 'I want to create a new project'")
            print("   3. Have a natural conversation about your idea")
            print("   4. POA will handle all the setup automatically\n")
            
            sys.exit(0)
        
        # Handle --claude-code flag
        if hasattr(args, 'claude_code') and args.claude_code:
            args.llm_provider = 'anthropic'
            args.default_model = 'claude-sonnet-4-0'
            print("Claude Code mode enabled: Using anthropic provider with claude-sonnet-4-0 model")
        
        # Validate CLI arguments early
        validation_errors = validate_cli_arguments(args)
        if validation_errors:
            print("❌ Configuration errors found:")
            for error in validation_errors:
                print(f"  - {error}")
            print("\nPlease fix these issues and try again, or run without arguments for interactive mode.")
            sys.exit(1)
        
        # Check if we have all required arguments (different for organization type)
        if args.project_type == 'organization':
            required_args = [args.project_name, args.organization_name, args.llm_provider, args.default_model]
            # Set default agents for organization if not specified
            if not args.agents:
                args.agents = 'organization_poa,organization_sma'
        else:
            required_args = [args.project_name, args.language, args.agents, args.llm_provider, args.default_model]
            
        if not all(required_args):
            print("Running in interactive mode...")
            config = interactive_mode()
        else:
            # Validate fullstack requirements
            if args.project_type == 'fullstack':
                if not args.frontend_language:
                    print("Error: --frontend-language is required for fullstack projects")
                    sys.exit(1)
                if not args.frontend_framework:
                    print("Error: --frontend-framework is required for fullstack projects")
                    sys.exit(1)
            
            # Handle QA configuration
            enable_qa = getattr(args, 'enable_qa', True)
            if getattr(args, 'disable_qa', False):
                enable_qa = False
            
            config = {
                'project_name': args.project_name,
                'project_type': args.project_type,
                'language': args.language,
                'frontend_language': args.frontend_language,
                'framework': args.framework,
                'backend_framework': args.backend_framework,
                'frontend_framework': args.frontend_framework,
                'agents': args.agents,
                'llm_provider': args.llm_provider,
                'default_model': args.default_model,
                'output_dir': args.output_dir,
                'enable_mcp': getattr(args, 'enable_mcp', False),
                'enable_search': getattr(args, 'enable_search', False),
                'enable_qa': enable_qa,
                'qa_coverage_threshold': getattr(args, 'qa_coverage_threshold', 85),
                'qa_max_performance_regression': getattr(args, 'qa_max_performance_regression', 20),
                'organization_name': getattr(args, 'organization_name', None)
            }
        
        # Create the setup core instance and run
        try:
            setup = SetupCore(config)
            setup.create_project()
            print(f"\n✅ Project '{config['project_name']}' created successfully!")
            print(f"📁 Location: {Path(config['output_dir']) / config['project_name']}")
            print("\nNext steps:")
            print(f"  1. cd {config['project_name']}")
            print("  2. Review the generated structure and configuration")
            print("  3. ./init.sh help  # To see available commands")
        except ValueError as e:
            print(f"\n❌ Configuration error: {e}")
            print("\nTroubleshooting tips:")
            print("  - Check that your project name contains only valid characters")
            print("  - Verify that all agent types are spelled correctly")
            print("  - Ensure the output directory path is valid and accessible")
            sys.exit(1)
        except RuntimeError as e:
            print(f"\n❌ Project creation failed: {e}")
            print("\nTroubleshooting tips:")
            print("  - Check disk space and file permissions")
            print("  - Ensure the output directory is writable")
            print("  - Try a different project name or location")
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            print("\nIf this problem persists, please report it at:")
            print("  https://github.com/anthropics/AgenticScrum/issues")
            sys.exit(1)
    
    elif args.command == 'add-repo':
        # Add repository to existing organization
        try:
            from .repository_manager import RepositoryManager
            
            org_path = Path(args.organization_dir)
            if not org_path.exists():
                print(f"❌ Error: Organization directory '{org_path}' not found")
                sys.exit(1)
            
            if not (org_path / '.agentic' / 'agentic_config.yaml').exists():
                print(f"❌ Error: '{org_path}' is not a valid AgenticScrum organization")
                sys.exit(1)
            
            repo_manager = RepositoryManager(org_path)
            repo_config = {
                'repo_name': args.repo_name,
                'language': args.language,
                'framework': args.framework,
                'agents': args.agents
            }
            
            repo_path = repo_manager.add_repository(repo_config)
            print(f"\n✅ Repository '{args.repo_name}' added successfully!")
            print(f"📁 Location: {repo_path}")
            print(f"🔗 Integrated with organization agents at {org_path}")
            
        except ImportError:
            print("❌ Error: Repository management not available")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Error adding repository: {e}")
            sys.exit(1)
    
    elif args.command == 'list-repos':
        # List repositories in organization
        try:
            org_path = Path(args.organization_dir)
            if not org_path.exists():
                print(f"❌ Error: Organization directory '{org_path}' not found")
                sys.exit(1)
            
            projects_dir = org_path / 'projects'
            if not projects_dir.exists():
                print(f"📂 No repositories found in organization at {org_path}")
                sys.exit(0)
            
            repos = [d for d in projects_dir.iterdir() if d.is_dir()]
            if not repos:
                print(f"📂 No repositories found in organization at {org_path}")
            else:
                print(f"📂 Repositories in organization '{org_path.name}':")
                for repo in sorted(repos):
                    config_file = repo / 'agentic_config.yaml'
                    if config_file.exists():
                        print(f"  ✅ {repo.name}")
                    else:
                        print(f"  ⚠️  {repo.name} (missing config)")
                        
        except Exception as e:
            print(f"❌ Error listing repositories: {e}")
            sys.exit(1)
    
    elif args.command == 'retrofit':
        # Import retrofit script
        try:
            # Add scripts directory to path
            scripts_path = Path(__file__).parent.parent / 'scripts'
            sys.path.insert(0, str(scripts_path))
            from retrofit_project import main as retrofit_main
            
            # Run retrofit analysis
            retrofit_args = ['assess', '--path', args.project_path]
            if args.output:
                retrofit_args.extend(['--output', args.output])
                
            print(f"🔍 Analyzing project at {args.project_path} for AgenticScrum integration...")
            retrofit_main(retrofit_args)
        except ImportError:
            print("❌ Error: retrofit_project.py not found in scripts directory")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Error during retrofit analysis: {e}")
            sys.exit(1)
    
    elif args.command == 'patch':
        # Patch command handler
        try:
            from .patching import AgenticPatcher
            from .patching.operations import (
                AddTemplateOperation, UpdateMCPOperation, FixCLIOperation,
                AddCommandOperation, SyncChangesOperation
            )
            
            # Initialize patcher
            patcher = AgenticPatcher()
            
            if args.operation == 'status':
                # Show patcher status
                status = patcher.get_status()
                print(f"🔧 AgenticScrum Patching System Status")
                print(f"📁 Framework: {status['framework_path']}")
                print(f"📊 Total patches applied: {status['total_patches']}")
                print(f"🗂️  Git available: {'✅' if status['git_available'] else '❌'}")
                print(f"💾 Backups enabled: {'✅' if status['backup_enabled'] else '❌'}")
                
                if status['recent_patches']:
                    print(f"\n📝 Recent patches:")
                    for patch in status['recent_patches']:
                        print(f"  • {patch['patch_id'][:8]} - {patch['operation']} ({patch['timestamp'][:10]})")
            
            elif args.operation == 'history':
                # Show patch history
                patches = patcher.get_patch_history()
                if not patches:
                    print("📝 No patches applied yet")
                else:
                    print(f"📝 Patch History ({len(patches)} patches)")
                    for patch in patches:
                        print(f"  {patch.patch_id[:8]} - {patch.operation}")
                        print(f"    📅 {patch.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
                        print(f"    📄 {patch.description}")
                        print(f"    📁 Files: {len(patch.files_modified)}")
                        if patch.git_commit:
                            print(f"    🌿 Git: {patch.git_commit[:8]}")
                        print()
            
            elif args.operation == 'rollback':
                # Rollback a patch
                if not args.patch_id:
                    print("❌ Error: --patch-id is required for rollback operation")
                    sys.exit(1)
                
                print(f"🔄 Rolling back patch {args.patch_id}...")
                patcher.rollback_patch(args.patch_id)
            
            elif args.operation == 'update-all':
                # Update all operation - comprehensive project update
                from .patching.operations.update_all import update_all
                
                try:
                    print("🔄 Applying comprehensive project update...")
                    print(f"📁 Project: {Path.cwd()}")
                    print(f"🔧 Framework: {patcher.framework_path}")
                    print("")
                    
                    result = update_all(patcher, dry_run=args.dry_run)
                    if result.success:
                        print("✅ Update-all operation completed successfully!")
                    else:
                        print(f"❌ Update-all operation failed: {result.message}")
                        sys.exit(1)
                        
                except Exception as e:
                    print(f"❌ Error in update-all operation: {str(e)}")
                    print("💡 Tip: Use --dry-run to preview changes before applying")
                    sys.exit(1)
            
            elif args.operation == 'add-template':
                # Add template operation
                if not args.target:
                    print("❌ Error: --target is required for add-template operation")
                    sys.exit(1)
                if not args.agent_type:
                    print("❌ Error: --agent-type is required for add-template operation")
                    sys.exit(1)
                
                template_op = AddTemplateOperation(patcher.framework_path, patcher.validator)
                
                def patch_function():
                    target_path = Path(args.target)
                    return template_op.add_template(args.agent_type, target_path, args.template_type)
                
                description = args.description or f"Add {args.template_type} template for {args.agent_type}"
                target_path = Path(args.target)
                files_to_modify = [patcher.framework_path / 'agentic_scrum_setup' / 'templates' / args.agent_type / f'{args.template_type}.yaml.j2']
                
                patcher.apply_patch('add-template', description, patch_function, files_to_modify, args.dry_run)
            
            elif args.operation == 'update-mcp':
                # Update MCP operation - auto-detect target if not provided
                target_path = Path(args.target) if args.target else Path.cwd()
                
                if not target_path.exists():
                    print(f"❌ Error: Target path does not exist: {target_path}")
                    sys.exit(1)
                
                mcp_op = UpdateMCPOperation(patcher.framework_path, patcher.validator)
                
                def patch_function():
                    if target_path.is_dir():
                        # Adding MCP to project
                        return mcp_op.add_mcp_to_project(target_path)
                    else:
                        # Updating MCP service
                        return mcp_op.update_mcp_service(target_path)
                
                description = args.description or f"Update MCP configuration/service"
                
                if target_path.is_dir():
                    files_to_modify = [target_path / '.mcp.json', target_path / '.mcp' / 'services']
                else:
                    files_to_modify = [patcher.framework_path / 'agentic_scrum_setup' / 'templates' / 'claude' / target_path.name]
                
                patcher.apply_patch('update-mcp', description, patch_function, files_to_modify, args.dry_run)
            
            elif args.operation == 'fix-cli':
                # Fix CLI operation
                cli_op = FixCLIOperation(patcher.framework_path, patcher.validator)
                
                def patch_function():
                    if args.target and Path(args.target).exists():
                        # Apply patch file
                        return cli_op.apply_cli_patch(Path(args.target))
                    else:
                        # Apply common fixes
                        description = args.description or "Apply common CLI fixes"
                        return cli_op.fix_argument_parsing(description)
                
                description = args.description or "Fix CLI issues"
                files_to_modify = [patcher.framework_path / 'agentic_scrum_setup' / 'cli.py']
                
                patcher.apply_patch('fix-cli', description, patch_function, files_to_modify, args.dry_run)
            
            elif args.operation == 'add-command':
                # Add command operation
                if not args.target:
                    print("❌ Error: --target is required for add-command operation (command name)")
                    sys.exit(1)
                
                cmd_op = AddCommandOperation(patcher.framework_path, patcher.validator)
                
                def patch_function():
                    # Basic command configuration
                    command_config = {
                        'description': args.description or f"{args.target} command",
                        'arguments': [],  # Can be extended
                        'handler': f'handle_{args.target}_command'
                    }
                    return cmd_op.add_cli_command(args.target, command_config)
                
                description = args.description or f"Add {args.target} command to CLI"
                files_to_modify = [patcher.framework_path / 'agentic_scrum_setup' / 'cli.py']
                
                patcher.apply_patch('add-command', description, patch_function, files_to_modify, args.dry_run)
            
            elif args.operation == 'sync-changes':
                # Sync changes operation - auto-detect target if not provided
                target_path = Path(args.target) if args.target else Path.cwd()
                
                if not target_path.exists():
                    print(f"❌ Error: Target path does not exist: {target_path}")
                    sys.exit(1)
                
                sync_op = SyncChangesOperation(patcher.framework_path, patcher.validator)
                
                def patch_function():
                    return sync_op.sync_from_project(target_path)
                
                description = args.description or f"Sync changes from {target_path.name}"
                
                # Execute sync operation directly (doesn't use standard patch system)
                try:
                    if args.dry_run:
                        print("🔍 DRY RUN: Sync changes operation")
                        print(f"📁 Source project: {target_path}")
                        print(f"🎯 Framework: {patcher.framework_path}")
                        print("ℹ️  No changes would be applied in dry run mode")
                    else:
                        modified_files = sync_op.sync_from_project(target_path)
                        print(f"✅ Synced {len(modified_files)} files from {target_path.name}")
                        
                        if modified_files:
                            print("📝 Modified framework files:")
                            for file_path in modified_files:
                                rel_path = file_path.relative_to(patcher.framework_path)
                                print(f"  • {rel_path}")
                except Exception as e:
                    print(f"❌ Error in sync-changes operation: {str(e)}")
                    print("💡 Tip: Use --dry-run to preview changes before applying")
                    sys.exit(1)
            
            elif args.operation == 'update-security':
                # Security update operation - comprehensive security training update
                from .patching.operations.update_security import update_security
                
                try:
                    print("🔒 Security Training Update")
                    print(f"📁 Project: {Path.cwd()}")
                    print(f"🔧 Framework: {patcher.framework_path}")
                    print("")
                    
                    result = update_security(patcher, dry_run=args.dry_run)
                    if result.success:
                        if not args.dry_run:
                            print("\n✅ Security update completed successfully!")
                    else:
                        print(f"❌ Security update failed: {result.message}")
                        sys.exit(1)
                        
                except Exception as e:
                    print(f"❌ Error in security update operation: {str(e)}")
                    print("💡 Tip: Use --dry-run to preview changes before applying")
                    sys.exit(1)
            
            else:
                print(f"❌ Error: Unknown patch operation: {args.operation}")
                sys.exit(1)
                
        except Exception as e:
            print(f"❌ Error in patch command: {e}")
            if hasattr(args, 'dry_run') and not args.dry_run:
                print("💡 Tip: Use --dry-run to preview changes before applying")
            sys.exit(1)


if __name__ == "__main__":
    main()