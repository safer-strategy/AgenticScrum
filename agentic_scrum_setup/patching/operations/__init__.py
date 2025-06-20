"""Patch operations for AgenticScrum framework updates.

This module contains all the specific patch operations that can be performed
on the AgenticScrum framework, including template updates, MCP services,
CLI fixes, and more.
"""

from .add_template import AddTemplateOperation
from .update_mcp import UpdateMCPOperation
from .fix_cli import FixCLIOperation
from .add_command import AddCommandOperation
from .sync_changes import SyncChangesOperation
from .update_security import update_security
from .add_background_agents import add_background_agents
from .update_all import update_all
from .add_animated_banner import add_animated_banner

__all__ = [
    'AddTemplateOperation',
    'UpdateMCPOperation', 
    'FixCLIOperation',
    'AddCommandOperation',
    'SyncChangesOperation',
    'update_security',
    'add_background_agents',
    'update_all',
    'add_animated_banner'
]