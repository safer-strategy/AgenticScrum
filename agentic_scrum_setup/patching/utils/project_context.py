"""Project context loader for template rendering in patching system."""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional


def load_project_context(project_path: Path) -> Dict[str, Any]:
    """
    Load project context for template rendering.
    
    Reads the project's agentic_config.yaml to extract template variables
    like project_name, language, agents, etc.
    
    Args:
        project_path: Path to the project being patched
        
    Returns:
        Dictionary of template variables for Jinja2 rendering
    """
    config_file = project_path / "agentic_config.yaml"
    
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f) or {}
                
            # Extract template variables with safe defaults
            context = {
                'project_name': config.get('project_name', project_path.name),
                'language': config.get('language', 'python'),
                'agents': config.get('agents', ['poa', 'sma', 'deva_python', 'qaa']),
                'enable_search': config.get('enable_search', False),
                'enable_mcp': config.get('enable_mcp', True),
                'llm_provider': config.get('llm_provider', 'anthropic'),
                'default_model': config.get('default_model', 'claude-sonnet-4-0'),
                'project_type': config.get('project_type', 'single'),
                'organization_name': config.get('organization_name', ''),
            }
            
            # Handle backend/frontend for fullstack projects
            if context['project_type'] == 'fullstack':
                context['backend_framework'] = config.get('backend_framework', 'fastapi')
                context['frontend_framework'] = config.get('frontend_framework', 'react')
                context['frontend_language'] = config.get('frontend_language', 'typescript')
            else:
                context['framework'] = config.get('framework', 'fastapi' if context['language'] == 'python' else '')
                
        except (yaml.YAMLError, IOError) as e:
            print(f"Warning: Could not load project config: {e}")
            context = _get_default_context(project_path)
    else:
        print(f"Info: No agentic_config.yaml found, using defaults")
        context = _get_default_context(project_path)
    
    # Add Jinja2 filters that might be used in templates
    context['tojson'] = lambda x: str(x) if isinstance(x, list) else x
    
    return context


def _get_default_context(project_path: Path) -> Dict[str, Any]:
    """Get default context when config file is missing."""
    return {
        'project_name': project_path.name,
        'language': 'python',
        'agents': ['poa', 'sma', 'deva_python', 'qaa'],
        'enable_search': False,
        'enable_mcp': True,
        'llm_provider': 'anthropic',
        'default_model': 'claude-sonnet-4-0',
        'project_type': 'single',
        'framework': 'fastapi',
        'organization_name': ''
    }


def detect_project_language(project_path: Path) -> Optional[str]:
    """
    Detect project language from file extensions if not in config.
    
    Args:
        project_path: Path to project
        
    Returns:
        Detected language or None
    """
    language_indicators = {
        'python': ['*.py', 'requirements.txt', 'setup.py', 'pyproject.toml'],
        'javascript': ['*.js', 'package.json', '*.jsx'],
        'typescript': ['*.ts', '*.tsx', 'tsconfig.json'],
        'java': ['*.java', 'pom.xml', 'build.gradle'],
        'go': ['*.go', 'go.mod'],
        'rust': ['*.rs', 'Cargo.toml'],
        'csharp': ['*.cs', '*.csproj'],
        'php': ['*.php', 'composer.json'],
        'ruby': ['*.rb', 'Gemfile']
    }
    
    for language, patterns in language_indicators.items():
        for pattern in patterns:
            if pattern.startswith('*'):
                # File extension check
                if list(project_path.rglob(pattern)):
                    return language
            else:
                # Specific file check
                if (project_path / pattern).exists():
                    return language
    
    return None