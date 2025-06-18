# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AgenticScrum is an open-source framework for structured AI-driven code generation that combines Scrum methodologies with AI agents. The project provides a fully-implemented CLI tool (`agentic-scrum-setup`) that scaffolds new AI-driven development projects with standardized structure, agent configurations, and continuous improvement mechanisms through feedback loops.

## Key Architecture & Structure

### Core Implementation

The project is implemented as a Python package with the following structure:

```
agentic_scrum_setup/
├── cli.py          # CLI entry point with argument parsing and interactive mode
├── setup_core.py   # Core project generation logic using Jinja2 templates
├── templates/      # Jinja2 templates for all generated files
└── tests/          # Comprehensive test suite

scripts/
├── collect_agent_metrics.py  # Performance metrics collection
├── feedback_analyzer.py      # Feedback pattern analysis
└── update_agent_config.py    # Automated configuration updates
```

**Key Classes:**
- `SetupCore` (setup_core.py:14) - Handles project generation, template rendering, and file creation
- CLI functions (cli.py) - Provides both command-line and interactive interfaces
- `AgentMetricsCollector` (collect_agent_metrics.py) - Tracks code quality metrics
- `FeedbackAnalyzer` (feedback_analyzer.py) - Identifies improvement patterns
- `AgentConfigUpdater` (update_agent_config.py) - Applies configuration improvements

### Template System

Templates are organized by purpose in `agentic_scrum_setup/templates/`:
- `claude/` - Claude-specific configurations (CLAUDE.md, .mcp.json, persona_rules.yaml)
- `common/` - Shared files (init.sh, docker-compose.yml)
- `checklists/` - Quality checklists for development workflow
- `standards/` - Coding standards templates
- Agent-specific directories (`poa/`, `sma/`, `deva_python/`, `qaa/`) - Individual agent persona configurations
- Language-specific directories (`python/`, `javascript/`, `java/`, `go/`, `rust/`, `csharp/`, `php/`, `ruby/`)
- Root-level templates (`.gitignore.j2`, `README.md.j2`, `agentic_config.yaml.j2`)

## Development Commands

### Setup and Installation

#### Production Use (Beta Testing)
```bash
# Install from PyPI (recommended for beta testing)
pip install agentic-scrum-setup==1.0.0b4

# Verify installation
python -c "import agentic_scrum_setup; print(f'AgenticScrum v{agentic_scrum_setup.__version__} installed')"
```

#### Development Setup
```bash
# Install for development
pip install -r requirements-dev.txt

# Install the CLI tool locally for development
pip install -e .
```

### Testing

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=agentic_scrum_setup

# Run tests with specific file
pytest agentic_scrum_setup/tests/test_cli.py

# Run specific test
pytest agentic_scrum_setup/tests/test_setup_core.py::TestSetupCore::test_init_sh_permissions
```

### Code Quality

```bash
# Format code with black
black agentic_scrum_setup/ tests/

# Lint code
flake8 agentic_scrum_setup/ tests/

# Type checking
mypy agentic_scrum_setup/
```

### Using the CLI

#### Production Use (PyPI Installation)
```bash
# Install from PyPI first
pip install agentic-scrum-setup==1.0.0b4

# Verify installation
python -c "import agentic_scrum_setup; print(f'AgenticScrum v{agentic_scrum_setup.__version__} installed')"

# Direct CLI usage (recommended for PyPI users)
agentic-scrum-setup init --project-name "MyProject" --language python --framework fastapi

# Interactive mode
agentic-scrum-setup init
```

#### Development Setup (Local Repository)
```bash
# Interactive mode (recommended for beginners)
./init.sh new

# Quick setup with defaults
./init.sh quick MyProject

# Direct CLI - Single language project
agentic-scrum-setup init \
  --project-name "MyProject" \
  --language python \
  --framework fastapi \
  --agents poa,sma,deva_python,qaa,saa \
  --llm-provider openai \
  --default-model gpt-4-turbo-preview

# Fullstack project
agentic-scrum-setup init \
  --project-name "MyFullstackApp" \
  --project-type fullstack \
  --language python \
  --backend-framework fastapi \
  --frontend-language typescript \
  --frontend-framework react \
  --agents poa,sma,deva_python,deva_typescript,qaa,saa \
  --llm-provider anthropic \
  --default-model claude-3-opus-20240229

# Organization project (NEW - multi-repository management)
agentic-scrum-setup init \
  --project-type organization \
  --project-name "MyOrganization" \
  --organization-name "MyCompany" \
  --llm-provider anthropic \
  --default-model claude-sonnet-4-0

# Add repository to organization
agentic-scrum-setup add-repo \
  --organization-dir ~/Organizations/MyCompany \
  --repo-name "backend-api" \
  --language python \
  --framework fastapi \
  --agents poa,sma,deva_python,qaa,saa

# List repositories in organization
agentic-scrum-setup list-repos \
  --organization-dir ~/Organizations/MyCompany

# Supported languages: python, javascript, typescript, java, go, rust, csharp, php, ruby
# Supported agents: poa, sma, deva_python, deva_javascript, deva_typescript, deva_claude_python, qaa, saa, organization_poa, organization_sma
# Supported frameworks: fastapi, express, spring, gin, actix, aspnet (backend); react, vue, angular, svelte (frontend)
# Supported project types: single, fullstack, organization
```

### Agent Performance Optimization

```bash
# Collect metrics for agent-generated code
python scripts/collect_agent_metrics.py --agent deva_python --file src/api/users.py --save

# Analyze feedback and generate recommendations
python scripts/feedback_analyzer.py --agent deva_python --output reports/

# Update agent configurations based on feedback
python scripts/update_agent_config.py recommend --agent deva_python
python scripts/update_agent_config.py apply --agent deva_python --dry-run
```

### Organization Management (NEW)

AgenticScrum now supports enterprise-grade multi-repository organizations with AI agent coordination:

```bash
# Create organization structure
agentic-scrum-setup init \
  --project-type organization \
  --organization-name "MyCompany" \
  --llm-provider anthropic \
  --default-model claude-sonnet-4-0 \
  --output-dir ~/Organizations

# Add repositories to organization
agentic-scrum-setup add-repo \
  --organization-dir ~/Organizations/MyCompany \
  --repo-name "user-service" \
  --language python \
  --framework fastapi \
  --agents poa,sma,deva_python,qaa

agentic-scrum-setup add-repo \
  --organization-dir ~/Organizations/MyCompany \
  --repo-name "web-app" \
  --language typescript \
  --framework react \
  --agents poa,sma,deva_typescript,qaa

# List and manage repositories
agentic-scrum-setup list-repos --organization-dir ~/Organizations/MyCompany

# Sync organization standards across all repositories
cd ~/Organizations/MyCompany
./shared/scripts/sync_standards.sh

# Start shared infrastructure services
cd shared && docker-compose up -d
```

#### Organization Features:
- **Portfolio-Level Planning:** Organization POA coordinates product strategy across all repositories
- **Cross-Project Coordination:** Organization SMA manages dependencies and sprints across teams  
- **Shared Standards:** Automatic propagation of coding standards to all repositories
- **Configuration Inheritance:** Organization settings cascade to individual repositories
- **Agent Memory Sharing:** Cross-project pattern recognition and knowledge transfer
- **Shared Infrastructure:** Common databases, monitoring, CI/CD, and development tools

#### Organization Agents:
- **organization_poa:** Portfolio Product Owner for strategic cross-project planning
- **organization_sma:** Cross-Project Scrum Master for coordination and process improvement

### Building and Distribution

```bash
# Build distribution packages
python setup.py sdist bdist_wheel

# Upload to PyPI (requires credentials)
twine upload dist/*
```

## Development Best Practices

- Always run 'tree --gitignore > dir_tree.txt' when new files are created
- Always git add commit and push
- Always add new stories to the spec/ directory
- **Datetime Editing**: remember to check the datetime before editing stories
- Use tmp/ in the project directory for your temp dir.

## Architecture Notes

[Rest of the file remains the same as in the original content]