"""Framework location discovery system for AgenticScrum patching.

This module provides functionality to automatically locate the AgenticScrum
installation directory from any location on the computer, supporting different
installation types (editable, pip install, etc.).
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, List
import importlib.util


class FrameworkDiscoveryError(Exception):
    """Raised when framework location cannot be determined."""
    pass


def find_agentic_scrum_location() -> Path:
    """Auto-discover AgenticScrum installation location.
    
    Returns:
        Path: Absolute path to AgenticScrum framework directory
        
    Raises:
        FrameworkDiscoveryError: If framework location cannot be determined
    """
    # Method 1: Check if we can import agentic_scrum_setup
    try:
        import agentic_scrum_setup
        module_path = Path(agentic_scrum_setup.__file__).parent
        framework_path = module_path.parent
        
        if validate_framework_installation(framework_path):
            return framework_path.resolve()
    except ImportError:
        pass
    
    # Method 2: Check pip installation locations
    pip_locations = get_pip_installation_paths()
    for location in pip_locations:
        if validate_framework_installation(location):
            return location.resolve()
    
    # Method 3: Check common development locations
    dev_locations = get_common_dev_locations()
    for location in dev_locations:
        if validate_framework_installation(location):
            return location.resolve()
    
    # Method 4: Search parent directories for AgenticScrum
    current_path = Path.cwd()
    for parent in [current_path] + list(current_path.parents):
        if parent.name == 'AgenticScrum' and validate_framework_installation(parent):
            return parent.resolve()
        
        # Check for AgenticScrum subdirectory
        agentic_dir = parent / 'AgenticScrum'
        if agentic_dir.exists() and validate_framework_installation(agentic_dir):
            return agentic_dir.resolve()
    
    raise FrameworkDiscoveryError(
        "Could not locate AgenticScrum framework installation. "
        "Please ensure AgenticScrum is properly installed or run from within an AgenticScrum project."
    )


def validate_framework_installation(path: Path) -> bool:
    """Validate that a path contains a valid AgenticScrum installation.
    
    Args:
        path: Path to check for AgenticScrum installation
        
    Returns:
        bool: True if valid AgenticScrum installation found
    """
    if not path.exists():
        return False
    
    # Check for required directory structure
    required_paths = [
        path / 'agentic_scrum_setup',
        path / 'agentic_scrum_setup' / '__init__.py',
        path / 'agentic_scrum_setup' / 'cli.py',
        path / 'agentic_scrum_setup' / 'setup_core.py',
        path / 'agentic_scrum_setup' / 'templates'
    ]
    
    for required_path in required_paths:
        if not required_path.exists():
            return False
    
    # Check for characteristic files
    characteristic_files = [
        path / 'pyproject.toml',
        path / 'init.sh',
        path / 'CLAUDE.md'
    ]
    
    # At least one characteristic file should exist
    if not any(f.exists() for f in characteristic_files):
        return False
    
    # Validate it's actually AgenticScrum by checking pyproject.toml content
    pyproject_file = path / 'pyproject.toml'
    if pyproject_file.exists():
        try:
            content = pyproject_file.read_text()
            if 'agentic-scrum-setup' in content or 'AgenticScrum' in content:
                return True
        except Exception:
            pass
    
    # Fallback: check setup.py content
    setup_file = path / 'setup.py'
    if setup_file.exists():
        try:
            content = setup_file.read_text()
            if 'agentic-scrum-setup' in content or 'AgenticScrum' in content:
                return True
        except Exception:
            pass
    
    return False


def get_pip_installation_paths() -> List[Path]:
    """Get possible pip installation locations for agentic-scrum-setup.
    
    Returns:
        List[Path]: List of potential installation paths
    """
    locations = []
    
    try:
        # Try to get site-packages locations
        import site
        site_packages = site.getsitepackages()
        for sp in site_packages:
            sp_path = Path(sp)
            agentic_path = sp_path / 'agentic_scrum_setup'
            if agentic_path.exists():
                # Get the parent directory that contains the source
                # For editable installs, look for .egg-link file
                egg_link = sp_path / 'agentic-scrum-setup.egg-link'
                if egg_link.exists():
                    try:
                        link_target = egg_link.read_text().strip().split('\n')[0]
                        locations.append(Path(link_target))
                    except Exception:
                        pass
                else:
                    # Regular pip install - the source is in site-packages
                    locations.append(agentic_path.parent)
        
        # Check user site-packages
        user_site = site.getusersitepackages()
        if user_site:
            user_path = Path(user_site)
            agentic_path = user_path / 'agentic_scrum_setup'
            if agentic_path.exists():
                locations.append(agentic_path.parent)
    except Exception:
        pass
    
    try:
        # Try using pip show command
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'show', '-f', 'agentic-scrum-setup'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            for line in lines:
                if line.startswith('Location:'):
                    location = line.split(':', 1)[1].strip()
                    location_path = Path(location)
                    
                    # Check for editable install
                    agentic_path = location_path / 'agentic_scrum_setup'
                    if agentic_path.exists():
                        locations.append(location_path)
    except Exception:
        pass
    
    return locations


def get_common_dev_locations() -> List[Path]:
    """Get common development locations where AgenticScrum might be installed.
    
    Returns:
        List[Path]: List of potential development paths
    """
    locations = []
    home = Path.home()
    
    # Common development directories
    dev_dirs = [
        'proj',
        'projects', 
        'Projects',
        'dev',
        'development',
        'code',
        'src',
        'source',
        'workspace',
        'work'
    ]
    
    for dev_dir in dev_dirs:
        dev_path = home / dev_dir
        if dev_path.exists():
            # Look for AgenticScrum directory
            agentic_path = dev_path / 'AgenticScrum'
            if agentic_path.exists():
                locations.append(agentic_path)
            
            # Look for any directory containing AgenticScrum
            try:
                for subdir in dev_path.iterdir():
                    if subdir.is_dir() and 'agentic' in subdir.name.lower():
                        if validate_framework_installation(subdir):
                            locations.append(subdir)
            except Exception:
                pass
    
    # Check current working directory and parents
    current = Path.cwd()
    for i in range(5):  # Check up to 5 levels up
        try:
            for item in current.iterdir():
                if (item.is_dir() and 
                    'agentic' in item.name.lower() and 
                    validate_framework_installation(item)):
                    locations.append(item)
        except Exception:
            pass
        
        if current.parent == current:  # Reached root
            break
        current = current.parent
    
    return locations


def get_framework_info(framework_path: Path) -> Dict[str, Any]:
    """Get information about the AgenticScrum framework installation.
    
    Args:
        framework_path: Path to AgenticScrum framework
        
    Returns:
        Dict containing framework information
    """
    info = {
        'path': str(framework_path),
        'version': None,
        'installation_type': 'unknown',
        'git_repository': False,
        'git_branch': None,
        'git_status': None,
        'editable': False
    }
    
    # Check if it's a git repository
    git_dir = framework_path / '.git'
    if git_dir.exists():
        info['git_repository'] = True
        
        try:
            # Get git branch
            result = subprocess.run(
                ['git', 'branch', '--show-current'],
                cwd=framework_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                info['git_branch'] = result.stdout.strip()
            
            # Get git status
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=framework_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                info['git_status'] = 'clean' if not result.stdout.strip() else 'modified'
        except Exception:
            pass
    
    # Get version from __init__.py
    init_file = framework_path / 'agentic_scrum_setup' / '__init__.py'
    if init_file.exists():
        try:
            content = init_file.read_text()
            for line in content.split('\n'):
                if line.strip().startswith('__version__'):
                    version_part = line.split('=')[1].strip().strip('"\'')
                    info['version'] = version_part
                    break
        except Exception:
            pass
    
    # Determine installation type
    if info['git_repository']:
        info['installation_type'] = 'development'
        info['editable'] = True
    else:
        # Check if it's in site-packages
        if 'site-packages' in str(framework_path):
            info['installation_type'] = 'pip'
        else:
            info['installation_type'] = 'local'
    
    return info


def verify_patch_compatibility(framework_path: Path) -> tuple[bool, List[str]]:
    """Verify that the framework installation is compatible with patching.
    
    Args:
        framework_path: Path to AgenticScrum framework
        
    Returns:
        Tuple of (is_compatible, list_of_issues)
    """
    issues = []
    
    # Check if we have write permissions
    if not os.access(framework_path, os.W_OK):
        issues.append(f"No write permissions for {framework_path}")
    
    # Check if it's a git repository (recommended for patching)
    if not (framework_path / '.git').exists():
        issues.append("Framework is not a git repository - rollback functionality will be limited")
    
    # Check for required directories
    required_dirs = [
        'agentic_scrum_setup',
        'agentic_scrum_setup/templates',
        'scripts'
    ]
    
    for required_dir in required_dirs:
        dir_path = framework_path / required_dir
        if not dir_path.exists():
            issues.append(f"Required directory missing: {required_dir}")
        elif not os.access(dir_path, os.W_OK):
            issues.append(f"No write permissions for directory: {required_dir}")
    
    # Check for critical files
    critical_files = [
        'agentic_scrum_setup/cli.py',
        'agentic_scrum_setup/setup_core.py',
        'pyproject.toml'
    ]
    
    for critical_file in critical_files:
        file_path = framework_path / critical_file
        if not file_path.exists():
            issues.append(f"Critical file missing: {critical_file}")
        elif not os.access(file_path, os.W_OK):
            issues.append(f"No write permissions for file: {critical_file}")
    
    return len(issues) == 0, issues