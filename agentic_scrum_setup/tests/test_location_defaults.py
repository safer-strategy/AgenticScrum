"""Tests for the smart project location defaults functionality."""

import os
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

from agentic_scrum_setup.cli import get_default_output_dir
from agentic_scrum_setup.setup_core import SetupCore


class TestLocationDefaults(unittest.TestCase):
    """Test cases for project location defaults and safety."""
    
    def test_default_dir_with_env_var(self):
        """Test that environment variable takes precedence."""
        with patch.dict(os.environ, {'AGENTIC_PROJECTS_DIR': '/custom/path'}):
            result = get_default_output_dir()
            self.assertEqual(result, '/custom/path')
    
    def test_default_dir_inside_agentic_scrum(self):
        """Test that ~/AgenticProjects is used when inside AgenticScrum."""
        with patch('pathlib.Path.cwd') as mock_cwd:
            mock_cwd.return_value = Path('/Users/test/AgenticScrum/sub/dir')
            result = get_default_output_dir()
            expected = str(Path.home() / 'AgenticProjects')
            self.assertEqual(result, expected)
    
    def test_default_dir_outside_agentic_scrum(self):
        """Test that current directory is used when outside AgenticScrum."""
        with patch('pathlib.Path.cwd') as mock_cwd:
            mock_cwd.return_value = Path('/Users/test/MyOtherProject')
            result = get_default_output_dir()
            self.assertEqual(result, '.')
    
    def test_validate_output_directory_warns_inside_agentic_scrum(self):
        """Test warning when creating project inside AgenticScrum."""
        config = {
            'project_name': 'TestProject',
            'language': 'python',
            'agents': 'poa,sma',
            'llm_provider': 'anthropic',
            'default_model': 'claude-3',
            'output_dir': '/Users/test/AgenticScrum/projects'
        }
        
        setup = SetupCore(config)
        
        # Mock input to simulate user declining
        with patch('builtins.input', return_value='n'):
            with self.assertRaises(ValueError) as context:
                setup.validate_output_directory()
            self.assertIn('Project creation cancelled', str(context.exception))
    
    def test_validate_output_directory_allows_with_confirmation(self):
        """Test that creation proceeds with user confirmation."""
        config = {
            'project_name': 'TestProject',
            'language': 'python',
            'agents': 'poa,sma',
            'llm_provider': 'anthropic',
            'default_model': 'claude-3',
            'output_dir': '/Users/test/AgenticScrum/projects'
        }
        
        setup = SetupCore(config)
        
        # Mock input to simulate user accepting
        with patch('builtins.input', return_value='y'):
            # Should not raise an exception
            setup.validate_output_directory()
    
    def test_validate_output_directory_blocks_system_dirs(self):
        """Test that system directories are blocked."""
        system_dirs = ['/usr/local/bin', '/etc/config', '/bin/scripts', 
                      '/sbin/tools', '/System/Library']
        
        for sys_dir in system_dirs:
            config = {
                'project_name': 'TestProject',
                'language': 'python',
                'agents': 'poa,sma',
                'llm_provider': 'anthropic',
                'default_model': 'claude-3',
                'output_dir': sys_dir
            }
            
            setup = SetupCore(config)
            
            with self.assertRaises(ValueError) as context:
                setup.validate_output_directory()
            self.assertIn('Cannot create projects in system directory', str(context.exception))
    
    def test_is_inside_git_repo_detection(self):
        """Test git repository detection."""
        config = {
            'project_name': 'TestProject',
            'language': 'python',
            'agents': 'poa,sma',
            'llm_provider': 'anthropic',
            'default_model': 'claude-3',
            'output_dir': '/tmp/test'
        }
        
        setup = SetupCore(config)
        
        # Test positive case - inside git repo
        with patch('pathlib.Path.exists') as mock_exists:
            mock_exists.return_value = True
            result = setup._is_inside_git_repo(Path('/some/git/repo'))
            self.assertTrue(result)
        
        # Test negative case - not inside git repo
        with patch('pathlib.Path.exists') as mock_exists:
            mock_exists.return_value = False
            result = setup._is_inside_git_repo(Path('/some/regular/dir'))
            self.assertFalse(result)
    
    def test_path_expansion(self):
        """Test that paths with ~ are properly expanded."""
        with patch.dict(os.environ, {'HOME': '/Users/test'}):
            config = {
                'project_name': 'TestProject',
                'language': 'python',
                'agents': 'poa,sma',
                'llm_provider': 'anthropic',
                'default_model': 'claude-3',
                'output_dir': '~/Projects'
            }
            
            setup = SetupCore(config)
            # The Path class should expand ~ automatically
            expected = Path('/Users/test/Projects/TestProject')
            self.assertEqual(setup.project_path.expanduser(), expected)


if __name__ == '__main__':
    unittest.main()