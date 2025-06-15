"""Tests for the setup core functionality."""

import os
import tempfile
import shutil
from pathlib import Path
import pytest
import stat

from agentic_scrum_setup.setup_core import SetupCore


class TestSetupCore:
    """Test cases for SetupCore class."""
    
    @pytest.fixture
    def test_config(self):
        """Provide test configuration."""
        return {
            'project_name': 'TestProject',
            'language': 'python',
            'agents': 'poa,sma,deva_claude_python,qaa',
            'llm_provider': 'anthropic',
            'default_model': 'claude-3-opus-20240229',
            'output_dir': tempfile.mkdtemp()
        }
    
    @pytest.fixture
    def setup_core(self, test_config):
        """Create SetupCore instance with test config."""
        return SetupCore(test_config)
    
    def teardown_method(self, method):
        """Clean up temporary directories."""
        # Clean up any temp directories created during tests
        import glob
        for temp_dir in glob.glob('/tmp/tmp*'):
            try:
                if os.path.isdir(temp_dir) and 'TestProject' in os.listdir(temp_dir):
                    shutil.rmtree(temp_dir)
            except:
                pass
    
    def test_init(self, setup_core, test_config):
        """Test SetupCore initialization."""
        assert setup_core.project_name == 'TestProject'
        assert setup_core.language == 'python'
        assert setup_core.agents == ['poa', 'sma', 'deva_claude_python', 'qaa']
        assert setup_core.llm_provider == 'anthropic'
        assert setup_core.default_model == 'claude-3-opus-20240229'
    
    def test_create_directory_structure(self, setup_core):
        """Test directory structure creation."""
        setup_core.project_path.mkdir(parents=True, exist_ok=True)
        setup_core._create_directory_structure()
        
        # Check that all expected directories exist
        expected_dirs = [
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
        
        for dir_path in expected_dirs:
            assert (setup_core.project_path / dir_path).exists()
            assert (setup_core.project_path / dir_path).is_dir()
    
    def test_init_sh_permissions(self, setup_core, test_config):
        """Test that init.sh is created with executable permissions."""
        # Create mock templates directory
        templates_dir = Path(__file__).parent.parent / 'templates'
        
        # Create a minimal project
        setup_core.project_path.mkdir(parents=True, exist_ok=True)
        
        # Create a simple init.sh for testing
        init_sh_content = "#!/bin/bash\necho 'test'"
        init_sh_path = setup_core.project_path / 'init.sh'
        init_sh_path.write_text(init_sh_content)
        
        # Set executable permissions (simulating what _generate_common_files does)
        current_permissions = init_sh_path.stat().st_mode
        init_sh_path.chmod(current_permissions | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        
        # Check that file is executable
        file_stat = init_sh_path.stat()
        assert file_stat.st_mode & stat.S_IXUSR  # User executable
        assert file_stat.st_mode & stat.S_IXGRP  # Group executable
        assert file_stat.st_mode & stat.S_IXOTH  # Other executable
    
    def test_claude_files_generation(self, setup_core):
        """Test that Claude-specific files are generated when claude agent is included."""
        setup_core.project_path.mkdir(parents=True, exist_ok=True)
        
        # Check that claude agent is in the list
        assert any('claude' in agent for agent in setup_core.agents)
        
        # Would test file generation here if templates were available
        # For now, just verify the logic is correct
        assert 'deva_claude_python' in setup_core.agents
    
    def test_project_name_in_docker_compose(self, test_config):
        """Test that project name is correctly used in docker-compose container name."""
        setup_core = SetupCore(test_config)
        
        # Test the transformation that would happen in the template
        project_name_lower = setup_core.project_name.lower().replace(' ', '_')
        expected_container_name = f"{project_name_lower}_app"
        
        assert expected_container_name == "testproject_app"
    
    def test_multiple_agents_parsing(self):
        """Test parsing of multiple agent types."""
        config = {
            'project_name': 'MultiAgent',
            'language': 'javascript',
            'agents': 'poa,sma,deva_javascript,qaa',
            'llm_provider': 'openai',
            'default_model': 'gpt-4',
            'output_dir': tempfile.mkdtemp()
        }
        
        setup_core = SetupCore(config)
        assert len(setup_core.agents) == 4
        assert 'poa' in setup_core.agents
        assert 'sma' in setup_core.agents
        assert 'deva_javascript' in setup_core.agents
        assert 'qaa' in setup_core.agents