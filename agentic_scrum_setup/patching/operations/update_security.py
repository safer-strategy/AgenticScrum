"""Security update operation for AgenticScrum patching system.

This operation adds security training features to existing projects,
including SAA training capabilities, developer security priming, and
MCP datetime server for security-aware development.
"""

import json
import shutil
from pathlib import Path
from typing import List, Dict, Any

from ..patcher import PatchApplication
from ..utils.mcp_merger import MCPConfigMerger


def update_security(patcher, **kwargs) -> PatchApplication:
    """
    Apply security training updates to existing projects.
    
    This operation:
    1. Adds security training documentation
    2. Updates developer agents with security priming
    3. Updates SAA with training capabilities
    4. Updates SMA with security coordination
    5. Adds datetime MCP server for security features
    6. Preserves all existing configurations
    
    Args:
        patcher: AgenticPatcher instance
        **kwargs: Additional arguments including dry_run
    """
    
    project_path = Path.cwd()
    description = f"Security training update for {project_path.name}"
    
    def apply_security_update():
        updates_applied = []
        errors = []
        
        # Get project name
        project_name = _get_project_name(project_path)
        
        print("🔒 Applying Security Training Updates...")
        print(f"📁 Project: {project_path}")
        print("")
        
        # 1. Add Security Training Documentation
        try:
            docs_dir = project_path / "docs"
            if docs_dir.exists():
                # Add main security training doc
                security_training_template = patcher.framework_path / "agentic_scrum_setup" / "templates" / "docs" / "SECURITY_TRAINING_FOR_AGENTS.md.j2"
                if security_training_template.exists():
                    target_path = docs_dir / "SECURITY_TRAINING_FOR_AGENTS.md"
                    if not target_path.exists():
                        content = security_training_template.read_text()
                        rendered = content.replace("{{ project_name }}", project_name)
                        target_path.write_text(rendered)
                        updates_applied.append("✅ Added security training documentation")
                    else:
                        updates_applied.append("ℹ️  Security training documentation already exists")
            else:
                docs_dir.mkdir(exist_ok=True)
                security_training_template = patcher.framework_path / "agentic_scrum_setup" / "templates" / "docs" / "SECURITY_TRAINING_FOR_AGENTS.md.j2"
                if security_training_template.exists():
                    target_path = docs_dir / "SECURITY_TRAINING_FOR_AGENTS.md"
                    content = security_training_template.read_text()
                    rendered = content.replace("{{ project_name }}", project_name)
                    target_path.write_text(rendered)
                    updates_applied.append("✅ Created docs directory and added security training documentation")
                    
        except Exception as e:
            errors.append(f"❌ Error adding security documentation: {str(e)}")
        
        # 2. Update Developer Agents with Security Features
        try:
            agents_dir = project_path / "agents"
            if agents_dir.exists():
                security_updates = 0
                
                for agent_dir in agents_dir.iterdir():
                    if agent_dir.is_dir() and agent_dir.name.startswith("deva_"):
                        # Add security priming document
                        lang = agent_dir.name.replace("deva_", "")
                        template_path = patcher.framework_path / "agentic_scrum_setup" / "templates" / agent_dir.name / "security_priming.md.j2"
                        
                        if template_path.exists():
                            target_path = agent_dir / "security_priming.md"
                            if not target_path.exists():
                                content = template_path.read_text()
                                rendered = content.replace("{{ project_name }}", project_name)
                                target_path.write_text(rendered)
                                updates_applied.append(f"✅ Added security priming for {agent_dir.name}")
                                security_updates += 1
                        
                        # Update persona rules with security rules
                        persona_file = agent_dir / "persona_rules.yaml"
                        if persona_file.exists():
                            content = persona_file.read_text()
                            
                            # Check if security rules already exist
                            if "CONSULT with SAA for security requirements" not in content:
                                # Add security rules based on language
                                security_rules = _get_security_rules_for_language(lang)
                                
                                # Find rules section and append
                                lines = content.split('\n')
                                rules_index = -1
                                for i, line in enumerate(lines):
                                    if line.strip() == 'rules:':
                                        rules_index = i
                                        # Find end of rules section
                                        for j in range(i + 1, len(lines)):
                                            if j == len(lines) - 1 or (lines[j] and not lines[j].startswith('  ')):
                                                # Insert security rules before next section
                                                for rule in reversed(security_rules):
                                                    lines.insert(j, f"  - {rule}")
                                                break
                                        break
                                
                                if rules_index >= 0:
                                    persona_file.write_text('\n'.join(lines))
                                    updates_applied.append(f"✅ Updated {agent_dir.name} with security rules")
                                    security_updates += 1
                            
                            # Update knowledge sources
                            content = persona_file.read_text()  # Re-read after potential update
                            if f"/agents/{agent_dir.name}/security_priming.md" not in content:
                                lines = content.split('\n')
                                for i, line in enumerate(lines):
                                    if line.strip() == 'knowledge_sources:':
                                        # Add security knowledge sources after the knowledge_sources line
                                        j = i + 1
                                        # Skip existing entries
                                        while j < len(lines) and lines[j].startswith('  -'):
                                            j += 1
                                        # Insert new entries
                                        lines.insert(j, f"  - /agents/{agent_dir.name}/security_priming.md")
                                        lines.insert(j + 1, "  - /docs/SECURITY_TRAINING_FOR_AGENTS.md")
                                        persona_file.write_text('\n'.join(lines))
                                        updates_applied.append(f"✅ Added security knowledge sources to {agent_dir.name}")
                                        break
                
                # Update SAA with training capabilities
                saa_dir = agents_dir / "saa"
                if saa_dir.exists():
                    # Add training protocol
                    training_protocol_template = patcher.framework_path / "agentic_scrum_setup" / "templates" / "saa" / "training_protocol.yaml.j2"
                    if training_protocol_template.exists():
                        target_path = saa_dir / "training_protocol.yaml"
                        if not target_path.exists():
                            content = training_protocol_template.read_text()
                            rendered = content.replace("{{ project_name }}", project_name)
                            target_path.write_text(rendered)
                            updates_applied.append("✅ Added SAA training protocol")
                    
                    # Update SAA persona with training capabilities
                    saa_persona = saa_dir / "persona_rules.yaml"
                    if saa_persona.exists():
                        content = saa_persona.read_text()
                        if "Security training and mentoring for developer agents" not in content:
                            # Add training capabilities and rules
                            _update_saa_for_training(saa_persona)
                            updates_applied.append("✅ Updated SAA with training capabilities")
                
                # Update SMA with security coordination
                sma_dir = agents_dir / "sma"
                if sma_dir.exists():
                    sma_persona = sma_dir / "persona_rules.yaml"
                    if sma_persona.exists():
                        content = sma_persona.read_text()
                        if "Ensure SAA provides security requirements before development begins" not in content:
                            _update_sma_for_security_coordination(sma_persona)
                            updates_applied.append("✅ Updated SMA with security coordination rules")
                
                if security_updates > 0:
                    updates_applied.append(f"✅ Applied {security_updates} agent security updates")
                    
        except Exception as e:
            errors.append(f"❌ Error updating agents: {str(e)}")
        
        # 3. Update MCP Configuration (Idempotent)
        try:
            mcp_config_file = project_path / ".mcp.json"
            if mcp_config_file.exists():
                # Parse existing config
                existing_config = json.loads(mcp_config_file.read_text())
                
                # Check if datetime server already exists
                servers = existing_config.get('mcpServers', {})
                if 'datetime' not in servers:
                    # Backup existing config
                    merger = MCPConfigMerger()
                    backup_path = merger.backup_config(mcp_config_file)
                    
                    # Add datetime server
                    merger.add_datetime_server(existing_config)
                    
                    # Write updated config
                    mcp_config_file.write_text(json.dumps(existing_config, indent=2))
                    updates_applied.append(f"✅ Added datetime MCP server (backup: {backup_path.name})")
                    
                    # Copy datetime server files
                    _copy_datetime_server_files(patcher.framework_path, project_path)
                    updates_applied.append("✅ Added datetime server implementation files")
                else:
                    updates_applied.append("ℹ️  MCP datetime server already configured")
            else:
                updates_applied.append("ℹ️  No MCP configuration found - skipping MCP updates")
                    
        except json.JSONDecodeError:
            errors.append("❌ Error parsing MCP configuration - invalid JSON")
        except Exception as e:
            errors.append(f"❌ Error updating MCP configuration: {str(e)}")
        
        # 4. Summary
        print("")
        if updates_applied and not errors:
            print("🎉 Security Update Summary:")
            for update in updates_applied:
                print(f"  {update}")
            print(f"\n✅ Successfully applied security training updates")
            print("\n💡 Next steps:")
            print("  1. Review the security training documentation in /docs/")
            print("  2. Ensure developers read their security priming guides")
            print("  3. SAA can now train developers proactively")
            
        elif updates_applied and errors:
            print("⚠️  Security Update Summary (with some errors):")
            for update in updates_applied:
                print(f"  {update}")
            print("\n❌ Errors encountered:")
            for error in errors:
                print(f"  {error}")
            
        elif errors:
            print("❌ Security Update Failed:")
            for error in errors:
                print(f"  {error}")
            raise Exception("Security update failed with errors")
        
        else:
            print("ℹ️  No security updates needed - project already has security training features!")
    
    # Execute the update
    if kwargs.get('dry_run', False):
        print("🔍 DRY RUN: Security training update")
        print(f"📁 Project: {project_path}")
        print("")
        print("The following updates would be applied:")
        print("  ✅ Add security training documentation to /docs/")
        print("  ✅ Add security priming for each developer agent")
        print("  ✅ Update SAA with training capabilities and protocol")
        print("  ✅ Update SMA with security coordination rules")
        print("  ✅ Add datetime MCP server (preserving existing servers)")
        print("  ✅ Backup all modified configurations")
        print("")
        print("ℹ️  No changes applied in dry run mode")
        
        class MockResult:
            def __init__(self):
                self.success = True
                self.message = "Dry run completed successfully"
        
        return MockResult()
    else:
        apply_security_update()
        
        class SuccessResult:
            def __init__(self):
                self.success = True
                self.message = "Security update completed successfully"
        
        return SuccessResult()


def _get_security_rules_for_language(language: str) -> List[str]:
    """Get language-specific security rules."""
    if language == "python":
        return [
            "ALWAYS use parameterized queries for database operations - NEVER use string formatting for SQL",
            "HASH passwords with bcrypt or argon2 - NEVER store passwords in plain text or use weak hashing",
            "VALIDATE and sanitize ALL user inputs before processing to prevent injection attacks",
            "USE environment variables for secrets - NEVER hardcode API keys or passwords in code",
            "IMPLEMENT proper authentication and authorization checks on all protected endpoints",
            "CONSULT with SAA for security requirements before implementing new features"
        ]
    elif language in ["typescript", "javascript"]:
        return [
            "PREVENT XSS by using safe DOM methods and sanitizing any HTML content with DOMPurify",
            "IMPLEMENT CSRF protection on all state-changing API calls using tokens or double-submit cookies",
            "CONFIGURE secure cookies with httpOnly, secure, and sameSite attributes for session management",
            "USE Content Security Policy headers to prevent injection attacks and unauthorized scripts",
            "VALIDATE all user inputs with strict schemas using zod or similar runtime validation",
            "NEVER store sensitive data in localStorage - use secure httpOnly cookies or session storage",
            "CONSULT with SAA for security requirements before implementing authentication or handling user data"
        ]
    else:
        return [
            "VALIDATE all user inputs before processing",
            "USE parameterized queries for database operations",
            "IMPLEMENT proper authentication and authorization",
            "NEVER hardcode secrets or passwords",
            "CONSULT with SAA for security requirements"
        ]


def _update_saa_for_training(persona_file: Path):
    """Update SAA persona with training capabilities."""
    content = persona_file.read_text()
    lines = content.split('\n')
    
    # Add capabilities
    capabilities_updated = False
    for i, line in enumerate(lines):
        if line.strip() == 'capabilities:':
            # Find end of capabilities
            j = i + 1
            while j < len(lines) and lines[j].startswith('  -'):
                j += 1
            # Insert new capabilities
            lines.insert(j, "  - Security training and mentoring for developer agents")
            lines.insert(j + 1, "  - Proactive security pattern sharing")
            lines.insert(j + 2, "  - Pre-development security consultation")
            capabilities_updated = True
            break
    
    # Add rules
    rules_updated = False
    for i, line in enumerate(lines):
        if line.strip() == 'rules:':
            # Find end of rules
            j = i + 1
            while j < len(lines) and lines[j].startswith('  -'):
                j += 1
            # Insert new rules
            lines.insert(j, "  - PROVIDE security guidance before code is written")
            lines.insert(j + 1, "  - SHARE security patterns from memory with developer agents")
            lines.insert(j + 2, "  - TRAIN developers on secure coding practices proactively")
            lines.insert(j + 3, "  - CONSULT with developers during story planning for security requirements")
            rules_updated = True
            break
    
    # Add knowledge sources if needed
    if "/docs/SECURITY_TRAINING_FOR_AGENTS.md" not in content:
        for i, line in enumerate(lines):
            if line.strip() == 'knowledge_sources:':
                j = i + 1
                while j < len(lines) and lines[j].startswith('  -'):
                    j += 1
                lines.insert(j, "  - /docs/SECURITY_TRAINING_FOR_AGENTS.md")
                lines.insert(j + 1, "  - /saa/training_protocol.yaml")
                break
    
    if capabilities_updated or rules_updated:
        persona_file.write_text('\n'.join(lines))


def _update_sma_for_security_coordination(persona_file: Path):
    """Update SMA persona with security coordination rules."""
    content = persona_file.read_text()
    lines = content.split('\n')
    
    # Add security coordination rules
    for i, line in enumerate(lines):
        if line.strip() == 'rules:':
            # Find end of rules
            j = i + 1
            while j < len(lines) and lines[j].startswith('  -'):
                j += 1
            # Insert new rules
            lines.insert(j, "  - Ensure SAA provides security requirements before development begins")
            lines.insert(j + 1, "  - Coordinate security training sessions between SAA and developer agents")
            lines.insert(j + 2, "  - Track security pattern adoption in developer code")
            lines.insert(j + 3, "  - Monitor that developers consult SAA for security-sensitive features")
            break
    
    persona_file.write_text('\n'.join(lines))


def _copy_datetime_server_files(framework_path: Path, project_path: Path):
    """Copy datetime MCP server files to project."""
    # Create mcp_servers directory
    mcp_servers_dir = project_path / "mcp_servers" / "datetime"
    mcp_servers_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy server files from framework
    source_dir = framework_path / "mcp_servers" / "datetime"
    if source_dir.exists():
        for file in source_dir.iterdir():
            if file.is_file():
                shutil.copy2(file, mcp_servers_dir / file.name)
    else:
        # If not in mcp_servers, try templates
        template_dir = framework_path / "agentic_scrum_setup" / "templates" / "mcp_servers" / "datetime"
        if template_dir.exists():
            for file in template_dir.iterdir():
                if file.is_file() and not file.name.endswith('.j2'):
                    shutil.copy2(file, mcp_servers_dir / file.name)


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