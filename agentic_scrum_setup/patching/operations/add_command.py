"""Add command operation for AgenticScrum patching system.

This module handles adding new CLI commands to the framework.
"""

import ast
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

from ..validation import PatchValidator


class AddCommandOperation:
    """Handles adding new CLI commands to the framework."""
    
    def __init__(self, framework_path: Path, validator: PatchValidator):
        """Initialize the operation.
        
        Args:
            framework_path: Path to AgenticScrum framework
            validator: Patch validator instance
        """
        self.framework_path = framework_path
        self.validator = validator
        self.cli_file = framework_path / 'agentic_scrum_setup' / 'cli.py'
        self.init_script = framework_path / 'init.sh'
    
    def add_cli_command(self, command_name: str, command_config: Dict[str, Any]) -> List[Path]:
        """Add a new CLI command to the framework.
        
        Args:
            command_name: Name of the new command
            command_config: Configuration for the command including arguments and handler
            
        Returns:
            List of files that were modified
        """
        if not self.cli_file.exists():
            raise ValueError(f"CLI file not found: {self.cli_file}")
        
        modified_files = []
        
        # Add command parser
        self._add_command_parser(command_name, command_config)
        modified_files.append(self.cli_file)
        
        # Add command handler
        if 'handler' in command_config:
            handler_file = self._add_command_handler(command_name, command_config['handler'])
            if handler_file:
                modified_files.append(handler_file)
        
        # Add command to init.sh if requested
        if command_config.get('add_to_init_script', False):
            self._add_to_init_script(command_name, command_config)
            modified_files.append(self.init_script)
        
        print(f"✅ Added new CLI command: {command_name}")
        return modified_files
    
    def add_subcommand(self, parent_command: str, subcommand_name: str, 
                      subcommand_config: Dict[str, Any]) -> List[Path]:
        """Add a subcommand to an existing command.
        
        Args:
            parent_command: Name of the parent command
            subcommand_name: Name of the subcommand
            subcommand_config: Configuration for the subcommand
            
        Returns:
            List of files that were modified
        """
        content = self.cli_file.read_text()
        
        # Find the parent command parser
        parent_parser_pattern = rf'{parent_command}_parser\s*=\s*subparsers\.add_parser'
        if not re.search(parent_parser_pattern, content):
            raise ValueError(f"Parent command '{parent_command}' not found")
        
        # Add subcommand to parent
        # This is a simplified implementation - a full version would parse the AST
        subcommand_code = self._generate_subcommand_code(
            parent_command, subcommand_name, subcommand_config
        )
        
        # Insert the subcommand code after the parent parser definition
        lines = content.split('\n')
        insert_index = None
        
        for i, line in enumerate(lines):
            if f'{parent_command}_parser =' in line and 'add_parser' in line:
                # Find the end of this command's argument definitions
                for j in range(i + 1, len(lines)):
                    if (lines[j].strip() == '' or 
                        'subparsers.add_parser' in lines[j] or
                        'elif args.command ==' in lines[j]):
                        insert_index = j
                        break
                break
        
        if insert_index is None:
            raise ValueError(f"Could not find insertion point for subcommand")
        
        # Insert subcommand code
        for line in subcommand_code.split('\n'):
            lines.insert(insert_index, line)
            insert_index += 1
        
        updated_content = '\n'.join(lines)
        
        # Validate the updated content
        validation_result = self.validator.validate_file_content(self.cli_file, updated_content)
        if not validation_result.is_valid:
            raise ValueError(f"Subcommand validation failed: {validation_result.error_message}")
        
        self.cli_file.write_text(updated_content)
        
        print(f"✅ Added subcommand '{subcommand_name}' to '{parent_command}'")
        return [self.cli_file]
    
    def add_patch_command(self) -> List[Path]:
        """Add the patch command to the CLI.
        
        Returns:
            List of files that were modified
        """
        patch_config = {
            'description': 'Apply patches to AgenticScrum framework',
            'arguments': [
                {
                    'name': 'operation',
                    'choices': ['add-template', 'update-mcp', 'fix-cli', 'add-command', 'sync-changes', 'rollback', 'history', 'status'],
                    'help': 'Patch operation to perform'
                },
                {
                    'name': '--target',
                    'type': str,
                    'help': 'Target file or path for the operation'
                },
                {
                    'name': '--description',
                    'type': str,
                    'help': 'Description of the patch'
                },
                {
                    'name': '--dry-run',
                    'action': 'store_true',
                    'help': 'Preview changes without applying them'
                },
                {
                    'name': '--force',
                    'action': 'store_true',
                    'help': 'Force apply patch even with warnings'
                }
            ],
            'handler': 'handle_patch_command'
        }
        
        return self.add_cli_command('patch', patch_config)
    
    def _add_command_parser(self, command_name: str, config: Dict[str, Any]) -> None:
        """Add command parser to the CLI file.
        
        Args:
            command_name: Name of the command
            config: Command configuration
        """
        content = self.cli_file.read_text()
        
        # Generate parser code
        parser_code = self._generate_parser_code(command_name, config)
        
        # Find where to insert the parser (after existing subparsers)
        lines = content.split('\n')
        insert_index = None
        
        # Look for the last subparser definition
        for i in range(len(lines) - 1, -1, -1):
            if 'subparsers.add_parser' in lines[i]:
                # Find the end of this parser's arguments
                for j in range(i + 1, len(lines)):
                    if (lines[j].strip() == '' or 
                        'subparsers.add_parser' in lines[j] or
                        'return parser' in lines[j] or
                        'def ' in lines[j]):
                        insert_index = j
                        break
                break
        
        if insert_index is None:
            # Find the subparsers creation and insert after it
            for i, line in enumerate(lines):
                if 'subparsers = parser.add_subparsers' in line:
                    insert_index = i + 2  # Skip the subparsers line and empty line
                    break
        
        if insert_index is None:
            raise ValueError("Could not find where to insert new command parser")
        
        # Insert parser code
        parser_lines = parser_code.split('\n')
        for i, line in enumerate(parser_lines):
            lines.insert(insert_index + i, line)
        
        # Add command handler to main function
        handler_code = self._generate_handler_code(command_name, config)
        
        # Find main function and add handler
        for i, line in enumerate(lines):
            if 'elif args.command ==' in line:
                # Find the last elif block
                last_elif_index = i
        
        # Insert new elif block
        handler_lines = handler_code.split('\n')
        for i, line in enumerate(handler_lines):
            lines.insert(last_elif_index + len(handler_lines) + i, line)
        
        updated_content = '\n'.join(lines)
        
        # Validate the updated content
        validation_result = self.validator.validate_file_content(self.cli_file, updated_content)
        if not validation_result.is_valid:
            raise ValueError(f"Command parser validation failed: {validation_result.error_message}")
        
        self.cli_file.write_text(updated_content)
    
    def _add_command_handler(self, command_name: str, handler_info: Dict[str, Any]) -> Optional[Path]:
        """Add command handler implementation.
        
        Args:
            command_name: Name of the command
            handler_info: Handler configuration
            
        Returns:
            Path to handler file if created, None otherwise
        """
        if isinstance(handler_info, str):
            # Simple handler name - add to main CLI file
            return None
        
        if isinstance(handler_info, dict) and 'file' in handler_info:
            # External handler file
            handler_file = self.framework_path / 'agentic_scrum_setup' / handler_info['file']
            handler_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Generate handler code
            handler_code = handler_info.get('code', self._generate_default_handler(command_name))
            
            # Validate handler code
            validation_result = self.validator.validate_file_content(handler_file, handler_code)
            if not validation_result.is_valid:
                raise ValueError(f"Handler validation failed: {validation_result.error_message}")
            
            handler_file.write_text(handler_code)
            return handler_file
        
        return None
    
    def _add_to_init_script(self, command_name: str, config: Dict[str, Any]) -> None:
        """Add command shortcut to init.sh script.
        
        Args:
            command_name: Name of the command
            config: Command configuration
        """
        if not self.init_script.exists():
            return
        
        content = self.init_script.read_text()
        
        # Generate shortcut code for init.sh
        shortcut_code = f'''
# {command_name.title()} command
"{command_name}")
    agentic-scrum-setup {command_name} "$@"
    ;;
'''
        
        # Find the case statement and add new case
        lines = content.split('\n')
        insert_index = None
        
        for i, line in enumerate(lines):
            if 'esac' in line:
                insert_index = i
                break
        
        if insert_index is not None:
            shortcut_lines = shortcut_code.strip().split('\n')
            for i, line in enumerate(shortcut_lines):
                lines.insert(insert_index + i, line)
            
            self.init_script.write_text('\n'.join(lines))
    
    def _generate_parser_code(self, command_name: str, config: Dict[str, Any]) -> str:
        """Generate parser code for a command.
        
        Args:
            command_name: Name of the command
            config: Command configuration
            
        Returns:
            Generated parser code
        """
        indent = '    '
        
        lines = [
            '',
            f'{indent}# {command_name.title()} command',
            f'{indent}{command_name}_parser = subparsers.add_parser(\'{command_name}\', help=\'{config.get("description", f"{command_name} operation")}\')']
        
        # Add arguments
        for arg_config in config.get('arguments', []):
            arg_line = f'{indent}{command_name}_parser.add_argument('
            
            # Positional or optional argument
            if arg_config['name'].startswith('--'):
                arg_line += f'\n{indent}    \'{arg_config["name"]}\','
            else:
                arg_line += f'\n{indent}    \'{arg_config["name"]}\','
            
            # Add argument properties
            if 'type' in arg_config:
                arg_line += f'\n{indent}    type={arg_config["type"].__name__},'
            
            if 'choices' in arg_config:
                choices_str = str(arg_config['choices'])
                arg_line += f'\n{indent}    choices={choices_str},'
            
            if 'action' in arg_config:
                arg_line += f'\n{indent}    action=\'{arg_config["action"]}\','
            
            if 'default' in arg_config:
                default_str = repr(arg_config['default'])
                arg_line += f'\n{indent}    default={default_str},'
            
            if 'help' in arg_config:
                help_str = repr(arg_config['help'])
                arg_line += f'\n{indent}    help={help_str}'
            
            arg_line += f'\n{indent})'
            lines.append(arg_line)
        
        return '\n'.join(lines)
    
    def _generate_handler_code(self, command_name: str, config: Dict[str, Any]) -> str:
        """Generate handler code for the main function.
        
        Args:
            command_name: Name of the command
            config: Command configuration
            
        Returns:
            Generated handler code
        """
        indent = '    '
        
        handler_name = config.get('handler', f'handle_{command_name}_command')
        
        lines = [
            '',
            f'{indent}elif args.command == \'{command_name}\':',
            f'{indent}    # {command_name.title()} command handler',
            f'{indent}    try:'
        ]
        
        if isinstance(config.get('handler'), str):
            # Simple function call
            lines.extend([
                f'{indent}        {handler_name}(args)',
                f'{indent}    except Exception as e:',
                f'{indent}        print(f"❌ Error in {command_name} command: {{e}}")',
                f'{indent}        sys.exit(1)'
            ])
        else:
            # Default implementation
            lines.extend([
                f'{indent}        print(f"🔧 Executing {command_name} command...")',
                f'{indent}        # TODO: Implement {command_name} functionality',
                f'{indent}        print(f"✅ {command_name.title()} completed successfully")',
                f'{indent}    except Exception as e:',
                f'{indent}        print(f"❌ Error in {command_name} command: {{e}}")',
                f'{indent}        sys.exit(1)'
            ])
        
        return '\n'.join(lines)
    
    def _generate_subcommand_code(self, parent_command: str, subcommand_name: str, 
                                 config: Dict[str, Any]) -> str:
        """Generate code for a subcommand.
        
        Args:
            parent_command: Name of parent command
            subcommand_name: Name of subcommand
            config: Subcommand configuration
            
        Returns:
            Generated subcommand code
        """
        indent = '    '
        
        lines = [
            '',
            f'{indent}# {subcommand_name} subcommand',
            f'{indent}{parent_command}_{subcommand_name}_parser = {parent_command}_subparsers.add_subparser(',
            f'{indent}    \'{subcommand_name}\',',
            f'{indent}    help=\'{config.get("description", f"{subcommand_name} operation")}\''
            f'{indent})'
        ]
        
        # Add arguments for subcommand
        for arg_config in config.get('arguments', []):
            arg_code = self._generate_argument_code(
                f'{parent_command}_{subcommand_name}_parser',
                arg_config
            )
            lines.append(arg_code)
        
        return '\n'.join(lines)
    
    def _generate_argument_code(self, parser_name: str, arg_config: Dict[str, Any]) -> str:
        """Generate code for adding an argument.
        
        Args:
            parser_name: Name of the parser variable
            arg_config: Argument configuration
            
        Returns:
            Generated argument code
        """
        indent = '    '
        
        code_parts = [f'{indent}{parser_name}.add_argument(']
        code_parts.append(f'{indent}    \'{arg_config["name"]}\',')
        
        if 'type' in arg_config:
            code_parts.append(f'{indent}    type={arg_config["type"].__name__},')
        
        if 'choices' in arg_config:
            choices_str = str(arg_config['choices'])
            code_parts.append(f'{indent}    choices={choices_str},')
        
        if 'action' in arg_config:
            code_parts.append(f'{indent}    action=\'{arg_config["action"]}\',')
        
        if 'default' in arg_config:
            default_str = repr(arg_config['default'])
            code_parts.append(f'{indent}    default={default_str},')
        
        if 'help' in arg_config:
            help_str = repr(arg_config['help'])
            code_parts.append(f'{indent}    help={help_str}')
        
        code_parts.append(f'{indent})')
        
        return '\n'.join(code_parts)
    
    def _generate_default_handler(self, command_name: str) -> str:
        """Generate default handler implementation.
        
        Args:
            command_name: Name of the command
            
        Returns:
            Default handler code
        """
        return f'''"""Handler for {command_name} command."""

def handle_{command_name}_command(args):
    """Handle {command_name} command.
    
    Args:
        args: Parsed command line arguments
    """
    print(f"🔧 Executing {command_name} command...")
    
    # TODO: Implement {command_name} functionality
    # Access arguments with: args.argument_name
    
    print(f"✅ {command_name.title()} completed successfully")
'''