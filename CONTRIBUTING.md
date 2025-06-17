# Contributing to AgenticScrum

Thank you for your interest in contributing to AgenticScrum! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Process](#development-process)
- [How to Contribute](#how-to-contribute)
- [Style Guidelines](#style-guidelines)
- [Testing](#testing)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct:

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on constructive criticism
- Accept feedback gracefully
- Prioritize the project's best interests

## Getting Started

### Prerequisites

- Python 3.8+
- Git
- Docker (for testing)
- A GitHub account

### Setting Up Your Development Environment

1. **Fork the repository**
   ```bash
   # Click "Fork" on GitHub, then clone your fork:
   git clone https://github.com/YOUR_USERNAME/AgenticScrum.git
   cd AgenticScrum
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies**
   ```bash
   pip install -r requirements-dev.txt
   pip install -e .
   ```

4. **Set up pre-commit hooks (coming soon)**
   ```bash
   pre-commit install
   ```

## Development Process

We follow the AgenticScrum methodology for our own development:

1. **Stories**: All work should be tracked in a story following our template
2. **Branches**: Create feature branches from `main`
3. **Testing**: Write tests for new functionality
4. **Documentation**: Update docs as needed
5. **Review**: All changes require code review

### Creating a New Story

1. Use the story template: `docs/STORY_TEMPLATE.md`
2. Place your story in the `spec/` directory
3. Name it: `STORY_XXX_BRIEF_DESCRIPTION.md`
4. Update the story as you work

### Branch Naming

- Feature: `feature/story-xxx-brief-description`
- Bugfix: `fix/story-xxx-brief-description`
- Documentation: `docs/brief-description`

## How to Contribute

### Reporting Bugs

1. Check if the bug is already reported in [Issues](https://github.com/safer-strategy/AgenticScrum/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - System information
   - Any relevant logs or screenshots

### Suggesting Features

1. Check existing issues and discussions
2. Open a new issue with the "enhancement" label
3. Describe the feature and its benefits
4. Provide use cases and examples

### Submitting Code

1. **Find or create an issue** for your contribution
2. **Comment on the issue** to claim it
3. **Create a feature branch** from `main`
4. **Write your code** following our style guidelines
5. **Write/update tests** as needed
6. **Update documentation** if applicable
7. **Submit a pull request**

## Style Guidelines

### Python Code Style

We follow PEP 8 with these additions:

```python
# Good: Descriptive variable names
project_name = "MyProject"
agent_configuration = load_config()

# Bad: Single letter or unclear names
p = "MyProject"
conf = load_config()
```

### Key Principles

1. **Clarity over cleverness**
2. **Explicit over implicit**
3. **Consistent naming conventions**
4. **Comprehensive docstrings**
5. **Type hints where beneficial**

### Code Formatting

```bash
# Format code with black
black agentic_scrum_setup/ tests/

# Check linting
flake8 agentic_scrum_setup/ tests/

# Type checking
mypy agentic_scrum_setup/
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=agentic_scrum_setup

# Run specific test file
pytest tests/test_setup_core.py

# Run with verbose output
pytest -xvs
```

### Writing Tests

1. **Test file naming**: `test_*.py`
2. **Test class naming**: `TestFeatureName`
3. **Test method naming**: `test_specific_behavior`
4. **Use fixtures** for common setup
5. **Test edge cases** and error conditions

Example:
```python
def test_project_creation_with_mcp_enabled(tmp_path):
    """Test that project creation works with MCP integration enabled."""
    config = {
        'project_name': 'TestProject',
        'output_dir': str(tmp_path),
        'enable_mcp': True
    }
    setup = SetupCore(config)
    setup.create_project()
    
    assert (tmp_path / 'TestProject' / '.agent-memory').exists()
```

### Test Coverage

- Aim for >95% code coverage
- Focus on testing behavior, not implementation
- Test both success and failure paths

## Documentation

### Types of Documentation

1. **Code Comments**: Explain "why", not "what"
2. **Docstrings**: All public functions/classes
3. **README**: Keep updated with new features
4. **User Guides**: In the `docs/` directory
5. **API Reference**: Generated from docstrings

### Documentation Style

```python
def create_project(config: Dict[str, Any]) -> None:
    """Create a new AgenticScrum project.
    
    Args:
        config: Project configuration dictionary containing:
            - project_name: Name of the project
            - language: Primary programming language
            - agents: List of AI agents to include
            
    Raises:
        ValueError: If configuration is invalid
        FileExistsError: If project already exists
        
    Example:
        >>> config = {'project_name': 'MyApp', 'language': 'python'}
        >>> create_project(config)
    """
```

## Pull Request Process

### Before Submitting

1. **Update your branch**
   ```bash
   git checkout main
   git pull upstream main
   git checkout your-feature-branch
   git rebase main
   ```

2. **Run all checks**
   ```bash
   pytest
   black --check .
   flake8
   ```

3. **Update documentation** and CHANGELOG.md

### PR Description Template

```markdown
## Description
Brief description of changes

## Related Issue
Fixes #123

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement

## Testing
- [ ] All tests pass
- [ ] Added new tests
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
```

### Review Process

1. **Automated checks** must pass
2. **Code review** by at least one maintainer
3. **Address feedback** promptly
4. **Squash commits** if requested
5. **Merge** when approved

## Release Process

1. **Version bump** following semantic versioning
2. **Update CHANGELOG.md** with release notes
3. **Tag release** on GitHub
4. **PyPI deployment** (automated)

## Getting Help

- **Discord**: [Join our community](#)
- **Discussions**: Use GitHub Discussions
- **Issues**: For bugs and features
- **Email**: maintainers@agenticscrum.dev

## Recognition

Contributors are recognized in:
- CHANGELOG.md for significant contributions
- GitHub contributors page
- Project documentation

Thank you for contributing to AgenticScrum! 🚀