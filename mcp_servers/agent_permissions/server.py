#!/usr/bin/env python3
"""
Agent Permissions MCP Server for AgenticScrum Background Agent System

This MCP server handles permission requests from background agents,
allowing them to make autonomous decisions within defined security boundaries.
"""

import json
import sqlite3
import asyncio
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
import os
import sys
import re

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from mcp import Server, Tool
from mcp.types import TextContent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AgentPermissionsServer:
    """MCP Server for handling autonomous agent permission requests."""
    
    def __init__(self):
        self.server = Server("agent-permissions")
        self.db_path = Path.home() / ".agenticscrum" / "agent_permissions.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.permission_mode = os.environ.get("PERMISSION_MODE", "autonomous")
        self.agent_id = os.environ.get("AGENT_ID", "unknown")
        self.init_database()
        self.setup_tools()
        self.load_permission_rules()
        
    def init_database(self):
        """Initialize SQLite database for permission audit logging."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS permission_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                agent_id TEXT NOT NULL,
                tool_name TEXT NOT NULL,
                input_data TEXT,
                decision TEXT NOT NULL,
                reason TEXT,
                story_id TEXT,
                metadata TEXT
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_agent_id ON permission_logs(agent_id);
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_decision ON permission_logs(decision);
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS permission_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_type_pattern TEXT NOT NULL,
                tool_pattern TEXT NOT NULL,
                action TEXT NOT NULL,
                priority INTEGER DEFAULT 0,
                conditions TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
        logger.info(f"Database initialized at {self.db_path}")
        
    def load_permission_rules(self):
        """Load default permission rules for agents."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Check if we have rules
        cursor.execute("SELECT COUNT(*) FROM permission_rules")
        if cursor.fetchone()[0] == 0:
            # Insert default rules
            default_rules = [
                # Developer agents can read/write code
                ("deva_*", "Read", "allow", 10, None),
                ("deva_*", "Write", "allow", 10, None),
                ("deva_*", "Edit", "allow", 10, None),
                ("deva_*", "MultiEdit", "allow", 10, None),
                ("deva_*", "Glob", "allow", 10, None),
                ("deva_*", "Grep", "allow", 10, None),
                ("deva_*", "LS", "allow", 10, None),
                
                # Bash commands need validation
                ("deva_*", "Bash", "validate", 5, json.dumps({
                    "allowed_patterns": [
                        r"^(npm|yarn|pnpm) (install|test|run|build)",
                        r"^python.*\.(py|test)",
                        r"^pytest",
                        r"^git (status|diff|log|branch)",
                        r"^(ls|pwd|echo|cat|grep|find)",
                        r"^mkdir -p",
                        r"^touch"
                    ],
                    "denied_patterns": [
                        r"rm -rf",
                        r"sudo",
                        r"chmod \+x",
                        r"curl.*\|(bash|sh)",
                        r"git (push|commit|merge|checkout|reset)"
                    ]
                })),
                
                # MCP tools generally allowed
                ("*", "mcp__memory__*", "allow", 8, None),
                ("*", "mcp__datetime__*", "allow", 8, None),
                ("*", "mcp__filesystem__*", "allow", 8, None),
                ("*", "mcp__agent_queue__*", "allow", 8, None),
                ("*", "mcp__agent_monitor__*", "allow", 8, None),
                
                # SMA has broader permissions
                ("sma", "*", "allow", 15, None),
                
                # QAA can search
                ("qaa", "WebSearch", "allow", 10, None),
                
                # Notebook operations for Python devs
                ("deva_python", "NotebookRead", "allow", 10, None),
                ("deva_python", "NotebookEdit", "allow", 10, None),
                
                # Todo operations for SMA
                ("sma", "TodoRead", "allow", 10, None),
                ("sma", "TodoWrite", "allow", 10, None),
                
                # Default deny for unlisted
                ("*", "*", "deny", 0, None)
            ]
            
            for rule in default_rules:
                cursor.execute("""
                    INSERT INTO permission_rules 
                    (agent_type_pattern, tool_pattern, action, priority, conditions)
                    VALUES (?, ?, ?, ?, ?)
                """, rule)
            
            conn.commit()
            logger.info("Loaded default permission rules")
        
        conn.close()
        
    def setup_tools(self):
        """Register MCP tools for permission handling."""
        
        @self.server.tool(
            "approve",
            "Handle permission request from background agent",
            {
                "tool_name": {"type": "string", "description": "Tool requesting permission"},
                "input": {"type": "object", "description": "Input parameters for the tool"},
                "agent_id": {"type": "string", "description": "Agent requesting permission", "default": None},
                "story_id": {"type": "string", "description": "Current story being worked on", "default": None}
            }
        )
        async def approve(tool_name: str, input: Dict[str, Any], 
                        agent_id: Optional[str] = None, 
                        story_id: Optional[str] = None) -> TextContent:
            """Handle permission request based on rules."""
            
            # Use provided agent_id or fall back to environment
            agent_id = agent_id or self.agent_id
            story_id = story_id or os.environ.get("STORY_ID", "unknown")
            
            # Check permission rules
            decision, reason = await self.check_permission(agent_id, tool_name, input)
            
            # Log the decision
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO permission_logs 
                (agent_id, tool_name, input_data, decision, reason, story_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                agent_id, 
                tool_name, 
                json.dumps(input), 
                decision,
                reason,
                story_id
            ))
            
            conn.commit()
            conn.close()
            
            # Return formatted response
            if decision == "allow":
                return TextContent(
                    type="text",
                    text=json.dumps({
                        "behavior": "allow",
                        "updatedInput": input
                    })
                )
            else:
                return TextContent(
                    type="text",
                    text=json.dumps({
                        "behavior": "deny",
                        "message": reason or f"Permission denied for {tool_name}"
                    })
                )
        
        @self.server.tool(
            "add_rule",
            "Add a new permission rule",
            {
                "agent_type_pattern": {"type": "string", "description": "Agent type pattern (e.g., deva_*, sma)"},
                "tool_pattern": {"type": "string", "description": "Tool name pattern (e.g., Bash, mcp__*)"},
                "action": {"type": "string", "description": "Action to take", "enum": ["allow", "deny", "validate"]},
                "priority": {"type": "integer", "description": "Rule priority (higher wins)", "default": 5},
                "conditions": {"type": "object", "description": "Additional conditions", "default": None}
            }
        )
        async def add_rule(agent_type_pattern: str, tool_pattern: str, 
                         action: str, priority: int = 5, 
                         conditions: Optional[Dict[str, Any]] = None) -> TextContent:
            """Add a new permission rule."""
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO permission_rules 
                (agent_type_pattern, tool_pattern, action, priority, conditions)
                VALUES (?, ?, ?, ?, ?)
            """, (
                agent_type_pattern,
                tool_pattern,
                action,
                priority,
                json.dumps(conditions) if conditions else None
            ))
            
            conn.commit()
            rule_id = cursor.lastrowid
            conn.close()
            
            return TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "rule_id": rule_id,
                    "message": f"Added {action} rule for {agent_type_pattern} using {tool_pattern}"
                })
            )
        
        @self.server.tool(
            "list_rules",
            "List permission rules",
            {
                "agent_type": {"type": "string", "description": "Filter by agent type", "default": None}
            }
        )
        async def list_rules(agent_type: Optional[str] = None) -> TextContent:
            """List permission rules."""
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            if agent_type:
                # Get rules that would apply to this agent type
                cursor.execute("""
                    SELECT id, agent_type_pattern, tool_pattern, action, priority, conditions
                    FROM permission_rules
                    WHERE ? GLOB agent_type_pattern OR agent_type_pattern = '*'
                    ORDER BY priority DESC
                """, (agent_type,))
            else:
                cursor.execute("""
                    SELECT id, agent_type_pattern, tool_pattern, action, priority, conditions
                    FROM permission_rules
                    ORDER BY priority DESC
                """)
            
            rules = cursor.fetchall()
            conn.close()
            
            rule_list = []
            for rule in rules:
                rule_list.append({
                    "id": rule[0],
                    "agent_type_pattern": rule[1],
                    "tool_pattern": rule[2],
                    "action": rule[3],
                    "priority": rule[4],
                    "conditions": json.loads(rule[5]) if rule[5] else None
                })
            
            return TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "count": len(rule_list),
                    "rules": rule_list
                })
            )
        
        @self.server.tool(
            "get_audit_log",
            "Get permission audit log",
            {
                "agent_id": {"type": "string", "description": "Filter by agent", "default": None},
                "decision": {"type": "string", "description": "Filter by decision", "default": None},
                "limit": {"type": "integer", "description": "Maximum results", "default": 100}
            }
        )
        async def get_audit_log(agent_id: Optional[str] = None,
                              decision: Optional[str] = None,
                              limit: int = 100) -> TextContent:
            """Get permission audit log."""
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            query = """
                SELECT timestamp, agent_id, tool_name, decision, reason, story_id
                FROM permission_logs
            """
            conditions = []
            params = []
            
            if agent_id:
                conditions.append("agent_id = ?")
                params.append(agent_id)
            
            if decision:
                conditions.append("decision = ?")
                params.append(decision)
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            logs = cursor.fetchall()
            conn.close()
            
            log_list = []
            for log in logs:
                log_list.append({
                    "timestamp": log[0],
                    "agent_id": log[1],
                    "tool_name": log[2],
                    "decision": log[3],
                    "reason": log[4],
                    "story_id": log[5]
                })
            
            return TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "count": len(log_list),
                    "logs": log_list
                })
            )
    
    async def check_permission(self, agent_id: str, tool_name: str, 
                             input_data: Dict[str, Any]) -> tuple[str, str]:
        """Check if agent has permission for tool based on rules."""
        
        # Extract agent type from agent_id (e.g., "deva_python_001" -> "deva_python")
        agent_type = "_".join(agent_id.split("_")[:-1]) if "_" in agent_id else agent_id
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Find matching rules
        cursor.execute("""
            SELECT action, priority, conditions
            FROM permission_rules
            WHERE (? GLOB agent_type_pattern OR agent_type_pattern = '*')
            AND (? GLOB tool_pattern OR tool_pattern = '*')
            ORDER BY priority DESC
            LIMIT 1
        """, (agent_type, tool_name))
        
        rule = cursor.fetchone()
        conn.close()
        
        if not rule:
            return "deny", "No matching permission rule found"
        
        action, priority, conditions = rule
        
        if action == "allow":
            return "allow", f"Permitted by rule (priority {priority})"
        
        elif action == "deny":
            return "deny", f"Denied by rule (priority {priority})"
        
        elif action == "validate":
            # Validate based on conditions
            if conditions:
                conditions_dict = json.loads(conditions)
                
                # Special handling for Bash commands
                if tool_name == "Bash" and "command" in input_data:
                    command = input_data["command"]
                    
                    # Check denied patterns first
                    if "denied_patterns" in conditions_dict:
                        for pattern in conditions_dict["denied_patterns"]:
                            if re.search(pattern, command, re.IGNORECASE):
                                return "deny", f"Command matches denied pattern: {pattern}"
                    
                    # Check allowed patterns
                    if "allowed_patterns" in conditions_dict:
                        for pattern in conditions_dict["allowed_patterns"]:
                            if re.search(pattern, command, re.IGNORECASE):
                                return "allow", f"Command matches allowed pattern: {pattern}"
                        
                        # No match in allowed patterns
                        return "deny", "Command does not match any allowed patterns"
            
            # Default validation result
            return "allow", "Passed validation"
        
        return "deny", "Unknown action type"
    
    async def run(self):
        """Run the MCP server."""
        from mcp.server.stdio import stdio_server
        
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )

if __name__ == "__main__":
    import asyncio
    
    server = AgentPermissionsServer()
    asyncio.run(server.run())