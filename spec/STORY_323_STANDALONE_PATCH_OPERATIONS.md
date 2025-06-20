# Story 323: Add Missing Operations to Standalone Patch Script

**Epic**: E009 - Patching System Robustness
**Story Points**: 2
**Priority**: P2 (High)
**Status**: Completed
**Sprint**: Next
**Assigned To**: deva_python

## Story Description

As a developer using the standalone agentic-patch script,
I want access to all patch operations including update-all and add-background-agents,
So that I can apply comprehensive updates from any project directory.

## Problem Statement

The standalone `scripts/agentic-patch` script is missing key operations that are available in the main CLI:
- `update-all` - Comprehensive project update
- `add-background-agents` - Add background agent system
- `update-security` - Add security training features

This forces users to work from the framework directory or use workarounds.

## Acceptance Criteria

1. **Operation Registration**
   - [ ] Add update-all to standalone script operations
   - [ ] Add add-background-agents operation
   - [ ] Add update-security operation
   - [ ] Maintain backward compatibility

2. **Operation Discovery**
   - [ ] Dynamically discover available operations
   - [ ] Support both class-based and function-based operations
   - [ ] Handle operation dependencies

3. **Error Handling**
   - [ ] Clear messages for missing dependencies
   - [ ] Graceful fallback for unavailable operations
   - [ ] Proper validation of operation arguments

4. **Help System**
   - [ ] Update help text with new operations
   - [ ] Include operation descriptions
   - [ ] Show required arguments for each operation

## Technical Implementation

### 1. Update Operation Registry
```python
# scripts/agentic-patch
def get_available_operations():
    """Get all available patch operations."""
    operations = {}
    
    # Import all operations
    try:
        from agentic_scrum_setup.patching.operations import (
            AddTemplateOperation,
            UpdateMCPOperation,
            FixCLIOperation,
            AddCommandOperation,
            SyncChangesOperation,
            update_security,
            add_background_agents,
            update_all
        )
        
        # Class-based operations
        operations['add-template'] = AddTemplateOperation
        operations['update-mcp'] = UpdateMCPOperation
        operations['fix-cli'] = FixCLIOperation
        operations['add-command'] = AddCommandOperation
        operations['sync-changes'] = SyncChangesOperation
        
        # Function-based operations
        operations['update-security'] = update_security
        operations['add-background-agents'] = add_background_agents
        operations['update-all'] = update_all
        
    except ImportError as e:
        print(f"Warning: Some operations unavailable: {e}")
    
    # Add built-in operations
    operations['rollback'] = 'rollback'
    operations['history'] = 'history'
    operations['status'] = 'status'
    
    return operations
```

### 2. Update Argument Parser
```python
def create_parser():
    """Create argument parser with all operations."""
    parser = argparse.ArgumentParser(
        prog='agentic-patch',
        description='AgenticScrum Remote Patching System'
    )
    
    # Get available operations
    operations = get_available_operations()
    operation_names = list(operations.keys())
    
    parser.add_argument(
        'operation',
        choices=operation_names,
        help='Patch operation to perform'
    )
    
    # Add operation-specific help
    operation_help = {
        'update-all': 'Apply all available updates to project',
        'add-background-agents': 'Add background agent execution system',
        'update-security': 'Add security training features',
        'add-template': 'Add new agent template',
        'update-mcp': 'Update MCP configuration',
        'fix-cli': 'Apply CLI fixes',
        'add-command': 'Add new command to CLI',
        'sync-changes': 'Sync changes back to framework',
        'rollback': 'Rollback a previous patch',
        'history': 'View patch history',
        'status': 'Show patching system status'
    }
    
    # ... rest of parser setup
```

### 3. Update Operation Execution
```python
def execute_operation(operation_name, patcher, args):
    """Execute the specified operation."""
    operations = get_available_operations()
    operation = operations.get(operation_name)
    
    if not operation:
        print(f"Error: Unknown operation '{operation_name}'")
        return False
    
    # Handle built-in operations
    if operation in ['rollback', 'history', 'status']:
        return handle_builtin_operation(operation, patcher, args)
    
    # Handle function-based operations
    if callable(operation) and not isinstance(operation, type):
        try:
            result = operation(
                patcher,
                target=args.target,
                description=args.description,
                dry_run=args.dry_run
            )
            return result.success if hasattr(result, 'success') else True
        except Exception as e:
            print(f"Error executing {operation_name}: {e}")
            return False
    
    # Handle class-based operations
    if isinstance(operation, type):
        try:
            op_instance = operation()
            # ... execute class-based operation
        except Exception as e:
            print(f"Error executing {operation_name}: {e}")
            return False
    
    return False
```

### 4. Add Operation Descriptions
```python
def show_operation_details(operation_name):
    """Show detailed help for an operation."""
    details = {
        'update-all': """
Apply comprehensive update to bring project up to date with latest framework.
Includes: MCP updates, agent templates, security features, init.sh patches.
        """,
        'add-background-agents': """
Add background agent execution system to project.
Includes: Runner script, MCP servers, init.sh commands, SMA updates.
        """,
        'update-security': """
Add security training features to project.
Includes: SAA training, developer priming, security documentation.
        """
    }
    
    if operation_name in details:
        print(f"\n{operation_name}:")
        print(details[operation_name])
```

## Testing Requirements

1. **Unit Tests**
   - Test operation discovery
   - Test argument parsing with new operations
   - Test operation execution dispatch

2. **Integration Tests**
   - Run each operation from standalone script
   - Verify operations work from different directories
   - Test with missing framework dependencies

3. **Manual Testing**
   - Test `agentic-patch update-all` from project directory
   - Test `agentic-patch add-background-agents`
   - Verify help text shows all operations

## Definition of Done

- [ ] All operations added to standalone script
- [ ] Operation discovery implemented
- [ ] Help system updated
- [ ] Error handling improved
- [ ] Tests written and passing
- [ ] Script works from any directory
- [ ] Documentation updated

## Dependencies

- Existing patch operations
- Framework discovery logic

## Notes

- Should maintain backward compatibility
- Consider making operation list dynamic
- May need to handle version mismatches

## Progress Tracking

- [x] Operation registry updated
- [x] Parser updated with new operations
- [x] Execution dispatch improved
- [x] Help system enhanced
- [x] Tests written
- [x] Manual testing complete
- [ ] PR created and reviewed

## Implementation Notes

Successfully added all missing operations to the standalone agentic-patch script:

1. **Dynamic Operation Discovery**: Added `get_available_operations()` that dynamically imports available operations
2. **Graceful Fallbacks**: Operations that aren't available show helpful messages about upgrading
3. **Framework Path Priority**: When --framework-path is specified, it takes priority over installed package
4. **Comprehensive Tests**: Created test suite with 8 tests covering all scenarios
5. **All operations work**: update-all, add-background-agents, and update-security all execute properly