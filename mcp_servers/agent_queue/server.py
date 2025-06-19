#!/usr/bin/env python3
"""
Agent Queue MCP Server for AgenticScrum Background Agent System

This MCP server manages the task queue for background agent execution,
allowing the SMA to assign stories to agents and track their progress.
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

class AgentQueueServer:
    """MCP Server for managing background agent task queue."""
    
    def __init__(self):
        self.server = Server("agent-queue")
        self.db_path = Path.home() / ".agenticscrum" / "agent_queue.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_database()
        self.setup_tools()
        
    def init_database(self):
        """Initialize SQLite database for task queue."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                story_id TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                agent_type TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                priority INTEGER DEFAULT 5,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                assigned_to TEXT,
                result TEXT,
                error TEXT,
                metadata TEXT
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_status ON tasks(status);
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_agent_type ON tasks(agent_type);
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS task_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                level TEXT NOT NULL,
                message TEXT NOT NULL,
                FOREIGN KEY (task_id) REFERENCES tasks(id)
            )
        """)
        
        conn.commit()
        conn.close()
        logger.info(f"Database initialized at {self.db_path}")
        
    def setup_tools(self):
        """Register MCP tools for task queue management."""
        
        @self.server.tool(
            "assign_story",
            "Assign a story to a background agent for autonomous execution",
            {
                "story_id": {"type": "string", "description": "Unique story identifier (e.g., STORY_318)"},
                "title": {"type": "string", "description": "Brief story title"},
                "description": {"type": "string", "description": "Full story description and requirements"},
                "agent_type": {"type": "string", "description": "Agent type to assign (e.g., deva_python, deva_typescript)"},
                "priority": {"type": "integer", "description": "Priority level (1-10, higher is more urgent)", "default": 5},
                "metadata": {"type": "object", "description": "Additional metadata", "default": {}}
            }
        )
        async def assign_story(story_id: str, title: str, description: str, 
                             agent_type: str, priority: int = 5, 
                             metadata: Dict[str, Any] = {}) -> TextContent:
            """Assign a story to the task queue."""
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            try:
                cursor.execute("""
                    INSERT INTO tasks (story_id, title, description, agent_type, priority, metadata)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (story_id, title, description, agent_type, priority, json.dumps(metadata)))
                
                conn.commit()
                task_id = cursor.lastrowid
                
                # Log assignment
                cursor.execute("""
                    INSERT INTO task_logs (task_id, level, message)
                    VALUES (?, ?, ?)
                """, (task_id, "INFO", f"Story assigned to {agent_type}"))
                
                conn.commit()
                
                return TextContent(
                    type="text",
                    text=json.dumps({
                        "success": True,
                        "task_id": task_id,
                        "message": f"Story {story_id} assigned to {agent_type} with priority {priority}"
                    })
                )
                
            except sqlite3.IntegrityError:
                return TextContent(
                    type="text",
                    text=json.dumps({
                        "success": False,
                        "error": f"Story {story_id} already exists in queue"
                    })
                )
            finally:
                conn.close()
        
        @self.server.tool(
            "get_next_task",
            "Get the next task for a specific agent type",
            {
                "agent_type": {"type": "string", "description": "Agent type requesting work"},
                "agent_id": {"type": "string", "description": "Unique agent instance ID", "default": None}
            }
        )
        async def get_next_task(agent_type: str, agent_id: Optional[str] = None) -> TextContent:
            """Get next available task for an agent."""
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Find highest priority pending task for this agent type
            cursor.execute("""
                SELECT id, story_id, title, description, priority, metadata
                FROM tasks
                WHERE agent_type = ? AND status = 'pending'
                ORDER BY priority DESC, created_at ASC
                LIMIT 1
            """, (agent_type,))
            
            task = cursor.fetchone()
            
            if not task:
                conn.close()
                return TextContent(
                    type="text",
                    text=json.dumps({
                        "success": False,
                        "message": f"No pending tasks for {agent_type}"
                    })
                )
            
            task_id, story_id, title, description, priority, metadata = task
            
            # Mark as in progress
            cursor.execute("""
                UPDATE tasks
                SET status = 'in_progress', 
                    started_at = CURRENT_TIMESTAMP,
                    assigned_to = ?
                WHERE id = ?
            """, (agent_id or agent_type, task_id))
            
            # Log assignment
            cursor.execute("""
                INSERT INTO task_logs (task_id, level, message)
                VALUES (?, ?, ?)
            """, (task_id, "INFO", f"Task started by {agent_id or agent_type}"))
            
            conn.commit()
            conn.close()
            
            return TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "task": {
                        "id": task_id,
                        "story_id": story_id,
                        "title": title,
                        "description": description,
                        "priority": priority,
                        "metadata": json.loads(metadata) if metadata else {}
                    }
                })
            )
        
        @self.server.tool(
            "update_task_status",
            "Update the status of a task",
            {
                "story_id": {"type": "string", "description": "Story ID to update"},
                "status": {"type": "string", "description": "New status", 
                          "enum": ["pending", "in_progress", "completed", "failed", "cancelled"]},
                "result": {"type": "string", "description": "Task result or output", "default": None},
                "error": {"type": "string", "description": "Error message if failed", "default": None}
            }
        )
        async def update_task_status(story_id: str, status: str, 
                                   result: Optional[str] = None, 
                                   error: Optional[str] = None) -> TextContent:
            """Update task status."""
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Get task ID
            cursor.execute("SELECT id FROM tasks WHERE story_id = ?", (story_id,))
            task_row = cursor.fetchone()
            
            if not task_row:
                conn.close()
                return TextContent(
                    type="text",
                    text=json.dumps({
                        "success": False,
                        "error": f"Task {story_id} not found"
                    })
                )
            
            task_id = task_row[0]
            
            # Update status
            updates = ["status = ?"]
            params = [status]
            
            if status in ["completed", "failed", "cancelled"]:
                updates.append("completed_at = CURRENT_TIMESTAMP")
            
            if result:
                updates.append("result = ?")
                params.append(result)
            
            if error:
                updates.append("error = ?")
                params.append(error)
            
            params.append(story_id)
            
            cursor.execute(f"""
                UPDATE tasks
                SET {', '.join(updates)}
                WHERE story_id = ?
            """, params)
            
            # Log status change
            cursor.execute("""
                INSERT INTO task_logs (task_id, level, message)
                VALUES (?, ?, ?)
            """, (task_id, "INFO", f"Status changed to {status}"))
            
            conn.commit()
            conn.close()
            
            return TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "message": f"Task {story_id} status updated to {status}"
                })
            )
        
        @self.server.tool(
            "list_tasks",
            "List tasks with optional filtering",
            {
                "status": {"type": "string", "description": "Filter by status", "default": None},
                "agent_type": {"type": "string", "description": "Filter by agent type", "default": None},
                "limit": {"type": "integer", "description": "Maximum results", "default": 50}
            }
        )
        async def list_tasks(status: Optional[str] = None, 
                           agent_type: Optional[str] = None, 
                           limit: int = 50) -> TextContent:
            """List tasks from the queue."""
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            query = "SELECT story_id, title, agent_type, status, priority, created_at, started_at, completed_at FROM tasks"
            conditions = []
            params = []
            
            if status:
                conditions.append("status = ?")
                params.append(status)
            
            if agent_type:
                conditions.append("agent_type = ?")
                params.append(agent_type)
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY priority DESC, created_at DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            tasks = cursor.fetchall()
            
            conn.close()
            
            task_list = []
            for task in tasks:
                task_list.append({
                    "story_id": task[0],
                    "title": task[1],
                    "agent_type": task[2],
                    "status": task[3],
                    "priority": task[4],
                    "created_at": task[5],
                    "started_at": task[6],
                    "completed_at": task[7]
                })
            
            return TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "count": len(task_list),
                    "tasks": task_list
                })
            )
        
        @self.server.tool(
            "get_task_status",
            "Get detailed status of a specific task",
            {
                "story_id": {"type": "string", "description": "Story ID to check"}
            }
        )
        async def get_task_status(story_id: str) -> TextContent:
            """Get detailed task status."""
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, title, description, agent_type, status, priority,
                       created_at, started_at, completed_at, assigned_to,
                       result, error, metadata
                FROM tasks
                WHERE story_id = ?
            """, (story_id,))
            
            task = cursor.fetchone()
            
            if not task:
                conn.close()
                return TextContent(
                    type="text",
                    text=json.dumps({
                        "success": False,
                        "error": f"Task {story_id} not found"
                    })
                )
            
            task_id = task[0]
            
            # Get recent logs
            cursor.execute("""
                SELECT timestamp, level, message
                FROM task_logs
                WHERE task_id = ?
                ORDER BY timestamp DESC
                LIMIT 10
            """, (task_id,))
            
            logs = cursor.fetchall()
            conn.close()
            
            task_data = {
                "story_id": story_id,
                "title": task[1],
                "description": task[2],
                "agent_type": task[3],
                "status": task[4],
                "priority": task[5],
                "created_at": task[6],
                "started_at": task[7],
                "completed_at": task[8],
                "assigned_to": task[9],
                "result": task[10],
                "error": task[11],
                "metadata": json.loads(task[12]) if task[12] else {},
                "recent_logs": [
                    {
                        "timestamp": log[0],
                        "level": log[1],
                        "message": log[2]
                    } for log in logs
                ]
            }
            
            return TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "task": task_data
                })
            )
        
        @self.server.tool(
            "cancel_task",
            "Cancel a pending or in-progress task",
            {
                "story_id": {"type": "string", "description": "Story ID to cancel"}
            }
        )
        async def cancel_task(story_id: str) -> TextContent:
            """Cancel a task."""
            return await update_task_status(story_id, "cancelled", 
                                          error="Task cancelled by user")
        
        @self.server.tool(
            "get_queue_stats",
            "Get statistics about the task queue",
            {}
        )
        async def get_queue_stats() -> TextContent:
            """Get queue statistics."""
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Get counts by status
            cursor.execute("""
                SELECT status, COUNT(*) 
                FROM tasks 
                GROUP BY status
            """)
            status_counts = dict(cursor.fetchall())
            
            # Get counts by agent type
            cursor.execute("""
                SELECT agent_type, COUNT(*) 
                FROM tasks 
                WHERE status IN ('pending', 'in_progress')
                GROUP BY agent_type
            """)
            agent_counts = dict(cursor.fetchall())
            
            # Get average completion time
            cursor.execute("""
                SELECT AVG(julianday(completed_at) - julianday(started_at)) * 24 * 60
                FROM tasks
                WHERE status = 'completed' 
                AND completed_at IS NOT NULL 
                AND started_at IS NOT NULL
            """)
            avg_completion = cursor.fetchone()[0]
            
            conn.close()
            
            return TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "stats": {
                        "by_status": status_counts,
                        "by_agent": agent_counts,
                        "avg_completion_minutes": round(avg_completion, 2) if avg_completion else None,
                        "total_tasks": sum(status_counts.values())
                    }
                })
            )
    
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
    
    server = AgentQueueServer()
    asyncio.run(server.run())