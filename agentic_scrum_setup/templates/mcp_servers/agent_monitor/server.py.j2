#!/usr/bin/env python3
"""
Agent Monitor MCP Server for AgenticScrum Background Agent System

This MCP server monitors background agent health, resource usage,
and provides real-time status information.
"""

import json
import sqlite3
import asyncio
import psutil
import os
import signal
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
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

class AgentMonitorServer:
    """MCP Server for monitoring background agent processes."""
    
    def __init__(self):
        self.server = Server("agent-monitor")
        self.db_path = Path.home() / ".agenticscrum" / "agent_monitor.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.project_root = Path.cwd()
        self.logs_dir = self.project_root / "logs" / "background_agents"
        self.init_database()
        self.setup_tools()
        
    def init_database(self):
        """Initialize SQLite database for monitoring data."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_processes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pid INTEGER NOT NULL,
                agent_type TEXT NOT NULL,
                story_id TEXT NOT NULL,
                session_id TEXT UNIQUE NOT NULL,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_heartbeat TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'running',
                cpu_percent REAL,
                memory_mb REAL,
                file_descriptors INTEGER,
                metadata TEXT
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_status ON agent_processes(status);
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_session ON agent_processes(session_id);
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                cpu_percent REAL,
                memory_mb REAL,
                file_descriptors INTEGER,
                io_reads INTEGER,
                io_writes INTEGER,
                FOREIGN KEY (session_id) REFERENCES agent_processes(session_id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                event_type TEXT NOT NULL,
                message TEXT,
                metadata TEXT,
                FOREIGN KEY (session_id) REFERENCES agent_processes(session_id)
            )
        """)
        
        conn.commit()
        conn.close()
        logger.info(f"Database initialized at {self.db_path}")
        
    def setup_tools(self):
        """Register MCP tools for agent monitoring."""
        
        @self.server.tool(
            "register_agent",
            "Register a new background agent process",
            {
                "pid": {"type": "integer", "description": "Process ID"},
                "agent_type": {"type": "string", "description": "Agent type"},
                "story_id": {"type": "string", "description": "Story being worked on"},
                "session_id": {"type": "string", "description": "Unique session identifier"}
            }
        )
        async def register_agent(pid: int, agent_type: str, 
                               story_id: str, session_id: str) -> TextContent:
            """Register a new agent process."""
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            try:
                # Get initial metrics
                metrics = self._get_process_metrics(pid)
                
                cursor.execute("""
                    INSERT INTO agent_processes 
                    (pid, agent_type, story_id, session_id, cpu_percent, memory_mb, file_descriptors)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    pid, agent_type, story_id, session_id,
                    metrics.get("cpu_percent", 0),
                    metrics.get("memory_mb", 0),
                    metrics.get("file_descriptors", 0)
                ))
                
                conn.commit()
                
                # Log registration event
                cursor.execute("""
                    INSERT INTO agent_events (session_id, event_type, message)
                    VALUES (?, ?, ?)
                """, (session_id, "registered", f"Agent {agent_type} started on {story_id}"))
                
                conn.commit()
                
                return TextContent(
                    type="text",
                    text=json.dumps({
                        "success": True,
                        "message": f"Registered agent {session_id}"
                    })
                )
                
            except sqlite3.IntegrityError:
                return TextContent(
                    type="text",
                    text=json.dumps({
                        "success": False,
                        "error": f"Session {session_id} already registered"
                    })
                )
            finally:
                conn.close()
        
        @self.server.tool(
            "heartbeat",
            "Update agent heartbeat and metrics",
            {
                "session_id": {"type": "string", "description": "Session identifier"}
            }
        )
        async def heartbeat(session_id: str) -> TextContent:
            """Update agent heartbeat."""
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Get PID for session
            cursor.execute("SELECT pid FROM agent_processes WHERE session_id = ?", (session_id,))
            row = cursor.fetchone()
            
            if not row:
                conn.close()
                return TextContent(
                    type="text",
                    text=json.dumps({
                        "success": False,
                        "error": f"Session {session_id} not found"
                    })
                )
            
            pid = row[0]
            metrics = self._get_process_metrics(pid)
            
            if metrics:
                # Update heartbeat and metrics
                cursor.execute("""
                    UPDATE agent_processes
                    SET last_heartbeat = CURRENT_TIMESTAMP,
                        cpu_percent = ?,
                        memory_mb = ?,
                        file_descriptors = ?
                    WHERE session_id = ?
                """, (
                    metrics["cpu_percent"],
                    metrics["memory_mb"],
                    metrics["file_descriptors"],
                    session_id
                ))
                
                # Record metrics
                cursor.execute("""
                    INSERT INTO performance_metrics 
                    (session_id, cpu_percent, memory_mb, file_descriptors, io_reads, io_writes)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    session_id,
                    metrics["cpu_percent"],
                    metrics["memory_mb"],
                    metrics["file_descriptors"],
                    metrics.get("io_reads", 0),
                    metrics.get("io_writes", 0)
                ))
                
                conn.commit()
                status = "alive"
            else:
                # Process not found
                cursor.execute("""
                    UPDATE agent_processes
                    SET status = 'dead'
                    WHERE session_id = ?
                """, (session_id,))
                
                conn.commit()
                status = "dead"
            
            conn.close()
            
            return TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "status": status,
                    "metrics": metrics
                })
            )
        
        @self.server.tool(
            "list_agents",
            "List active background agents",
            {
                "include_dead": {"type": "boolean", "description": "Include dead processes", "default": False}
            }
        )
        async def list_agents(include_dead: bool = False) -> TextContent:
            """List agent processes."""
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            if include_dead:
                cursor.execute("""
                    SELECT session_id, pid, agent_type, story_id, status, 
                           started_at, last_heartbeat, cpu_percent, memory_mb
                    FROM agent_processes
                    ORDER BY started_at DESC
                """)
            else:
                cursor.execute("""
                    SELECT session_id, pid, agent_type, story_id, status,
                           started_at, last_heartbeat, cpu_percent, memory_mb
                    FROM agent_processes
                    WHERE status = 'running'
                    ORDER BY started_at DESC
                """)
            
            agents = cursor.fetchall()
            conn.close()
            
            # Check if processes are still alive
            agent_list = []
            for agent in agents:
                session_id, pid, agent_type, story_id, status, started_at, last_heartbeat, cpu, memory = agent
                
                # Check if process is actually running
                is_alive = self._is_process_alive(pid)
                
                agent_list.append({
                    "session_id": session_id,
                    "pid": pid,
                    "agent_type": agent_type,
                    "story_id": story_id,
                    "status": "running" if is_alive else "dead",
                    "started_at": started_at,
                    "last_heartbeat": last_heartbeat,
                    "cpu_percent": cpu,
                    "memory_mb": memory,
                    "uptime_minutes": self._calculate_uptime(started_at)
                })
            
            return TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "count": len(agent_list),
                    "agents": agent_list
                })
            )
        
        @self.server.tool(
            "get_metrics",
            "Get detailed metrics for an agent",
            {
                "session_id": {"type": "string", "description": "Session identifier"},
                "duration_minutes": {"type": "integer", "description": "History duration", "default": 60}
            }
        )
        async def get_metrics(session_id: str, duration_minutes: int = 60) -> TextContent:
            """Get agent performance metrics."""
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Get agent info
            cursor.execute("""
                SELECT pid, agent_type, story_id, status, started_at
                FROM agent_processes
                WHERE session_id = ?
            """, (session_id,))
            
            agent = cursor.fetchone()
            if not agent:
                conn.close()
                return TextContent(
                    type="text",
                    text=json.dumps({
                        "success": False,
                        "error": f"Session {session_id} not found"
                    })
                )
            
            pid, agent_type, story_id, status, started_at = agent
            
            # Get recent metrics
            cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=duration_minutes)
            cursor.execute("""
                SELECT timestamp, cpu_percent, memory_mb, file_descriptors, io_reads, io_writes
                FROM performance_metrics
                WHERE session_id = ? AND timestamp > ?
                ORDER BY timestamp DESC
                LIMIT 100
            """, (session_id, cutoff_time.isoformat()))
            
            metrics = cursor.fetchall()
            
            # Get recent events
            cursor.execute("""
                SELECT timestamp, event_type, message
                FROM agent_events
                WHERE session_id = ?
                ORDER BY timestamp DESC
                LIMIT 20
            """, (session_id,))
            
            events = cursor.fetchall()
            conn.close()
            
            # Calculate statistics
            if metrics:
                cpu_values = [m[1] for m in metrics if m[1] is not None]
                memory_values = [m[2] for m in metrics if m[2] is not None]
                
                stats = {
                    "avg_cpu_percent": sum(cpu_values) / len(cpu_values) if cpu_values else 0,
                    "max_cpu_percent": max(cpu_values) if cpu_values else 0,
                    "avg_memory_mb": sum(memory_values) / len(memory_values) if memory_values else 0,
                    "max_memory_mb": max(memory_values) if memory_values else 0
                }
            else:
                stats = {
                    "avg_cpu_percent": 0,
                    "max_cpu_percent": 0,
                    "avg_memory_mb": 0,
                    "max_memory_mb": 0
                }
            
            return TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "agent": {
                        "session_id": session_id,
                        "pid": pid,
                        "agent_type": agent_type,
                        "story_id": story_id,
                        "status": status,
                        "started_at": started_at,
                        "uptime_minutes": self._calculate_uptime(started_at)
                    },
                    "statistics": stats,
                    "recent_metrics": [
                        {
                            "timestamp": m[0],
                            "cpu_percent": m[1],
                            "memory_mb": m[2],
                            "file_descriptors": m[3],
                            "io_reads": m[4],
                            "io_writes": m[5]
                        } for m in metrics[:10]  # Last 10 data points
                    ],
                    "recent_events": [
                        {
                            "timestamp": e[0],
                            "event_type": e[1],
                            "message": e[2]
                        } for e in events
                    ]
                })
            )
        
        @self.server.tool(
            "terminate_agent",
            "Terminate a background agent process",
            {
                "session_id": {"type": "string", "description": "Session identifier"},
                "force": {"type": "boolean", "description": "Force kill if graceful fails", "default": False}
            }
        )
        async def terminate_agent(session_id: str, force: bool = False) -> TextContent:
            """Terminate an agent process."""
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute("SELECT pid FROM agent_processes WHERE session_id = ?", (session_id,))
            row = cursor.fetchone()
            
            if not row:
                conn.close()
                return TextContent(
                    type="text",
                    text=json.dumps({
                        "success": False,
                        "error": f"Session {session_id} not found"
                    })
                )
            
            pid = row[0]
            
            try:
                if self._is_process_alive(pid):
                    # Try graceful termination first
                    os.kill(pid, signal.SIGTERM)
                    
                    # Wait a bit
                    await asyncio.sleep(2)
                    
                    # Check if still alive
                    if self._is_process_alive(pid) and force:
                        os.kill(pid, signal.SIGKILL)
                    
                    # Update status
                    cursor.execute("""
                        UPDATE agent_processes
                        SET status = 'terminated'
                        WHERE session_id = ?
                    """, (session_id,))
                    
                    # Log event
                    cursor.execute("""
                        INSERT INTO agent_events (session_id, event_type, message)
                        VALUES (?, ?, ?)
                    """, (session_id, "terminated", "Process terminated by user"))
                    
                    conn.commit()
                    message = "Process terminated successfully"
                else:
                    message = "Process was already dead"
                
                conn.close()
                return TextContent(
                    type="text",
                    text=json.dumps({
                        "success": True,
                        "message": message
                    })
                )
                
            except ProcessLookupError:
                conn.close()
                return TextContent(
                    type="text",
                    text=json.dumps({
                        "success": True,
                        "message": "Process not found (already terminated)"
                    })
                )
            except Exception as e:
                conn.close()
                return TextContent(
                    type="text",
                    text=json.dumps({
                        "success": False,
                        "error": str(e)
                    })
                )
        
        @self.server.tool(
            "get_logs",
            "Get agent execution logs",
            {
                "session_id": {"type": "string", "description": "Session identifier"},
                "lines": {"type": "integer", "description": "Number of lines", "default": 100}
            }
        )
        async def get_logs(session_id: str, lines: int = 100) -> TextContent:
            """Get agent logs."""
            log_file = self.logs_dir / f"{session_id}.log"
            
            if not log_file.exists():
                return TextContent(
                    type="text",
                    text=json.dumps({
                        "success": False,
                        "error": f"Log file not found for session {session_id}"
                    })
                )
            
            try:
                # Read last N lines
                with open(log_file, 'r') as f:
                    all_lines = f.readlines()
                    last_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
                
                return TextContent(
                    type="text",
                    text=json.dumps({
                        "success": True,
                        "session_id": session_id,
                        "line_count": len(last_lines),
                        "logs": "".join(last_lines)
                    })
                )
            except Exception as e:
                return TextContent(
                    type="text",
                    text=json.dumps({
                        "success": False,
                        "error": str(e)
                    })
                )
        
        @self.server.tool(
            "cleanup_dead",
            "Clean up dead agent records",
            {
                "older_than_hours": {"type": "integer", "description": "Clean records older than N hours", "default": 24}
            }
        )
        async def cleanup_dead(older_than_hours: int = 24) -> TextContent:
            """Clean up old dead agent records."""
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=older_than_hours)
            
            # Get sessions to clean
            cursor.execute("""
                SELECT session_id
                FROM agent_processes
                WHERE status IN ('dead', 'terminated')
                AND last_heartbeat < ?
            """, (cutoff_time.isoformat(),))
            
            sessions = [row[0] for row in cursor.fetchall()]
            
            if sessions:
                # Delete metrics
                cursor.execute("""
                    DELETE FROM performance_metrics
                    WHERE session_id IN ({})
                """.format(','.join('?' * len(sessions))), sessions)
                
                # Delete events
                cursor.execute("""
                    DELETE FROM agent_events
                    WHERE session_id IN ({})
                """.format(','.join('?' * len(sessions))), sessions)
                
                # Delete agent records
                cursor.execute("""
                    DELETE FROM agent_processes
                    WHERE session_id IN ({})
                """.format(','.join('?' * len(sessions))), sessions)
                
                conn.commit()
            
            conn.close()
            
            return TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "cleaned": len(sessions),
                    "message": f"Cleaned {len(sessions)} dead agent records"
                })
            )
    
    def _get_process_metrics(self, pid: int) -> Optional[Dict[str, Any]]:
        """Get process metrics using psutil."""
        try:
            process = psutil.Process(pid)
            
            # Get CPU percent (non-blocking)
            cpu_percent = process.cpu_percent(interval=0.1)
            
            # Get memory info
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
            
            # Get file descriptors
            try:
                file_descriptors = len(process.open_files())
            except:
                file_descriptors = 0
            
            # Get I/O counters if available
            try:
                io_counters = process.io_counters()
                io_reads = io_counters.read_count
                io_writes = io_counters.write_count
            except:
                io_reads = 0
                io_writes = 0
            
            return {
                "cpu_percent": round(cpu_percent, 2),
                "memory_mb": round(memory_mb, 2),
                "file_descriptors": file_descriptors,
                "io_reads": io_reads,
                "io_writes": io_writes
            }
            
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return None
    
    def _is_process_alive(self, pid: int) -> bool:
        """Check if process is alive."""
        try:
            process = psutil.Process(pid)
            return process.is_running()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return False
    
    def _calculate_uptime(self, started_at: str) -> float:
        """Calculate uptime in minutes."""
        try:
            start_time = datetime.fromisoformat(started_at.replace('Z', '+00:00'))
            now = datetime.now(timezone.utc)
            delta = now - start_time
            return round(delta.total_seconds() / 60, 2)
        except:
            return 0.0
    
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
    
    server = AgentMonitorServer()
    asyncio.run(server.run())