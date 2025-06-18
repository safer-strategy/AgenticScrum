"""Add template operation for AgenticScrum patching system.

This module handles adding new agent templates to the framework,
including validation, proper placement, and registration.
"""

import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional

from ..validation import PatchValidator, ValidationResult


class AddTemplateOperation:
    """Handles adding new agent templates to the framework."""
    
    def __init__(self, framework_path: Path, validator: PatchValidator):
        """Initialize the operation.
        
        Args:
            framework_path: Path to AgenticScrum framework
            validator: Patch validator instance
        """
        self.framework_path = framework_path
        self.validator = validator
        self.templates_dir = framework_path / 'agentic_scrum_setup' / 'templates'
    
    def add_template(self, agent_type: str, template_file: Path, 
                    template_type: str = 'persona_rules') -> List[Path]:
        """Add a new agent template to the framework.
        
        Args:
            agent_type: Type of agent (e.g., 'deva_rust', 'qaa_advanced')
            template_file: Path to template file to add
            template_type: Type of template ('persona_rules', 'memory_patterns', etc.)
            
        Returns:
            List of files that were modified/created
        """
        if not template_file.exists():
            raise ValueError(f"Template file not found: {template_file}")
        
        # Validate template file
        validation_result = self.validator.validate_template_file(template_file)
        if not validation_result.is_valid:
            raise ValueError(f"Template validation failed: {validation_result.error_message}")
        
        # Determine target directory
        agent_template_dir = self.templates_dir / agent_type
        agent_template_dir.mkdir(parents=True, exist_ok=True)
        
        # Determine target filename
        if template_type == 'persona_rules':
            target_filename = 'persona_rules.yaml.j2'
        elif template_type == 'memory_patterns':
            target_filename = 'memory_patterns.yaml.j2'
        elif template_type == 'search_patterns':
            target_filename = 'search_patterns.yaml.j2'
        else:
            # Use original filename with .j2 extension if not present
            if template_file.suffix != '.j2':
                target_filename = template_file.name + '.j2'
            else:
                target_filename = template_file.name
        
        target_path = agent_template_dir / target_filename
        
        # Copy template file
        shutil.copy2(template_file, target_path)
        
        modified_files = [target_path]
        
        # Update agent registry if needed
        registry_files = self._update_agent_registry(agent_type)
        modified_files.extend(registry_files)
        
        return modified_files
    
    def add_template_content(self, agent_type: str, template_content: str,
                           template_type: str = 'persona_rules') -> List[Path]:
        """Add a new agent template from content string.
        
        Args:
            agent_type: Type of agent
            template_content: Template content as string
            template_type: Type of template
            
        Returns:
            List of files that were modified/created
        """
        # Create temporary file to validate content
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml.j2', delete=False) as f:
            f.write(template_content)
            temp_path = Path(f.name)
        
        try:
            # Validate content
            validation_result = self.validator.validate_file_content(temp_path, template_content)
            if not validation_result.is_valid:
                raise ValueError(f"Template content validation failed: {validation_result.error_message}")
            
            # Use add_template with temporary file
            return self.add_template(agent_type, temp_path, template_type)
        finally:
            # Clean up temporary file
            if temp_path.exists():
                temp_path.unlink()
    
    def add_language_support(self, language: str, framework: Optional[str] = None) -> List[Path]:
        """Add complete language support with templates.
        
        Args:
            language: Programming language to add support for
            framework: Optional framework for the language
            
        Returns:
            List of files that were modified/created
        """
        modified_files = []
        
        # Create basic developer agent template
        agent_type = f'deva_{language}'
        template_content = self._generate_language_template(language, framework)
        
        files = self.add_template_content(agent_type, template_content)
        modified_files.extend(files)
        
        # Add language-specific directories if they don't exist
        lang_template_dir = self.templates_dir / language
        lang_template_dir.mkdir(exist_ok=True)
        
        # Create basic project templates for the language
        project_templates = self._generate_project_templates(language, framework)
        for template_name, content in project_templates.items():
            template_path = lang_template_dir / template_name
            template_path.write_text(content)
            modified_files.append(template_path)
        
        return modified_files
    
    def _update_agent_registry(self, agent_type: str) -> List[Path]:
        """Update agent registry to include new agent type.
        
        Args:
            agent_type: Type of agent to register
            
        Returns:
            List of files that were modified
        """
        modified_files = []
        
        # Update CLI.py to include new agent in choices
        cli_file = self.framework_path / 'agentic_scrum_setup' / 'cli.py'
        if cli_file.exists():
            content = cli_file.read_text()
            
            # Find known_agents set and add new agent
            if f"'{agent_type}'" not in content:
                # Look for known_agents definition
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if 'known_agents = {' in line:
                        # Find the closing brace
                        for j in range(i, len(lines)):
                            if '}' in lines[j] and 'known_agents' in lines[i:j+1]:
                                # Insert new agent before closing brace
                                indent = '                '  # Match existing indentation
                                lines.insert(j, f"{indent}'{agent_type}',")
                                break
                        break
                
                # Write back updated content
                cli_file.write_text('\n'.join(lines))
                modified_files.append(cli_file)
        
        return modified_files
    
    def _generate_language_template(self, language: str, framework: Optional[str] = None) -> str:
        """Generate a basic template for a new language.
        
        Args:
            language: Programming language
            framework: Optional framework
            
        Returns:
            Template content string
        """
        framework_part = f" and {framework}" if framework else ""
        
        template = f'''# {language.title()} Developer Agent{framework_part}
role: "Developer Agent - {language.title()} Specialist"
goal: "Generate high-quality, idiomatic {language} code{framework_part}"
backstory: |
  You are an expert {language} developer with deep knowledge of the language's
  best practices, patterns, and ecosystem{framework_part}.

capabilities:
  - "{language.title()} language expertise"
  - "Code optimization and performance"
  - "Testing and debugging"'''

        if framework:
            template += f'\n  - "{framework} framework expertise"'
        
        template += f'''
  - "Security best practices"

rules:
  - "ALWAYS write clean, readable {language} code"
  - "ALWAYS include appropriate error handling"
  - "ALWAYS write tests for new functionality"
  - "PREFER idiomatic {language} patterns"'''

        if framework:
            template += f'\n  - "FOLLOW {framework} best practices and conventions"'
        
        template += f'''
  - "DOCUMENT complex logic with clear comments"

tools:
  - "{{{{ project_name }}}}_memory"
  - "{{{{ project_name }}}}_search"

memory_patterns:
  code_patterns:
    - "Remember successful {language} implementations"
    - "Track common bugs and their solutions"
    - "Store performance optimization techniques"
  
  learning_triggers:
    - "New {language} language features encountered"
    - "Framework updates or changes"
    - "Performance improvements discovered"

search_integration:
  triggers:
    - "Need current {language} best practices"
    - "Looking for {language} library recommendations"'''

        if framework:
            template += f'\n    - "Need {framework} documentation or examples"'
        
        template += '''
    - "Performance optimization techniques"
    - "Security vulnerability information"

context_sharing:
  - "Share {language} patterns with other developer agents"
  - "Coordinate on multi-language projects"
  - "Report framework updates to team"

quality_standards:
  code_style: "Follow {language} community standards"
  testing: "Comprehensive unit and integration tests"
  documentation: "Clear docstrings and comments"
  security: "Follow OWASP guidelines"'''

        return template.format(language=language)
    
    def _generate_project_templates(self, language: str, framework: Optional[str] = None) -> Dict[str, str]:
        """Generate basic project templates for a language.
        
        Args:
            language: Programming language
            framework: Optional framework
            
        Returns:
            Dictionary of template name -> content
        """
        templates = {}
        
        # Basic gitignore template
        if language == 'python':
            templates['gitignore.j2'] = '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Testing
.pytest_cache/
.coverage
htmlcov/

# Environment
.env
.env.local'''

        elif language == 'javascript' or language == 'typescript':
            templates['gitignore.j2'] = '''# Dependencies
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Production builds
/dist
/build

# Environment variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db'''

        # Basic README template
        templates['README.md.j2'] = f'''# {{{{ project_name }}}}

{language.title()} project generated with AgenticScrum.

## Setup

[Setup instructions for {language}]

## Development

[Development workflow for {language}]

## Testing

[Testing instructions for {language}]
'''
        
        return templates