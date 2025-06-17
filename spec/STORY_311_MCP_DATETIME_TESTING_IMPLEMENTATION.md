# Story 311: MCP DateTime Service Testing & Local Implementation

**Epic:** 03 - MCP Memory and Search Integration  
**Story Points:** 5  
**Priority:** P0 (Critical - Must validate our own implementation works!)  
**Status:** To Do  
**Assigned To:** [Developer Name]  
**Created:** 2025-01-18  
**Start Date:** [YYYY-MM-DD HH:MM]  
**Last Update:** [YYYY-MM-DD HH:MM]  
**Completed:** [YYYY-MM-DD HH:MM]  

## 📋 User Story

**As an AgenticScrum developer,** I want the DateTime MCP service tested and validated within the AgenticScrum project itself, **so that** we can ensure it works properly before deploying it to other projects and have a reference implementation for others to follow.

**⚠️ CRITICAL REQUIREMENTS:**
- **Dogfooding**: AgenticScrum project must use its own DateTime service
- **Real Validation**: Actual MCP communication testing, not just unit tests
- **Reference Implementation**: This becomes the example for other projects
- **Complete Infrastructure**: Service management, monitoring, and troubleshooting tools

## 🎯 Acceptance Criteria

### Phase 1: Local DateTime Service Setup (Critical)
- [ ] **AgenticScrum MCP Configuration**: Create `.mcp.json` for this project with DateTime service
- [ ] **Local DateTime Installation**: Copy and configure `mcp_servers/datetime/` in project root
- [ ] **Service Dependencies**: Install DateTime service dependencies and requirements
- [ ] **Agent Configuration**: Configure local agents to use the DateTime service
- [ ] **Service Management**: Add DateTime service management to local `init.sh`

### Phase 2: Validation & Testing
- [ ] **End-to-End Testing**: Test each agent persona (POA, SMA, QAA, SAA) using datetime functions
- [ ] **MCP Protocol Validation**: Verify actual Claude ↔ MCP server communication works
- [ ] **Performance Validation**: Confirm <50ms response time in real environment
- [ ] **Agent Integration Testing**: Test all datetime patterns from agent personas
- [ ] **Error Scenario Testing**: Test failure modes, invalid inputs, and service unavailability

### Phase 3: Management Infrastructure
- [ ] **MCP Service Manager**: Create `scripts/mcp_manager.py` for lifecycle management
- [ ] **Health Monitoring**: Implement service health checks and status reporting
- [ ] **Service Lifecycle**: Start/stop/restart/status commands for DateTime service
- [ ] **Logging & Debugging**: Comprehensive logging and troubleshooting tools
- [ ] **Dependency Automation**: Automated setup and installation scripts

### Phase 4: Documentation & Reference
- [ ] **Real Usage Examples**: Document actual DateTime service usage in AgenticScrum
- [ ] **Troubleshooting Guide**: Based on real issues encountered during implementation
- [ ] **Best Practices Documentation**: Lessons learned and optimization tips
- [ ] **Reference Implementation**: Complete setup guide for other projects

## 🔧 Technical Implementation Details

### Current Architecture Analysis
**Gap Identified**: We built a comprehensive DateTime MCP service but haven't tested it in a real AgenticScrum environment. This is a critical validation gap that could reveal integration issues, performance problems, or usability challenges.

**Current State**: 
- DateTime MCP service exists in templates
- Agent personas include datetime patterns
- No actual MCP configuration for AgenticScrum project
- No real-world testing or validation

### Phase 1 Implementation

#### 1. Create AgenticScrum MCP Configuration
**New File:** `.mcp.json`
```json
{
  "mcpServers": {
    "datetime": {
      "command": "python",
      "args": ["mcp_servers/datetime/server.py"],
      "description": "Built-in datetime service for AgenticScrum development"
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/AgenticScrum"],
      "description": "Filesystem access for AgenticScrum project"
    },
    "git": {
      "command": "npx", 
      "args": ["-y", "@modelcontextprotocol/server-git"],
      "description": "Git operations for version control"
    }
  },
  "projectContext": {
    "name": "AgenticScrum",
    "description": "AI-driven Agile development framework with MCP integration",
    "rootPath": "/AgenticScrum",
    "primaryLanguage": "python",
    "framework": "AgenticScrum"
  }
}
```

#### 2. Install DateTime Service Locally
**Action:** Copy DateTime service to project root
```bash
# Copy DateTime service from templates to project root
cp -r agentic_scrum_setup/templates/mcp_servers ./

# Install dependencies
cd mcp_servers/datetime
pip install -r requirements.txt
cd ../..
```

#### 3. Enhanced init.sh for MCP Management
**File:** `init.sh` (new file for AgenticScrum project)
```bash
#!/bin/bash

# MCP Service Management
function start_mcp_services() {
    info "Starting MCP services..."
    
    # Start DateTime service
    if [[ -f "mcp_servers/datetime/server.py" ]]; then
        python mcp_servers/datetime/server.py &
        DATETIME_PID=$!
        echo $DATETIME_PID > .datetime_service.pid
        success "DateTime MCP service started (PID: $DATETIME_PID)"
    fi
}

function stop_mcp_services() {
    info "Stopping MCP services..."
    
    if [[ -f ".datetime_service.pid" ]]; then
        kill $(cat .datetime_service.pid) 2>/dev/null
        rm .datetime_service.pid
        success "DateTime MCP service stopped"
    fi
}

function status_mcp_services() {
    info "MCP Service Status:"
    
    if [[ -f ".datetime_service.pid" ]] && kill -0 $(cat .datetime_service.pid) 2>/dev/null; then
        echo "  DateTime Service: ✅ Running (PID: $(cat .datetime_service.pid))"
    else
        echo "  DateTime Service: ❌ Stopped"
    fi
}
```

### Phase 2 Implementation

#### 1. End-to-End Testing Framework
**New File:** `tests/test_mcp_integration.py`
```python
#!/usr/bin/env python3
"""Integration tests for MCP DateTime service."""

import unittest
import asyncio
import json
from datetime import datetime
import subprocess
import time
import requests

class TestMCPDateTimeIntegration(unittest.TestCase):
    """Test MCP DateTime service integration."""
    
    @classmethod
    def setUpClass(cls):
        """Start MCP DateTime service for testing."""
        cls.server_process = subprocess.Popen([
            'python', 'mcp_servers/datetime/server.py'
        ])
        time.sleep(2)  # Allow service to start
    
    @classmethod 
    def tearDownClass(cls):
        """Stop MCP DateTime service."""
        cls.server_process.terminate()
        cls.server_process.wait()
    
    def test_datetime_service_health(self):
        """Test that DateTime service is running and responding."""
        # Implementation for health check
        pass
    
    def test_agent_datetime_integration(self):
        """Test that agents can use datetime functions."""
        # Test each agent persona's datetime patterns
        pass
    
    def test_performance_requirements(self):
        """Test that response times are under 50ms."""
        # Performance validation
        pass
```

#### 2. Agent Integration Validation
**Test Scenarios:**
- POA creating user stories with timestamps
- SMA tracking sprint progress and ceremony timing
- QAA monitoring test execution duration
- SAA tracking vulnerability remediation time

### Phase 3 Implementation

#### 1. MCP Service Manager
**New File:** `scripts/mcp_manager.py`
```python
#!/usr/bin/env python3
"""MCP Service Management Utility for AgenticScrum."""

import argparse
import subprocess
import json
import time
import psutil
from pathlib import Path
from typing import Dict, List, Optional

class MCPServiceManager:
    """Manage MCP services lifecycle."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.config_file = self.project_root / ".mcp.json"
        self.pid_dir = self.project_root / ".mcp_pids"
        self.pid_dir.mkdir(exist_ok=True)
    
    def start_service(self, service_name: str) -> bool:
        """Start a specific MCP service."""
        config = self._load_config()
        if service_name not in config.get("mcpServers", {}):
            print(f"Service {service_name} not found in configuration")
            return False
        
        service_config = config["mcpServers"][service_name]
        cmd = [service_config["command"]] + service_config["args"]
        
        try:
            process = subprocess.Popen(cmd)
            pid_file = self.pid_dir / f"{service_name}.pid"
            pid_file.write_text(str(process.pid))
            print(f"Started {service_name} (PID: {process.pid})")
            return True
        except Exception as e:
            print(f"Failed to start {service_name}: {e}")
            return False
    
    def stop_service(self, service_name: str) -> bool:
        """Stop a specific MCP service."""
        pid_file = self.pid_dir / f"{service_name}.pid"
        if not pid_file.exists():
            print(f"Service {service_name} is not running")
            return False
        
        try:
            pid = int(pid_file.read_text())
            process = psutil.Process(pid)
            process.terminate()
            process.wait(timeout=5)
            pid_file.unlink()
            print(f"Stopped {service_name}")
            return True
        except Exception as e:
            print(f"Failed to stop {service_name}: {e}")
            return False
    
    def status(self) -> Dict[str, bool]:
        """Get status of all MCP services."""
        config = self._load_config()
        status = {}
        
        for service_name in config.get("mcpServers", {}):
            pid_file = self.pid_dir / f"{service_name}.pid"
            if pid_file.exists():
                try:
                    pid = int(pid_file.read_text())
                    process = psutil.Process(pid)
                    status[service_name] = process.is_running()
                except:
                    status[service_name] = False
            else:
                status[service_name] = False
        
        return status
    
    def health_check(self, service_name: str) -> Dict[str, any]:
        """Perform health check on service."""
        # Implementation for service health validation
        pass
```

#### 2. Enhanced Logging and Monitoring
**Features:**
- Service startup/shutdown logging
- Performance metrics collection
- Error tracking and reporting
- Health check scheduling

### Testing Requirements

#### Unit Tests:
- [ ] MCP service manager functionality
- [ ] Health check accuracy
- [ ] Configuration validation
- [ ] Error handling scenarios

#### Integration Tests:
- [ ] Complete MCP communication workflow
- [ ] Agent datetime function usage
- [ ] Service lifecycle management
- [ ] Performance benchmarking under load

#### Manual Testing Scenarios:
- [ ] Start/stop DateTime service via init.sh
- [ ] Use DateTime functions in each agent persona
- [ ] Test service recovery after crashes
- [ ] Validate configuration changes take effect

## 🚧 Blockers

None identified - all dependencies are internal to the project

## 📝 Plan / Approach

### Phase 1: Foundation Setup (1 day)
1. Create `.mcp.json` configuration for AgenticScrum project
2. Copy DateTime service to project root (`mcp_servers/`)
3. Install dependencies and test basic functionality
4. Create basic init.sh with MCP management

### Phase 2: Testing & Validation (1.5 days)
1. Implement comprehensive integration tests
2. Test each agent persona with DateTime functions
3. Validate MCP protocol communication
4. Performance testing and optimization

### Phase 3: Management Infrastructure (1.5 days)
1. Build complete MCP service manager utility
2. Implement health monitoring and logging
3. Add advanced service lifecycle features
4. Create troubleshooting and diagnostic tools

### Phase 4: Documentation & Polish (1 day)
1. Document real usage examples and patterns
2. Create troubleshooting guide based on testing
3. Write best practices and optimization guide
4. Finalize reference implementation documentation

## 🔄 Progress Updates & Notes

**[YYYY-MM-DD HH:MM] (@[Developer]):**
- [Progress update or note]
- [Decisions made or issues encountered]
- [Next steps or blockers identified]

## ✅ Review Checklist

- [ ] AgenticScrum project configured with DateTime MCP service
- [ ] DateTime service running and accessible locally
- [ ] All agent personas successfully using datetime functions
- [ ] Complete MCP service management infrastructure
- [ ] Comprehensive integration tests passing
- [ ] Performance requirements validated (<50ms response time)
- [ ] Error handling and recovery mechanisms working
- [ ] Reference implementation documentation complete
- [ ] Pull Request created and linked: [PR #___]

## 🎉 Completion Notes

_To be filled when story is completed_

---

**Definition of Done:**
- [ ] AgenticScrum project successfully using its own DateTime MCP service
- [ ] Complete end-to-end testing of MCP communication
- [ ] Service management infrastructure implemented and tested
- [ ] Reference implementation documented with real examples
- [ ] No regression in existing functionality
- [ ] Performance targets met in real environment
- [ ] Troubleshooting guide created based on actual usage
- [ ] Merged to main development branch

**Dependencies:**
- Story 310 (DateTime MCP Service Implementation) - ✅ Completed

---

## 📚 Implementation Notes

### Why Local Testing is Critical

1. **Validation**: Ensures our DateTime service actually works in practice
2. **Reference Implementation**: Provides example for other AgenticScrum projects
3. **Issue Discovery**: Reveals integration problems before deployment
4. **Performance Validation**: Tests real-world performance characteristics
5. **User Experience**: Validates the agent interaction patterns work smoothly

### Success Metrics

1. **Functionality**: DateTime service responds to all agent requests
2. **Performance**: <50ms average response time under normal load
3. **Reliability**: Service stays running for 24+ hours without issues
4. **Usability**: Agents can effectively use datetime functions in workflows
5. **Maintainability**: Service can be easily started, stopped, and debugged

### Future Expansion

This implementation provides the foundation for:
- Additional MCP services (file operations, metrics, configuration)
- Multi-project MCP service deployment
- Advanced monitoring and alerting
- Performance optimization and scaling
- Integration with CI/CD pipelines