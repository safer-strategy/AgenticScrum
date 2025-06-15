"""Tests for the CLI module."""

import sys
from unittest.mock import patch, MagicMock
import pytest

from agentic_scrum_setup.cli import parse_arguments, interactive_mode, main


class TestCLI:
    """Test cases for CLI functionality."""
    
    def test_parse_arguments_init_command(self):
        """Test parsing init command with all arguments."""
        test_args = [
            'agentic-scrum-setup',
            'init',
            '--project-name', 'TestProject',
            '--language', 'python',
            '--agents', 'poa,sma,deva_python,qaa',
            '--llm-provider', 'openai',
            '--default-model', 'gpt-4',
            '--output-dir', '/tmp/test'
        ]
        
        with patch.object(sys, 'argv', test_args):
            parser = parse_arguments()
            args = parser.parse_args()
            
            assert args.command == 'init'
            assert args.project_name == 'TestProject'
            assert args.language == 'python'
            assert args.agents == 'poa,sma,deva_python,qaa'
            assert args.llm_provider == 'openai'
            assert args.default_model == 'gpt-4'
            assert args.output_dir == '/tmp/test'
    
    def test_parse_arguments_no_command(self):
        """Test parsing with no command."""
        test_args = ['agentic-scrum-setup']
        
        with patch.object(sys, 'argv', test_args):
            parser = parse_arguments()
            args = parser.parse_args()
            assert args.command is None
    
    @patch('builtins.input')
    def test_interactive_mode(self, mock_input):
        """Test interactive mode prompts."""
        # Mock user inputs
        mock_input.side_effect = [
            'MyProject',      # Project name
            '1',              # Language choice (python)
            'poa,sma,qaa',    # Agents
            '2',              # LLM provider (anthropic)
            'claude-3-opus'   # Model
        ]
        
        result = interactive_mode()
        
        assert result['project_name'] == 'MyProject'
        assert result['language'] == 'python'
        assert result['agents'] == 'poa,sma,qaa'
        assert result['llm_provider'] == 'anthropic'
        assert result['default_model'] == 'claude-3-opus'
        assert result['output_dir'] == '.'
    
    @patch('builtins.input')
    def test_interactive_mode_with_defaults(self, mock_input):
        """Test interactive mode with default values."""
        # Mock user inputs with some empty (using defaults)
        mock_input.side_effect = [
            'DefaultProject',  # Project name
            'python',         # Language by name
            '',               # Agents (use default)
            'openai',         # Provider by name
            ''                # Model (use default)
        ]
        
        result = interactive_mode()
        
        assert result['project_name'] == 'DefaultProject'
        assert result['language'] == 'python'
        assert result['agents'] == 'poa,sma,deva_python,qaa'  # Default
        assert result['llm_provider'] == 'openai'
        assert result['default_model'] == 'gpt-4-turbo-preview'  # Default for openai
    
    @patch('agentic_scrum_setup.cli.SetupCore')
    @patch('sys.exit')
    def test_main_with_complete_args(self, mock_exit, mock_setup_core):
        """Test main function with complete arguments."""
        test_args = [
            'agentic-scrum-setup',
            'init',
            '--project-name', 'TestProject',
            '--language', 'python',
            '--agents', 'poa,sma',
            '--llm-provider', 'openai',
            '--default-model', 'gpt-4'
        ]
        
        mock_instance = MagicMock()
        mock_setup_core.return_value = mock_instance
        
        with patch.object(sys, 'argv', test_args):
            main()
        
        # Verify SetupCore was called with correct config
        mock_setup_core.assert_called_once()
        config = mock_setup_core.call_args[0][0]
        assert config['project_name'] == 'TestProject'
        assert config['language'] == 'python'
        
        # Verify create_project was called
        mock_instance.create_project.assert_called_once()
    
    @patch('builtins.input')
    @patch('agentic_scrum_setup.cli.SetupCore')
    def test_main_triggers_interactive_mode(self, mock_setup_core, mock_input):
        """Test main function triggers interactive mode when args missing."""
        test_args = ['agentic-scrum-setup', 'init']  # Missing required args
        
        # Mock interactive inputs
        mock_input.side_effect = [
            'InteractiveProject',
            '1',  # python
            'poa',
            '1',  # openai
            'gpt-4'
        ]
        
        mock_instance = MagicMock()
        mock_setup_core.return_value = mock_instance
        
        with patch.object(sys, 'argv', test_args):
            main()
        
        # Verify SetupCore was called
        mock_setup_core.assert_called_once()
        config = mock_setup_core.call_args[0][0]
        assert config['project_name'] == 'InteractiveProject'