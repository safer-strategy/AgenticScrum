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

```bash
# Install for development
pip install -r requirements-dev.txt

# Install the CLI tool locally
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

# Fullstack project (new feature)
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

# Supported languages: python, javascript, typescript, java, go, rust, csharp, php, ruby
# Supported agents: poa, sma, deva_python, deva_javascript, deva_typescript, deva_claude_python, qaa, saa
# Supported frameworks: fastapi, express, spring, gin, actix, aspnet (backend); react, vue, angular, svelte (frontend)
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

## Architecture Notes

### CLI Design
The CLI supports both command-line arguments and interactive mode. When required arguments are missing, it automatically falls back to interactive prompts. See `interactive_mode()` function in cli.py:91. The CLI now supports fullstack projects with separate backend and frontend configurations.

### Template Rendering
All project files are generated using Jinja2 templates with the following context variables:
- `project_name` - Name of the project being created
- `project_type` - 'single' or 'fullstack'
- `language` - Primary programming language (backend for fullstack)
- `frontend_language` - Frontend language for fullstack projects
- `framework` - Framework for single language projects
- `backend_framework` - Backend framework for fullstack
- `frontend_framework` - Frontend framework for fullstack
- `agents` - List of selected AI agents
- `llm_provider` - Selected LLM provider
- `default_model` - Default model for the provider

### File Permissions
The `init.sh` script is automatically made executable using proper Unix permissions (setup_core.py:186). This is tested in test_setup_core.py:74.

### Agent Configuration
Agents are mapped to directory structures in setup_core.py:133. Available agents include:
- `poa` - Product Owner Agent
- `sma` - Scrum Master Agent
- `deva_python`, `deva_javascript`, `deva_typescript` - Language-specific developer agents
- `deva_claude_python` - Claude-specialized Python developer
- `qaa` - QA Agent
- `saa` - Security Audit Agent (new)

### Fullstack Support
When `project_type=fullstack`, the system:
1. Creates separate `/backend` and `/frontend` directories
2. Generates language-appropriate structures for each
3. Configures multiple developer agents (one per language)
4. Creates separate standards and linter configs for each stack

### Feedback Loop System
The framework includes a comprehensive feedback loop system:
1. **Metrics Collection**: Automated tracking of complexity, coverage, and quality
2. **Feedback Analysis**: Pattern identification from code reviews
3. **Automated Updates**: Configuration improvements based on feedback
4. **Continuous Improvement**: Agent configurations evolve based on performance data

### Language-Specific File Generation
The framework automatically generates appropriate dependency and configuration files based on the selected language:
- Python: `requirements.txt` and `__init__.py` files
- JavaScript/TypeScript: `package.json` with appropriate dependencies
- Java: `pom.xml` with Maven configuration and standard directory structure
- Go: `go.mod` with module definition
- Rust: `Cargo.toml` with package configuration and `src/main.rs`
- C#: `.csproj` file with .NET configuration
- PHP: `composer.json` with PSR-4 autoloading
- Ruby: `Gemfile` with development dependencies

### .gitignore Management
Comprehensive `.gitignore` generation with 600+ patterns covering:
- Language-specific build artifacts and dependencies
- IDE and editor temporary files
- Framework-specific patterns (Django, Laravel, React, etc.)
- AgenticScrum-specific directories (`.mcp_cache/`, `agent_outputs/`, `sprint_artifacts/`)
- Cloud provider and security-related files

## Retrofitting Existing Projects

AgenticScrum supports gradual integration into existing codebases through the retrofitting system:

### Assessment Script
```bash
python scripts/retrofit_project.py assess --path /path/to/project
```
- Analyzes languages, frameworks, structure, and complexity
- Generates customized retrofit plan
- Estimates timeline and identifies risks

### Retrofit Templates
Located in `agentic_scrum_setup/templates/retrofit/`:
- `retrofit_persona_rules.yaml.j2` - Agent configuration that respects existing patterns
- Templates include pattern matching and code style preservation

### Key Retrofitting Features
1. **Non-disruptive Integration**: Preserves existing structure and workflows
2. **Pattern Learning**: Agents analyze and match existing code patterns
3. **Phased Adoption**: Start with one agent, expand gradually
4. **CI/CD Integration**: Works with existing pipelines
5. **Team-Friendly**: Enhances rather than replaces current processes

See [Retrofitting Guide](docs/RETROFITTING_GUIDE.md) for detailed instructions.

## MCP DateTime Service Integration

AgenticScrum includes a comprehensive DateTime MCP service for time operations, timezone handling, and sprint calculations. This service is fully validated and production-ready.

### DateTime Service Features

The DateTime MCP service provides 9 core functions:

1. **get_current_time(timezone_name)** - Get current time in any timezone
2. **format_datetime(timestamp, format_type)** - Format dates in various formats  
3. **add_time(timestamp, **kwargs)** - Add time durations (days, hours, minutes, etc.)
4. **calculate_duration(start, end)** - Calculate time between timestamps
5. **convert_timezone(timestamp, from_tz, to_tz)** - Convert between timezones
6. **calculate_business_days(start_date, end_date)** - Business day calculations
7. **calculate_sprint_dates(start_date, length)** - Agile sprint planning dates
8. **get_relative_time(timestamp)** - Human-readable relative time ("2 hours ago")
9. **get_time_until(target_timestamp)** - Time remaining until target

### Using DateTime Service Commands

```bash
# MCP Service Management
./init.sh mcp-start       # Start DateTime MCP service
./init.sh mcp-stop        # Stop DateTime MCP service  
./init.sh mcp-status      # Check service status
./init.sh mcp-test        # Test DateTime functionality

# Advanced Service Management
python scripts/mcp_manager.py status              # Detailed service status
python scripts/mcp_manager.py start datetime      # Start specific service
python scripts/mcp_manager.py health datetime     # Health check
python scripts/mcp_manager.py logs datetime -f    # Follow service logs
```

### DateTime Service Usage Patterns by Agent

**Product Owner Agent (POA):**
- User story timestamps: `get_current_time("America/New_York")`
- Sprint planning: `calculate_sprint_dates("2025-01-06", 14)`
- Stakeholder meeting scheduling: `convert_timezone("2025-01-15T14:00:00", "UTC", "Europe/London")`

**Scrum Master Agent (SMA):**
- Sprint progress tracking: `get_time_until("2025-01-20T17:00:00Z")`
- Ceremony timing: `add_time("2025-01-13T09:00:00Z", hours=1)`
- Retrospective scheduling: `calculate_business_days("2025-01-06", "2025-01-20")`

**QA Agent (QAA):**
- Test execution duration: `calculate_duration("2025-01-10T09:00:00Z", "2025-01-10T17:00:00Z")`
- Bug age tracking: `get_relative_time("2025-01-05T10:30:00Z")`
- Review deadlines: `add_time("2025-01-15T09:00:00Z", days=3)`

**Security Audit Agent (SAA):**
- Vulnerability remediation deadlines: `add_time("2025-01-10T00:00:00Z", days=30)`
- Certificate expiration monitoring: `get_time_until("2025-12-31T23:59:59Z")`
- Security review scheduling: `calculate_business_days("2025-01-15", "2025-01-30")`

### MCP Configuration Structure

The `.mcp.json` file configures all MCP services:

```json
{
  "mcpServers": {
    "datetime": {
      "command": "python",
      "args": ["mcp_servers/datetime/server.py"],
      "description": "Built-in datetime service for time operations"
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/project/path"],
      "description": "Filesystem access for project files"
    },
    "git": {
      "command": "npx", 
      "args": ["-y", "@modelcontextprotocol/server-git"],
      "description": "Git operations for version control"
    }
  }
}
```

### DateTime Service Dependencies

```bash
# Required dependencies (auto-installed)
pip install pytz>=2024.1
pip install python-dateutil>=2.8.2
pip install mcp>=0.1.0
```

### Performance Characteristics

- **Response Time**: All DateTime operations complete in <50ms
- **Memory Usage**: Typically <10MB RAM per service instance
- **Timezone Support**: Full pytz timezone database (500+ timezones)
- **Business Day Rules**: Configurable holidays and weekend handling
- **Sprint Alignment**: Automatic Monday alignment for Agile workflows

### Testing and Validation

The DateTime service includes comprehensive testing:

```bash
# Run DateTime integration tests
python -m pytest tests/test_mcp_integration.py -v

# Test specific functionality
python -c "
import sys; sys.path.append('mcp_servers/datetime')
from datetime_tools import DateTimeTools
dt = DateTimeTools()
print(dt.get_current_time('UTC'))
"
```

### Troubleshooting DateTime Service

**Service won't start:**
- Check dependencies: `pip install -r mcp_servers/datetime/requirements.txt`
- Verify Python path: `which python`
- Check logs: `python scripts/mcp_manager.py logs datetime`

**Performance issues:**
- Monitor memory: `python scripts/mcp_manager.py health datetime`
- Check service status: `./init.sh mcp-status`
- Restart service: `python scripts/mcp_manager.py restart datetime`

**Timezone errors:**
- Update pytz: `pip install --upgrade pytz`
- Verify timezone names: Use standard IANA timezone identifiers
- Check system locale settings

### DateTime Service Architecture

```
mcp_servers/datetime/
├── datetime_tools.py    # Core DateTime functionality (9 methods)
├── server.py           # MCP server wrapper with tool registration  
├── requirements.txt    # Service dependencies
└── README.md          # Service documentation

logs/
├── datetime_stdout.log # Service output logs
├── datetime_stderr.log # Service error logs
└── mcp_manager.log    # Service manager logs

.mcp_pids/
└── datetime.pid       # Service process ID file
```

The DateTime service is designed for:
- **High Availability**: Automatic restart capabilities
- **Production Reliability**: Comprehensive error handling
- **Developer Experience**: Clear APIs and consistent responses
- **AgenticScrum Integration**: Optimized for Agile workflows

## Important Implementation Details

1. **Template Loading**: Uses Jinja2 FileSystemLoader with trim_blocks and lstrip_blocks enabled for clean output
2. **Error Handling**: CLI provides user-friendly error messages and falls back to interactive mode gracefully
3. **Extensibility**: New languages and agents can be added by creating appropriate templates
4. **MCP Integration**: Generates `.mcp.json` configuration for Claude Code integration when Claude agents are selected
5. **File Permissions**: Automatically sets executable permissions on generated scripts (init.sh)
6. **Testing**: Comprehensive test coverage including CLI parsing, file generation, permissions, and security features
7. **Package Distribution**: Includes all templates via setup.py package_data configuration
8. **Security**: Generates `.sample` files for sensitive configs and comprehensive `.gitignore` patterns
9. **Framework Support**: Automatically adjusts project structure based on framework selection (FastAPI, Express, React, etc.)
10. **Agent Optimization**: Feedback loop system allows continuous improvement of agent configurations based on performance metrics
11. **MCP DateTime Service**: Production-ready DateTime service with <50ms response time, comprehensive timezone support, and Agile-optimized sprint calculations