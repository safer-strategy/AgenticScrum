# Epic 02: Claude Model Integration

**Epic ID:** 02
**Epic Name:** Claude Model Integration and Optimization
**Epic Goal:** Update AgenticScrum to use Claude models as defaults, optimize agent configurations for Claude's capabilities, and ensure seamless integration with Claude Code IDE.

## Overview

This epic encompasses the complete transition from OpenAI-centric defaults to Claude/Anthropic defaults throughout the AgenticScrum framework. The implementation must maintain backward compatibility while optimizing for Claude Code usage.

### Key Principles
1. Use model aliases (e.g., `claude-sonnet-4-0`) instead of specific model IDs for future-proofing
2. Recognize that Claude Code controls actual model parameters (temperature, max_tokens)
3. Provide agent-specific model recommendations based on task complexity
4. Update all documentation and examples to reflect Claude as the primary use case

---

## Story 201: Update Default Model Configurations

**Story Points:** 3
**Priority:** P1 (High - Core configuration changes)
**Status:** Completed
**Dependencies:** None

### 📋 User Story

**As a** developer using Claude Code, **I want** AgenticScrum to default to Claude models with appropriate configurations, **so that** I can immediately start using the framework without manual configuration changes.

### 🎯 Acceptance Criteria

#### Generic Template Updates
- [x] Update `agentic_scrum_setup/templates/generic_persona_rules.yaml.j2`:
  - [x] Change line 9: `provider: "{{ llm_provider if llm_provider else 'anthropic' }}"`
  - [x] Change line 10: `model: "{{ default_model if default_model else 'claude-sonnet-4-0' }}"`
  - [x] Add comment after line 10: `# Model alias for future-proofing - maps to latest version`
  - [x] Comment out lines 11-12 (temperature, max_tokens) with explanation:
    ```yaml
    # Note: When using Claude Code, these parameters are controlled by the IDE
    # temperature: 0.3  # Informational only - Claude Code overrides this
    # max_tokens: 4096  # Informational only - Claude Code overrides this
    ```

#### Project Configuration Template
- [x] Update `agentic_scrum_setup/templates/agentic_config.yaml.j2`:
  - [x] Add comment after line 8 explaining provider options
  - [x] Add model selection guide comment after line 9:
    ```yaml
    # Claude model selection guide:
    # - claude-opus-4-0: Most capable, best for complex planning and architecture
    # - claude-sonnet-4-0: Fast & balanced, recommended for development (default)
    # - claude-3-5-haiku-latest: Fastest, good for simple tasks
    ```

#### Testing
- [ ] Verify generated files use anthropic as default provider
- [ ] Verify generated files use claude-sonnet-4-0 as default model
- [ ] Ensure backward compatibility with OpenAI configurations

---

## Story 202: Update Agent Persona Templates

**Story Points:** 5
**Priority:** P1 (High - Agent-specific optimizations)
**Status:** Completed
**Dependencies:** Story 201

### 📋 User Story

**As a** developer, **I want** each agent to have Claude-optimized configurations with appropriate model recommendations, **so that** agents perform optimally based on their specific responsibilities.

### 🎯 Acceptance Criteria

#### Product Owner Agent (POA)
- [x] Update `agentic_scrum_setup/templates/poa/persona_rules.yaml.j2`:
  - [x] Update llm_config section (lines 9-13):
    ```yaml
    llm_config:
      provider: "{{ llm_provider }}"
      model: "{{ default_model }}"
      # Recommended: claude-opus-4-0 for complex requirement analysis and planning
      # Note: Claude Code controls actual temperature and token limits
      # temperature: 0.3  # Lower for consistent requirement documentation
      # max_tokens: 4096  # Sufficient for detailed user stories
    ```

#### Scrum Master Agent (SMA)  
- [x] Update `agentic_scrum_setup/templates/sma/persona_rules.yaml.j2`:
  - [x] Update llm_config with recommendation:
    ```yaml
    # Recommended: claude-sonnet-4-0 for efficient process coordination
    ```

#### QA Agent (QAA)
- [x] Update `agentic_scrum_setup/templates/qaa/persona_rules.yaml.j2`:
  - [x] Update llm_config with recommendation:
    ```yaml
    # Recommended: claude-sonnet-4-0 for thorough code review and test generation
    ```

#### Security Audit Agent (SAA)
- [x] Update `agentic_scrum_setup/templates/saa/persona_rules.yaml.j2`:
  - [x] Update llm_config with recommendation:
    ```yaml
    # Recommended: claude-opus-4-0 for deep security analysis with extended thinking
    ```

#### Developer Agents (DEVA)
- [x] Updated generic_persona_rules.yaml.j2 which is used for all DEVA agents
- [x] Updated persona_rules_advanced.yaml.j2 for custom agent configurations
- [x] Each includes Claude-specific comments:
    ```yaml
    # Recommended: claude-sonnet-4-0 for fast code generation with 64K output capacity
    ```

#### Testing
- [ ] Generate project with all agents and verify configurations
- [ ] Ensure model recommendations are included as comments
- [ ] Verify no hardcoded temperature/max_tokens values

---

## Story 203: Update CLI and Interactive Mode

**Story Points:** 4
**Priority:** P1 (High - User-facing changes)
**Status:** Completed
**Dependencies:** Stories 201, 202

### 📋 User Story

**As a** user of the CLI, **I want** the interactive setup to prioritize Claude/Anthropic options and provide clear model selection guidance, **so that** I can easily configure my project for Claude Code.

### 🎯 Acceptance Criteria

#### CLI Updates
- [x] Update `agentic_scrum_setup/cli.py`:
  - [x] Modify LLM provider prompt to list 'anthropic' first
  - [x] Add Claude model selection when anthropic is chosen:
    ```python
    claude_models = [
        ('claude-opus-4-0', 'Most capable - Best for planning & complex analysis'),
        ('claude-sonnet-4-0', 'Balanced (Recommended) - Fast with 64K output'),
        ('claude-3-5-sonnet-latest', 'Previous generation - Still very capable'),
        ('claude-3-5-haiku-latest', 'Fastest - Good for simple tasks'),
    ]
    ```
  - [x] Update help text to mention Claude Code compatibility
  - [x] Add `--claude-code` flag that sets optimal defaults automatically

#### Default Examples
- [x] Update all CLI examples in help text to use:
  - `--llm-provider anthropic`
  - `--default-model claude-sonnet-4-0`

#### Interactive Mode Enhancements
- [x] Add prompt: "Are you using Claude Code? (Y/n)"
  - [x] If yes, add note about model parameter handling
  - [x] If yes, suggest claude-sonnet-4-0 as default

#### Testing
- [ ] Test interactive mode flow with Claude selection
- [ ] Verify --claude-code flag sets correct defaults
- [ ] Ensure backward compatibility with existing CLI args

---

## Story 204: Update Documentation and Examples

**Story Points:** 3
**Priority:** P2 (Medium - Documentation)
**Status:** Completed
**Dependencies:** Stories 201-203

### 📋 User Story

**As a** new user, **I want** all documentation and tutorials to show Claude/Anthropic examples, **so that** I can follow along using Claude Code without translation.

### 🎯 Acceptance Criteria

#### Tutorial.md Updates
- [x] Update all command examples:
  - [x] Line 71-72: Change to `--llm-provider "anthropic" --default-model "claude-sonnet-4-0"`
  - [x] Update the provider selection explanation
  - [x] Add new section "### Using with Claude Code" after Step 2

#### Claude Code Section Content
- [x] Include explanation of model parameter handling
- [x] Provide model selection strategy:
  ```markdown
  ### Model Selection Strategy
  - **Planning & Architecture**: Use `/model opus` for complex analysis
  - **Development**: Use `/model sonnet` (default) for coding
  - **Quick Tasks**: Use `/model haiku` for simple operations
  ```

#### README.md Updates  
- [x] Update main example to use Anthropic
- [x] Add "Claude Code Integration" section
- [x] Update compatibility notes

#### New Documentation
- [x] Create `docs/CLAUDE_CODE_GUIDE.md`:
  - [x] Model selection best practices
  - [x] Parameter handling explanation
  - [x] Tips for optimal performance
  - [x] Troubleshooting common issues

#### Testing
- [ ] Verify all examples are executable
- [ ] Check for any remaining OpenAI references
- [ ] Validate markdown formatting

---

## Story 205: Add Claude Code Integration Support

**Story Points:** 2
**Priority:** P2 (Medium - Enhancement)
**Status:** Completed
**Dependencies:** Stories 201-204

### 📋 User Story

**As a** Claude Code user, **I want** AgenticScrum to generate Claude Code-specific configuration files, **so that** my project integrates seamlessly with the IDE.

### 🎯 Acceptance Criteria

#### Claude Configuration Template
- [x] Update `agentic_scrum_setup/templates/claude/CLAUDE.md.j2`:
  - [x] Add model recommendation section
  - [x] Include AgenticScrum-specific guidance
  - [x] Add agent-to-model mapping guide

#### MCP Configuration
- [x] Create/update `.mcp.json` template:
  - [x] Include AgenticScrum-specific configuration
  - [x] Add model recommendations per agent
  - [x] Configure key paths and commands

#### Project Integration
- [x] Add to project generation when Claude agents selected:
  - [x] Generate CLAUDE.md in project root
  - [x] Include .mcp.json if applicable
  - [x] Updated logic to also generate for anthropic provider

#### Testing
- [ ] Generate project with Claude agents
- [ ] Verify CLAUDE.md contains correct information
- [ ] Test in actual Claude Code environment

---

## Implementation Notes

### File Change Summary
1. **Templates** (11 files):
   - generic_persona_rules.yaml.j2
   - agentic_config.yaml.j2
   - poa/persona_rules.yaml.j2
   - sma/persona_rules.yaml.j2
   - qaa/persona_rules.yaml.j2
   - saa/persona_rules.yaml.j2
   - claude/CLAUDE.md.j2
   - Developer agent templates (multiple)

2. **Code** (1 file):
   - cli.py

3. **Documentation** (3+ files):
   - Tutorial.md
   - README.md
   - New: docs/CLAUDE_CODE_GUIDE.md

### Migration Strategy
1. Maintain backward compatibility with `llm_provider` parameter
2. Use conditional defaults that check for existing OpenAI configs
3. Provide clear migration guide for existing users

### Testing Checklist
- [ ] Unit tests for CLI changes
- [ ] Integration tests for project generation
- [ ] Manual testing with Claude Code
- [ ] Regression testing with OpenAI configs
- [ ] Documentation review and validation

### Rollout Plan
1. Implement Stories 201-202 (Core configs)
2. Test thoroughly
3. Implement Stories 203-204 (User-facing)
4. Beta test with Claude Code users
5. Implement Story 205 (Enhancements)
6. Full release with migration guide