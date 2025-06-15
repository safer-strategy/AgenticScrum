"""Core setup functionality for AgenticScrum projects."""

import os
import stat
import shutil
from pathlib import Path
from typing import Dict, List, Optional
from jinja2 import Environment, FileSystemLoader, Template


class SetupCore:
    """Core class for setting up AgenticScrum projects."""
    
    def __init__(self, config: Dict[str, str]):
        """Initialize the setup core with configuration.
        
        Args:
            config: Dictionary containing project configuration
        """
        self.config = config
        self.project_name = config['project_name']
        self.language = config['language']
        self.agents = config['agents'].split(',')
        self.llm_provider = config['llm_provider']
        self.default_model = config['default_model']
        self.output_dir = Path(config['output_dir'])
        self.project_path = self.output_dir / self.project_name
        
        # Setup Jinja2 environment
        template_dir = Path(__file__).parent / 'templates'
        self.jinja_env = Environment(
            loader=FileSystemLoader(template_dir),
            trim_blocks=True,
            lstrip_blocks=True
        )
    
    def create_project(self):
        """Create the complete project structure."""
        # Create main project directory
        self.project_path.mkdir(parents=True, exist_ok=True)
        
        # Create directory structure
        self._create_directory_structure()
        
        # Generate configuration files
        self._generate_config_files()
        
        # Generate agent configurations
        self._generate_agent_configs()
        
        # Generate common files
        self._generate_common_files()
        
        # Generate language-specific files
        self._generate_language_files()
        
        # Generate documentation
        self._generate_documentation()
    
    def _create_directory_structure(self):
        """Create the standard AgenticScrum directory structure."""
        directories = [
            'agents',
            'src',
            'tests',
            'docs/requirements/user_stories',
            'docs/architecture',
            'docs/sprint_reports',
            'standards/linter_configs',
            'checklists',
            'scripts'
        ]
        
        for directory in directories:
            (self.project_path / directory).mkdir(parents=True, exist_ok=True)
    
    def _generate_config_files(self):
        """Generate global configuration files."""
        # Generate agentic_config.yaml
        agentic_config = self.jinja_env.get_template('agentic_config.yaml.j2').render(
            project_name=self.project_name,
            language=self.language,
            llm_provider=self.llm_provider,
            default_model=self.default_model,
            agents=self.agents
        )
        (self.project_path / 'agentic_config.yaml').write_text(agentic_config)
        
        # Generate .gitignore
        gitignore = self.jinja_env.get_template('.gitignore.j2').render(
            language=self.language
        )
        (self.project_path / '.gitignore').write_text(gitignore)
    
    def _generate_agent_configs(self):
        """Generate configurations for each specified agent."""
        agent_mapping = {
            'poa': 'product_owner_agent',
            'sma': 'scrum_master_agent',
            'deva_python': 'developer_agent/python_expert',
            'deva_javascript': 'developer_agent/javascript_expert',
            'deva_claude_python': 'developer_agent/claude_python_expert',
            'qaa': 'qa_agent'
        }
        
        for agent in self.agents:
            if agent in agent_mapping:
                agent_dir = self.project_path / 'agents' / agent_mapping[agent]
                agent_dir.mkdir(parents=True, exist_ok=True)
                
                # Generate persona_rules.yaml
                if 'claude' in agent:
                    template_name = 'claude/persona_rules.yaml.j2'
                else:
                    template_name = f'{agent}/persona_rules.yaml.j2'
                
                try:
                    persona_rules = self.jinja_env.get_template(template_name).render(
                        project_name=self.project_name,
                        language=self.language,
                        default_model=self.default_model,
                        llm_provider=self.llm_provider
                    )
                except:
                    # Use generic template if specific one doesn't exist
                    persona_rules = self.jinja_env.get_template('generic_persona_rules.yaml.j2').render(
                        agent_type=agent,
                        project_name=self.project_name,
                        language=self.language,
                        default_model=self.default_model,
                        llm_provider=self.llm_provider
                    )
                
                (agent_dir / 'persona_rules.yaml').write_text(persona_rules)
                
                # Generate priming_script.md
                priming_script = self.jinja_env.get_template('generic_priming_script.md.j2').render(
                    agent_type=agent,
                    project_name=self.project_name
                )
                (agent_dir / 'priming_script.md').write_text(priming_script)
    
    def _generate_common_files(self):
        """Generate common project files."""
        # Generate init.sh
        init_script = self.jinja_env.get_template('common/init.sh.j2').render(
            project_name=self.project_name
        )
        init_script_path = self.project_path / 'init.sh'
        init_script_path.write_text(init_script)
        
        # Make init.sh executable
        current_permissions = init_script_path.stat().st_mode
        init_script_path.chmod(current_permissions | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        
        # Generate docker-compose.yml
        docker_compose = self.jinja_env.get_template('common/docker-compose.yml.j2').render(
            project_name=self.project_name
        )
        (self.project_path / 'docker-compose.yml').write_text(docker_compose)
        
        # Generate CLAUDE.md if claude agent is included
        if any('claude' in agent for agent in self.agents):
            claude_md = self.jinja_env.get_template('claude/CLAUDE.md.j2').render(
                project_name=self.project_name,
                language=self.language
            )
            (self.project_path / 'CLAUDE.md').write_text(claude_md)
            
            # Generate .mcp.json
            mcp_json = self.jinja_env.get_template('claude/.mcp.json.j2').render(
                project_name=self.project_name
            )
            (self.project_path / '.mcp.json').write_text(mcp_json)
    
    def _generate_language_files(self):
        """Generate language-specific files."""
        if self.language == 'python':
            requirements = self.jinja_env.get_template('python/requirements.txt.j2').render()
            (self.project_path / 'requirements.txt').write_text(requirements)
            
            # Create __init__.py files
            (self.project_path / 'src' / '__init__.py').touch()
            (self.project_path / 'tests' / '__init__.py').touch()
        
        elif self.language in ['javascript', 'typescript']:
            package_json = self.jinja_env.get_template('javascript/package.json.j2').render(
                project_name=self.project_name,
                is_typescript=self.language == 'typescript'
            )
            (self.project_path / 'package.json').write_text(package_json)
        
        elif self.language == 'java':
            pom_xml = self.jinja_env.get_template('java/pom.xml.j2').render(
                project_name=self.project_name
            )
            (self.project_path / 'pom.xml').write_text(pom_xml)
            
            # Create Java directory structure
            java_package_path = self.project_path / 'src' / 'main' / 'java' / 'com' / 'example'
            java_package_path.mkdir(parents=True, exist_ok=True)
            test_package_path = self.project_path / 'src' / 'test' / 'java' / 'com' / 'example'
            test_package_path.mkdir(parents=True, exist_ok=True)
        
        elif self.language == 'go':
            go_mod = self.jinja_env.get_template('go/go.mod.j2').render(
                project_name=self.project_name
            )
            (self.project_path / 'go.mod').write_text(go_mod)
        
        elif self.language == 'rust':
            cargo_toml = self.jinja_env.get_template('rust/Cargo.toml.j2').render(
                project_name=self.project_name
            )
            (self.project_path / 'Cargo.toml').write_text(cargo_toml)
            
            # Create Rust directory structure
            (self.project_path / 'src').mkdir(exist_ok=True)
            (self.project_path / 'src' / 'main.rs').write_text('fn main() {\n    println!("Hello, world!");\n}')
        
        elif self.language == 'csharp':
            project_name_clean = self.project_name.replace(' ', '')
            csproj = self.jinja_env.get_template('csharp/project.csproj.j2').render(
                project_name=self.project_name
            )
            (self.project_path / f'{project_name_clean}.csproj').write_text(csproj)
        
        elif self.language == 'php':
            composer_json = self.jinja_env.get_template('php/composer.json.j2').render(
                project_name=self.project_name
            )
            (self.project_path / 'composer.json').write_text(composer_json)
        
        elif self.language == 'ruby':
            gemfile = self.jinja_env.get_template('ruby/Gemfile.j2').render(
                project_name=self.project_name
            )
            (self.project_path / 'Gemfile').write_text(gemfile)
    
    def _generate_documentation(self):
        """Generate documentation files."""
        # Generate README.md
        readme = self.jinja_env.get_template('README.md.j2').render(
            project_name=self.project_name,
            language=self.language,
            agents=self.agents,
            has_claude_agent=any('claude' in agent for agent in self.agents)
        )
        (self.project_path / 'README.md').write_text(readme)
        
        # Generate coding standards
        coding_standards = self.jinja_env.get_template('standards/coding_standards.md.j2').render(
            language=self.language
        )
        (self.project_path / 'standards' / 'coding_standards.md').write_text(coding_standards)
        
        # Generate linter configurations
        linter_configs_dir = self.project_path / 'standards' / 'linter_configs'
        linter_configs_dir.mkdir(parents=True, exist_ok=True)
        
        if self.language == 'python':
            # Generate .flake8
            flake8_config = self.jinja_env.get_template('python/.flake8.j2').render()
            (linter_configs_dir / '.flake8').write_text(flake8_config)
            
            # Generate pyproject.toml
            pyproject_config = self.jinja_env.get_template('python/pyproject.toml.j2').render()
            (linter_configs_dir / 'pyproject.toml').write_text(pyproject_config)
            
        elif self.language in ['javascript', 'typescript']:
            # Generate .eslintrc.json
            eslint_config = self.jinja_env.get_template('javascript/.eslintrc.json.j2').render()
            (linter_configs_dir / '.eslintrc.json').write_text(eslint_config)
            
            # Generate .prettierrc.json
            prettier_config = self.jinja_env.get_template('javascript/.prettierrc.json.j2').render()
            (linter_configs_dir / '.prettierrc.json').write_text(prettier_config)
        
        # Generate checklists
        checklists = [
            'definition_of_done.md',
            'code_review_checklist.md',
            'sprint_planning_checklist.md'
        ]
        
        for checklist in checklists:
            checklist_content = self.jinja_env.get_template(f'checklists/{checklist}.j2').render(
                project_name=self.project_name
            )
            (self.project_path / 'checklists' / checklist).write_text(checklist_content)