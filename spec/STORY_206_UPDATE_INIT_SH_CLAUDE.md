# Story 206: Update init.sh CLI Defaults for Claude Integration

**Epic:** 02 - Claude Model Integration and Optimization  
**Story Points:** 2  
**Priority:** P1 (High - Critical for Claude Code users)  
**Status:** To Do  
**Assigned To:** [Unassigned]  
**Created:** 2025-01-17  
**Last Update:** 2025-01-17 09:00  

## 📋 User Story

**As a Claude Code user,** I want init.sh to default to Anthropic/Claude configurations and provide model selection guidance, **so that** I can quickly set up AgenticScrum projects optimized for Claude without manual configuration changes.

**⚠️ CRITICAL REQUIREMENTS:**
- **Docker Management**: All developers must use `init.sh` to manage Docker containers
- **Regression Testing**: All changes should be tested for regression against existing functionality 
- **Project Requirements**: All changes should be compatible with the project requirements and architecture

## 🎯 Acceptance Criteria

### Default Configuration Updates
- [ ] **Default Provider**: Change DEFAULT_LLM_PROVIDER from "openai" to "anthropic" (line 23)
- [ ] **Default Model**: Change DEFAULT_MODEL from "gpt-4-turbo-preview" to "claude-sonnet-4-0" (line 24)
- [ ] **Quick Setup**: Update quick_setup function to use Anthropic defaults (lines 410-413)
- [ ] **Custom Setup**: Update custom_setup default values to use Anthropic (lines 457-458)

### Claude Model Selection
- [ ] **Provider Order**: Reorder LLM provider options to list Anthropic first (lines 339-342)
- [ ] **Model Selection Dialog**: When Anthropic is selected, show Claude model options with descriptions
- [ ] **Model Descriptions**: Include helpful descriptions for each Claude model:
  - claude-opus-4-0: Most capable - Best for planning & complex analysis
  - claude-sonnet-4-0: Balanced (Recommended) - Fast with 64K output
  - claude-3-5-sonnet-latest: Previous generation - Still very capable
  - claude-3-5-haiku-latest: Fastest - Good for simple tasks

### Claude Code Integration
- [ ] **Claude Code Prompt**: Add "Are you using Claude Code? (Y/n)" prompt in interactive mode
- [ ] **Parameter Guidance**: If Claude Code user, display note about model parameter handling
- [ ] **Model Recommendation**: Suggest claude-sonnet-4-0 as default for Claude Code users

### CLI Enhancements
- [ ] **--claude-code Flag**: Add new command-line flag that sets optimal Claude defaults
- [ ] **Help Text Update**: Update help text to mention Claude Code compatibility
- [ ] **Example Updates**: Change help examples to show Anthropic usage

## 🔧 Technical Implementation Details

### Current Architecture Analysis
**File:** `init.sh`
- **Current Defaults**: Lines 23-24 set OpenAI as default provider with gpt-4-turbo-preview
- **Current Flow**: Provider selection → Model uses provider default → No model-specific selection
- **Current State**: OpenAI-centric with Anthropic as option 2

### Required Changes

#### 1. Update Default Constants
**Location:** Lines 23-24
```bash
# Current
DEFAULT_LLM_PROVIDER="openai"
DEFAULT_MODEL="gpt-4-turbo-preview"

# New
DEFAULT_LLM_PROVIDER="anthropic"
DEFAULT_MODEL="claude-sonnet-4-0"
```

#### 2. Reorder and Enhance Provider Selection
**Current Implementation:** Lines 338-351
```bash
echo "1) OpenAI"
echo "2) Anthropic"
echo "3) Google"
echo "4) Local (Ollama)"
```

**New Implementation:**
```bash
echo "1) Anthropic (Claude)"
echo "2) OpenAI"
echo "3) Google"
echo "4) Local (Ollama)"

# Add Claude model selection when Anthropic chosen
if [ "$llm_choice" = "1" ]; then
    echo
    echo -e "${BOLD}Select Claude Model:${NC}"
    echo "1) claude-sonnet-4-0 (Balanced - Recommended)"
    echo "2) claude-opus-4-0 (Most capable - Complex tasks)"
    echo "3) claude-3-5-sonnet-latest (Previous generation)"
    echo "4) claude-3-5-haiku-latest (Fastest - Simple tasks)"
    read -p "$(echo -e ${BOLD}Choice [1-4]:${NC} )" model_choice
    # Set model based on choice
fi
```

#### 3. Add Claude Code Detection
**Location:** After project type selection (around line 158)
```bash
# Claude Code Integration Check
echo
read -p "$(echo -e ${BOLD}Are you using Claude Code? (Y/n):${NC} )" claude_code
if [ "$claude_code" != "n" ] && [ "$claude_code" != "N" ]; then
    echo -e "${CYAN}Note: Claude Code controls temperature and token limits${NC}"
    echo -e "${CYAN}Recommended model: claude-sonnet-4-0 for development${NC}"
    # Set flag for later use
    using_claude_code=true
fi
```

#### 4. Add --claude-code Command
**Location:** Main script logic (line 502+)
```bash
"claude-code")
    check_installation
    # Quick setup with Claude defaults
    project_name=$2
    if [ -z "$project_name" ]; then
        echo -e "${RED}Error: Project name required${NC}"
        echo -e "${YELLOW}Usage: ./init.sh claude-code <project-name>${NC}"
        exit 1
    fi
    # Run with optimal Claude settings
    ;;
```

### File Modification Plan

#### Primary Files to Modify:
1. **`init.sh`** (lines 23-24, 338-351, 410-413, 457-458, 502+)
   - Update default constants
   - Reorder provider selection
   - Add Claude model selection dialog
   - Add Claude Code detection
   - Update quick and custom setup defaults
   - Add --claude-code command

### Testing Requirements

#### Unit Tests:
- [ ] Default values correctly set to Anthropic/Claude
- [ ] Provider selection shows Anthropic first
- [ ] Claude model selection appears when Anthropic chosen
- [ ] --claude-code flag sets correct defaults

#### Integration Tests:
- [ ] Interactive mode with Claude selection works correctly
- [ ] Quick setup uses new defaults
- [ ] Custom setup suggests new defaults
- [ ] Generated commands use correct provider/model

#### Manual Testing Scenarios:
- [ ] Run ./init.sh new and verify Anthropic is option 1
- [ ] Select Anthropic and verify model selection dialog
- [ ] Test Claude Code prompt and guidance
- [ ] Run ./init.sh claude-code MyProject
- [ ] Verify backward compatibility with existing commands

## 🚧 Blockers

None identified

## 📝 Plan / Approach

### Phase 1: Update Defaults (30 min)
1. Update DEFAULT_LLM_PROVIDER and DEFAULT_MODEL
2. Update quick_setup function defaults
3. Update custom_setup function defaults

### Phase 2: Enhance Interactive Mode (45 min)
1. Reorder LLM provider options
2. Add Claude model selection dialog
3. Add Claude Code detection prompt
4. Update help text

### Phase 3: Add CLI Support (30 min)
1. Add --claude-code command handler
2. Update help documentation
3. Test all modes

## 🔄 Progress Updates & Notes

**[2025-01-17 09:00] (@Mike):**
- Story created based on gaps identified between init.sh and EPIC_2_CLAUDE_INTEGRATION.md
- All acceptance criteria align with Epic 02 requirements

## ✅ Review Checklist

- [ ] All default values updated to Anthropic/Claude
- [ ] Provider selection lists Anthropic first
- [ ] Claude model selection dialog implemented
- [ ] Claude Code detection and guidance added
- [ ] --claude-code flag working correctly
- [ ] Help text updated with Claude examples
- [ ] Backward compatibility maintained
- [ ] Manual testing completed
- [ ] Pull Request created and linked: [PR #___]

## 🎉 Completion Notes

_To be filled when story is completed_

---

**Definition of Done:**
- [ ] Code implemented and peer-reviewed
- [ ] Manual testing completed against all acceptance criteria
- [ ] No regression in existing functionality
- [ ] Documentation updated (help text, examples)
- [ ] Merged to main development branch
- [ ] No critical bugs related to the story

**Dependencies:**
- Story 201 (Update Default Model Configurations) - ✅ Completed
- Story 202 (Update Agent Persona Templates) - ✅ Completed
- Story 203 (Update CLI and Interactive Mode) - ✅ Completed (except init.sh)