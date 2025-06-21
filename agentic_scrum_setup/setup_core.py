"""Core setup functionality for AgenticScrum projects."""

import os
import re
import stat
import shutil
from pathlib import Path
from typing import Dict, List, Optional
from jinja2 import Environment, FileSystemLoader, Template, TemplateNotFound


class SetupCore:
    """Core class for setting up AgenticScrum projects."""
    
    def __init__(self, config: Dict[str, str]):
        """Initialize the setup core with configuration.
        
        Args:
            config: Dictionary containing project configuration
        """
        self.config = config
        self.project_name = config['project_name']
        self.project_type = config.get('project_type', 'single')
        self.language = config['language']
        self.frontend_language = config.get('frontend_language', None)
        self.agents = config['agents'].split(',')
        self.llm_provider = config['llm_provider']
        self.default_model = config['default_model']
        self.output_dir = Path(config['output_dir'])
        self.project_path = self.output_dir / self.project_name
        self.framework = config.get('framework', None)  # For single projects
        self.backend_framework = config.get('backend_framework', None)  # For fullstack
        self.frontend_framework = config.get('frontend_framework', None)  # For fullstack
        self.enable_mcp = config.get('enable_mcp', False)
        self.enable_search = config.get('enable_search', False)
        
        # Setup Jinja2 environment
        template_dir = Path(__file__).parent / 'templates'
        self.jinja_env = Environment(
            loader=FileSystemLoader(template_dir),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Validate configuration after setup
        self._validate_configuration()
    
    def _validate_configuration(self):
        """Validate all configuration parameters."""
        self._validate_project_name()
        self._validate_agents()
        self._validate_output_directory_security()
    
    def _validate_project_name(self):
        """Validate project name for filesystem safety."""
        if not self.project_name or not self.project_name.strip():
            raise ValueError("Project name cannot be empty")
        
        # Check for invalid characters that could cause filesystem issues
        invalid_chars = r'[<>:"/\\|?*\x00-\x1f]'
        if re.search(invalid_chars, self.project_name):
            raise ValueError(
                f"Project name '{self.project_name}' contains invalid characters. "
                "Project names cannot contain: < > : \" / \\ | ? * or control characters. "
                "Use only letters, numbers, hyphens, and underscores."
            )
        
        # Check for reserved names on Windows
        reserved_names = {
            'CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 'COM5',
            'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2', 'LPT3', 'LPT4',
            'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
        }
        if self.project_name.upper() in reserved_names:
            raise ValueError(
                f"Project name '{self.project_name}' is a reserved name on Windows. "
                "Please choose a different name."
            )
        
        # Check length (most filesystems have 255 character limits)
        if len(self.project_name) > 200:
            raise ValueError(
                f"Project name '{self.project_name}' is too long ({len(self.project_name)} characters). "
                "Please use a name shorter than 200 characters."
            )
    
    def _validate_agents(self):
        """Validate that all specified agents are known."""
        # Known agent types mapping
        known_agents = {
            'poa': 'poa',
            'sma': 'sma', 
            'deva_python': 'deva_python',
            'deva_javascript': 'deva_javascript',
            'deva_typescript': 'deva_typescript',
            'deva_claude_python': 'deva_claude_python',
            'qaa': 'qaa',
            'saa': 'saa',
            'organization_poa': 'organization_poa',
            'organization_sma': 'organization_sma'
        }
        
        unknown_agents = []
        for agent in self.agents:
            agent = agent.strip()
            if agent and agent not in known_agents:
                unknown_agents.append(agent)
        
        if unknown_agents:
            raise ValueError(
                f"Unknown agent types: {', '.join(unknown_agents)}. "
                f"Valid agents are: {', '.join(sorted(known_agents.keys()))}. "
                "Please check your agent list for typos."
            )
    
    def _validate_output_directory_security(self):
        """Validate output directory to prevent path traversal attacks."""
        try:
            # Convert to absolute path and resolve any symbolic links
            abs_output = self.output_dir.resolve()
            abs_project = self.project_path.resolve()
            
            # Check for path traversal attempts
            if '..' in str(self.output_dir) or '..' in self.project_name:
                raise ValueError(
                    "Path traversal detected in output directory or project name. "
                    "Relative paths with '..' are not allowed for security reasons."
                )
            
            # Ensure project path is within or equal to output directory
            try:
                abs_project.relative_to(abs_output)
            except ValueError:
                raise ValueError(
                    f"Project path '{abs_project}' is not within output directory '{abs_output}'. "
                    "This could indicate a path traversal attempt."
                )
                
        except (OSError, RuntimeError) as e:
            raise ValueError(
                f"Invalid output directory or project name: {e}. "
                "Please ensure the path is valid and accessible."
            )

    def validate_output_directory(self):
        """Validate the output directory is appropriate."""
        abs_path = self.output_dir.absolute()
        project_abs_path = self.project_path.absolute()
        
        # Check if inside AgenticScrum
        if 'AgenticScrum' in str(project_abs_path):
            print(f"\n⚠️  WARNING: You're creating a project inside AgenticScrum!")
            print(f"   Location: {project_abs_path}")
            print(f"   Recommended: ~/AgenticProjects/{self.project_name}")
            response = input("Continue anyway? [y/N]: ")
            if response.lower() != 'y':
                raise ValueError("Project creation cancelled")
        
        # Check system directories
        forbidden_paths = ['/usr', '/etc', '/bin', '/sbin', '/System', '/Windows']
        for forbidden in forbidden_paths:
            if str(project_abs_path).startswith(forbidden):
                raise ValueError(f"Cannot create projects in system directory: {forbidden}")
        
        # Check if project directory already exists and is not empty
        if self.project_path.exists():
            try:
                # Get list of existing items
                existing_items = list(self.project_path.iterdir())
                
                if existing_items:
                    print(f"\n⚠️  WARNING: Directory already exists and is not empty!")
                    print(f"   Location: {project_abs_path}")
                    print(f"   Existing files may be overwritten!")
                    
                    # Show some of the existing files
                    print(f"   Found {len(existing_items)} existing items, including:")
                    for f in existing_items[:5]:
                        print(f"     - {f.name}")
                    if len(existing_items) > 5:
                        print(f"     ... and {len(existing_items) - 5} more")
                    
                    response = input("\nContinue and potentially overwrite files? [y/N]: ")
                    if response.lower() != 'y':
                        raise ValueError("Project creation cancelled")
            except PermissionError:
                print(f"\n❌ ERROR: Cannot access directory: {project_abs_path}")
                print("   Please check permissions or choose a different location")
                raise ValueError("Cannot access target directory")
        
        # Check if inside another git repo (excluding AgenticScrum)
        if self._is_inside_git_repo(abs_path) and 'AgenticScrum' not in str(abs_path):
            print(f"\n⚠️  WARNING: Target directory is inside a git repository")
            print(f"   This will create nested git repositories which can cause:")
            print(f"   - Git tracking conflicts")
            print(f"   - Confusion about which repo controls which files")
            print(f"   - Problems with git submodules")
            print(f"\n   Recommended alternatives:")
            print(f"   1. Create your project outside this repository")
            print(f"   2. Add the project path to .gitignore of the parent repo")
            response = input("\nContinue anyway? [y/N]: ")
            if response.lower() != 'y':
                raise ValueError("Project creation cancelled")
    
    def _is_inside_git_repo(self, path: Path) -> bool:
        """Check if path is inside a git repository."""
        current = path
        while current != current.parent:
            if (current / '.git').exists():
                return True
            current = current.parent
        return False
    
    def create_project(self):
        """Create the complete project structure."""
        # Handle organization project type differently
        if self.project_type == 'organization':
            from .organization_setup import OrganizationSetup
            org_setup = OrganizationSetup(self.config)
            org_setup.create_organization()
            return
        
        try:
            # Validate output directory first
            self.validate_output_directory()
            
            # Show where project will be created
            print(f"\n📍 Creating project at: {self.project_path.absolute()}")
            
            # Create main project directory
            try:
                self.project_path.mkdir(parents=True, exist_ok=True)
            except (OSError, PermissionError) as e:
                raise RuntimeError(
                    f"Failed to create project directory '{self.project_path}': {e}. "
                    "Please check permissions and ensure the path is valid."
                )
            
            # Create directory structure
            try:
                self._create_directory_structure()
            except (OSError, PermissionError) as e:
                raise RuntimeError(
                    f"Failed to create project directory structure: {e}. "
                    "Please check disk space and permissions."
                )
            
            # Generate configuration files
            try:
                self._generate_config_files()
            except (TemplateNotFound, ValueError) as e:
                raise RuntimeError(
                    f"Failed to generate configuration files: {e}. "
                    "Please check your project configuration and try again."
                )
            
            # Generate agent configurations
            try:
                self._generate_agent_configs()
            except (TemplateNotFound, ValueError) as e:
                raise RuntimeError(
                    f"Failed to generate agent configurations: {e}. "
                    "Please verify your agent list contains valid agent types."
                )
            
            # Generate common files
            try:
                self._generate_common_files()
            except (TemplateNotFound, OSError) as e:
                raise RuntimeError(
                    f"Failed to generate common files: {e}. "
                    "Please check template integrity and disk space."
                )
            
            # Generate language-specific files
            try:
                self._generate_language_files()
            except (TemplateNotFound, ValueError) as e:
                raise RuntimeError(
                    f"Failed to generate language-specific files for {self.language}: {e}. "
                    "Please verify your language and framework selections are supported."
                )
            
            # Generate documentation
            try:
                self._generate_documentation()
            except (TemplateNotFound, OSError) as e:
                raise RuntimeError(
                    f"Failed to generate documentation files: {e}. "
                    "Please check template availability and disk space."
                )
            
            # Generate scripts
            try:
                self._generate_scripts()
            except (TemplateNotFound, OSError) as e:
                raise RuntimeError(
                    f"Failed to generate script files: {e}. "
                    "Please check template availability and script permissions."
                )
            
            # Generate QA validation system
            try:
                self._generate_qa_system()
            except (TemplateNotFound, OSError) as e:
                raise RuntimeError(
                    f"Failed to generate QA validation system: {e}. "
                    "Please check QA template availability and disk space."
                )
            
            # Create memory structure for MCP integration
            if self.enable_mcp:
                try:
                    self._create_memory_structure()
                except OSError as e:
                    raise RuntimeError(
                        f"Failed to create MCP memory structure: {e}. "
                        "Please check disk space and permissions."
                    )
                    
        except Exception as e:
            # Clean up partially created project on failure
            if self.project_path.exists():
                try:
                    shutil.rmtree(self.project_path)
                    print(f"\n🧹 Cleaned up partially created project directory.")
                except OSError:
                    print(f"\n⚠️  Warning: Could not clean up {self.project_path}. You may need to remove it manually.")
            raise
    
    def _create_directory_structure(self):
        """Create the standard AgenticScrum directory structure."""
        if self.project_type == 'fullstack':
            # Fullstack project structure
            directories = [
                'agents',
                'backend/src',
                'backend/tests',
                'frontend/src',
                'frontend/tests',
                'docs/requirements/user_stories',
                'docs/architecture',
                'docs/sprint_reports',
                'standards/backend/linter_configs',
                'standards/frontend/linter_configs',
                'checklists',
                'scripts',
                'qa/reports/automated',
                'qa/reports/bugs/critical',
                'qa/reports/bugs/high',
                'qa/reports/bugs/medium',
                'qa/reports/bugs/low',
                'qa/reports/validation',
                'qa/agents/qa_automation_agent',
                'qa/agents/background_qa_runner',
                'qa/templates',
                'qa/queue',
                'qa/scripts',
                'qa/config'
            ]
        else:
            # Single language project structure
            directories = [
                'agents',
                'src',
                'tests',
                'docs/requirements/user_stories',
                'docs/architecture',
                'docs/sprint_reports',
                'standards/linter_configs',
                'checklists',
                'scripts',
                'qa/reports/automated',
                'qa/reports/bugs/critical',
                'qa/reports/bugs/high',
                'qa/reports/bugs/medium',
                'qa/reports/bugs/low',
                'qa/reports/validation',
                'qa/agents/qa_automation_agent',
                'qa/agents/background_qa_runner',
                'qa/templates',
                'qa/queue',
                'qa/scripts',
                'qa/config'
            ]
        
        for directory in directories:
            (self.project_path / directory).mkdir(parents=True, exist_ok=True)
    
    def _generate_config_files(self):
        """Generate global configuration files."""
        # Generate agentic_config.yaml
        from datetime import datetime
        created_date = datetime.now().strftime('%Y-%m-%d')
        
        agentic_config = self.jinja_env.get_template('agentic_config.yaml.j2').render(
            project_name=self.project_name,
            language=self.language,
            llm_provider=self.llm_provider,
            default_model=self.default_model,
            agents=self.agents,
            created_date=created_date
        )
        (self.project_path / 'agentic_config.yaml').write_text(agentic_config)
        
        # Generate agentic_config.yaml.sample
        agentic_config_sample = self.jinja_env.get_template('agentic_config.yaml.sample.j2').render(
            project_name=self.project_name,
            language=self.language,
            llm_provider=self.llm_provider,
            default_model=self.default_model,
            agents=self.agents,
            created_date=created_date
        )
        (self.project_path / 'agentic_config.yaml.sample').write_text(agentic_config_sample)
        
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
            'deva_typescript': 'developer_agent/typescript_expert',
            'deva_java': 'developer_agent/java_expert',
            'deva_go': 'developer_agent/go_expert',
            'deva_rust': 'developer_agent/rust_expert',
            'deva_csharp': 'developer_agent/csharp_expert',
            'deva_claude_python': 'developer_agent/claude_python_expert',
            'qaa': 'qa_agent',
            'saa': 'security_audit_agent'
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
                        llm_provider=self.llm_provider,
                        framework=self.framework
                    )
                except (FileNotFoundError, TemplateNotFound) as e:
                    # Use generic template if specific one doesn't exist
                    print(f"Warning: Specific template for {agent} not found, using generic template. ({e})")
                    persona_rules = self.jinja_env.get_template('generic_persona_rules.yaml.j2').render(
                        agent_type=agent,
                        project_name=self.project_name,
                        language=self.language,
                        default_model=self.default_model,
                        llm_provider=self.llm_provider
                    )
                
                (agent_dir / 'persona_rules.yaml').write_text(persona_rules)
                
                # Generate priming_script.md
                if agent == 'saa':
                    priming_template_name = 'saa/priming_script.md.j2'
                else:
                    priming_template_name = 'generic_priming_script.md.j2'
                
                try:
                    priming_script = self.jinja_env.get_template(priming_template_name).render(
                        agent_type=agent,
                        project_name=self.project_name,
                        language=self.language,
                        framework=self.framework
                    )
                except (FileNotFoundError, TemplateNotFound) as e:
                    # Fallback to generic template
                    print(f"Warning: Specific priming script template for {agent} not found, using generic template. ({e})")
                    priming_script = self.jinja_env.get_template('generic_priming_script.md.j2').render(
                        agent_type=agent,
                        project_name=self.project_name
                    )
                
                (agent_dir / 'priming_script.md').write_text(priming_script)
                
                # Generate agent MCP configuration for memory integration
                if self.llm_provider == 'anthropic' or any('claude' in a for a in self.agents):
                    agent_mcp_config = self.jinja_env.get_template('agents/agent_mcp_config.json.j2').render(
                        agent_type=agent
                    )
                    (agent_dir / 'mcp_config.json').write_text(agent_mcp_config)
    
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
        
        # Generate CLAUDE.md if claude agent is included or using anthropic provider
        if any('claude' in agent for agent in self.agents) or self.config.get('llm_provider') == 'anthropic':
            # Check if CLAUDE.md already exists (retrofit scenario)
            existing_claude_content = None
            existing_claude_path = self.project_path / 'CLAUDE.md'
            if self.config.get('is_retrofit') and existing_claude_path.exists():
                try:
                    existing_claude_content = existing_claude_path.read_text()
                except Exception:
                    pass
            
            # Use adaptive template if retrofitting, otherwise use standard
            template_name = 'claude/CLAUDE_ADAPTIVE.md.j2' if existing_claude_content else 'claude/CLAUDE.md.j2'
            
            claude_md = self.jinja_env.get_template(template_name).render(
                project_name=self.project_name,
                language=self.language,
                agents=self.agents,
                enable_mcp=self.enable_mcp,
                enable_search=self.enable_search,
                existing_claude_content=existing_claude_content,
                is_retrofit=self.config.get('is_retrofit', False),
                framework=self.framework or self.backend_framework,
                project_type=self.project_type,
                project_description=self.config.get('project_description'),
                security_requirements=self.config.get('security_requirements'),
                compliance_requirements=self.config.get('compliance_requirements'),
                qa_coverage_threshold=self.config.get('qa_coverage_threshold', 85)
            )
            (self.project_path / 'CLAUDE.md').write_text(claude_md)
            
            # Generate .mcp.json if MCP is enabled
            if self.enable_mcp:
                mcp_json = self.jinja_env.get_template('claude/.mcp.json.j2').render(
                    project_name=self.project_name,
                    language=self.language,
                    agents=self.agents,
                    enable_search=self.enable_search
                )
                (self.project_path / '.mcp.json').write_text(mcp_json)
                
                # Copy MCP servers to project
                self._copy_mcp_servers()
        
        # Generate .env.sample for all projects (MCP support is optional)
        env_sample = self.jinja_env.get_template('.env.sample').render()
        (self.project_path / '.env.sample').write_text(env_sample)
    
    def _generate_language_files(self):
        """Generate language-specific files."""
        if self.project_type == 'fullstack':
            self._generate_fullstack_files()
        else:
            self._generate_single_language_files()
    
    def _generate_single_language_files(self):
        """Generate files for single language projects."""
        if self.language == 'python':
            # Check if using FastAPI framework
            if self.framework == 'fastapi':
                requirements = self.jinja_env.get_template('python/fastapi_requirements.txt.j2').render()
                # Create FastAPI project structure
                (self.project_path / 'app').mkdir(exist_ok=True)
                (self.project_path / 'app' / '__init__.py').touch()
                (self.project_path / 'app' / 'api').mkdir(exist_ok=True)
                (self.project_path / 'app' / 'api' / '__init__.py').touch()
                (self.project_path / 'app' / 'core').mkdir(exist_ok=True)
                (self.project_path / 'app' / 'core' / '__init__.py').touch()
                (self.project_path / 'app' / 'models').mkdir(exist_ok=True)
                (self.project_path / 'app' / 'models' / '__init__.py').touch()
                (self.project_path / 'app' / 'schemas').mkdir(exist_ok=True)
                (self.project_path / 'app' / 'schemas' / '__init__.py').touch()
                (self.project_path / 'app' / 'services').mkdir(exist_ok=True)
                (self.project_path / 'app' / 'services' / '__init__.py').touch()
            else:
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
    
    def _generate_fullstack_files(self):
        """Generate files for fullstack projects."""
        # Backend files
        backend_path = self.project_path / 'backend'
        
        if self.language == 'python':
            if self.backend_framework == 'fastapi':
                requirements = self.jinja_env.get_template('python/fastapi_requirements.txt.j2').render()
                (backend_path / 'requirements.txt').write_text(requirements)
                
                # Create FastAPI structure
                (backend_path / 'app').mkdir(exist_ok=True)
                (backend_path / 'app' / '__init__.py').touch()
                (backend_path / 'app' / 'api').mkdir(exist_ok=True)
                (backend_path / 'app' / 'api' / '__init__.py').touch()
                (backend_path / 'app' / 'core').mkdir(exist_ok=True)
                (backend_path / 'app' / 'core' / '__init__.py').touch()
                (backend_path / 'app' / 'models').mkdir(exist_ok=True)
                (backend_path / 'app' / 'models' / '__init__.py').touch()
                (backend_path / 'app' / 'schemas').mkdir(exist_ok=True)
                (backend_path / 'app' / 'schemas' / '__init__.py').touch()
                (backend_path / 'app' / 'services').mkdir(exist_ok=True)
                (backend_path / 'app' / 'services' / '__init__.py').touch()
            else:
                requirements = self.jinja_env.get_template('python/requirements.txt.j2').render()
                (backend_path / 'requirements.txt').write_text(requirements)
            
            # Python __init__ files
            (backend_path / 'src' / '__init__.py').touch()
            (backend_path / 'tests' / '__init__.py').touch()
        
        elif self.language in ['javascript', 'typescript']:
            if self.backend_framework == 'express':
                package_json = self.jinja_env.get_template('javascript/express_package.json.j2').render(
                    project_name=f"{self.project_name}-backend",
                    is_typescript=self.language == 'typescript'
                )
                (backend_path / 'package.json').write_text(package_json)
        
        elif self.language == 'java' and self.backend_framework == 'spring':
            pom_xml = self.jinja_env.get_template('java/spring_pom.xml.j2').render(
                project_name=f"{self.project_name}-backend"
            )
            (backend_path / 'pom.xml').write_text(pom_xml)
            
            # Create Java structure
            java_path = backend_path / 'src' / 'main' / 'java' / 'com' / 'example'
            java_path.mkdir(parents=True, exist_ok=True)
            test_path = backend_path / 'src' / 'test' / 'java' / 'com' / 'example'
            test_path.mkdir(parents=True, exist_ok=True)
        
        # Frontend files
        frontend_path = self.project_path / 'frontend'
        
        if self.frontend_language in ['javascript', 'typescript']:
            if self.frontend_framework == 'react':
                package_json = self.jinja_env.get_template('javascript/react_package.json.j2').render(
                    project_name=f"{self.project_name}-frontend",
                    is_typescript=self.frontend_language == 'typescript'
                )
                (frontend_path / 'package.json').write_text(package_json)
                
                # Create React structure
                (frontend_path / 'src').mkdir(exist_ok=True)
                (frontend_path / 'public').mkdir(exist_ok=True)
                
                if self.frontend_language == 'typescript':
                    tsconfig = self.jinja_env.get_template('typescript/tsconfig.json.j2').render()
                    (frontend_path / 'tsconfig.json').write_text(tsconfig)
            
            elif self.frontend_framework in ['vue', 'angular', 'svelte']:
                # Basic package.json for other frameworks
                package_json = self.jinja_env.get_template('javascript/package.json.j2').render(
                    project_name=f"{self.project_name}-frontend",
                    is_typescript=self.frontend_language == 'typescript'
                )
                (frontend_path / 'package.json').write_text(package_json)
    
    def _generate_documentation(self):
        """Generate documentation files."""
        # Generate README.md
        readme = self.jinja_env.get_template('README.md.j2').render(
            project_name=self.project_name,
            project_type=self.project_type,
            language=self.language,
            frontend_language=self.frontend_language,
            framework=self.framework,
            backend_framework=self.backend_framework,
            frontend_framework=self.frontend_framework,
            agents=self.agents,
            has_claude_agent=any('claude' in agent for agent in self.agents)
        )
        (self.project_path / 'README.md').write_text(readme)
        
        # Generate SECURITY.md
        security_doc = self.jinja_env.get_template('docs/SECURITY.md.j2').render(
            project_name=self.project_name,
            language=self.language,
            llm_provider=self.llm_provider
        )
        (self.project_path / 'docs' / 'SECURITY.md').write_text(security_doc)
        
        # Generate PROJECT_SCOPE.md
        project_scope = self.jinja_env.get_template('docs/PROJECT_SCOPE.md.j2').render(
            project_name=self.project_name,
            language=self.language,
            project_type=self.project_type
        )
        (self.project_path / 'docs' / 'PROJECT_SCOPE.md').write_text(project_scope)
        
        # Generate PROJECT_KICKOFF.md
        project_kickoff = self.jinja_env.get_template('docs/PROJECT_KICKOFF.md.j2').render(
            project_name=self.project_name,
            has_mcp=self.enable_mcp,
            has_search=self.enable_search,
            agents=self.agents
        )
        (self.project_path / 'docs' / 'PROJECT_KICKOFF.md').write_text(project_kickoff)
        
        # Generate PRD.md if conversational mode or retrofit
        if self.config.get('conversation_derived') or self.config.get('is_retrofit'):
            from datetime import datetime
            prd = self.jinja_env.get_template('docs/PRD.md.j2').render(
                project_name=self.project_name,
                current_date=datetime.now().strftime('%Y-%m-%d'),
                project_vision=self.config.get('project_vision', ''),
                project_description=self.config.get('project_description', '')
            )
            (self.project_path / 'docs' / 'PRD.md').write_text(prd)
            
            # Generate PROJECT_SUMMARY.md
            summary = self.jinja_env.get_template('docs/PROJECT_SUMMARY.md.j2').render(
                project_name=self.project_name,
                current_date=datetime.now().strftime('%Y-%m-%d'),
                current_year=datetime.now().year,
                current_quarter=f"Q{(datetime.now().month-1)//3 + 1}",
                next_quarter=f"Q{((datetime.now().month-1)//3 + 2) % 4 or 4}",
                project_vision=self.config.get('project_vision', ''),
                project_description=self.config.get('project_description', ''),
                team_size=self.config.get('team_size', 'TBD')
            )
            (self.project_path / 'docs' / 'PROJECT_SUMMARY.md').write_text(summary)
        
        # Generate coding standards
        coding_standards = self.jinja_env.get_template('standards/coding_standards.md.j2').render(
            language=self.language
        )
        (self.project_path / 'standards' / 'coding_standards.md').write_text(coding_standards)
        
        # Generate linter configurations
        if self.project_type == 'fullstack':
            # Backend linter configs
            backend_linter_dir = self.project_path / 'standards' / 'backend' / 'linter_configs'
            self._generate_linter_configs(self.language, backend_linter_dir, self.backend_framework)
            
            # Frontend linter configs
            frontend_linter_dir = self.project_path / 'standards' / 'frontend' / 'linter_configs'
            self._generate_linter_configs(self.frontend_language, frontend_linter_dir, self.frontend_framework)
        else:
            # Single language linter configs
            linter_configs_dir = self.project_path / 'standards' / 'linter_configs'
            linter_configs_dir.mkdir(parents=True, exist_ok=True)
            self._generate_linter_configs(self.language, linter_configs_dir, self.framework)
    
    def _generate_linter_configs(self, language, linter_dir, framework=None):
        """Generate linter configurations for a specific language."""
        linter_dir.mkdir(parents=True, exist_ok=True)
        
        if language == 'python':
            # Generate .flake8
            flake8_config = self.jinja_env.get_template('python/.flake8.j2').render()
            (linter_dir / '.flake8').write_text(flake8_config)
            
            # Generate pyproject.toml
            pyproject_config = self.jinja_env.get_template('python/pyproject.toml.j2').render()
            (linter_dir / 'pyproject.toml').write_text(pyproject_config)
            
        elif language in ['javascript', 'typescript']:
            # Check if using React framework
            if framework == 'react':
                if language == 'typescript':
                    eslint_config = self.jinja_env.get_template('typescript/.eslintrc.react.json.j2').render()
                    # Also generate tsconfig.json
                    tsconfig = self.jinja_env.get_template('typescript/tsconfig.json.j2').render()
                    (self.project_path / 'tsconfig.json').write_text(tsconfig)
                else:
                    eslint_config = self.jinja_env.get_template('javascript/.eslintrc.react.json.j2').render()
            else:
                # Generate standard .eslintrc.json
                eslint_config = self.jinja_env.get_template('javascript/.eslintrc.json.j2').render()
            
            (linter_dir / '.eslintrc.json').write_text(eslint_config)
            
            # Generate .prettierrc.json
            prettier_config = self.jinja_env.get_template('javascript/.prettierrc.json.j2').render()
            (linter_dir / '.prettierrc.json').write_text(prettier_config)
        
        # Generate checklists
        checklists = [
            'definition_of_done.md',
            'code_review_checklist.md',
            'sprint_planning_checklist.md',
            'security_audit_checklist.md'
        ]
        
        for checklist in checklists:
            checklist_content = self.jinja_env.get_template(f'checklists/{checklist}.j2').render(
                project_name=self.project_name
            )
            (self.project_path / 'checklists' / checklist).write_text(checklist_content)
    
    def _generate_scripts(self):
        """Generate utility scripts for the project."""
        # Generate check-secrets.sh pre-commit hook
        check_secrets = self.jinja_env.get_template('scripts/check-secrets.sh').render()
        check_secrets_path = self.project_path / 'scripts' / 'check-secrets.sh'
        check_secrets_path.write_text(check_secrets)
        
        # Make check-secrets.sh executable
        current_permissions = check_secrets_path.stat().st_mode
        check_secrets_path.chmod(current_permissions | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        
        # Create .git/hooks directory if project is a git repo
        git_hooks_dir = self.project_path / '.git' / 'hooks'
        if git_hooks_dir.parent.exists():
            git_hooks_dir.mkdir(exist_ok=True)
            # Copy as pre-commit hook
            pre_commit_path = git_hooks_dir / 'pre-commit'
            shutil.copy2(check_secrets_path, pre_commit_path)
            # Make pre-commit executable
            current_permissions = pre_commit_path.stat().st_mode
            pre_commit_path.chmod(current_permissions | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    
    def _create_memory_structure(self):
        """Create agent memory directory structure for MCP integration."""
        memory_root = self.project_path / '.agent-memory'
        
        # Agent-specific directories
        agent_dirs = ['poa', 'sma', 'deva', 'qaa', 'saa', 'shared']
        
        for agent_dir in agent_dirs:
            dir_path = memory_root / agent_dir
            dir_path.mkdir(parents=True, exist_ok=True)
            
            # Initialize empty JSONL files with starter content
            if agent_dir == 'shared':
                # Shared memory gets project initialization entry
                init_entry = {
                    "timestamp": "{{ '{' }}{{ '\"' }}timestamp{{ '\"' }}: {{ '\"' }}{{ '{:.3f}'.format(time.time()) }}{{ '\"' }},",
                    "type": "project_init",
                    "project_name": self.project_name,
                    "language": self.language,
                    "agents": self.agents,
                    "framework": self.framework or self.backend_framework
                }
                # Write as JSON lines format
                (dir_path / 'timeline.jsonl').write_text('')
                (dir_path / 'architecture.jsonl').write_text('')
            else:
                # Agent-specific memory files
                (dir_path / 'main.jsonl').touch()
                
                # Create specialized memory files based on agent type
                if agent_dir == 'poa':
                    (dir_path / 'requirements.jsonl').touch()
                    (dir_path / 'decisions.jsonl').touch()
                elif agent_dir == 'sma':
                    (dir_path / 'retrospectives.jsonl').touch()
                    (dir_path / 'impediments.jsonl').touch()
                elif agent_dir == 'deva':
                    (dir_path / 'patterns.jsonl').touch()
                    (dir_path / 'refactors.jsonl').touch()
                elif agent_dir == 'qaa':
                    (dir_path / 'test-strategies.jsonl').touch()
                    (dir_path / 'bug-patterns.jsonl').touch()
                elif agent_dir == 'saa':
                    (dir_path / 'vulnerabilities.jsonl').touch()
                    (dir_path / 'mitigations.jsonl').touch()
        
        # Create README for memory directory
        memory_readme = '''# Agent Memory Directory

This directory contains persistent memory for AI agents in the AgenticScrum framework.

## Structure

- `poa/` - Product Owner Agent memories (requirements, decisions)
- `sma/` - Scrum Master Agent memories (retrospectives, impediments)
- `deva/` - Developer Agent memories (code patterns, refactoring decisions)
- `qaa/` - QA Agent memories (test strategies, bug patterns)
- `saa/` - Security Agent memories (vulnerabilities, mitigations)
- `shared/` - Cross-agent shared knowledge (timeline, architecture)

## File Format

All memory files use JSONL (JSON Lines) format for efficient append operations.
Each line is a complete JSON object representing a memory entry.

## Privacy Note

This directory is gitignored by default to protect project-specific learnings.
Consider backing up important memories using the memory export utilities.
'''
        (memory_root / 'README.md').write_text(memory_readme)
    
    def _copy_mcp_servers(self):
        """Copy MCP server files to the project directory."""
        template_dir = Path(__file__).parent / 'templates'
        mcp_servers_template_dir = template_dir / 'mcp_servers'
        
        if mcp_servers_template_dir.exists():
            project_mcp_dir = self.project_path / 'mcp_servers'
            
            # Copy the entire mcp_servers directory
            if project_mcp_dir.exists():
                shutil.rmtree(project_mcp_dir)
            shutil.copytree(mcp_servers_template_dir, project_mcp_dir)
            
            # Make server.py files executable
            for server_file in project_mcp_dir.rglob('server.py'):
                current_permissions = server_file.stat().st_mode
                server_file.chmod(current_permissions | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    
    def _generate_qa_system(self):
        """Generate the complete QA validation system."""
        # QA system configuration from CLI or defaults
        qa_enabled = self.config.get('enable_qa', True)
        
        if not qa_enabled:
            return
            
        from datetime import datetime
        
        # Prepare QA configuration context
        qa_config = {
            'enabled': True,
            'validation_modes': ['automatic', 'manual'],
            'background_agents': {
                'enabled': True,
                'max_concurrent': 3,
                'auto_assignment': True,
                'retry_policy': {
                    'max_retries': 3,
                    'backoff_multiplier': 2,
                    'max_backoff_minutes': 10
                }
            },
            'validation_layers': {
                'code_quality': True,
                'functional': True,
                'integration': True,
                'user_experience': True
            },
            'bug_detection': {
                'enabled': True,
                'auto_reporting': True,
                'severity_thresholds': {
                    'critical': 0,
                    'high': 2,
                    'medium': 5,
                    'low': 10
                }
            },
            'quality_gates': {
                'minimum_coverage': self.config.get('qa_coverage_threshold', 85),
                'max_performance_regression': self.config.get('qa_max_performance_regression', 20),
                'security_scan_required': True
            },
            'reporting': {
                'daily_summary': True,
                'weekly_trends': True,
                'real_time_alerts': True
            }
        }
        
        # Create template context
        template_context = {
            'project_name': self.project_name,
            'language': self.language,
            'framework': self.framework or self.backend_framework,
            'environment': 'development',
            'llm_provider': self.llm_provider,
            'default_model': self.default_model,
            'qa': qa_config,
            'version': '1.0.0',
            'agentic_scrum_version': '1.0.0',
            'ansible_date_time': {
                'iso8601': datetime.now().isoformat()
            }
        }
        
        # Generate QA README
        qa_readme = self.jinja_env.get_template('qa/README.md.j2').render(**template_context)
        (self.project_path / 'qa' / 'README.md').write_text(qa_readme)
        
        # Generate QA queue management files
        qa_queue_files = [
            ('qa/queue/pending_validation.json.j2', 'qa/queue/pending_validation.json'),
            ('qa/queue/active_qa_sessions.json.j2', 'qa/queue/active_qa_sessions.json'),
            ('qa/queue/bugfix_queue.json.j2', 'qa/queue/bugfix_queue.json')
        ]
        
        for template_file, output_file in qa_queue_files:
            content = self.jinja_env.get_template(template_file).render(**template_context)
            (self.project_path / output_file).write_text(content)
        
        # Generate QA report templates
        qa_template_files = [
            ('qa/templates/bug_report_template.md.j2', 'qa/templates/bug_report_template.md'),
            ('qa/templates/validation_report_template.md.j2', 'qa/templates/validation_report_template.md'),
            ('qa/templates/test_execution_report.md.j2', 'qa/templates/test_execution_report.md')
        ]
        
        for template_file, output_file in qa_template_files:
            content = self.jinja_env.get_template(template_file).render(**template_context)
            (self.project_path / output_file).write_text(content)
        
        # Generate QA configuration files
        qa_config_files = [
            ('qa/config/qa_config.yaml.j2', 'qa/config/qa_config.yaml'),
            ('qa/config/validation_rules.yaml.j2', 'qa/config/validation_rules.yaml')
        ]
        
        for template_file, output_file in qa_config_files:
            content = self.jinja_env.get_template(template_file).render(**template_context)
            (self.project_path / output_file).write_text(content)
        
        # Generate enhanced QA agent configurations
        qa_agent_files = [
            ('qa/agents/qa_automation_agent/persona_rules.yaml.j2', 'qa/agents/qa_automation_agent/persona_rules.yaml'),
            ('qa/agents/background_qa_runner/persona_rules.yaml.j2', 'qa/agents/background_qa_runner/persona_rules.yaml')
        ]
        
        for template_file, output_file in qa_agent_files:
            content = self.jinja_env.get_template(template_file).render(**template_context)
            (self.project_path / output_file).write_text(content)
        
        # Generate QA MCP configuration for agent integration
        if self.enable_mcp:
            qa_mcp_config = self.jinja_env.get_template('agents/agent_mcp_config.json.j2').render(
                agent_type='qa_automation_agent'
            )
            (self.project_path / 'qa' / 'agents' / 'qa_automation_agent' / 'mcp_config.json').write_text(qa_mcp_config)
            
            bg_mcp_config = self.jinja_env.get_template('agents/agent_mcp_config.json.j2').render(
                agent_type='background_qa_runner'
            )
            (self.project_path / 'qa' / 'agents' / 'background_qa_runner' / 'mcp_config.json').write_text(bg_mcp_config)