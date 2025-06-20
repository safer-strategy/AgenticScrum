"""Tests for init.sh parser."""

import pytest
from pathlib import Path
import tempfile

from agentic_scrum_setup.patching.utils.init_sh_parser import InitShParser


class TestInitShParser:
    """Test init.sh parsing and modification."""
    
    def test_parse_simple_init_sh(self):
        """Test parsing a simple init.sh structure."""
        content = '''#!/bin/bash

function info() {
  echo "INFO: $*"
}

function main() {
  case "$1" in
    help)
      show_help
      ;;
    test)
      run_tests
      ;;
    *)
      info "Unknown command"
      ;;
  esac
}

main "$@"
'''
        parser = InitShParser(content)
        
        # Check function detection
        assert 'info' in parser.functions
        assert 'main' in parser.functions
        
        # Check case detection
        assert 'help' in parser.cases
        assert 'test' in parser.cases
        assert '*' in parser.cases
        
        # Check main function boundaries
        assert parser.main_func_start is not None
        assert parser.main_func_end is not None
    
    def test_add_new_case(self):
        """Test adding a new case to the switch statement."""
        content = '''#!/bin/bash

function main() {
  case "$1" in
    help)
      show_help
      ;;
    test)
      run_tests
      ;;
    *)
      echo "Unknown"
      ;;
  esac
}

main "$@"
'''
        parser = InitShParser(content)
        
        # Add new case
        success = parser.add_case('build', [
            '# Build the project',
            'run_build'
        ], after_case='test')
        
        assert success
        
        # Verify it was added
        result = parser.get_content()
        assert 'build)' in result
        assert 'run_build' in result
        
        # Verify order (should be after test)
        lines = result.split('\n')
        build_idx = next(i for i, line in enumerate(lines) if 'build)' in line)
        test_idx = next(i for i, line in enumerate(lines) if 'test)' in line)
        assert build_idx > test_idx
    
    def test_add_function(self):
        """Test adding a new function."""
        content = '''#!/bin/bash

# --- Main Dispatcher ---

function main() {
  echo "main"
}

main "$@"
'''
        parser = InitShParser(content)
        
        # Add new function
        success = parser.add_function('setup_env', [
            'export PATH="/usr/local/bin:$PATH"',
            'echo "Environment configured"'
        ])
        
        assert success
        
        # Verify it was added
        result = parser.get_content()
        assert 'function setup_env()' in result
        assert 'export PATH' in result
        
        # Verify it's before main dispatcher
        lines = result.split('\n')
        func_idx = next(i for i, line in enumerate(lines) if 'function setup_env()' in line)
        main_idx = next(i for i, line in enumerate(lines) if '# --- Main Dispatcher ---' in line)
        assert func_idx < main_idx
    
    def test_case_exists(self):
        """Test checking if cases exist."""
        content = '''#!/bin/bash

function main() {
  case "$1" in
    help|--help|-h)
      show_help
      ;;
    test)
      run_tests
      ;;
    *)
      echo "Unknown"
      ;;
  esac
}
'''
        parser = InitShParser(content)
        
        # Check exact matches
        assert parser.case_exists('test')
        
        # Check multi-case patterns
        assert parser.case_exists('help')
        assert parser.case_exists('--help')
        assert parser.case_exists('-h')
        
        # Check non-existent
        assert not parser.case_exists('build')
    
    def test_idempotent_operations(self):
        """Test that operations are idempotent."""
        content = '''#!/bin/bash

function main() {
  case "$1" in
    help)
      show_help
      ;;
    *)
      echo "Unknown"
      ;;
  esac
}
'''
        parser = InitShParser(content)
        
        # Add case once
        success1 = parser.add_case('test', ['run_tests'])
        assert success1
        
        # Try to add same case again
        success2 = parser.add_case('test', ['run_tests'])
        assert not success2  # Should fail
        
        # Content should only have one test case
        result = parser.get_content()
        assert result.count('test)') == 1
    
    def test_handle_different_formatting(self):
        """Test parsing with different formatting styles."""
        content = '''#!/bin/bash

main()
{
    case "$1" in
        "help") show_help ;;
        'test') run_tests ;;
        build)
            compile_project
            ;;
        *) echo "Unknown" ;;
    esac
}
'''
        parser = InitShParser(content)
        
        # Should detect all cases despite formatting
        assert parser.case_exists('help')
        assert parser.case_exists('test')
        assert parser.case_exists('build')
        assert parser.case_exists('*')
    
    def test_update_case(self):
        """Test updating an existing case."""
        content = '''#!/bin/bash

function main() {
  case "$1" in
    test)
      echo "Old test"
      ;;
    *)
      echo "Unknown"
      ;;
  esac
}
'''
        parser = InitShParser(content)
        
        # Update test case
        success = parser.update_case('test', [
            'echo "New test implementation"',
            'run_all_tests',
            'generate_report'
        ])
        
        assert success
        
        # Verify update
        result = parser.get_content()
        assert 'echo "New test implementation"' in result
        assert 'run_all_tests' in result
        assert 'generate_report' in result
        assert 'echo "Old test"' not in result
    
    def test_complex_init_sh(self):
        """Test with a more complex real-world init.sh."""
        content = '''#!/bin/bash

set -euo pipefail

# Colors
readonly RED='\\033[0;31m'
readonly GREEN='\\033[0;32m'
readonly RESET='\\033[0m'

# Helper functions
function info() {
  echo -e "${GREEN}INFO:${RESET} $*"
}

function error() {
  echo -e "${RED}ERROR:${RESET} $*" >&2
}

# --- Main Functions ---

function show_help() {
  cat << EOF
Usage: $0 [command]

Commands:
  help    Show this help
  test    Run tests
  build   Build project
EOF
}

function run_tests() {
  info "Running tests..."
  pytest
}

# --- Main Dispatcher ---

function main() {
  local cmd="${1:-help}"
  shift || true
  
  case "$cmd" in
    help|--help|-h)
      show_help
      ;;
    test)
      run_tests "$@"
      ;;
    build)
      info "Building..."
      make build
      ;;
    *)
      error "Unknown command: $cmd"
      show_help
      exit 1
      ;;
  esac
}

# Run main
main "$@"
'''
        parser = InitShParser(content)
        
        # Add agent command after test
        success = parser.add_case('agent', [
            '# Agent management',
            'shift',
            'manage_agents "$@"'
        ], after_case='test')
        
        assert success
        
        # Add agent function
        success = parser.add_function('manage_agents', [
            'local subcmd="$1"',
            'case "$subcmd" in',
            '  list) list_agents ;;',
            '  *) error "Unknown agent command" ;;',
            'esac'
        ])
        
        assert success
        
        # Verify structure is maintained
        result = parser.get_content()
        
        # Original structure should be preserved
        assert '# Colors' in result
        assert '# --- Main Functions ---' in result
        assert '# --- Main Dispatcher ---' in result
        
        # New additions should be present
        assert 'agent)' in result
        assert 'function manage_agents()' in result
    
    def test_preserve_indentation(self):
        """Test that indentation is preserved correctly."""
        content = '''#!/bin/bash

function main() {
    case "$1" in
        help)
            show_help
            ;;
        test)
            run_tests
            ;;
    esac
}
'''
        parser = InitShParser(content)
        
        # Add new case - should match existing indentation
        parser.add_case('build', ['run_build'], after_case='test')
        
        result = parser.get_content()
        lines = result.split('\n')
        
        # Find the build case line
        build_line = next(line for line in lines if 'build)' in line)
        test_line = next(line for line in lines if 'test)' in line)
        
        # Should have same indentation
        assert len(build_line) - len(build_line.lstrip()) == \
               len(test_line) - len(test_line.lstrip())
    
    def test_no_main_function(self):
        """Test handling script without main function."""
        content = '''#!/bin/bash

case "$1" in
  help)
    echo "Help"
    ;;
  *)
    echo "Unknown"
    ;;
esac
'''
        parser = InitShParser(content)
        
        # Should not crash
        assert parser.main_func_start is None
        assert parser.main_func_end is None
        
        # But should still detect cases if not in main
        # (This parser focuses on main function cases, so these won't be detected)
        assert len(parser.cases) == 0