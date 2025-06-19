"""AgenticScrum Remote Patching System.

This module provides functionality to patch and update the AgenticScrum framework
from any project directory on the same computer, enabling seamless development
workflow improvements without directory switching.

Core Features:
- Framework location discovery
- Safe patch application with rollback
- Git integration for version control
- Template and configuration updates
- CLI fixes and new command additions
"""

from .discovery import find_agentic_scrum_location, validate_framework_installation
from .patcher import AgenticPatcher, PatchError, PatchValidationError
from .validation import PatchValidator, ValidationResult

__all__ = [
    'find_agentic_scrum_location',
    'validate_framework_installation', 
    'AgenticPatcher',
    'PatchError',
    'PatchValidationError',
    'PatchValidator',
    'ValidationResult'
]

__version__ = '1.0.0'