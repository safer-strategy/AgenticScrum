# AgenticScrum Retrofitting Guide

## Overview

This guide provides a systematic approach to integrating AgenticScrum methodology into existing codebases. Unlike starting fresh with a new project, retrofitting requires careful consideration of existing architecture, team workflows, and gradual adoption strategies.

## Table of Contents

1. [Pre-Retrofit Assessment](#pre-retrofit-assessment)
2. [Phase 1: Assessment and Planning](#phase-1-assessment-and-planning)
3. [Phase 2: Minimal Setup](#phase-2-minimal-setup)
4. [Phase 3: Agent Introduction](#phase-3-agent-introduction)
5. [Phase 4: Gradual Expansion](#phase-4-gradual-expansion)
6. [Phase 5: Full Integration](#phase-5-full-integration)
7. [Common Patterns and Solutions](#common-patterns-and-solutions)
8. [Troubleshooting](#troubleshooting)
9. [Migration Scripts](#migration-scripts)

## Pre-Retrofit Assessment

Before beginning the retrofitting process, evaluate your project using the [Retrofit Assessment Checklist](../checklists/retrofit_assessment.md).

### Key Questions

1. **Project Structure**
   - Is your codebase monolithic or microservices?
   - Single language or polyglot?
   - Existing CI/CD pipelines?

2. **Team Readiness**
   - Current development methodology?
   - Team size and structure?
   - Openness to AI-assisted development?

3. **Technical Constraints**
   - Existing tooling and frameworks?
   - Security and compliance requirements?
   - Performance considerations?

## Phase 1: Assessment and Planning

### 1.1 Analyze Current Structure

```bash
# Use the assessment script to analyze your project
python scripts/retrofit_project.py assess --path /path/to/your/project

# This generates a report with:
# - Project structure analysis
# - Language and framework detection
# - Existing standards identification
# - Retrofit complexity score
```

### 1.2 Create Retrofit Plan

Based on the assessment, create a phased adoption plan:

```yaml
# retrofit_plan.yaml
project: MyExistingProject
retrofit_strategy: gradual  # gradual, department, or feature-based
phases:
  - phase: 1
    duration: 2 weeks
    goals:
      - Set up AgenticScrum configuration
      - Create initial agent personas
      - Pilot with one small feature
  - phase: 2
    duration: 1 month
    goals:
      - Introduce DeveloperAgent for new features
      - Establish code review with QAAgent
```

## Phase 2: Minimal Setup

### 2.1 Install AgenticScrum Without Disruption

```bash
# Clone AgenticScrum to a tools directory
mkdir tools && cd tools
git clone https://github.com/yourusername/AgenticScrum.git
cd AgenticScrum
./init.sh install
```

### 2.2 Create AgenticScrum Configuration

Create an `agentic_config.yaml` in your project root:

```yaml
# Minimal configuration for existing projects
project_name: "MyExistingProject"
project_type: "retrofit"
integration_mode: "non-disruptive"

# Point to existing directories
source_directories:
  - src/
  - lib/
  - app/

test_directories:
  - tests/
  - spec/
  - test/

# Existing standards references
standards:
  existing_linter: ".eslintrc.json"
  existing_formatter: ".prettierrc"
  
# LLM Configuration
llm_provider: "openai"
default_model: "gpt-4-turbo-preview"
```

### 2.3 Create Initial Agent Directory

```bash
# Create agents directory without disrupting existing structure
mkdir -p agents/{poa,sma,deva,qaa,saa}

# Use retrofit templates
python scripts/retrofit_project.py init-agents \
  --project-path . \
  --languages "python,javascript" \
  --frameworks "django,react"
```

## Phase 3: Agent Introduction

### 3.1 Start with ProductOwnerAgent

Begin with the least disruptive agent:

```yaml
# agents/poa/persona_rules.yaml
role: "Product Owner Agent - Retrofit Specialist"
goal: "Manage feature requests and create user stories that respect existing architecture"
backstory: |
  You are joining an established project with existing patterns and conventions.
  Your role is to translate new requirements into user stories that integrate
  seamlessly with the current codebase.

rules:
  - "ALWAYS analyze existing code patterns before creating user stories"
  - "ALWAYS respect current architectural decisions"
  - "SUGGEST incremental improvements rather than rewrites"
  - "CREATE stories that can be implemented without breaking existing functionality"

knowledge_sources:
  - "docs/existing_architecture.md"  # Document your current architecture
  - "docs/api_documentation.md"      # Existing API docs
  - "README.md"                      # Project readme
```

### 3.2 Introduce DeveloperAgent Gradually

Start with a specialized developer agent for new features:

```yaml
# agents/deva/retrofit_specialist/persona_rules.yaml
role: "Developer Agent - Retrofit Integration Specialist"
goal: "Generate code that seamlessly integrates with existing codebase patterns"
backstory: |
  You are a senior developer who has thoroughly studied this codebase.
  You understand its patterns, conventions, and architectural decisions.
  Your code must blend in perfectly with existing code.

capabilities:
  - "Pattern recognition in existing code"
  - "Matching existing code style exactly"
  - "Incremental refactoring"
  - "Backward compatibility maintenance"

rules:
  - "ALWAYS match the exact coding style of surrounding code"
  - "ALWAYS use existing utility functions and patterns"
  - "ALWAYS maintain backward compatibility"
  - "NEVER introduce new dependencies without approval"
  - "PREFER extending existing modules over creating new ones"
```

### 3.3 Create Priming Scripts for Existing Code Context

```markdown
# agents/deva/retrofit_specialist/priming_script.md

You are working on an existing codebase with established patterns. Before generating any code:

1. Study the existing code structure in the target directory
2. Identify and match:
   - Naming conventions (camelCase, snake_case, etc.)
   - Import styles and organization
   - Error handling patterns
   - Logging patterns
   - Test structure and naming

## Code Analysis Results
<!-- This section is auto-populated by the retrofit script -->
- Primary Language: Python 3.8
- Framework: Django 3.2
- Code Style: PEP 8 with 120 char line limit
- Test Framework: pytest
- Common Patterns:
  - Service layer pattern for business logic
  - Repository pattern for data access
  - Custom exceptions in errors.py
  - Centralized logging with app.logger

## Your Task
[Current user story or task will be inserted here]

## Integration Guidelines
- New code goes in the existing module structure
- Follow the established layering (views -> services -> repositories)
- Use existing base classes and mixins
- Add tests following existing test patterns
```

## Phase 4: Gradual Expansion

### 4.1 Feature-Based Adoption

Adopt AgenticScrum for new features while maintaining existing code:

```bash
# Create a feature branch for AgenticScrum adoption
git checkout -b feature/agentic-scrum-integration

# Set up feature-specific configuration
cat > agents/feature_config.yaml << EOF
adoption_mode: "new_features_only"
features:
  - name: "user-authentication-v2"
    agents: ["poa", "deva_python", "qaa"]
    start_date: "2024-01-15"
  - name: "payment-integration"
    agents: ["poa", "deva_python", "saa", "qaa"]
    start_date: "2024-02-01"
EOF
```

### 4.2 Department-Based Adoption

For larger teams, adopt by department:

```yaml
# agents/adoption_plan.yaml
departments:
  frontend_team:
    start_date: "2024-01-15"
    agents: ["poa", "deva_typescript", "qaa"]
    pilot_features: ["dashboard-redesign"]
    
  backend_team:
    start_date: "2024-02-01"
    agents: ["poa", "deva_python", "saa", "qaa"]
    pilot_features: ["api-v2-endpoints"]
    
  mobile_team:
    start_date: "2024-03-01"
    agents: ["poa", "deva_kotlin", "qaa"]
    pilot_features: ["offline-sync"]
```

### 4.3 Integrate with Existing Tools

```python
# scripts/integrate_existing_tools.py
import subprocess
import yaml

def integrate_with_ci():
    """Add AgenticScrum checks to existing CI pipeline"""
    # Read existing CI configuration
    with open('.github/workflows/ci.yml', 'r') as f:
        ci_config = yaml.safe_load(f)
    
    # Add AgenticScrum steps
    agentic_steps = [
        {
            'name': 'Run AgenticScrum QA Agent',
            'run': 'python scripts/run_qa_agent.py --mode retrofit'
        },
        {
            'name': 'Security Audit for New Code',
            'run': 'python scripts/run_saa_agent.py --scope new-changes'
        }
    ]
    
    # Insert after existing tests
    ci_config['jobs']['test']['steps'].extend(agentic_steps)
    
    # Write updated configuration
    with open('.github/workflows/ci.yml', 'w') as f:
        yaml.dump(ci_config, f)
```

## Phase 5: Full Integration

### 5.1 Complete Agent Ecosystem

Once comfortable with the agents, expand to full ecosystem:

```bash
# Generate full agent set based on your project analysis
python scripts/retrofit_project.py generate-full-agents \
  --analyze-existing \
  --preserve-patterns \
  --output agents/
```

### 5.2 Migrate Existing Documentation

Convert existing docs to AgenticScrum format:

```bash
# Migrate existing requirements to user stories
python scripts/migrate_requirements.py \
  --input docs/requirements.txt \
  --output docs/requirements/user_stories/

# Convert existing tasks to sprint backlog
python scripts/migrate_tasks.py \
  --source jira \
  --output docs/requirements/product_backlog.md
```

### 5.3 Establish Feedback Loops

```yaml
# agents/feedback_config.yaml
feedback_loops:
  code_quality:
    frequency: "after_each_pr"
    metrics:
      - "code_coverage_delta"
      - "complexity_change"
      - "style_consistency"
    
  agent_performance:
    frequency: "weekly"
    metrics:
      - "acceptance_rate"
      - "revision_count"
      - "time_to_completion"
```

## Common Patterns and Solutions

### Pattern 1: Legacy Code with No Tests

**Problem**: Existing code lacks tests, making agent-generated code risky.

**Solution**: Create a transition strategy:
```yaml
# agents/deva/legacy_handler/persona_rules.yaml
legacy_code_rules:
  - "ALWAYS write tests for new code, even if surrounding code lacks tests"
  - "SUGGEST test creation for modified legacy code"
  - "CREATE integration tests to verify legacy code interactions"
  - "USE snapshot testing for complex legacy outputs"
```

### Pattern 2: Mixed Code Standards

**Problem**: Inconsistent coding standards across the codebase.

**Solution**: Create region-specific agents:
```python
# scripts/create_region_agents.py
def create_region_specific_agent(code_region, detected_style):
    """Create agents that match specific code regions"""
    agent_config = {
        'role': f'Developer Agent for {code_region}',
        'style_rules': detected_style,
        'enforcement': 'match_surrounding'
    }
    return agent_config
```

### Pattern 3: Complex Dependencies

**Problem**: Tightly coupled code makes agent integration difficult.

**Solution**: Use facade pattern for agent interaction:
```python
# agents/facades/legacy_system_facade.py
class LegacySystemFacade:
    """Facade to simplify agent interaction with legacy systems"""
    
    def __init__(self):
        self.legacy_auth = ComplexAuthSystem()
        self.legacy_db = OldDatabaseLayer()
        
    def simple_authenticate(self, user, password):
        """Simplified auth for agents"""
        # Complex legacy logic hidden
        return self.legacy_auth.multi_step_auth(user, password)
```

## Troubleshooting

### Issue: Agents generating incompatible code

```bash
# Diagnose style mismatches
python scripts/diagnose_style.py --file generated_code.py --compare-with existing_code.py

# Update agent configuration
python scripts/update_agent_style.py --agent deva_python --learn-from src/
```

### Issue: Performance degradation

```yaml
# agents/performance_config.yaml
optimization_rules:
  - "ALWAYS profile code that interacts with critical paths"
  - "PREFER existing optimized functions over new implementations"
  - "MEASURE performance impact of new features"
```

### Issue: Team resistance

Create gradual adoption strategies:
```markdown
# docs/team_adoption_plan.md
## Week 1-2: Awareness
- Demo sessions showing AgenticScrum benefits
- Pilot with volunteer developers

## Week 3-4: Assisted Adoption
- Pair programming with agents
- Human reviews all agent output

## Week 5-6: Supervised Autonomy
- Agents generate initial code
- Developers refine and approve

## Week 7+: Full Integration
- Agents as full team members
- Focus on oversight and strategy
```

## Migration Scripts

### Automated Retrofit Script

```python
#!/usr/bin/env python3
# scripts/retrofit_project.py

import argparse
import os
import ast
import json
from pathlib import Path

class ProjectRetrofitter:
    def __init__(self, project_path):
        self.project_path = Path(project_path)
        self.analysis_results = {}
        
    def analyze_project(self):
        """Analyze existing project structure and patterns"""
        self.analysis_results = {
            'languages': self.detect_languages(),
            'frameworks': self.detect_frameworks(),
            'structure': self.analyze_structure(),
            'patterns': self.detect_patterns(),
            'complexity': self.calculate_complexity()
        }
        return self.analysis_results
    
    def detect_languages(self):
        """Detect programming languages used"""
        language_extensions = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.go': 'go',
            '.rs': 'rust',
            '.rb': 'ruby',
            '.php': 'php',
            '.cs': 'csharp'
        }
        
        languages = {}
        for ext, lang in language_extensions.items():
            files = list(self.project_path.rglob(f'*{ext}'))
            if files:
                languages[lang] = len(files)
                
        return languages
    
    def detect_frameworks(self):
        """Detect frameworks based on configuration files"""
        framework_indicators = {
            'package.json': self.detect_js_frameworks,
            'requirements.txt': self.detect_python_frameworks,
            'pom.xml': self.detect_java_frameworks,
            'go.mod': self.detect_go_frameworks,
        }
        
        frameworks = []
        for indicator, detector in framework_indicators.items():
            if (self.project_path / indicator).exists():
                frameworks.extend(detector())
                
        return frameworks
    
    def generate_retrofit_plan(self):
        """Generate a customized retrofit plan"""
        plan = {
            'phases': [],
            'agent_configuration': {},
            'integration_points': []
        }
        
        # Phase 1: Minimal setup
        plan['phases'].append({
            'name': 'Minimal Setup',
            'duration': '1 week',
            'tasks': [
                'Install AgenticScrum tools',
                'Create agentic_config.yaml',
                'Set up initial POA agent'
            ]
        })
        
        # Determine which agents to introduce based on languages
        for language in self.analysis_results['languages']:
            plan['agent_configuration'][f'deva_{language}'] = {
                'priority': 'high' if language == 'python' else 'medium',
                'customization_needed': True
            }
            
        return plan
    
    def create_retrofit_config(self):
        """Create initial retrofit configuration files"""
        config = {
            'project_name': self.project_path.name,
            'project_type': 'retrofit',
            'existing_structure': self.analysis_results['structure'],
            'detected_languages': list(self.analysis_results['languages'].keys()),
            'detected_frameworks': self.analysis_results['frameworks'],
            'retrofit_strategy': 'gradual',
            'preserve_existing': True
        }
        
        config_path = self.project_path / 'agentic_config.yaml'
        # Write configuration...
        
        return config_path

def main():
    parser = argparse.ArgumentParser(description='Retrofit existing project with AgenticScrum')
    parser.add_argument('command', choices=['assess', 'plan', 'init-agents', 'integrate'])
    parser.add_argument('--path', required=True, help='Path to existing project')
    parser.add_argument('--output', help='Output directory for generated files')
    
    args = parser.parse_args()
    
    retrofitter = ProjectRetrofitter(args.path)
    
    if args.command == 'assess':
        results = retrofitter.analyze_project()
        print(json.dumps(results, indent=2))
    elif args.command == 'plan':
        plan = retrofitter.generate_retrofit_plan()
        print(json.dumps(plan, indent=2))
    # ... implement other commands

if __name__ == '__main__':
    main()
```

## Next Steps

1. Run the assessment script on your project
2. Review the generated retrofit plan
3. Start with Phase 1 and progress at your team's pace
4. Customize agent configurations based on your needs
5. Monitor metrics and adjust approach as needed

Remember: Successful retrofitting is about gradual adoption and respecting existing work while introducing improvements incrementally.