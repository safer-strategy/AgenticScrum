"""Update All - Comprehensive project update operation."""

import shutil
from pathlib import Path
from typing import List, Dict, Any

from ..patcher import PatchApplication
from ..utils.project_context import load_project_context
from ..utils.template_renderer import TemplateRenderer

def update_all(patcher, **kwargs) -> PatchApplication:
    """
    Comprehensive update that applies all relevant patches to bring a project 
    up to date with the latest AgenticScrum framework.
    
    This operation:
    1. Updates MCP configurations with latest templates
    2. Syncs agent templates and persona rules
    3. Updates init.sh with latest features
    4. Applies CLI improvements
    5. Updates coding standards and checklists
    
    Args:
        patcher: AgenticPatcher instance
        **kwargs: Additional arguments (target path is auto-detected)
    """
    
    project_path = Path.cwd()
    description = f"Comprehensive update of project at {project_path}"
    
    def apply_comprehensive_update():
        updates_applied = []
        errors = []
        
        # Load project context for template rendering
        context = load_project_context(project_path)
        renderer = TemplateRenderer(context)
        
        # 1. Update init.sh with latest template (most important)
        try:
            init_sh_path = project_path / "init.sh"
            if init_sh_path.exists():
                # Use the standalone patch script
                patch_script = patcher.framework_path / "scripts" / "patch-project-init.sh"
                if patch_script.exists():
                    import subprocess
                    result = subprocess.run([str(patch_script)], 
                                          cwd=str(project_path), 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        updates_applied.append("✅ Updated init.sh with latest framework integration")
                    else:
                        errors.append(f"❌ Failed to update init.sh: {result.stderr}")
                else:
                    errors.append("❌ Patch script not found - cannot update init.sh")
            else:
                updates_applied.append("ℹ️  No init.sh found - skipping init.sh update")
        except Exception as e:
            errors.append(f"❌ Error updating init.sh: {str(e)}")
        
        # 2. Update MCP configurations if they exist
        try:
            mcp_files = [".mcp.json", ".mcp-secrets.json.sample"]
            mcp_updated = False
            
            for mcp_file in mcp_files:
                template_path = patcher.framework_path / "agentic_scrum_setup" / "templates" / "claude" / f"{mcp_file}.j2"
                target_path = project_path / mcp_file
                
                if template_path.exists() and not target_path.exists():
                    # Render template with project context
                    renderer.render_file(template_path, target_path)
                    updates_applied.append(f"✅ Added {mcp_file}")
                    mcp_updated = True
                elif template_path.exists() and target_path.exists() and mcp_file == ".mcp.json":
                    # Existing MCP config - merge instead of overwrite
                    try:
                        from ..utils.mcp_merger import MCPConfigMerger
                        merger = MCPConfigMerger()
                        
                        project_name = _get_project_name(project_path)
                        backup_path = merger.merge_configs_safely(template_path, target_path, project_name, context)
                        
                        if backup_path:
                            updates_applied.append(f"✅ Updated {mcp_file} (preserved customizations, backup: {backup_path.name})")
                            mcp_updated = True
                        else:
                            updates_applied.append(f"ℹ️  {mcp_file} is already up to date")
                            
                    except Exception as e:
                        errors.append(f"⚠️  Could not merge {mcp_file}: {str(e)}")
                elif template_path.exists() and target_path.exists():
                    # Other files (.mcp-secrets.json.sample) - simple check
                    template_content = template_path.read_text()
                    current_content = target_path.read_text()
                    if len(template_content) != len(current_content):
                        project_name = _get_project_name(project_path)
                        rendered = template_content.replace("{{ project_name }}", project_name)
                        target_path.write_text(rendered)
                        updates_applied.append(f"✅ Updated {mcp_file}")
                        mcp_updated = True
            
            if not mcp_updated:
                updates_applied.append("ℹ️  MCP configurations are up to date")
                
        except Exception as e:
            errors.append(f"❌ Error updating MCP configurations: {str(e)}")
        
        # 3. Update agent templates with latest persona rules
        try:
            agents_dir = project_path / "agents"
            if agents_dir.exists():
                agent_updates = 0
                
                for agent_dir in agents_dir.iterdir():
                    if agent_dir.is_dir():
                        # Check for agent-specific updates
                        persona_file = agent_dir / "persona_rules.yaml"
                        if persona_file.exists():
                            # Look for corresponding template in framework
                            agent_name = agent_dir.name
                            template_dirs = [
                                patcher.framework_path / "agentic_scrum_setup" / "templates" / agent_name,
                                patcher.framework_path / "agentic_scrum_setup" / "templates" / "common"
                            ]
                            
                            for template_dir in template_dirs:
                                template_file = template_dir / "persona_rules.yaml.j2"
                                if template_file.exists():
                                    # Simple check - if template is newer or significantly different
                                    template_content = template_file.read_text()
                                    if "memory_patterns" in template_content and "memory_patterns" not in persona_file.read_text():
                                        # This is a newer template with memory patterns
                                        project_name = _get_project_name(project_path)
                                        rendered = template_content.replace("{{ project_name }}", project_name)
                                        persona_file.write_text(rendered)
                                        updates_applied.append(f"✅ Updated {agent_name} persona with memory patterns")
                                        agent_updates += 1
                                    break
                
                if agent_updates == 0:
                    updates_applied.append("ℹ️  Agent personas are up to date")
                    
        except Exception as e:
            errors.append(f"❌ Error updating agent templates: {str(e)}")
        
        # 4. Update coding standards and checklists if outdated
        try:
            standards_updates = 0
            standards_dir = project_path / "standards"
            if standards_dir.exists():
                # Check for coding standards updates
                coding_standards = standards_dir / "coding_standards.md"
                template_standards = patcher.framework_path / "agentic_scrum_setup" / "templates" / "standards" / "coding_standards.md.j2"
                
                if template_standards.exists():
                    template_content = template_standards.read_text()
                    if coding_standards.exists():
                        current_content = coding_standards.read_text()
                        # Simple heuristic: if template is significantly longer, it's probably newer
                        if len(template_content) > len(current_content) * 1.2:
                            project_name = _get_project_name(project_path)
                            rendered = template_content.replace("{{ project_name }}", project_name)
                            coding_standards.write_text(rendered)
                            updates_applied.append("✅ Updated coding standards")
                            standards_updates += 1
                    else:
                        project_name = _get_project_name(project_path)
                        rendered = template_content.replace("{{ project_name }}", project_name)
                        coding_standards.write_text(rendered)
                        updates_applied.append("✅ Added missing coding standards")
                        standards_updates += 1
            
            if standards_updates == 0:
                updates_applied.append("ℹ️  Coding standards are up to date")
                
        except Exception as e:
            errors.append(f"❌ Error updating coding standards: {str(e)}")
        
        # 5. Apply security updates
        try:
            # Import and run security update
            from .update_security import update_security
            
            # Create a mock patcher with just what we need
            class MockPatcher:
                def __init__(self, fw_path):
                    self.framework_path = fw_path
            
            mock_patcher = MockPatcher(patcher.framework_path)
            
            # Run security update in embedded mode (no duplicate output)
            print("\n📋 Checking for security updates...")
            from io import StringIO
            import sys
            old_stdout = sys.stdout
            sys.stdout = StringIO()
            
            try:
                result = update_security(mock_patcher, dry_run=False)
                output = sys.stdout.getvalue()
                if "Successfully applied security training updates" in output:
                    updates_applied.append("✅ Applied security training updates")
                elif "No security updates needed" in output:
                    updates_applied.append("ℹ️  Security features are up to date")
                else:
                    # Extract specific updates from output
                    for line in output.split('\n'):
                        if line.strip().startswith('✅'):
                            updates_applied.append(line.strip())
            finally:
                sys.stdout = old_stdout
                
        except Exception as e:
            errors.append(f"❌ Error applying security updates: {str(e)}")
        
        # 6. Apply background agent system
        try:
            # Import and run background agent update
            from .add_background_agents import add_background_agents
            
            # Run background agent update in embedded mode
            print("\n🤖 Checking for background agent system...")
            old_stdout = sys.stdout
            sys.stdout = StringIO()
            
            try:
                result = add_background_agents(mock_patcher, dry_run=False)
                output = sys.stdout.getvalue()
                if "Background Agent System Added Successfully" in output:
                    updates_applied.append("✅ Added background agent execution system")
                elif "background agent system already configured" in output:
                    updates_applied.append("ℹ️  Background agent system is up to date")
                else:
                    # Extract specific updates from output
                    for line in output.split('\n'):
                        if line.strip().startswith('✅'):
                            updates_applied.append(line.strip())
            finally:
                sys.stdout = old_stdout
                
        except Exception as e:
            errors.append(f"❌ Error adding background agent system: {str(e)}")
        
        # 7. Add animated banner if not present
        try:
            # Check if animated banner is already present
            init_sh_content = init_sh_path.read_text() if init_sh_path.exists() else ""
            if init_sh_path.exists() and "show_animated_banner" not in init_sh_content:
                # Import and apply animated banner
                from .add_animated_banner import add_animated_banner
                
                # Create a simple mock patcher for the operation
                class SimplePatcher:
                    def __init__(self, fw_path):
                        self.framework_path = fw_path
                
                simple_patcher = SimplePatcher(patcher.framework_path)
                result = add_animated_banner(simple_patcher, dry_run=False)
                
                if result.success:
                    updates_applied.append("✅ Added animated ASCII art banner to init.sh")
                else:
                    errors.append("⚠️  Could not add animated banner")
            elif init_sh_path.exists():
                updates_applied.append("ℹ️  Animated banner already present in init.sh")
                
        except Exception as e:
            errors.append(f"⚠️  Error checking animated banner: {str(e)}")
        
        # 8. Summary
        if updates_applied and not errors:
            print("\n🎉 Project Update Summary:")
            for update in updates_applied:
                print(f"  {update}")
            print(f"\n✅ Successfully applied {len([u for u in updates_applied if u.startswith('✅')])} updates")
            
        elif updates_applied and errors:
            print("\n⚠️  Project Update Summary (with some errors):")
            for update in updates_applied:
                print(f"  {update}")
            print("\n❌ Errors encountered:")
            for error in errors:
                print(f"  {error}")
            print(f"\n✅ Applied {len([u for u in updates_applied if u.startswith('✅')])} updates with {len(errors)} errors")
            
        elif errors:
            print("\n❌ Project Update Failed:")
            for error in errors:
                print(f"  {error}")
            raise Exception("Update failed with errors")
        
        else:
            print("\nℹ️  No updates needed - project is already up to date!")
    
    files_to_modify = [
        project_path / "init.sh",
        project_path / ".mcp.json",
        project_path / "agents",
        project_path / "standards"
    ]
    
    # For the update-all operation, we handle dry-run differently
    dry_run = kwargs.get('dry_run', False)
    
    if dry_run:
        print("🔍 DRY RUN: Comprehensive project update")
        print(f"📁 Project: {project_path}")
        print("")
        print("The following updates would be applied:")
        print("  ✅ Update init.sh with latest framework integration")
        print("  ✅ Update MCP configurations if outdated")
        print("  ✅ Update agent personas with memory patterns")
        print("  ✅ Update coding standards and checklists")
        print("")
        print("ℹ️  No changes applied in dry run mode")
        
        # Return a mock success result for dry run
        class MockResult:
            def __init__(self):
                self.success = True
                self.message = "Dry run completed successfully"
        
        return MockResult()
    else:
        # Apply the actual updates
        apply_comprehensive_update()
        
        # Return success result
        class SuccessResult:
            def __init__(self):
                self.success = True
                self.message = "Update completed successfully"
        
        return SuccessResult()

def _get_project_name(project_path: Path) -> str:
    """Extract project name from agentic_config.yaml."""
    config_file = project_path / "agentic_config.yaml"
    if not config_file.exists():
        return project_path.name
    
    try:
        import yaml
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
            # Try different possible locations for project name
            name = config.get('project_name', '')
            if not name and 'project' in config:
                name = config['project'].get('name', '')
            return name or project_path.name
    except Exception:
        return project_path.name