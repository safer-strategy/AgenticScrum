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
        description='AgenticScrum Project Setup Utility - Initialize AI-driven development projects'
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
        '--language',
        type=str,
        choices=['python', 'javascript', 'typescript', 'java', 'go', 'rust', 'csharp', 'php', 'ruby'],
        help='Primary programming language for the project'
    )
    init_parser.add_argument(
        '--framework',
        type=str,
        choices=['fastapi', 'react', 'nodejs', 'electron'],
        help='Optional framework to use (e.g., fastapi for Python, react for JS/TS)'
    )
    init_parser.add_argument(
        '--agents',
        type=str,
        help='Comma-separated list of agents (e.g., poa,sma,deva_python,qaa,deva_claude_python)'
    )
    init_parser.add_argument(
        '--llm-provider',
        type=str,
        choices=['openai', 'anthropic', 'azure', 'local'],
        help='LLM provider to use'
    )
    init_parser.add_argument(
        '--default-model',
        type=str,
        help='Default model to use (e.g., gpt-4-turbo-preview, claude-3-opus)'
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
    
    # Language
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
    
    # Agents
    print("\nAvailable agents:")
    print("  - poa (ProductOwnerAgent)")
    print("  - sma (ScrumMasterAgent)")
    print("  - deva_python (Python DeveloperAgent)")
    print("  - deva_javascript (JavaScript DeveloperAgent)")
    print("  - deva_claude_python (Claude-specialized Python DeveloperAgent)")
    print("  - qaa (QAAgent)")
    
    agents_input = input("Enter agents (comma-separated, e.g., poa,sma,deva_python,qaa): ").strip()
    agents = agents_input if agents_input else "poa,sma,deva_python,qaa"
    
    # LLM Provider
    print("\nAvailable LLM providers:")
    providers = ['openai', 'anthropic', 'azure', 'local']
    for i, provider in enumerate(providers, 1):
        print(f"  {i}. {provider}")
    
    provider_choice = input("Select LLM provider (number or name): ").strip()
    if provider_choice.isdigit():
        provider_idx = int(provider_choice) - 1
        if 0 <= provider_idx < len(providers):
            llm_provider = providers[provider_idx]
        else:
            llm_provider = 'openai'
    else:
        llm_provider = provider_choice if provider_choice in providers else 'openai'
    
    # Default model
    model_suggestions = {
        'openai': 'gpt-4-turbo-preview',
        'anthropic': 'claude-3-opus-20240229',
        'azure': 'gpt-4',
        'local': 'llama2'
    }
    default_model = input(f"Default model (suggested: {model_suggestions.get(llm_provider, 'gpt-4')}): ").strip()
    if not default_model:
        default_model = model_suggestions.get(llm_provider, 'gpt-4')
    
    return {
        'project_name': project_name,
        'language': language,
        'framework': framework,
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
        # Check if we have all required arguments
        if not all([args.project_name, args.language, args.agents, args.llm_provider, args.default_model]):
            print("Running in interactive mode...")
            config = interactive_mode()
        else:
            config = {
                'project_name': args.project_name,
                'language': args.language,
                'framework': args.framework,
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