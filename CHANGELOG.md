# Changelog

All notable changes to AgenticScrum will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0-beta.10] - 2025-01-21

### Added
- **Conversational Onboarding System** - Natural language project setup through POA-guided conversations
  - Users can describe projects in their own words instead of filling technical forms
  - Supports multiple input formats: informal descriptions, formal PRDs, technical specs
  - Automatic detection of existing projects for non-invasive retrofitting
  - New modules: conversational_onboarding.py and codebase_analyzer.py
  - --conversational flag for CLI
- **Autonomous QA Validation System** - Background QA agent monitoring and validation
  - Continuous quality checks without human intervention
  - qa_daemon.sh: Background monitoring service
  - qa_runner.py: Core QA execution engine with multiple validation modules
  - story_completion_trigger.py: Automated story completion detection
  - Enhanced agentic_config.yaml with QA-specific configurations
- Enhanced POA persona rules for conversational interactions
- Adaptive CLAUDE.md template for retrofit scenarios
- PRD.md and PROJECT_SUMMARY.md templates
- Comprehensive QA infrastructure templates

### Changed
- Updated init.sh with QA daemon management commands
- Enhanced setup_core.py to handle conversational mode and QA integration
- Improved README.md with documentation for new features

## [1.0.0-beta.9] - 2025-01-20

### Added
- Story 309: Production readiness fixes (4 test fixes, documentation alignment)
- Story 308: Project scoping questionnaire (PROJECT_SCOPE.md) and kickoff guide
- Story 307: Smart project location defaults and safety validation
- Story 306: MCP documentation and setup guides
- Story 305: Memory management utilities (export, analyze, prune)
- Story 304: Perplexity search integration for web search capabilities
- Story 303: Agent memory schemas and cross-agent sharing patterns
- Story 302: Memory directory structure with MCP configuration
- Story 301: Secure API key management system

### Changed
- Updated README to clarify workflow orchestration is a future feature
- Fixed test failures related to MCP integration prompts
- Improved security pattern matching to avoid false positives
- Made Perplexity search conditional in MCP configuration

### Fixed
- test_interactive_mode_with_defaults: Added missing MCP prompt input
- test_mcp_json_includes_perplexity: Enabled MCP in test configuration
- test_memory_directory_structure_supports_search_cache: Enabled MCP in test config
- test_no_hardcoded_secrets: Refined pattern matching to exclude model names

## [1.0.0-beta.2] - 2025-01-17

### Added
- Epic 3: MCP Memory and Search Integration
  - Persistent agent memory system
  - Perplexity search integration
  - Memory management utilities
  - Comprehensive MCP documentation

### Changed
- Updated all agent personas with memory patterns
- Enhanced security with API key validation

## [1.0.0-beta.1] - 2025-01-16

### Added
- Epic 2: Claude Model Integration and Optimization
  - Claude/Anthropic as default LLM provider
  - Model-specific recommendations per agent
  - Claude Code detection and optimization
  - --claude-code flag for quick setup

### Changed
- Default model changed to claude-sonnet-4-0
- Interactive mode prioritizes Anthropic
- Updated all documentation for Claude integration

## [1.0.0-alpha] - 2025-01-15

### Added
- Epic 1: Core AgenticScrum Scaffolding
  - CLI with init command
  - Interactive setup mode
  - 8 specialized AI agents (POA, SMA, DevA variants, QAA, SAA)
  - Multi-language support (9 languages)
  - Framework-specific project structures
  - Fullstack project support
  - Docker environment management
  - Comprehensive test suite

### Security
- Secure configuration templates
- API key environment variable management
- Comprehensive .gitignore patterns

## [0.1.0] - 2025-01-10

### Added
- Initial project structure
- Basic CLI framework
- Core agent templates
- Documentation framework

[Unreleased]: https://github.com/safer-strategy/AgenticScrum/compare/v1.0.0-beta.2...HEAD
[1.0.0-beta.2]: https://github.com/safer-strategy/AgenticScrum/compare/v1.0.0-beta.1...v1.0.0-beta.2
[1.0.0-beta.1]: https://github.com/safer-strategy/AgenticScrum/compare/v1.0.0-alpha...v1.0.0-beta.1
[1.0.0-alpha]: https://github.com/safer-strategy/AgenticScrum/compare/v0.1.0...v1.0.0-alpha
[0.1.0]: https://github.com/safer-strategy/AgenticScrum/releases/tag/v0.1.0