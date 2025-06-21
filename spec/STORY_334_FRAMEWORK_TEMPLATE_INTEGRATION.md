# STORY_334: Framework Template Integration

**Date**: 2025-06-21  
**Priority**: P2 (Medium)  
**Story Points**: 8  
**Assigned to**: deva_python  
**Epic**: AUTONOMOUS_QA_VALIDATION_SYSTEM  
**Sprint**: Next  

## User Story

As a framework user, I want QA validation capabilities to be available in all new projects so that quality is built-in from the start.

## Background

The autonomous QA validation system must be fully integrated into the AgenticScrum framework template system so that all new projects automatically include QA validation capabilities. This story implements the template integration, project initialization updates, and ensures backward compatibility with existing projects.

## Acceptance Criteria

1. **QA Templates Integration**
   - [ ] Add QA templates to `agentic_scrum_setup/templates/qa/` directory
   - [ ] Create Jinja2 templates for all QA components
   - [ ] Integrate QA directory structure with project generation
   - [ ] Add QA configuration options to template variables
   - [ ] Ensure QA templates follow existing naming conventions

2. **Project Initialization Integration**
   - [ ] Integrate QA agent creation in project initialization
   - [ ] Add QA validation workflow to `init.sh` generation
   - [ ] Include QA queue management in project setup
   - [ ] Add QA MCP servers to project configuration
   - [ ] Support QA-specific environment variables

3. **Configuration Integration**
   - [ ] Add QA configuration to `agentic_config.yaml.j2`
   - [ ] Include QA settings in project configuration
   - [ ] Add QA agent personas to agent configuration
   - [ ] Integrate QA validation triggers with project settings
   - [ ] Support customizable QA validation rules

4. **CLI and Init Script Integration**
   - [ ] Add QA validation commands to `init.sh` template
   - [ ] Include QA status checking in CLI
   - [ ] Add QA report generation commands
   - [ ] Integrate QA agent management with existing agent commands
   - [ ] Support QA validation queue management

5. **Backward Compatibility**
   - [ ] Ensure existing projects remain functional
   - [ ] Support incremental QA system adoption
   - [ ] Provide migration path for existing projects
   - [ ] Maintain compatibility with existing agent systems
   - [ ] Support opt-in QA validation for legacy projects

6. **Documentation and Examples**
   - [ ] Update project documentation with QA capabilities
   - [ ] Create QA validation examples and tutorials
   - [ ] Document QA configuration options
   - [ ] Provide troubleshooting guides for QA issues
   - [ ] Include QA best practices in framework documentation

## Technical Implementation Details

### QA Template Directory Structure

```
agentic_scrum_setup/templates/qa/
├── README.md.j2                    # QA system documentation
├── directory_structure.j2           # QA directory creation template
├── reports/
│   ├── bug_report_template.md.j2
│   ├── validation_report_template.md.j2
│   └── test_execution_report.md.j2
├── queue/
│   ├── pending_validation.json.j2
│   ├── active_qa_sessions.json.j2
│   └── bugfix_queue.json.j2
├── agents/
│   ├── qa_automation_agent/
│   │   └── persona_rules.yaml.j2
│   └── background_qa_runner/
│       └── persona_rules.yaml.j2
├── scripts/
│   ├── qa_monitor.py.j2
│   ├── validation_runner.py.j2
│   └── bug_detector.py.j2
└── config/
    ├── qa_config.yaml.j2
    └── validation_rules.yaml.j2
```

### Enhanced Setup Core Integration

```python
# Enhanced setup_core.py integration
from pathlib import Path
from typing import Dict, Any, List

class QATemplateIntegration:
    """Integrates QA templates with AgenticScrum project generation."""
    
    def __init__(self, setup_core):
        self.setup_core = setup_core
        self.qa_template_dir = Path(__file__).parent / "templates" / "qa"
        
    def integrate_qa_templates(self, project_config: Dict[str, Any]) -> bool:
        """Integrate QA templates into project generation."""
        
        try:
            # Add QA configuration to project config
            qa_config = self.generate_qa_config(project_config)
            project_config['qa'] = qa_config
            
            # Create QA directory structure
            self.create_qa_directories(project_config)
            
            # Render QA templates
            self.render_qa_templates(project_config)
            
            # Update agent configurations
            self.update_agent_configurations(project_config)
            
            # Integrate QA into init.sh
            self.integrate_qa_init_commands(project_config)
            
            # Update MCP configuration
            self.add_qa_mcp_servers(project_config)
            
            return True
            
        except Exception as e:
            logging.error(f"Failed to integrate QA templates: {e}")
            return False
    
    def generate_qa_config(self, project_config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate QA-specific configuration."""
        
        return {
            'enabled': True,
            'validation_modes': ['automatic', 'manual'],
            'background_agents': {
                'enabled': True,
                'max_concurrent': 3,
                'auto_assignment': True
            },
            'validation_layers': {
                'code_quality': True,
                'functional': True,
                'integration': True,
                'user_experience': True
            },
            'bug_detection': {
                'enabled': True,
                'auto_reporting': True,
                'severity_thresholds': {
                    'critical': 0,
                    'high': 2,
                    'medium': 5,
                    'low': 10
                }
            },
            'reporting': {
                'daily_summary': True,
                'weekly_trends': True,
                'real_time_alerts': True
            },
            'quality_gates': {
                'minimum_coverage': 85,
                'max_performance_regression': 20,
                'security_scan_required': True
            }
        }
    
    def create_qa_directories(self, project_config: Dict[str, Any]):
        """Create QA directory structure in project."""
        
        project_path = Path(project_config['output_dir']) / project_config['project_name']
        
        qa_directories = [
            'qa',
            'qa/reports',
            'qa/reports/automated',
            'qa/reports/bugs',
            'qa/reports/bugs/critical',
            'qa/reports/bugs/high',
            'qa/reports/bugs/medium',
            'qa/reports/bugs/low',
            'qa/reports/validation',
            'qa/agents',
            'qa/agents/qa_automation_agent',
            'qa/agents/background_qa_runner',
            'qa/templates',
            'qa/queue',
            'qa/scripts',
            'qa/config'
        ]
        
        for directory in qa_directories:
            dir_path = project_path / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            logging.info(f"Created QA directory: {dir_path}")
    
    def render_qa_templates(self, project_config: Dict[str, Any]):
        """Render all QA templates with project configuration."""
        
        project_path = Path(project_config['output_dir']) / project_config['project_name']
        
        qa_templates = [
            ('README.md.j2', 'qa/README.md'),
            ('reports/bug_report_template.md.j2', 'qa/templates/bug_report_template.md'),
            ('reports/validation_report_template.md.j2', 'qa/templates/validation_report_template.md'),
            ('reports/test_execution_report.md.j2', 'qa/templates/test_execution_report.md'),
            ('queue/pending_validation.json.j2', 'qa/queue/pending_validation.json'),
            ('queue/active_qa_sessions.json.j2', 'qa/queue/active_qa_sessions.json'),
            ('queue/bugfix_queue.json.j2', 'qa/queue/bugfix_queue.json'),
            ('config/qa_config.yaml.j2', 'qa/config/qa_config.yaml'),
            ('config/validation_rules.yaml.j2', 'qa/config/validation_rules.yaml')
        ]
        
        for template_file, output_file in qa_templates:
            template_path = self.qa_template_dir / template_file
            output_path = project_path / output_file
            
            if template_path.exists():
                rendered_content = self.setup_core.render_template(template_path, project_config)
                output_path.write_text(rendered_content, encoding='utf-8')
                logging.info(f"Rendered QA template: {output_file}")
```

### Enhanced Agent Configuration

```python
class QAAgentIntegration:
    """Integrates QA agents with existing agent system."""
    
    def update_agent_configurations(self, project_config: Dict[str, Any]):
        """Update agent configurations to include QA capabilities."""
        
        project_path = Path(project_config['output_dir']) / project_config['project_name']
        
        # Enhance existing QAA agent
        self.enhance_qaa_agent(project_path, project_config)
        
        # Add background QA runner agent
        self.add_background_qa_agent(project_path, project_config)
        
        # Update SMA with QA monitoring capabilities
        self.update_sma_qa_capabilities(project_path, project_config)
        
        # Update other agents with QA awareness
        self.add_qa_awareness_to_agents(project_path, project_config)
    
    def enhance_qaa_agent(self, project_path: Path, project_config: Dict[str, Any]):
        """Enhance existing QAA agent with autonomous capabilities."""
        
        qaa_persona_path = project_path / "agents" / "qaa" / "persona_rules.yaml"
        
        if qaa_persona_path.exists():
            # Load enhanced QAA template
            enhanced_template = self.qa_template_dir / "agents" / "qa_automation_agent" / "persona_rules.yaml.j2"
            
            if enhanced_template.exists():
                enhanced_content = self.setup_core.render_template(enhanced_template, project_config)
                qaa_persona_path.write_text(enhanced_content, encoding='utf-8')
                logging.info("Enhanced QAA agent with autonomous capabilities")
    
    def add_background_qa_agent(self, project_path: Path, project_config: Dict[str, Any]):
        """Add background QA runner agent configuration."""
        
        bg_qa_dir = project_path / "agents" / "background_qa_runner"
        bg_qa_dir.mkdir(parents=True, exist_ok=True)
        
        # Render background QA agent template
        bg_template = self.qa_template_dir / "agents" / "background_qa_runner" / "persona_rules.yaml.j2"
        
        if bg_template.exists():
            bg_content = self.setup_core.render_template(bg_template, project_config)
            bg_persona_path = bg_qa_dir / "persona_rules.yaml"
            bg_persona_path.write_text(bg_content, encoding='utf-8')
            logging.info("Added background QA runner agent")
```

### Init.sh Integration

```python
class InitShQAIntegration:
    """Integrates QA commands into init.sh template."""
    
    def integrate_qa_init_commands(self, project_config: Dict[str, Any]):
        """Add QA commands to init.sh template."""
        
        # Load existing init.sh template
        init_template_path = Path("agentic_scrum_setup/templates/common/init.sh.j2")
        
        if init_template_path.exists():
            init_content = init_template_path.read_text()
            
            # Add QA function definitions
            qa_functions = self.generate_qa_functions()
            
            # Add QA case statements
            qa_cases = self.generate_qa_cases()
            
            # Insert QA content into template
            updated_init = self.insert_qa_content(init_content, qa_functions, qa_cases)
            
            # Write updated template
            init_template_path.write_text(updated_init, encoding='utf-8')
            logging.info("Integrated QA commands into init.sh template")
    
    def generate_qa_functions(self) -> str:
        """Generate QA function definitions for init.sh."""
        
        return '''
# QA Validation Functions
qa_status() {
    info "QA Validation System Status"
    echo "=========================="
    
    # Check QA queue status
    if [[ -f "qa/queue/pending_validation.json" ]]; then
        pending_count=$(python3 -c "import json; data=json.load(open('qa/queue/pending_validation.json')); print(len(data.get('queue', [])))")
        info "Pending validations: $pending_count"
    fi
    
    # Check active validations
    if [[ -f "qa/queue/active_qa_sessions.json" ]]; then
        active_count=$(python3 -c "import json; data=json.load(open('qa/queue/active_qa_sessions.json')); print(len(data.get('active_sessions', [])))")
        info "Active validations: $active_count"
    fi
    
    # Check recent bugs
    if [[ -d "qa/reports/bugs" ]]; then
        recent_bugs=$(find qa/reports/bugs -name "*.md" -mtime -1 | wc -l)
        info "Bugs found (last 24h): $recent_bugs"
    fi
}

qa_validate() {
    local story_id="$1"
    
    if [[ -z "$story_id" ]]; then
        error "Usage: $0 qa validate <story_id>"
        exit 1
    fi
    
    info "Starting QA validation for $story_id"
    
    # Trigger validation
    if [[ -f "qa/scripts/validation_runner.py" ]]; then
        python3 qa/scripts/validation_runner.py --story-id "$story_id"
    else
        error "QA validation runner not found"
        exit 1
    fi
}

qa_reports() {
    local report_type="${1:-summary}"
    
    info "Generating QA reports: $report_type"
    
    case "$report_type" in
        summary)
            if [[ -f "qa/scripts/qa_monitor.py" ]]; then
                python3 qa/scripts/qa_monitor.py --report summary
            fi
            ;;
        bugs)
            info "Recent bug reports:"
            find qa/reports/bugs -name "*.md" -mtime -7 -exec echo "  {}" \\;
            ;;
        trends)
            if [[ -f "qa/scripts/qa_monitor.py" ]]; then
                python3 qa/scripts/qa_monitor.py --report trends
            fi
            ;;
        *)
            error "Unknown report type: $report_type"
            echo "Available types: summary, bugs, trends"
            ;;
    esac
}'''
    
    def generate_qa_cases(self) -> str:
        """Generate QA case statements for init.sh."""
        
        return '''
        qa)
            # QA Validation commands
            shift
            case "${1:-status}" in
                status)
                    qa_status
                    ;;
                validate)
                    shift
                    qa_validate "$@"
                    ;;
                reports)
                    shift
                    qa_reports "$@"
                    ;;
                *)
                    error "Unknown QA command: $1"
                    echo "Available commands: status, validate, reports"
                    exit 1
                    ;;
            esac
            ;;'''
```

### Configuration Integration

```python
class ConfigurationIntegration:
    """Integrates QA configuration with project configuration."""
    
    def update_agentic_config(self, project_config: Dict[str, Any]):
        """Update agentic_config.yaml.j2 with QA settings."""
        
        config_template_path = Path("agentic_scrum_setup/templates/agentic_config.yaml.j2")
        
        if config_template_path.exists():
            config_content = config_template_path.read_text()
            
            # Add QA configuration section
            qa_config_section = '''
# QA Validation Configuration
qa_validation:
  enabled: {{ qa.enabled | default(true) }}
  validation_modes: {{ qa.validation_modes | default(['automatic', 'manual']) | tojson }}
  
  background_agents:
    enabled: {{ qa.background_agents.enabled | default(true) }}
    max_concurrent: {{ qa.background_agents.max_concurrent | default(3) }}
    auto_assignment: {{ qa.background_agents.auto_assignment | default(true) }}
  
  validation_layers:
    code_quality: {{ qa.validation_layers.code_quality | default(true) }}
    functional: {{ qa.validation_layers.functional | default(true) }}
    integration: {{ qa.validation_layers.integration | default(true) }}
    user_experience: {{ qa.validation_layers.user_experience | default(true) }}
  
  bug_detection:
    enabled: {{ qa.bug_detection.enabled | default(true) }}
    auto_reporting: {{ qa.bug_detection.auto_reporting | default(true) }}
    severity_thresholds:
      critical: {{ qa.bug_detection.severity_thresholds.critical | default(0) }}
      high: {{ qa.bug_detection.severity_thresholds.high | default(2) }}
      medium: {{ qa.bug_detection.severity_thresholds.medium | default(5) }}
      low: {{ qa.bug_detection.severity_thresholds.low | default(10) }}
  
  quality_gates:
    minimum_coverage: {{ qa.quality_gates.minimum_coverage | default(85) }}
    max_performance_regression: {{ qa.quality_gates.max_performance_regression | default(20) }}
    security_scan_required: {{ qa.quality_gates.security_scan_required | default(true) }}
'''
            
            # Insert QA configuration into template
            updated_config = self.insert_qa_config(config_content, qa_config_section)
            config_template_path.write_text(updated_config, encoding='utf-8')
            logging.info("Updated agentic_config.yaml.j2 with QA configuration")
```

## Integration Points

- **Setup Core**: Integrate with `setup_core.py` for project generation
- **Template System**: Add QA templates to existing template structure
- **Agent System**: Enhance existing agent configurations
- **CLI System**: Integrate QA commands into `init.sh` template
- **Configuration**: Add QA settings to project configuration
- **MCP Servers**: Include QA MCP servers in project setup

## Definition of Done

- [ ] QA templates added to framework template directory
- [ ] Project initialization integration complete
- [ ] QA agent creation integrated with project setup
- [ ] Configuration integration functional
- [ ] CLI and init script integration working
- [ ] Backward compatibility maintained
- [ ] Documentation updated with QA capabilities
- [ ] Migration path for existing projects provided
- [ ] Comprehensive error handling and logging
- [ ] Unit tests written and passing
- [ ] Integration tests written and passing
- [ ] Code follows existing AgenticScrum coding standards
- [ ] All files added to git and committed

## Dependencies

- STORY_325: QA Infrastructure Setup
- STORY_326: Enhanced QAA Agent Configuration
- Existing template system (`setup_core.py`)
- Existing CLI system (`cli.py`)
- Project configuration system

## Success Metrics

- New projects include QA validation: 100%
- Template rendering success rate: >99%
- Backward compatibility: 100% of existing projects remain functional
- QA system adoption in new projects: >90%
- Template integration performance: <5 seconds additional setup time