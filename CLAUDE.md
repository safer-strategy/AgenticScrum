# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AgenticScrum is an open-source framework for structured AI-driven code generation that combines Scrum methodologies with AI agents. The project provides a fully-implemented CLI tool (`agentic-scrum-setup`) that scaffolds new AI-driven development projects with standardized structure and agent configurations.

## Key Architecture & Structure

### Core Implementation

The project is implemented as a Python package with the following structure:

```
agentic_scrum_setup/
├── cli.py          # CLI entry point with argument parsing and interactive mode
├── setup_core.py   # Core project generation logic using Jinja2 templates
└── templates/      # Jinja2 templates for all generated files
```

**Key Classes:**
- `SetupCore` (setup_core.py:14) - Handles project generation, template rendering, and file creation
- CLI functions (cli.py) - Provides both command-line and interactive interfaces

### Template System

Templates are organized by purpose in `agentic_scrum_setup/templates/`:
- `claude/` - Claude-specific configurations (CLAUDE.md, .mcp.json, persona_rules.yaml)
- `common/` - Shared files (init.sh, docker-compose.yml)
- `checklists/` - Quality checklists for development workflow
- `standards/` - Coding standards templates
- Language-specific directories (`python/`, `javascript/`)

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

# Run specific test file
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
# Run in interactive mode
agentic-scrum-setup init

# Run with all arguments
agentic-scrum-setup init \
  --project-name "MyProject" \
  --language python \
  --agents poa,sma,deva_claude_python,qaa \
  --llm-provider anthropic \
  --default-model claude-3-opus-20240229 \
  --output-dir ./projects
```

### Building and Distribution

```bash
# Build distribution packages
python setup.py sdist bdist_wheel

# Upload to PyPI (requires credentials)
twine upload dist/*
```

## Architecture Notes

### CLI Design
The CLI supports both command-line arguments and interactive mode. When required arguments are missing, it automatically falls back to interactive prompts. See `interactive_mode()` function in cli.py:61.

### Template Rendering
All project files are generated using Jinja2 templates with the following context variables:
- `project_name` - Name of the project being created
- `language` - Primary programming language
- `agents` - List of selected AI agents
- `llm_provider` - Selected LLM provider
- `default_model` - Default model for the provider

### File Permissions
The `init.sh` script is automatically made executable using proper Unix permissions (setup_core.py:116). This is tested in test_setup_core.py:74.

### Agent Configuration
Agents are mapped to directory structures in setup_core.py:94. Claude-specific agents get specialized templates from the `claude/` directory.

## Important Implementation Details

1. **Template Loading**: Uses Jinja2 FileSystemLoader with trim_blocks and lstrip_blocks enabled for clean output
2. **Error Handling**: CLI provides user-friendly error messages and falls back to interactive mode gracefully
3. **Extensibility**: New languages and agents can be added by creating appropriate templates
4. **Testing**: Comprehensive test coverage including CLI parsing, file generation, and permissions
5. **Package Distribution**: Includes all templates via MANIFEST.in configuration