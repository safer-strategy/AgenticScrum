# Story 321: Fix Template Variable Substitution in Patching System

**Epic**: E009 - Patching System Robustness
**Story Points**: 3
**Priority**: P1 (Critical)
**Status**: Ready
**Sprint**: Next
**Assigned To**: deva_python

## Story Description

As a developer using the AgenticScrum patching system,
I want template variables to be properly substituted when patching existing projects,
So that patched files contain actual values instead of Jinja2 template syntax.

## Problem Statement

When applying patches to existing projects, template variables like `{{ project_name }}`, `{{ language }}`, and `{{ agents | tojson }}` are being copied literally instead of being substituted with actual project values. This breaks JSON files and other configurations.

## Acceptance Criteria

1. **Project Context Loading**
   - [ ] Patching system reads `agentic_config.yaml` from target project
   - [ ] Extracts project_name, language, agents, and other template variables
   - [ ] Falls back to sensible defaults if config is missing

2. **Template Rendering**
   - [ ] All .j2 template files are rendered with project context before copying
   - [ ] Non-template files are copied as-is
   - [ ] JSON files maintain valid syntax after substitution

3. **Variable Resolution**
   - [ ] `{{ project_name }}` → actual project name
   - [ ] `{{ language }}` → project's primary language
   - [ ] `{{ agents | tojson }}` → JSON array of agents
   - [ ] `{% if enable_search %}` blocks → evaluated based on project config

4. **Error Handling**
   - [ ] Clear error messages when template variables can't be resolved
   - [ ] Validation of rendered output (especially JSON)
   - [ ] Rollback on template rendering failure

## Technical Implementation

### 1. Add Project Context Loader
```python
# agentic_scrum_setup/patching/utils/project_context.py
def load_project_context(project_path: Path) -> Dict[str, Any]:
    """Load project context for template rendering."""
    config_file = project_path / "agentic_config.yaml"
    
    if config_file.exists():
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
            
        # Extract template variables
        context = {
            'project_name': config.get('project_name', project_path.name),
            'language': config.get('language', 'python'),
            'agents': config.get('agents', ['poa', 'sma', 'deva_python', 'qaa']),
            'enable_search': config.get('enable_search', False),
            'enable_mcp': config.get('enable_mcp', True),
            # Add more as needed
        }
    else:
        # Fallback defaults
        context = {
            'project_name': project_path.name,
            'language': 'python',
            'agents': ['poa', 'sma', 'deva_python', 'qaa'],
            'enable_search': False,
            'enable_mcp': True
        }
    
    return context
```

### 2. Update Patch Operations
```python
# In each patch operation that copies templates
from jinja2 import Template

def apply_template_file(template_path: Path, target_path: Path, context: Dict):
    """Apply template with proper substitution."""
    template_content = template_path.read_text()
    
    # Render template
    template = Template(template_content)
    rendered = template.render(**context)
    
    # Validate if JSON
    if target_path.suffix == '.json':
        try:
            json.loads(rendered)
        except json.JSONDecodeError as e:
            raise ValueError(f"Template rendering produced invalid JSON: {e}")
    
    # Write rendered content
    target_path.write_text(rendered)
```

## Testing Requirements

1. **Unit Tests**
   - Test context loading from various project configurations
   - Test template rendering with different variable combinations
   - Test JSON validation after rendering

2. **Integration Tests**
   - Patch a project with all template variables
   - Patch a project with minimal config
   - Patch a project with missing config file

3. **Manual Testing**
   - Apply update_all to existing project
   - Verify .mcp.json has no template syntax
   - Verify all agent names are resolved correctly

## Definition of Done

- [ ] Project context loader implemented and tested
- [ ] All patch operations updated to use template rendering
- [ ] JSON validation added for .json files
- [ ] Unit tests pass with >90% coverage
- [ ] Integration tests verify real project patching
- [ ] Documentation updated with template variable list
- [ ] No template syntax remains in patched files

## Dependencies

- Jinja2 (already in requirements)
- PyYAML (already in requirements)

## Notes

- This is critical for the patching system to work correctly
- Affects all patch operations that copy template files
- Should be backwards compatible with existing patches

## Progress Tracking

- [ ] Context loader implemented
- [ ] Template rendering integrated
- [ ] Validation added
- [ ] Tests written
- [ ] Documentation updated
- [ ] PR created and reviewed