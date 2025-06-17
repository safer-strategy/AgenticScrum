"""Tests for the smart project location defaults functionality."""

import os
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock, PropertyMock

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


    def test_validate_existing_non_empty_directory_warning(self):
        """Test warning when project directory exists and is not empty."""
        config = {
            'project_name': 'TestProject',
            'language': 'python',
            'agents': 'poa,sma',
            'llm_provider': 'anthropic',
            'default_model': 'claude-3',
            'output_dir': '/tmp/test'
        }
        
        setup = SetupCore(config)
        
        # Mock the project path to exist and have files
        with patch.object(Path, 'exists') as mock_exists:
            with patch.object(Path, 'iterdir') as mock_iterdir:
                # Make project path exist
                mock_exists.return_value = True
                
                # Mock some files in the directory
                mock_files = [
                    MagicMock(name='README.md'),
                    MagicMock(name='.gitignore'),
                    MagicMock(name='src/')
                ]
                for mock_file in mock_files:
                    mock_file.name = mock_file._mock_name
                
                mock_iterdir.return_value = iter(mock_files)
                
                # Mock input to decline
                with patch('builtins.input', return_value='n'):
                    with self.assertRaises(ValueError) as context:
                        setup.validate_output_directory()
                    self.assertIn('Project creation cancelled', str(context.exception))
    
    def test_validate_existing_empty_directory_allowed(self):
        """Test that empty existing directories are allowed without warning."""
        config = {
            'project_name': 'TestProject',
            'language': 'python',
            'agents': 'poa,sma',
            'llm_provider': 'anthropic',
            'default_model': 'claude-3',
            'output_dir': '/home/user/projects'
        }
        
        setup = SetupCore(config)
        
        # Mock the project path to exist but be empty
        with patch.object(Path, 'exists') as mock_exists:
            with patch.object(Path, 'iterdir') as mock_iterdir:
                with patch.object(setup, '_is_inside_git_repo', return_value=False):
                    # Make project path exist
                    mock_exists.return_value = True
                    
                    # Mock empty directory
                    mock_iterdir.return_value = iter([])
                    
                    # Should not raise any exception
                    setup.validate_output_directory()
    
    def test_validate_permission_error_handling(self):
        """Test handling of permission errors when checking directory."""
        config = {
            'project_name': 'TestProject',
            'language': 'python',
            'agents': 'poa,sma',
            'llm_provider': 'anthropic',
            'default_model': 'claude-3',
            'output_dir': '/tmp/test'
        }
        
        setup = SetupCore(config)
        
        # Mock the project path to exist and raise PermissionError
        with patch.object(Path, 'exists') as mock_exists:
            with patch.object(Path, 'iterdir') as mock_iterdir:
                # Make project path exist
                mock_exists.return_value = True
                
                # Mock permission error
                mock_iterdir.side_effect = PermissionError("Access denied")
                
                with self.assertRaises(ValueError) as context:
                    setup.validate_output_directory()
                self.assertIn('Cannot access target directory', str(context.exception))
    
    def test_validate_git_repo_enhanced_warning(self):
        """Test enhanced git repository warning with detailed information."""
        config = {
            'project_name': 'TestProject',
            'language': 'python',
            'agents': 'poa,sma',
            'llm_provider': 'anthropic',
            'default_model': 'claude-3',
            'output_dir': '/tmp/existing-repo'
        }
        
        setup = SetupCore(config)
        
        # Mock to be inside a git repo
        with patch.object(setup, '_is_inside_git_repo', return_value=True):
            with patch('builtins.input', return_value='n') as mock_input:
                with patch('builtins.print') as mock_print:
                    with self.assertRaises(ValueError):
                        setup.validate_output_directory()
                    
                    # Check that enhanced warning was displayed
                    print_calls = [str(call) for call in mock_print.call_args_list]
                    self.assertTrue(any('nested git repositories' in str(call) for call in print_calls))
                    self.assertTrue(any('Recommended alternatives:' in str(call) for call in print_calls))


if __name__ == '__main__':
    unittest.main()