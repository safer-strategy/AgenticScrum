"""Tests for framework-specific functionality."""

import tempfile
from pathlib import Path
import pytest

from agentic_scrum_setup.setup_core import SetupCore


class TestFrameworkSupport:
    """Test cases for framework-specific generation."""
    
    @pytest.fixture
    def fastapi_config(self):
        """Provide FastAPI test configuration."""
        return {
            'project_name': 'FastAPIProject',
            'language': 'python',
            'framework': 'fastapi',
            'agents': 'poa,sma,deva_python,qaa',
            'llm_provider': 'openai',
            'default_model': 'gpt-4',
            'output_dir': tempfile.mkdtemp()
        }
    
    @pytest.fixture
    def react_config(self):
        """Provide React test configuration."""
        return {
            'project_name': 'ReactProject',
            'language': 'typescript',
            'framework': 'react',
            'agents': 'poa,sma,deva_javascript,qaa',
            'llm_provider': 'anthropic',
            'default_model': 'claude-3-opus',
            'output_dir': tempfile.mkdtemp()
        }
    
    def test_fastapi_project_structure(self, fastapi_config):
        """Test FastAPI-specific project structure."""
        setup_core = SetupCore(fastapi_config)
        setup_core.create_project()
        
        project_path = Path(fastapi_config['output_dir']) / 'FastAPIProject'
        
        # Check FastAPI-specific directories
        assert (project_path / 'app').exists()
        assert (project_path / 'app' / '__init__.py').exists()
        assert (project_path / 'app' / 'api').exists()
        assert (project_path / 'app' / 'core').exists()
        assert (project_path / 'app' / 'models').exists()
        assert (project_path / 'app' / 'schemas').exists()
        assert (project_path / 'app' / 'services').exists()
        
        # Check requirements.txt has FastAPI dependencies
        requirements = (project_path / 'requirements.txt').read_text()
        assert 'fastapi' in requirements
        assert 'uvicorn' in requirements
        assert 'pydantic' in requirements
        assert 'sqlalchemy' in requirements
    
    def test_react_project_configuration(self, react_config):
        """Test React-specific configuration files."""
        setup_core = SetupCore(react_config)
        setup_core.create_project()
        
        project_path = Path(react_config['output_dir']) / 'ReactProject'
        
        # Check TypeScript configuration
        assert (project_path / 'tsconfig.json').exists()
        tsconfig = (project_path / 'tsconfig.json').read_text()
        assert '"jsx": "react-jsx"' in tsconfig
        
        # Check React-specific ESLint configuration
        eslint_path = project_path / 'standards' / 'linter_configs' / '.eslintrc.json'
        assert eslint_path.exists()
        eslint_config = eslint_path.read_text()
        assert 'plugin:react/recommended' in eslint_config
        assert 'react-hooks' in eslint_config
    
    def test_framework_in_readme(self, fastapi_config):
        """Test that framework information appears in README."""
        setup_core = SetupCore(fastapi_config)
        setup_core.create_project()
        
        project_path = Path(fastapi_config['output_dir']) / 'FastAPIProject'
        readme = (project_path / 'README.md').read_text()
        
        # Check FastAPI-specific structure in README
        assert 'app/' in readme
        assert 'FastAPI application' in readme
        assert 'api/' in readme
        assert 'schemas/' in readme
    
    def test_framework_coding_standards(self, fastapi_config, react_config):
        """Test framework-specific coding standards."""
        # Test FastAPI standards
        setup_core = SetupCore(fastapi_config)
        setup_core.create_project()
        
        project_path = Path(fastapi_config['output_dir']) / 'FastAPIProject'
        standards = (project_path / 'standards' / 'coding_standards.md').read_text()
        
        assert 'FastAPI Standards' in standards
        assert 'Pydantic' in standards
        assert 'async/await' in standards
        
        # Test React standards
        setup_core = SetupCore(react_config)
        setup_core.create_project()
        
        project_path = Path(react_config['output_dir']) / 'ReactProject'
        standards = (project_path / 'standards' / 'coding_standards.md').read_text()
        
        assert 'React Standards' in standards
        assert 'hooks' in standards
        assert 'useState' in standards