# Development Procedures

This document outlines the standardized development procedures for AgenticScrum, including build, testing, and release workflows.

## Build System

AgenticScrum uses modern Python packaging with PEP 625 compliance for PyPI distribution.

### Prerequisites

```bash
# Install build dependencies
pip install build twine

# Install development dependencies
pip install -r requirements-dev.txt
```

### Modern Build Commands (PEP 625 Compliant)

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info/

# Build source distribution and wheel
python -m build --sdist --wheel

# Validate package integrity
twine check dist/*

# Generated files (PEP 625 compliant):
# - dist/agentic_scrum_setup-X.Y.Z-py3-none-any.whl
# - dist/agentic_scrum_setup-X.Y.Z.tar.gz (underscores for compliance)
```

### Legacy vs Modern Build

**❌ Old (deprecated):**
```bash
python setup.py sdist bdist_wheel  # Non-PEP 625 compliant
```

**✅ New (PEP 625 compliant):**
```bash
python -m build --sdist --wheel    # Automatic compliance
```

## Release Workflow

### Version Management

1. **Update version** in `agentic_scrum_setup/__init__.py`:
   ```python
   __version__ = "1.0.0-beta.X"
   ```

2. **Update documentation** version references:
   - `README.md`
   - `BETA_LAUNCH.md`
   - `spec/STORY_*.md` files as needed

### PyPI Release Process

```bash
# 1. Build the package
python -m build --sdist --wheel

# 2. Validate package integrity
twine check dist/*

# 3. Upload to Test PyPI (optional)
twine upload --repository testpypi dist/*

# 4. Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ agentic-scrum-setup==X.Y.Z

# 5. Upload to Production PyPI
twine upload dist/*

# 6. Verify global availability
pip install agentic-scrum-setup==X.Y.Z
```

### Documentation Updates

After each release, update:

1. **Version references** in all documentation
2. **Installation commands** with latest version
3. **Story completion status** in spec/ files
4. **CLAUDE.md** with any new procedures

## Testing Procedures

### Unit Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=agentic_scrum_setup

# Run specific test file
pytest agentic_scrum_setup/tests/test_cli.py
```

### Integration Testing

```bash
# Test CLI functionality
./init.sh new  # Interactive mode
./init.sh quick TestProject  # Quick mode

# Test PyPI installation
pip install agentic-scrum-setup==X.Y.Z
agentic-scrum-setup init --project-name "Test" --language python
```

### Code Quality

```bash
# Format code
black agentic_scrum_setup/ tests/

# Lint code
flake8 agentic_scrum_setup/ tests/

# Type checking
mypy agentic_scrum_setup/
```

## Development Best Practices

### File Structure Updates

When creating new files:
```bash
# Update directory tree
tree --gitignore > dir_tree.txt

# Commit changes
git add .
git commit -m "descriptive message"
git push
```

### Story Management

1. **Create new stories** in `spec/` directory using `docs/STORY_TEMPLATE.md`
2. **Update story status** as work progresses
3. **Complete stories** with final status and timestamps

### Configuration Changes

When modifying build configuration:

1. **Test locally** with `python -m build`
2. **Validate** with `twine check dist/*`
3. **Update documentation** as needed
4. **Version bump** for releases

## Build Configuration Files

### pyproject.toml

Modern Python packaging configuration with:
- PEP 625 compliant build system
- SPDX license format
- Dynamic version loading
- Comprehensive dependencies

### setup.py

Minimal compatibility wrapper:
```python
from setuptools import setup
setup()  # All config in pyproject.toml
```

### MANIFEST.in

Controls package file inclusion:
```
recursive-include agentic_scrum_setup/templates *.j2
recursive-include agentic_scrum_setup/templates *.sample
recursive-include agentic_scrum_setup/templates *.sh
recursive-include agentic_scrum_setup/templates *.py
recursive-include agentic_scrum_setup/templates *.md
recursive-include agentic_scrum_setup/templates *.txt
recursive-include agentic_scrum_setup/templates *.json
recursive-include agentic_scrum_setup/templates *.yaml
recursive-include agentic_scrum_setup/templates *.yml
```

## Troubleshooting

### Build Issues

**Problem:** Package files missing from distribution
**Solution:** Check MANIFEST.in includes all necessary file patterns

**Problem:** PEP 625 compliance warnings
**Solution:** Use `python -m build` instead of `setup.py`

**Problem:** License deprecation warnings
**Solution:** Use SPDX format in pyproject.toml: `license = "MIT"`

### PyPI Upload Issues

**Problem:** Filename not PEP 625 compliant
**Solution:** Modern build tools automatically handle normalization

**Problem:** Authentication errors
**Solution:** Use API tokens with `twine upload --username __token__ --password <token>`

## Continuous Integration

### GitHub Actions (Future)

```yaml
name: Build and Test
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install build twine
          pip install -r requirements-dev.txt
      - name: Build package
        run: python -m build
      - name: Validate package
        run: twine check dist/*
      - name: Run tests
        run: pytest --cov=agentic_scrum_setup
```

## Summary

This development procedure ensures:
- ✅ PEP 625 compliant builds
- ✅ Validated package integrity
- ✅ Consistent release workflow
- ✅ Comprehensive testing
- ✅ Modern Python packaging standards

Follow these procedures for all development work to maintain consistency and compliance with Python packaging standards.