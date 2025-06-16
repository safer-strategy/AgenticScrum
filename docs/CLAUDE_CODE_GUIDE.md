# Claude Code Integration Guide

This guide provides comprehensive information for using AgenticScrum with Claude Code (claude.ai/code).

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Model Selection Best Practices](#model-selection-best-practices)
- [Parameter Handling](#parameter-handling)
- [Agent-Specific Recommendations](#agent-specific-recommendations)
- [Tips for Optimal Performance](#tips-for-optimal-performance)
- [Troubleshooting](#troubleshooting)

## Overview

AgenticScrum is fully optimized for Claude Code, providing seamless integration with Claude's powerful AI models. The framework automatically configures optimal settings when used with Claude Code, while maintaining flexibility for other LLM providers.

## Quick Start

### Using the CLI with Claude Code Flag

The fastest way to set up a project for Claude Code:

```bash
agentic-scrum-setup init \
  --project-name MyProject \
  --language python \
  --agents poa,sma,deva_python,qaa \
  --claude-code
```

This automatically configures:
- Provider: `anthropic`
- Model: `claude-sonnet-4-0`
- Claude Code-optimized settings

### Interactive Mode for Claude Code

When running `agentic-scrum-setup init` without arguments, you'll be asked:

```
Are you using Claude Code? (Y/n):
```

Answering "Y" will automatically configure optimal settings for Claude Code.

## Model Selection Best Practices

Claude Code provides multiple models via the `/model` command. Here's when to use each:

### Claude Opus 4 (`/model opus`)
**Alias:** `claude-opus-4-0`  
**Best for:**
- Complex architectural decisions
- System design and planning
- Analyzing intricate requirements
- Security audits requiring deep analysis
- Extended thinking for challenging problems

**AgenticScrum Agents:** Recommended for POA (Product Owner) and SAA (Security Audit)

### Claude Sonnet 4 (`/model sonnet`) - RECOMMENDED DEFAULT
**Alias:** `claude-sonnet-4-0`  
**Best for:**
- General development tasks
- Code generation and refactoring
- Writing tests and documentation
- Code reviews
- Most day-to-day programming tasks

**AgenticScrum Agents:** Recommended for SMA (Scrum Master), DEVA (Developer), and QAA (QA)

### Claude Haiku 3.5 (`/model haiku`)
**Alias:** `claude-3-5-haiku-latest`  
**Best for:**
- Quick fixes and simple tasks
- Syntax corrections
- Simple explanations
- Rapid prototyping

## Parameter Handling

### Important Note on Model Parameters

When using Claude Code, the IDE controls these parameters directly:
- **Temperature**: Set via IDE preferences
- **Max Tokens**: Determined by Claude Code
- **Response Format**: Managed by the IDE

The AgenticScrum configuration files include these parameters for documentation and compatibility with other providers, but they are **ignored when using Claude Code**.

### Configuration Example

In your `agentic_config.yaml`:
```yaml
llm:
  provider: "anthropic"
  model: "claude-sonnet-4-0"  # Uses model alias for future-proofing
  api_key: "${ANTHROPIC_API_KEY}"  # Not needed for Claude Code
```

In agent persona files:
```yaml
llm_config:
  provider: "anthropic"
  model: "claude-sonnet-4-0"
  # Note: Temperature and max_tokens are controlled by Claude Code
  # temperature: 0.3  # Informational only
  # max_tokens: 4096  # Informational only
```

## Agent-Specific Recommendations

### Product Owner Agent (POA)
- **Recommended Model**: `claude-opus-4-0`
- **Use Case**: Complex requirement analysis, user story creation, backlog management
- **Switch Command**: `/model opus` when working on POA tasks

### Scrum Master Agent (SMA)
- **Recommended Model**: `claude-sonnet-4-0`
- **Use Case**: Sprint coordination, process optimization, team facilitation
- **Switch Command**: `/model sonnet` (default)

### Developer Agents (DEVA)
- **Recommended Model**: `claude-sonnet-4-0`
- **Use Case**: Code generation, implementation, refactoring
- **Benefits**: 64K token output capacity for large code generation
- **Switch Command**: `/model sonnet` (default)

### QA Agent (QAA)
- **Recommended Model**: `claude-sonnet-4-0`
- **Use Case**: Code review, test generation, quality checks
- **Switch Command**: `/model sonnet` (default)

### Security Audit Agent (SAA)
- **Recommended Model**: `claude-opus-4-0`
- **Use Case**: Deep security analysis, vulnerability assessment
- **Benefits**: Extended thinking capability for thorough analysis
- **Switch Command**: `/model opus` when performing security audits

## Tips for Optimal Performance

### 1. Model Switching Strategy
- Start with Sonnet 4 as your default
- Switch to Opus 4 for complex planning or deep analysis
- Use Haiku for quick, simple tasks to save time

### 2. Context Management
- Claude Code maintains conversation context automatically
- Use clear, descriptive file and function names
- Reference specific files using the pattern `filename.ext:line_number`

### 3. Working with Agents
- Let each agent focus on their specialized domain
- Use agent personas to maintain consistent behavior
- Reference the agent's `persona_rules.yaml` for their capabilities

### 4. Code Generation
- Leverage Sonnet 4's 64K output capacity for large files
- Use iterative refinement for complex implementations
- Always verify generated code with QAA practices

### 5. Performance Optimization
- Use appropriate models for each task (don't use Opus for simple fixes)
- Batch related tasks together
- Clear context when switching between major features

## Troubleshooting

### Common Issues and Solutions

#### Issue: Model parameters not being respected
**Solution**: Remember that Claude Code controls temperature and max_tokens directly. These settings in config files are informational only.

#### Issue: API key errors when using Claude Code
**Solution**: Claude Code doesn't require API keys. These are only needed for standalone API usage.

#### Issue: Model not found errors
**Solution**: Use the model aliases (e.g., `claude-sonnet-4-0`) instead of specific model IDs. These aliases always point to the latest version.

#### Issue: Conflicting agent recommendations
**Solution**: Follow the agent-specific model recommendations above. When in doubt, use Sonnet 4.

### Getting Help

1. Check the agent's `persona_rules.yaml` for configuration details
2. Review the generated `CLAUDE.md` in your project root
3. Consult the main AgenticScrum documentation
4. Report issues at: https://github.com/safer-strategy/AgenticScrum/issues

## Best Practices Summary

1. **Use Model Aliases**: Always use aliases like `claude-sonnet-4-0` for future compatibility
2. **Default to Sonnet 4**: It's the best balance of speed and capability
3. **Switch Models Purposefully**: Use `/model` commands based on task complexity
4. **Ignore Parameter Warnings**: Temperature and token settings in configs are for other providers
5. **Leverage Agent Specialization**: Let each agent work with their recommended model

## Conclusion

AgenticScrum with Claude Code provides a powerful, structured approach to AI-driven development. By following these guidelines and leveraging the appropriate models for each task, you can maximize productivity while maintaining code quality and project organization.