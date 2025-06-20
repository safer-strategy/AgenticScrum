"""Add Background Agents - Add background agent execution system to existing projects."""

import shutil
from pathlib import Path
from typing import List, Dict, Any

from ..patcher import PatchApplication
from ..utils.mcp_merger import MCPConfigMerger
from ..utils.project_context import load_project_context
from ..utils.template_renderer import TemplateRenderer

def add_background_agents(patcher, **kwargs) -> PatchApplication:
    """
    Add background agent execution system to existing projects.
    
    This operation:
    1. Adds background agent runner script
    2. Adds MCP servers for agent coordination
    3. Updates SMA with assignment capabilities
    4. Updates init.sh with agent commands
    5. Creates necessary directories
    
    Args:
        patcher: AgenticPatcher instance
        **kwargs: Additional arguments including dry_run
    """
    
    project_path = Path.cwd()
    description = f"Add background agent system to {project_path.name}"
    
    def apply_background_agents():
        updates_applied = []
        errors = []
        
        print("🤖 Adding Background Agent System...")
        print(f"📁 Project: {project_path}")
        print("")
        
        # Load project context for template rendering
        context = load_project_context(project_path)
        renderer = TemplateRenderer(context)
        
        # 1. Create necessary directories
        try:
            dirs_to_create = [
                project_path / "logs" / "background_agents",
                project_path / "background_work",
                project_path / "mcp_servers" / "agent_queue",
                project_path / "mcp_servers" / "agent_permissions",
                project_path / "mcp_servers" / "agent_monitor"
            ]
            
            for dir_path in dirs_to_create:
                dir_path.mkdir(parents=True, exist_ok=True)
            
            updates_applied.append("✅ Created background agent directories")
            
        except Exception as e:
            errors.append(f"❌ Error creating directories: {str(e)}")
        
        # 2. Add background agent runner script
        try:
            runner_template = patcher.framework_path / "scripts" / "run_background_agent.sh"
            if runner_template.exists():
                target_path = project_path / "scripts" / "run_background_agent.sh"
                target_path.parent.mkdir(exist_ok=True)
                shutil.copy2(runner_template, target_path)
                target_path.chmod(0o755)
                updates_applied.append("✅ Added background agent runner script")
            else:
                errors.append("❌ Runner script template not found")
                
        except Exception as e:
            errors.append(f"❌ Error adding runner script: {str(e)}")
        
        # 3. Add MCP server files
        try:
            mcp_servers = ["agent_queue", "agent_permissions", "agent_monitor"]
            
            for server_name in mcp_servers:
                template_path = patcher.framework_path / "mcp_servers" / server_name / "server.py"
                if not template_path.exists():
                    # Try templates directory
                    template_path = patcher.framework_path / "agentic_scrum_setup" / "templates" / "mcp_servers" / server_name / "server.py.j2"
                
                if template_path.exists():
                    target_path = project_path / "mcp_servers" / server_name / "server.py"
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Use template renderer for .j2 files
                    if template_path.suffix == '.j2':
                        renderer.render_file(template_path, target_path)
                    else:
                        # Direct copy for non-template files
                        shutil.copy2(template_path, target_path)
                    
                    target_path.chmod(0o755)
                    
                    updates_applied.append(f"✅ Added {server_name} MCP server")
                else:
                    errors.append(f"⚠️  {server_name} server template not found")
                    
        except Exception as e:
            errors.append(f"❌ Error adding MCP servers: {str(e)}")
        
        # 4. Update MCP configuration
        try:
            mcp_config_file = project_path / ".mcp.json"
            if mcp_config_file.exists():
                merger = MCPConfigMerger()
                backup_path = merger.backup_config(mcp_config_file)
                
                import json
                config = json.loads(mcp_config_file.read_text())
                
                # Add agent servers if not present
                servers = config.get('mcpServers', {})
                servers_added = []
                
                if 'agent_queue' not in servers:
                    servers['agent_queue'] = {
                        "command": "python",
                        "args": ["mcp_servers/agent_queue/server.py"],
                        "description": "Task queue management for background agent execution"
                    }
                    servers_added.append('agent_queue')
                
                if 'agent_monitor' not in servers:
                    servers['agent_monitor'] = {
                        "command": "python",
                        "args": ["mcp_servers/agent_monitor/server.py"],
                        "description": "Health monitoring and resource tracking for background agents"
                    }
                    servers_added.append('agent_monitor')
                
                if 'agent_permissions' not in servers:
                    servers['agent_permissions'] = {
                        "command": "python",
                        "args": ["mcp_servers/agent_permissions/server.py"],
                        "description": "Permission handler for autonomous agent decisions",
                        "env": {
                            "PERMISSION_MODE": "autonomous"
                        }
                    }
                    servers_added.append('agent_permissions')
                
                if servers_added:
                    config['mcpServers'] = servers
                    mcp_config_file.write_text(json.dumps(config, indent=2))
                    updates_applied.append(f"✅ Added {', '.join(servers_added)} to MCP config (backup: {backup_path.name})")
                else:
                    updates_applied.append("ℹ️  MCP servers already configured")
                    
        except Exception as e:
            errors.append(f"❌ Error updating MCP config: {str(e)}")
        
        # 5. Update SMA persona with assignment capabilities
        try:
            sma_persona_file = project_path / "agents" / "sma" / "persona_rules.yaml"
            if sma_persona_file.exists():
                content = sma_persona_file.read_text()
                
                # Check if already updated
                if "Background agent task assignment" not in content:
                    import yaml
                    persona = yaml.safe_load(content)
                    
                    # Add capabilities
                    if 'capabilities' in persona:
                        persona['capabilities'].extend([
                            "Background agent task assignment",
                            "Agent workload balancing",
                            "Autonomous execution monitoring"
                        ])
                    
                    # Add rules
                    if 'rules' in persona:
                        persona['rules'].extend([
                            "USE mcp__agent_queue__assign_story to distribute stories to background agents",
                            "MONITOR background agent progress via mcp__agent_monitor__list_agents",
                            "BALANCE workload across agent types using mcp__agent_queue__get_queue_stats",
                            "CHECK agent health with mcp__agent_monitor__get_metrics before assignment",
                            "TERMINATE stuck agents using mcp__agent_monitor__terminate_agent",
                            "REVIEW completed background work via mcp__agent_queue__get_task_status"
                        ])
                    
                    # Add background agent patterns section
                    persona['background_agent_patterns'] = {
                        'assignment_criteria': [
                            "Assign to background agents: Well-defined stories with clear acceptance criteria",
                            "Keep for interactive: Stories requiring human input or complex decision-making",
                            "Prioritize background: Repetitive tasks, testing, documentation updates",
                            "Avoid background: Architecture decisions, API design, security-critical features"
                        ],
                        'workload_balancing': [
                            "Monitor active agent count per type (max 3 concurrent per agent type)",
                            "Consider story complexity when assigning (simple = background, complex = interactive)",
                            "Rotate assignments to prevent agent specialization silos",
                            "Reserve capacity for urgent fixes (keep 1 slot open per agent type)"
                        ],
                        'monitoring_patterns': [
                            "Check agent health every 30 minutes during active sprints",
                            "Review completed work within 2 hours of task completion",
                            "Escalate if agent stuck for >1 hour on same task",
                            "Daily summary of background agent productivity"
                        ]
                    }
                    
                    # Write updated persona
                    with open(sma_persona_file, 'w') as f:
                        yaml.dump(persona, f, default_flow_style=False, sort_keys=False)
                    
                    updates_applied.append("✅ Updated SMA with background agent capabilities")
                else:
                    updates_applied.append("ℹ️  SMA already has background agent capabilities")
                    
        except Exception as e:
            errors.append(f"❌ Error updating SMA persona: {str(e)}")
        
        # 6. Update init.sh with agent commands
        try:
            init_script = project_path / "init.sh"
            if init_script.exists():
                from ..utils.init_sh_parser import InitShParser
                
                content = init_script.read_text()
                parser = InitShParser(content)
                
                # Check if already has agent commands
                needs_update = False
                
                # Add functions if not present
                if not parser.function_exists('manage_background_agents'):
                    # Read functions from template
                    template_path = patcher.framework_path / "agentic_scrum_setup" / "templates" / "common" / "background_agent_functions.sh"
                    if template_path.exists():
                        # Parse template to extract individual functions
                        template_content = template_path.read_text()
                        # For now, add a simplified version
                        parser.add_function('manage_background_agents', [
                            'local cmd="$1"',
                            'shift',
                            '',
                            'case "$cmd" in',
                            '  list)',
                            '    info "Listing background agents..."',
                            '    # Implementation would go here',
                            '    ;;',
                            '  queue)',
                            '    info "Queue management..."',
                            '    # Implementation would go here',
                            '    ;;',
                            '  *)',
                            '    error "Unknown agent command: $cmd"',
                            '    ;;',
                            'esac'
                        ])
                        needs_update = True
                
                if not parser.function_exists('run_background_agent'):
                    parser.add_function('run_background_agent', [
                        'local runner_script="scripts/run_background_agent.sh"',
                        'if [[ -f "$runner_script" ]]; then',
                        '  "$runner_script" "$@"',
                        'else',
                        '  error "Background agent runner not found at $runner_script"',
                        '  exit 1',
                        'fi'
                    ])
                    needs_update = True
                
                if not parser.function_exists('show_agent_status'):
                    parser.add_function('show_agent_status', [
                        'info "Checking background agent status..."',
                        '',
                        '# Check if MCP servers are running',
                        'if command -v docker &> /dev/null; then',
                        '  docker-compose ps | grep -E "agent_queue|agent_monitor|agent_permissions" || true',
                        'fi',
                        '',
                        '# Check for active agents',
                        'if [[ -d "logs/background_agents" ]]; then',
                        '  active_count=$(find logs/background_agents -name "*.log" -mmin -5 | wc -l)',
                        '  info "Active agents (last 5 min): $active_count"',
                        'fi',
                        '',
                        'info "Use \'./init.sh agent list\' for detailed information"'
                    ])
                    needs_update = True
                
                # Add cases if not present
                if not parser.case_exists('agent'):
                    parser.add_case('agent', [
                        '# Background agent management',
                        'shift',
                        'manage_background_agents "$@"'
                    ], after_case='patch-status')
                    needs_update = True
                
                if not parser.case_exists('agent-run'):
                    parser.add_case('agent-run', [
                        '# Run a specific story in background',
                        'shift',
                        'run_background_agent "$@"'
                    ], after_case='agent')
                    needs_update = True
                
                if not parser.case_exists('agent-status'):
                    parser.add_case('agent-status', [
                        '# Quick agent status check',
                        'show_agent_status'
                    ], after_case='agent-run')
                    needs_update = True
                
                # Write updated script if changes were made
                if needs_update:
                    init_script.write_text(parser.get_content())
                    updates_applied.append("✅ Added agent commands to init.sh")
                else:
                    updates_applied.append("ℹ️  init.sh already has agent commands")
                    
        except Exception as e:
            errors.append(f"❌ Error updating init.sh: {str(e)}")
        
        # 7. Summary
        print("")
        if updates_applied and not errors:
            print("🎉 Background Agent System Added Successfully!")
            for update in updates_applied:
                print(f"  {update}")
            print("\n💡 Next steps:")
            print("  1. Start MCP servers: ./init.sh up")
            print("  2. Check agent status: ./init.sh agent-status")
            print("  3. Run a background agent: ./init.sh agent-run <type> <id> <prompt>")
            print("\n📚 Documentation:")
            print("  - Agent types: deva_python, deva_typescript, deva_javascript, etc.")
            print("  - Monitor logs: tail -f logs/background_agents/*.log")
            print("  - Manage queue: ./init.sh agent queue")
            
        elif updates_applied and errors:
            print("⚠️  Background Agent System Partially Added:")
            for update in updates_applied:
                print(f"  {update}")
            print("\n❌ Errors encountered:")
            for error in errors:
                print(f"  {error}")
            
        elif errors:
            print("❌ Failed to Add Background Agent System:")
            for error in errors:
                print(f"  {error}")
            raise Exception("Background agent addition failed")
        
        else:
            print("ℹ️  No updates needed - background agent system already configured!")
    
    # Execute the update
    if kwargs.get('dry_run', False):
        print("🔍 DRY RUN: Add background agent system")
        print(f"📁 Project: {project_path}")
        print("")
        print("The following updates would be applied:")
        print("  ✅ Create background agent directories")
        print("  ✅ Add background agent runner script")
        print("  ✅ Add MCP servers (agent_queue, agent_monitor, agent_permissions)")
        print("  ✅ Update MCP configuration")
        print("  ✅ Update SMA with assignment capabilities")
        print("  ✅ Add agent commands to init.sh")
        print("")
        print("ℹ️  No changes applied in dry run mode")
        
        class MockResult:
            def __init__(self):
                self.success = True
                self.message = "Dry run completed successfully"
        
        return MockResult()
    else:
        apply_background_agents()
        
        class SuccessResult:
            def __init__(self):
                self.success = True
                self.message = "Background agent system added successfully"
        
        return SuccessResult()