"""Tests for init.sh updater."""

import pytest
from pathlib import Path
import tempfile

from agentic_scrum_setup.patching.utils.init_sh_updater import InitShUpdater


class TestInitShUpdater:
    """Test init.sh high-level update operations."""
    
    def create_simple_init_sh(self, tmpdir):
        """Create a simple init.sh for testing."""
        init_sh_content = '''#!/bin/bash

function main() {
  case "$1" in
    help)
      echo "Help"
      ;;
    test)
      echo "Test"
      ;;
    *)
      echo "Unknown command"
      ;;
  esac
}

main "$@"
'''
        init_sh_path = Path(tmpdir) / "init.sh"
        init_sh_path.write_text(init_sh_content)
        init_sh_path.chmod(0o755)
        return init_sh_path
    
    def test_add_patch_commands(self):
        """Test adding patch commands to init.sh."""
        with tempfile.TemporaryDirectory() as tmpdir:
            init_sh_path = self.create_simple_init_sh(tmpdir)
            
            updater = InitShUpdater(init_sh_path)
            updates = updater.add_patch_commands()
            
            assert len(updates) > 0
            assert any('patch' in u for u in updates)
            
            # Save and verify
            saved = updater.save()
            assert saved
            
            # Check content
            content = init_sh_path.read_text()
            assert 'patch)' in content
            assert 'patch-status)' in content
            assert 'handle_patch_command' in content
    
    def test_add_agent_commands(self):
        """Test adding agent commands to init.sh."""
        with tempfile.TemporaryDirectory() as tmpdir:
            init_sh_path = self.create_simple_init_sh(tmpdir)
            
            updater = InitShUpdater(init_sh_path)
            updates = updater.add_agent_commands()
            
            assert len(updates) > 0
            assert any('agent' in u for u in updates)
            
            # Save and verify
            saved = updater.save()
            assert saved
            
            # Check content
            content = init_sh_path.read_text()
            assert 'agent)' in content
            assert 'agent-run)' in content
            assert 'agent-status)' in content
            assert 'manage_background_agents' in content
            assert 'run_background_agent' in content
            assert 'show_agent_status' in content
    
    def test_add_docker_commands(self):
        """Test adding Docker commands to init.sh."""
        with tempfile.TemporaryDirectory() as tmpdir:
            init_sh_path = self.create_simple_init_sh(tmpdir)
            
            updater = InitShUpdater(init_sh_path)
            updates = updater.add_docker_commands()
            
            assert len(updates) > 0
            
            # Save and verify
            saved = updater.save()
            assert saved
            
            # Check content
            content = init_sh_path.read_text()
            assert 'up)' in content
            assert 'down)' in content
            assert 'start_services' in content
            assert 'stop_services' in content
    
    def test_ensure_helper_functions(self):
        """Test adding helper functions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            init_sh_path = self.create_simple_init_sh(tmpdir)
            
            updater = InitShUpdater(init_sh_path)
            updates = updater.ensure_helper_functions()
            
            # Should add info, warn, error, success
            assert len(updates) == 4
            
            # Save and verify
            saved = updater.save()
            assert saved
            
            # Check content
            content = init_sh_path.read_text()
            assert 'function info()' in content
            assert 'function warn()' in content
            assert 'function error()' in content
            assert 'function success()' in content
    
    def test_update_all(self):
        """Test comprehensive update."""
        with tempfile.TemporaryDirectory() as tmpdir:
            init_sh_path = self.create_simple_init_sh(tmpdir)
            
            updater = InitShUpdater(init_sh_path)
            saved, updates = updater.update_all()
            
            assert saved
            assert len(updates) > 5  # Should have many updates
            
            # Check all features were added
            content = init_sh_path.read_text()
            
            # Helper functions
            assert 'function info()' in content
            
            # Patch commands
            assert 'patch)' in content
            assert 'patch-status)' in content
            
            # Agent commands
            assert 'agent)' in content
            assert 'agent-run)' in content
            assert 'agent-status)' in content
            
            # Docker commands
            assert 'up)' in content
            assert 'down)' in content
    
    def test_idempotent_updates(self):
        """Test that updates are idempotent."""
        with tempfile.TemporaryDirectory() as tmpdir:
            init_sh_path = self.create_simple_init_sh(tmpdir)
            
            # First update
            updater1 = InitShUpdater(init_sh_path)
            saved1, updates1 = updater1.update_all()
            
            assert saved1
            assert len(updates1) > 0
            
            # Second update - should do nothing
            updater2 = InitShUpdater(init_sh_path)
            saved2, updates2 = updater2.update_all()
            
            assert not saved2  # Nothing to save
            assert len(updates2) == 0  # No updates needed
    
    def test_complex_init_sh_update(self):
        """Test updating a more complex init.sh."""
        complex_content = '''#!/bin/bash

set -euo pipefail

# Project initialization script

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$SCRIPT_DIR"

# Colors
readonly RED='\\033[0;31m'
readonly GREEN='\\033[0;32m'
readonly RESET='\\033[0m'

# --- Utility Functions ---

function check_dependencies() {
  echo "Checking dependencies..."
}

# --- Main Dispatcher ---

function main() {
  local cmd="${1:-help}"
  shift || true
  
  case "$cmd" in
    help|--help|-h)
      show_help
      ;;
    init)
      initialize_project
      ;;
    test)
      run_tests "$@"
      ;;
    *)
      echo "Unknown command: $cmd"
      show_help
      exit 1
      ;;
  esac
}

# Entry point
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  main "$@"
fi
'''
        
        with tempfile.TemporaryDirectory() as tmpdir:
            init_sh_path = Path(tmpdir) / "init.sh"
            init_sh_path.write_text(complex_content)
            
            updater = InitShUpdater(init_sh_path)
            saved, updates = updater.update_all()
            
            assert saved
            
            # Check structure is preserved
            content = init_sh_path.read_text()
            assert '# Project initialization script' in content
            assert '# --- Utility Functions ---' in content
            assert '# --- Main Dispatcher ---' in content
            assert 'readonly SCRIPT_DIR' in content
            
            # Check new commands were added
            assert 'patch)' in content
            assert 'agent)' in content
            assert 'up)' in content
    
    def test_preserve_custom_cases(self):
        """Test that custom cases are preserved."""
        content_with_custom = '''#!/bin/bash

function main() {
  case "$1" in
    help)
      show_help
      ;;
    custom-command)
      # User's custom command
      do_custom_stuff
      ;;
    another-custom)
      # Another custom command
      do_another_thing
      ;;
    *)
      echo "Unknown"
      ;;
  esac
}

main "$@"
'''
        
        with tempfile.TemporaryDirectory() as tmpdir:
            init_sh_path = Path(tmpdir) / "init.sh"
            init_sh_path.write_text(content_with_custom)
            
            updater = InitShUpdater(init_sh_path)
            saved, updates = updater.update_all()
            
            assert saved
            
            # Check custom cases are preserved
            content = init_sh_path.read_text()
            assert 'custom-command)' in content
            assert 'do_custom_stuff' in content
            assert 'another-custom)' in content
            assert 'do_another_thing' in content