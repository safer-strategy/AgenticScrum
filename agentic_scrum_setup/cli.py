#!/usr/bin/env python3
"""Command-line interface for AgenticScrum setup utility."""

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from .setup_core import SetupCore


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
        choices=['single', 'fullstack'],
        default='single',
        help='Project type: single language or fullstack (default: single)'
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
        default='.',
        help='Directory to create the project in (default: current directory)'
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
    
    project_type_choice = input("Select project type [1]: ").strip() or "1"
    project_type = 'fullstack' if project_type_choice == "2" else 'single'
    
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
        'output_dir': '.'
    }


def main():
    """Main entry point for the CLI."""
    parser = parse_arguments()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    if args.command == 'init':
        # Handle --claude-code flag
        if hasattr(args, 'claude_code') and args.claude_code:
            args.llm_provider = 'anthropic'
            args.default_model = 'claude-sonnet-4-0'
            print("Claude Code mode enabled: Using anthropic provider with claude-sonnet-4-0 model")
        
        # Check if we have all required arguments
        if not all([args.project_name, args.language, args.agents, args.llm_provider, args.default_model]):
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
                'output_dir': args.output_dir
            }
        
        # Create the setup core instance and run
        setup = SetupCore(config)
        try:
            setup.create_project()
            print(f"\n✅ Project '{config['project_name']}' created successfully!")
            print(f"📁 Location: {Path(config['output_dir']) / config['project_name']}")
            print("\nNext steps:")
            print(f"  1. cd {config['project_name']}")
            print("  2. Review the generated structure and configuration")
            print("  3. ./init.sh help  # To see available commands")
        except Exception as e:
            print(f"\n❌ Error creating project: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()